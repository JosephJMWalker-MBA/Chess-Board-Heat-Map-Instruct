import sys
import json
import hashlib
import struct
import subprocess
from src.chessheat.ml_runtime import configure_runtime, initialize_model_cpu_then_mps, build_frozen_adam, FROZEN_SEEDS

def hash_dict(d):
    import torch
    m = hashlib.sha256()
    for k in sorted(d.keys()):
        m.update(str(k).encode('utf-8'))
        v = d[k]
        if isinstance(v, torch.Tensor):
            t = v.cpu().detach().contiguous()
            m.update(str(t.dtype).encode('utf-8'))
            m.update(str(t.shape).encode('utf-8'))
            flat = t.view(-1)
            if t.dtype == torch.float32:
                float_list = flat.tolist()
                m.update(struct.pack(f'{len(float_list)}f', *float_list))
            elif t.dtype in (torch.long, torch.int64):
                long_list = flat.tolist()
                m.update(struct.pack(f'{len(long_list)}q', *long_list))
            elif t.dtype == torch.uint8:
                byte_list = flat.tolist()
                m.update(bytes(byte_list))
            else:
                raise RuntimeError(f"Unsupported dtype {t.dtype} for hashing")
        elif isinstance(v, dict):
            m.update(hash_dict(v).encode('utf-8'))
        else:
            m.update(str(v).encode('utf-8'))
    return m.hexdigest()

def get_frozen_learner_factory():
    import torch.nn as nn
    import torch
    class FrozenLearner(nn.Module):
        def __init__(self):
            super().__init__()
            self.conv1 = nn.Conv2d(19, 64, kernel_size=3, padding=1)
            self.relu1 = nn.ReLU()
            self.conv2 = nn.Conv2d(64, 64, kernel_size=3, padding=1)
            self.relu2 = nn.ReLU()
            self.conv3 = nn.Conv2d(64, 64, kernel_size=3, padding=1)
            self.relu3 = nn.ReLU()
            self.gap = nn.AdaptiveAvgPool2d((1, 1))
            self.side_linear = nn.Linear(270, 128)
            self.relu_side = nn.ReLU()
            self.fusion = nn.Linear(192, 128)
            self.relu_fusion = nn.ReLU()
            self.output = nn.Linear(128, 3)
            
        def forward(self, spatial, side):
            x = self.relu1(self.conv1(spatial))
            x = self.relu2(self.conv2(x))
            x = self.relu3(self.conv3(x))
            x = self.gap(x).view(x.size(0), -1)
            y = self.relu_side(self.side_linear(side))
            f = torch.cat([x, y], dim=1)
            f = self.relu_fusion(self.fusion(f))
            return self.output(f)
    return lambda torch_mod: FrozenLearner()

def assert_finite(t, name):
    import torch
    if not torch.isfinite(t).all():
        raise RuntimeError(f"Non-finite values in {name}")

