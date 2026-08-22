import os
import platform
import random
import torch

PINNED_TORCH_VERSION = "2.13.0"
PINNED_DEVICE = "mps"
FROZEN_SEEDS = {1729, 2718, 31415, 65537, 104729}

def validate_runtime_environment() -> None:
    if torch.__version__ != PINNED_TORCH_VERSION:
        raise RuntimeError(f"Expected torch {PINNED_TORCH_VERSION}, got {torch.__version__}")
    
    if platform.system() != "Darwin" or platform.machine() != "arm64":
        raise RuntimeError(f"Expected Darwin arm64, got {platform.system()} {platform.machine()}")
        
    if not torch.backends.mps.is_built() or not torch.backends.mps.is_available():
        raise RuntimeError("MPS is not built or available")
        
    if os.environ.get("PYTORCH_MPS_FAST_MATH") != "0":
        raise RuntimeError("PYTORCH_MPS_FAST_MATH must be '0'")
    if os.environ.get("PYTORCH_ENABLE_MPS_FALLBACK") != "0":
        raise RuntimeError("PYTORCH_ENABLE_MPS_FALLBACK must be '0'")
    if os.environ.get("PYTORCH_MPS_PREFER_METAL") != "0":
        raise RuntimeError("PYTORCH_MPS_PREFER_METAL must be '0'")
    if os.environ.get("PYTHONHASHSEED") != "0":
        raise RuntimeError("PYTHONHASHSEED must be '0'")

def configure_runtime(seed: int) -> torch.device:
    if seed not in FROZEN_SEEDS:
        raise ValueError(f"Seed {seed} is not in the frozen set {FROZEN_SEEDS}")
        
    validate_runtime_environment()
    
    torch.use_deterministic_algorithms(True, warn_only=False)
    torch.set_deterministic_debug_mode("error")
    torch.set_default_dtype(torch.float32)
    torch.set_float32_matmul_precision("highest")
    
    random.seed(seed)
    torch.manual_seed(seed)
    torch.mps.manual_seed(seed)
    
    return torch.device(PINNED_DEVICE)
