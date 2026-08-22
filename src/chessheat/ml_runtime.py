import os
import sys
import platform
import sysconfig
import subprocess
import hashlib
import json
import pathlib
import importlib
import importlib.metadata
import random
from typing import Callable, Any

PINNED_TORCH_VERSION = "2.13.0"
PINNED_DEVICE = "mps"
FROZEN_SEEDS = {1729, 2718, 31415, 65537, 104729}

def _get_system_info(cmd: list[str]) -> str:
    try:
        return subprocess.check_output(cmd, text=True).strip()
    except Exception:
        return ""


def validate_canonical_import_path():
    expected_root = os.environ.get("CHESSHEAT_REPO_ROOT")
    if not expected_root:
        raise RuntimeError("CHESSHEAT_REPO_ROOT not set")
    expected_path = pathlib.Path(expected_root).resolve() / "src" / "chessheat" / "ml_runtime.py"
    actual_path = pathlib.Path(__file__).resolve()
    if actual_path != expected_path:
        raise RuntimeError(f"Canonical import path mismatch. Expected {expected_path}, got {actual_path}")

def validate_package_lock_v3():
    root = pathlib.Path(os.environ.get("CHESSHEAT_REPO_ROOT", "."))
    lock_path = root / "artifacts" / "research" / "ml_runtime_package_lock_v3.json"
    with open(lock_path) as f:
        lock_data = json.load(f)
    
    # Check that this lock file exactly matches expected (to be checked by code lock)
    for pkg, expected_version in lock_data.items():
        try:
            actual_version = importlib.metadata.version(pkg)
            if actual_version != expected_version:
                raise RuntimeError(f"Package {pkg} version mismatch. Expected {expected_version}, got {actual_version}")
        except importlib.metadata.PackageNotFoundError:
            raise RuntimeError(f"Package {pkg} is missing")

def validate_code_lock_v3():
    root = pathlib.Path(os.environ.get("CHESSHEAT_REPO_ROOT", "."))
    lock_path = root / "artifacts" / "research" / "ml_runtime_code_lock_v3.json"
    with open(lock_path) as f:
        lock_data = json.load(f)
        
    for rel_path, expected_hash in lock_data.items():
        file_path = root / rel_path
        h = hashlib.sha256(file_path.read_bytes()).hexdigest()
        if h != expected_hash:
            raise RuntimeError(f"Code lock mismatch for {rel_path}. Expected {expected_hash}, got {h}")
            
    # Also verify no tracked working-tree modification exists for locked files
    # (Checking diff is a bit tricky inside python, but we can do a quick subprocess check)
    files = list(lock_data.keys())
    try:
        subprocess.check_call(["git", "diff", "--quiet", "--"] + files, cwd=str(root))
        subprocess.check_call(["git", "diff", "--cached", "--quiet", "--"] + files, cwd=str(root))
    except subprocess.CalledProcessError:
        raise RuntimeError(f"Tracked modifications exist for critical files: {files}")

def validate_runtime_identity():
    if "torch" in sys.modules:
        raise RuntimeError("torch was imported before ChessHeat ML runtime preflight")

    if os.environ.get("CHESSHEAT_ML_RUNTIME_ID") != "CHESSHEAT_ML_RUNTIME_V3":
        raise RuntimeError("CHESSHEAT_ML_RUNTIME_ID must be 'CHESSHEAT_ML_RUNTIME_V3'")
    if os.environ.get("PYTHONHASHSEED") != "0":
        raise RuntimeError("PYTHONHASHSEED must be '0'")
    if os.environ.get("PYTORCH_MPS_FAST_MATH") != "0":
        raise RuntimeError("PYTORCH_MPS_FAST_MATH must be '0'")
    if os.environ.get("PYTORCH_ENABLE_MPS_FALLBACK") != "0":
        raise RuntimeError("PYTORCH_ENABLE_MPS_FALLBACK must be '0'")
    if os.environ.get("PYTORCH_MPS_PREFER_METAL") != "0":
        raise RuntimeError("PYTORCH_MPS_PREFER_METAL must be '0'")

    if platform.python_implementation() != "CPython":
        raise RuntimeError("Expected CPython")
    if sys.version_info[:3] != (3, 13, 5):
        raise RuntimeError(f"Expected Python 3.13.5, got {sys.version_info}")
    if sysconfig.get_config_var("SOABI") != "cpython-313-darwin":
        raise RuntimeError("Expected SOABI cpython-313-darwin")
    if platform.system() != "Darwin":
        raise RuntimeError("Expected Darwin")
    if platform.machine() != "arm64":
        raise RuntimeError("Expected arm64")
    if platform.release() != "25.6.0":
        raise RuntimeError("Expected Darwin release 25.6.0")
        
    sw_vers_product = _get_system_info(["/usr/bin/sw_vers", "-productVersion"])
    if sw_vers_product != "26.6.2":
        raise RuntimeError(f"Expected macOS 26.6.2, got {sw_vers_product}")
        
    sw_vers_build = _get_system_info(["/usr/bin/sw_vers", "-buildVersion"])
    if sw_vers_build != "25G83":
        raise RuntimeError(f"Expected macOS build 25G83, got {sw_vers_build}")
        
    hw_model = _get_system_info(["/usr/sbin/sysctl", "-n", "hw.model"])
    if hw_model != "Mac16,10":
        raise RuntimeError(f"Expected Mac16,10, got {hw_model}")
        
    chip = _get_system_info(["/usr/sbin/sysctl", "-n", "machdep.cpu.brand_string"])
    if chip != "Apple M4":
        raise RuntimeError(f"Expected Apple M4, got {chip}")
        
    memsize = _get_system_info(["/usr/sbin/sysctl", "-n", "hw.memsize"])
    if memsize != "17179869184":
        raise RuntimeError(f"Expected memsize 17179869184, got {memsize}")

    executable = pathlib.Path(sys.executable).resolve()
    h = hashlib.sha256(executable.read_bytes()).hexdigest()
    if h != "542c879fdc2cfe0be223e4729082bac529780d90c6d811c853de852765b35a35":
        raise RuntimeError("Python executable hash mismatch")

    validate_canonical_import_path()
    validate_package_lock_v3()
    validate_code_lock_v3()

    dist_version = importlib.metadata.version("torch")
    if dist_version != PINNED_TORCH_VERSION:
        raise RuntimeError(f"Expected installed torch distribution {PINNED_TORCH_VERSION}")