def run_single_process(seed: int, batch_size: int, root_weighted: bool):
    ctx = configure_runtime(seed)
    torch = ctx.torch
    import torch.nn as nn
    
    model = initialize_model_cpu_then_mps(get_frozen_learner_factory(), ctx)
    optimizer = build_frozen_adam(model, torch)
    
    criterion = nn.CrossEntropyLoss(reduction="none" if root_weighted else "mean")
    
    spatial_tensor = (torch.arange(batch_size * 19 * 8 * 8, dtype=torch.float32).view(batch_size, 19, 8, 8) / (batch_size * 19 * 8 * 8)).to(ctx.device)
    side_tensor = (torch.arange(batch_size * 270, dtype=torch.float32).view(batch_size, 270) / (batch_size * 270)).to(ctx.device)
    target_tensor = (torch.arange(batch_size) % 3).to(torch.long).to(ctx.device)
    
    assert spatial_tensor.device.type == "mps"
    assert side_tensor.device.type == "mps"
    assert target_tensor.device.type == "mps"
    
    # roots: A=1, B=2, C=5 (if batch_size is 8)
    # We will just map the 8 elements. If batch_size != 8 and root_weighted=True, we adapt.
    if root_weighted:
        # Just map everything to 3 roots to test reduction
        roots = torch.tensor([0]*(batch_size//3) + [1]*(batch_size//3) + [2]*(batch_size - 2*(batch_size//3)), device=ctx.device)
    
    for _ in range(3):
        optimizer.zero_grad()
        logits = model(spatial_tensor, side_tensor)
        assert logits.device.type == "mps"
        assert_finite(logits, "logits")
        
        if root_weighted:
            unreduced_loss = criterion(logits, target_tensor)
            # mean within each root, then mean across roots
            mask0 = (roots == 0).float(); r0 = (unreduced_loss * mask0).sum() / mask0.sum().clamp(min=1)
            mask1 = (roots == 1).float(); r1 = (unreduced_loss * mask1).sum() / mask1.sum().clamp(min=1)
            mask2 = (roots == 2).float(); r2 = (unreduced_loss * mask2).sum() / mask2.sum().clamp(min=1)
            loss = (r0 + r1 + r2) / 3.0
        else:
            loss = criterion(logits, target_tensor)
            
        assert_finite(loss, "loss")
        loss.backward()
        
        for name, p in model.named_parameters():
            if p.grad is not None:
                assert_finite(p.grad, f"grad {name}")
                assert p.grad.device.type == "mps"
        

        optimizer.step()
        
        # Check optimizer state finiteness
        for param, state in optimizer.state.items():
            for key, val in state.items():
                if isinstance(val, torch.Tensor) and val.is_floating_point():
                    assert_finite(val, f"opt state {key}")
                    if val.dim() > 0:
                        assert val.device.type == "mps"

        
        for name, p in model.named_parameters():
            assert_finite(p, f"param {name}")
    
    torch.mps.synchronize()
    
    # Hashing
    h_model = hash_dict(model.state_dict())
    h_opt = hash_dict(optimizer.state_dict()['state'])
    h_cpu = hashlib.sha256(bytes(torch.get_rng_state().tolist())).hexdigest()
    h_mps = hashlib.sha256(bytes(torch.mps.get_rng_state().tolist())).hexdigest()
    
    print(f"MODEL:{h_model}")
    print(f"OPT:{h_opt}")
    print(f"CPU:{h_cpu}")
    print(f"MPS:{h_mps}")


def validate_triplicate_hashes(records, condition_name):
    if len(records) != 3:
        raise ValueError("Expected 3 records")
    for r in records:
        if "MODEL" not in r or "OPT" not in r or "CPU" not in r or "MPS" not in r:
            raise ValueError(f"Missing keys in record: {r}")
        for k in ["MODEL", "OPT", "CPU", "MPS"]:
            if not r[k] or len(r[k]) != 64:
                raise ValueError(f"Malformed {k} SHA in record: {r[k]}")
    
    # Assert equality across the 3 runs
    for k in ["MODEL", "OPT", "CPU", "MPS"]:
        if records[0][k] != records[1][k] or records[0][k] != records[2][k]:
            raise ValueError(f"Mismatch in {k} across 3 runs for {condition_name}")

def validate_v1_baseline(seed, records):
    expected_models = {
        1729: "26a5f5e7f8d4f6f5fd0e76603d57a9e02d59786acb3152ae69592c6836d3698f",
        2718: "31cc5f98b5706150de1f5965c8241aa1b89f509e558659b5b259bbef6c43f8c6",
        31415: "b118807352d234ac8c9c325e860ca5d9727c00ea827f4d4bd0f5ded153d8dc18",
        65537: "864cf3bd40362bc29ab858ed0fbb641922c91a353e5686148837a26dca475b40",
        104729: "0430e90e5f98afac47d8df07d949dac99f06f031127b5048e52eeb6da703d43f"
    }
    if seed not in expected_models:
        raise ValueError(f"Unknown seed {seed}")
    
    validate_triplicate_hashes(records, f"baseline_seed_{seed}")
    if records[0]["MODEL"] != expected_models[seed]:
        raise ValueError(f"Baseline mismatch for seed {seed}. Expected {expected_models[seed]}, got {records[0]['MODEL']}")

def main():
    if len(sys.argv) >= 3 and sys.argv[1] == "--run-subprocess":
        seed = int(sys.argv[2])
        batch_size = int(sys.argv[3])
        root_weighted = (sys.argv[4] == "1")
        run_single_process(seed, batch_size, root_weighted)
        sys.exit(0)
        
    print("Running MPS determinism validation V3...")
    results = {"baseline": {}, "shapes": {}, "root_weighted": {}}
    
    all_passed = True
    

    # 1. Baseline: batch_size=64, root_weighted=False (must match V1 exactly)
    for seed in sorted(FROZEN_SEEDS):
        hashes = []
        for i in range(3):
            proc = subprocess.run(
                ["scripts/run_ml_runtime_v3.sh", __file__, "--run-subprocess", str(seed), "64", "0"],
                capture_output=True, text=True
            )
            if proc.returncode != 0:
                print(proc.stderr)
                sys.exit(1)
                
            out = {}
            for line in proc.stdout.splitlines():
                if ":" in line:
                    k, v = line.split(":", 1)
                    if k in ["MODEL", "OPT", "CPU", "MPS"]:
                        out[k] = v.strip()
            hashes.append(out)
        validate_v1_baseline(seed, hashes)
        results["baseline"][seed] = hashes
        
    # 2. Short shapes: batch sizes [1, 2, 17, 63] (seed=1729)
    for bs in [1, 2, 17, 63]:
        hashes = []
        for i in range(3):
            proc = subprocess.run(
                ["scripts/run_ml_runtime_v3.sh", __file__, "--run-subprocess", "1729", str(bs), "0"],
                capture_output=True, text=True
            )
            if proc.returncode != 0:
                print(proc.stderr)
                sys.exit(1)
            out = {}
            for line in proc.stdout.splitlines():
                if ":" in line:
                    k, v = line.split(":", 1)
                    if k in ["MODEL", "OPT", "CPU", "MPS"]:
                        out[k] = v.strip()
            hashes.append(out)
        validate_triplicate_hashes(hashes, f"shape_{bs}")
        results["shapes"][bs] = hashes

    # 3. Root-weighted: batch_size=8, root_weighted=True (seed=1729)
    hashes = []
    for i in range(3):
        proc = subprocess.run(
            ["scripts/run_ml_runtime_v3.sh", __file__, "--run-subprocess", "1729", "8", "1"],
            capture_output=True, text=True
        )
        if proc.returncode != 0:
            print(proc.stderr)
            sys.exit(1)
        out = {}
        for line in proc.stdout.splitlines():
            if ":" in line:
                k, v = line.split(":", 1)
                if k in ["MODEL", "OPT", "CPU", "MPS"]:
                    out[k] = v.strip()
        hashes.append(out)
    validate_triplicate_hashes(hashes, "root_weighted_8")
    results["root_weighted"]["8"] = hashes
    
    results["status"] = "PASS"
    results["runtime_id"] = "CHESSHEAT_ML_RUNTIME_V3"
    
    print("All checks passed successfully.")

    with open("artifacts/research/ml_runtime_validation_hashes_v3.json", "w") as f:
        json.dump(results, f, sort_keys=True, separators=(",",":"), allow_nan=False)
if __name__ == "__main__":
    main()
