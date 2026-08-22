import pytest
import torch
import os
import platform
import json
from src.chessheat.ml_runtime import configure_runtime, validate_runtime_environment, PINNED_TORCH_VERSION, PINNED_DEVICE

def test_torch_version_exact():
    assert torch.__version__ == PINNED_TORCH_VERSION
    assert PINNED_TORCH_VERSION == "2.13.0"

def test_platform_exact():
    assert platform.system() == "Darwin"
    assert platform.machine() == "arm64"

def test_device_mps():
    assert PINNED_DEVICE == "mps"
    assert torch.backends.mps.is_built()
    assert torch.backends.mps.is_available()

def test_environment_variables_required():
    env = os.environ.copy()
    try:
        os.environ["PYTORCH_MPS_FAST_MATH"] = "1"
        with pytest.raises(RuntimeError, match="PYTORCH_MPS_FAST_MATH"):
            validate_runtime_environment()
    finally:
        os.environ.clear()
        os.environ.update(env)

def test_rejected_unknown_seed():
    with pytest.raises(ValueError, match="not in the frozen set"):
        configure_runtime(42)

def test_valid_seeds_accepted_and_deterministic_flags(monkeypatch):
    monkeypatch.setenv("PYTORCH_MPS_FAST_MATH", "0")
    monkeypatch.setenv("PYTORCH_ENABLE_MPS_FALLBACK", "0")
    monkeypatch.setenv("PYTORCH_MPS_PREFER_METAL", "0")
    monkeypatch.setenv("PYTHONHASHSEED", "0")
    
    device = configure_runtime(1729)
    assert device.type == "mps"
    
    assert torch.are_deterministic_algorithms_enabled()
    assert torch.is_deterministic_algorithms_warn_only_enabled() is False
    assert torch.get_deterministic_debug_mode() == 2  # 2 corresponds to error mode
    assert torch.get_default_dtype() == torch.float32
    assert torch.get_float32_matmul_precision() == "highest"

def test_runtime_artifact_schema():
    with open("artifacts/research/ml_runtime_pin_v1.json") as f:
        pin = json.load(f)
        
    assert pin["runtime_id"] == "CHESSHEAT_ML_RUNTIME_V1"
    assert pin["protocol_binding"]["protocol_json_sha"] == "ea1242de3b2f0ac1613ac9b838f014ad00ae8910cfd51d8b99c6fb77f15e29ef"
    assert "wheel_manifest" in pin
    assert "sha256" in pin["wheel_manifest"]
