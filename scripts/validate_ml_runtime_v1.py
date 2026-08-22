import os
import sys
import json
import hashlib
import subprocess
import torch
import torch.nn as nn
from src.chessheat.ml_runtime import configure_runtime, FROZEN_SEEDS

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

def hash_state_dict(state_dict):
    import struct
    m = hashlib.sha256()
    for k in sorted(state_dict.keys()):
        m.update(k.encode('utf-8'))
        t = state_dict[k].cpu().detach().contiguous()
        m.update(str(t.dtype).encode('utf-8'))
        m.update(str(t.shape).encode('utf-8'))
        
        # Serialize float32 tensors without numpy
        flat = t.view(-1)
        if t.dtype == torch.float32:
            import struct
            # Pack float32 array into bytes
            float_list = flat.tolist()
            m.update(struct.pack(f'{len(float_list)}f', *float_list))
        elif t.dtype == torch.long:
            long_list = flat.tolist()
            m.update(struct.pack(f'{len(long_list)}q', *long_list))
        else:
            raise RuntimeError(f"Unsupported dtype {t.dtype} for hashing")
            
    return m.hexdigest()

def run_single_process(seed: int):
    device = configure_runtime(seed)
    
    model = FrozenLearner().to(device)
    optimizer = torch.optim.Adam(
        model.parameters(),
        lr=0.001,
        betas=(0.9, 0.999),
        eps=1e-8,
        weight_decay=1e-5,
        amsgrad=False
    )
    criterion = nn.CrossEntropyLoss()
    
    # Check all parameters are on MPS
    for name, param in model.named_parameters():
        assert param.device.type == "mps", f"Param {name} is on {param.device}, expected mps"
        
    BATCH = 64
    
    # Deterministic arithmetic tensors, no random dataloader
    # spatial: 0 to BATCH*19*8*8-1 normalized
    spatial_tensor = torch.arange(BATCH * 19 * 8 * 8, dtype=torch.float32).view(BATCH, 19, 8, 8) / (BATCH * 19 * 8 * 8)
    spatial_tensor = spatial_tensor.to(device)
    assert spatial_tensor.device.type == "mps"
    
    side_tensor = torch.arange(BATCH * 270, dtype=torch.float32).view(BATCH, 270) / (BATCH * 270)
    side_tensor = side_tensor.to(device)
    assert side_tensor.device.type == "mps"
    
    target_tensor = (torch.arange(BATCH) % 3).to(torch.long).to(device)
    
    for step in range(3):
        optimizer.zero_grad()
        out = model(spatial_tensor, side_tensor)
        loss = criterion(out, target_tensor)
        loss.backward()
        optimizer.step()
        
    torch.mps.synchronize()
    
    # Final hash
    h = hash_state_dict(model.state_dict())
    print(f"HASH:{h}")

def main():
    if len(sys.argv) == 3 and sys.argv[1] == "--run-seed":
        seed = int(sys.argv[2])
        run_single_process(seed)
        sys.exit(0)
        
    print("Running MPS determinism validation...")
    results = {}
    
    env = os.environ.copy()
    env["PYTHONHASHSEED"] = "0"
    env["PYTORCH_MPS_FAST_MATH"] = "0"
    env["PYTORCH_ENABLE_MPS_FALLBACK"] = "0"
    env["PYTORCH_MPS_PREFER_METAL"] = "0"
    env["PYTHONPATH"] = "src:."
    
    all_passed = True
    
    for seed in sorted(FROZEN_SEEDS):
        hashes = []
        for i in range(3):
            proc = subprocess.run(
                [sys.executable, __file__, "--run-seed", str(seed)],
                env=env,
                capture_output=True,
                text=True
            )
            if proc.returncode != 0:
                print(f"Process failed for seed {seed}, run {i}:")
                print(proc.stdout)
                print(proc.stderr)
                sys.exit(1)
            
            output = proc.stdout
            h = None
            for line in output.splitlines():
                if line.startswith("HASH:"):
                    h = line.split("HASH:")[1].strip()
            if not h:
                print(f"No hash found in output for seed {seed}, run {i}.")
                print(proc.stdout)
                sys.exit(1)
            hashes.append(h)
        
        results[seed] = hashes
        print(f"Seed {seed}: {hashes}")
        if not (hashes[0] == hashes[1] == hashes[2]):
            print(f"MISMATCH for seed {seed}!")
            all_passed = False
            
    with open("artifacts/research/ml_runtime_validation_hashes_v1.json", "w") as f:
        json.dump(results, f, sort_keys=True, indent=2)
        
    if all_passed:
        print("ALL PASSED: MPS execution is deterministic across multiple fresh processes.")
        sys.exit(0)
    else:
        print("FAILED: Hashes are not identical.")
        sys.exit(1)

if __name__ == "__main__":
    main()
