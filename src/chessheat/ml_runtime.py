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

def validate_runtime_identity():
    if "torch" in sys.modules:
        raise RuntimeError("torch was imported before ChessHeat ML runtime preflight")

    if os.environ.get("CHESSHEAT_ML_RUNTIME_ID") != "CHESSHEAT_ML_RUNTIME_V2":
        raise RuntimeError("CHESSHEAT_ML_RUNTIME_ID must be 'CHESSHEAT_ML_RUNTIME_V2'")
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
        fused=None
    )
