import os
import sys
import subprocess
import json
import pytest

def run_script_with_env(env_updates):
    env = os.environ.copy()
    env.update(env_updates)
    code = """
import sys
try:
    from chessheat.ml_runtime import configure_runtime
    configure_runtime(1729)
    print("OK")
    sys.exit(0)
except Exception as e:
    print(str(e))
    sys.exit(1)
"""
    result = subprocess.run(
        [sys.executable, "-c", code],
        env=env,
        capture_output=True,
        text=True
    )
    return result.returncode, result.stdout.strip(), result.stderr.strip()

def test_missing_torch():
    # If torch is already imported, it should fail
    env = os.environ.copy()
    env["CHESSHEAT_ML_RUNTIME_ID"] = "CHESSHEAT_ML_RUNTIME_V2"
    env["PYTHONHASHSEED"] = "0"
    env["PYTORCH_MPS_FAST_MATH"] = "0"
    env["PYTORCH_ENABLE_MPS_FALLBACK"] = "0"
    env["PYTORCH_MPS_PREFER_METAL"] = "0"
    env["PYTHONPATH"] = "src:."
    
    code = """
import sys
import torch
try:
    from chessheat.ml_runtime import configure_runtime
    configure_runtime(1729)
    print("OK")
    sys.exit(0)
except Exception as e:
    print(str(e))
    sys.exit(1)
"""
    result = subprocess.run([sys.executable, "-c", code], env=env, capture_output=True, text=True)
    assert result.returncode != 0
    assert "torch was imported before ChessHeat ML runtime preflight" in result.stdout

def test_valid_env():
    env = {
        "CHESSHEAT_ML_RUNTIME_ID": "CHESSHEAT_ML_RUNTIME_V2",
        "PYTHONHASHSEED": "0",
        "PYTORCH_MPS_FAST_MATH": "0",
        "PYTORCH_ENABLE_MPS_FALLBACK": "0",
        "PYTORCH_MPS_PREFER_METAL": "0",
        "PYTHONPATH": "src:."
    }
    code, stdout, stderr = run_script_with_env(env)
    assert code == 0, f"Expected 0, got {code}: {stdout} {stderr}"
    assert stdout == "OK"

def test_invalid_env_missing():
    env = {
        "CHESSHEAT_ML_RUNTIME_ID": "CHESSHEAT_ML_RUNTIME_V2",
        "PYTHONHASHSEED": "0",
        "PYTORCH_MPS_FAST_MATH": "0",
        "PYTORCH_ENABLE_MPS_FALLBACK": "0",
        "PYTHONPATH": "src:."
    }
    code, stdout, stderr = run_script_with_env(env)
    assert code != 0

def test_invalid_seed():
    env = os.environ.copy()
    env.update({
        "CHESSHEAT_ML_RUNTIME_ID": "CHESSHEAT_ML_RUNTIME_V2",
        "PYTHONHASHSEED": "0",
        "PYTORCH_MPS_FAST_MATH": "0",
        "PYTORCH_ENABLE_MPS_FALLBACK": "0",
        "PYTORCH_MPS_PREFER_METAL": "0",
        "PYTHONPATH": "src:."
    })
    code = """
import sys
try:
    from chessheat.ml_runtime import configure_runtime
    configure_runtime(9999) # invalid seed
    print("OK")
    sys.exit(0)
except Exception as e:
    print(str(e))
    sys.exit(1)
"""
    result = subprocess.run([sys.executable, "-c", code], env=env, capture_output=True, text=True)
    assert result.returncode != 0
    assert "not in the frozen set" in result.stdout

def test_factory_mps_rejection():
    env = os.environ.copy()
    env.update({
        "CHESSHEAT_ML_RUNTIME_ID": "CHESSHEAT_ML_RUNTIME_V2",
        "PYTHONHASHSEED": "0",
        "PYTORCH_MPS_FAST_MATH": "0",
        "PYTORCH_ENABLE_MPS_FALLBACK": "0",
        "PYTORCH_MPS_PREFER_METAL": "0",
        "PYTHONPATH": "src:."
    })
    code = """
import sys
try:
    from chessheat.ml_runtime import configure_runtime, initialize_model_cpu_then_mps
    ctx = configure_runtime(1729)
    def bad_factory(torch):
        import torch.nn as nn
        class BadModel(nn.Module):
            def __init__(self):
                super().__init__()
                self.fc = nn.Linear(10, 10, device="mps")
        return BadModel()
    initialize_model_cpu_then_mps(bad_factory, ctx)
    print("OK")
    sys.exit(0)
except Exception as e:
    print(str(e))
    sys.exit(1)
"""
    result = subprocess.run([sys.executable, "-c", code], env=env, capture_output=True, text=True)
    assert result.returncode != 0
    assert "was not initialized on CPU" in result.stdout

def test_launcher():
    code = """
import sys
from src.chessheat.ml_runtime import configure_runtime
configure_runtime(1729)
print("OK")
sys.exit(0)
"""
    with open("tests/test_launcher.py", "w") as f:
        f.write(code)
    result = subprocess.run(["scripts/run_ml_runtime_v2.sh", "tests/test_launcher.py"], capture_output=True, text=True)
    assert result.returncode == 0
    assert result.stdout.strip() == "OK"