class RuntimeContext:
    def __init__(self, torch_module, device, seed: int):
        self.torch = torch_module
        self.device = device
        self.seed = seed

_runtime_configured = False
_configured_seed = None

def configure_runtime(seed: int) -> RuntimeContext:
    global _runtime_configured, _configured_seed
    
    if _runtime_configured:
        if seed != _configured_seed:
            raise RuntimeError("Runtime already configured with a different seed in this process")
        import torch
        return RuntimeContext(torch, torch.device(PINNED_DEVICE), seed)
        
    if seed not in FROZEN_SEEDS:
        raise ValueError(f"Seed {seed} is not in the frozen set {FROZEN_SEEDS}")
        
    validate_runtime_identity()
    
    torch = importlib.import_module("torch")
    
    if torch.__version__ != PINNED_TORCH_VERSION:
        raise RuntimeError(f"Expected torch {PINNED_TORCH_VERSION}, got {torch.__version__}")
    if torch.version.git_version != "cf30153c4c131c8164ee7798e5022d810682e2cb":
        raise RuntimeError(f"Expected torch git cf30153c4c131c8164ee7798e5022d810682e2cb")
        
    if not torch.backends.mps.is_built() or not torch.backends.mps.is_available():
        raise RuntimeError("MPS is not built or available")
    
    # Optional test for device count if present
    if hasattr(torch.mps, "device_count") and torch.mps.device_count() < 1:
        raise RuntimeError("MPS device count < 1")
    
    torch.use_deterministic_algorithms(True, warn_only=False)
    torch.set_deterministic_debug_mode("error")
    torch.set_default_dtype(torch.float32)
    torch.set_float32_matmul_precision("highest")
    
    random.seed(seed)
    torch.manual_seed(seed)
    torch.mps.manual_seed(seed)
    
    _runtime_configured = True
    _configured_seed = seed
    
    return RuntimeContext(torch, torch.device(PINNED_DEVICE), seed)

def initialize_model_cpu_then_mps(model_factory: Callable[[Any], Any], runtime_context: RuntimeContext) -> Any:
    torch = runtime_context.torch
    model = model_factory(torch)
    
    for name, param in model.named_parameters():
        if param.device.type != "cpu":
            raise RuntimeError(f"Parameter {name} was not initialized on CPU: {param.device}")
    for name, buf in model.named_buffers():
        if buf.device.type != "cpu":
            raise RuntimeError(f"Buffer {name} was not initialized on CPU: {buf.device}")
            
    model.to(runtime_context.device)
    
    for name, param in model.named_parameters():
        if param.device.type != runtime_context.device.type:
            raise RuntimeError(f"Parameter {name} failed to transfer to {runtime_context.device}")
    for name, buf in model.named_buffers():
        if buf.device.type != runtime_context.device.type:
            raise RuntimeError(f"Buffer {name} failed to transfer to {runtime_context.device}")
            
    return model

def build_frozen_adam(model, torch_module):
    # PyTorch 2.13.0 specific defaults explicitization
    return torch_module.optim.Adam(
        model.parameters(),
        lr=0.001,
        betas=(0.9, 0.999),
        eps=1e-8,
        weight_decay=1e-5,
        amsgrad=False,
        foreach=None,
        maximize=False,
        capturable=False,
        differentiable=False,
        fused=None,
        decoupled_weight_decay=False
    )
