import os
import sys
import subprocess
import json
import pytest
import tempfile
import pathlib

def run_script_with_env(env_updates, extra_code=""):
    env = os.environ.copy()
    env.update(env_updates)
    code = f"""
import sys
import os
try:
    from chessheat.ml_runtime import configure_runtime
    configure_runtime(1729)
    {extra_code}
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

def get_base_env():
    root = str(pathlib.Path(__file__).parent.parent.resolve())
    return {
        "CHESSHEAT_ML_RUNTIME_ID": "CHESSHEAT_ML_RUNTIME_V3",
        "PYTHONHASHSEED": "0",
        "PYTORCH_MPS_FAST_MATH": "0",
        "PYTORCH_ENABLE_MPS_FALLBACK": "0",
        "PYTORCH_MPS_PREFER_METAL": "0",
        "PYTHONPATH": f"{root}/src:{root}",
        "PYTHONNOUSERSITE": "1",
        "CHESSHEAT_REPO_ROOT": root
    }

def test_missing_torch():
    env = get_base_env()
    code = """
import sys
import os
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
    assert "torch was imported before" in result.stdout

def test_valid_env():
    env = get_base_env()
    code, stdout, stderr = run_script_with_env(env)
    assert code == 0, f"Expected 0, got {code}: {stdout} {stderr}"
    assert stdout.endswith("OK")

def test_invalid_env_missing():
    env = get_base_env()
    del env["PYTORCH_MPS_FAST_MATH"]
    code, stdout, stderr = run_script_with_env(env)
    assert code != 0

def test_invalid_env_wrong():
    env = get_base_env()
    env["CHESSHEAT_ML_RUNTIME_ID"] = "CHESSHEAT_ML_RUNTIME_V2"
    code, stdout, stderr = run_script_with_env(env)
    assert code != 0
    assert "CHESSHEAT_ML_RUNTIME_ID must be 'CHESSHEAT_ML_RUNTIME_V3'" in stdout

def test_invalid_seed():
    env = get_base_env()
    code = """
import sys
import os
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

def test_all_frozen_seeds():
    env = get_base_env()
    for s in [1729, 2718, 31415, 65537, 104729]:
        code = f"""
import sys, os
from chessheat.ml_runtime import configure_runtime
configure_runtime({s})
"""
        res = subprocess.run([sys.executable, "-c", code], env=env, capture_output=True, text=True)
        assert res.returncode == 0

def test_second_seed_rejected():
    env = get_base_env()
    code = """
import sys, os
try:
    from chessheat.ml_runtime import configure_runtime
    configure_runtime(1729)
    configure_runtime(2718)
    sys.exit(0)
except Exception as e:
    print(str(e))
    sys.exit(1)
"""
    result = subprocess.run([sys.executable, "-c", code], env=env, capture_output=True, text=True)
    assert result.returncode != 0
    assert "different seed" in result.stdout

def test_factory_mps_rejection():
    env = get_base_env()
    code = """
import sys
import os
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
from chessheat.ml_runtime import configure_runtime
configure_runtime(1729)
print("OK")
sys.exit(0)
"""
    with tempfile.TemporaryDirectory() as td:
        tf = os.path.join(td, "test_launcher_script.py")
        with open(tf, "w") as f:
            f.write(code)
        result = subprocess.run(["scripts/run_ml_runtime_v3.sh", tf], capture_output=True, text=True)
        assert result.returncode == 0
        assert "OK" in result.stdout.strip()


def test_hostile_pythonpath():
    with tempfile.TemporaryDirectory() as td, tempfile.TemporaryDirectory() as td2:
        shadow_dir = os.path.join(td, "chessheat")
        os.makedirs(shadow_dir)
        with open(os.path.join(shadow_dir, "__init__.py"), "w") as f:
            f.write("")
        with open(os.path.join(shadow_dir, "ml_runtime.py"), "w") as f:
            f.write("print('MALICIOUS SHADOW RUNTIME EXECUTED')")
            
        code = '''
from chessheat.ml_runtime import configure_runtime
configure_runtime(1729)
import sys
print('SUCCESS_CANONICAL')
sys.exit(0)
'''
        tf = os.path.join(td2, "test_launcher_script.py")
        with open(tf, "w") as f:
            f.write(code)
            
        env = os.environ.copy()
        env["PYTHONPATH"] = td
        result = subprocess.run(["scripts/run_ml_runtime_v3.sh", tf], env=env, capture_output=True, text=True)
        assert result.returncode == 0
        assert "MALICIOUS" not in result.stdout
        assert "MALICIOUS" not in result.stderr
        assert "SUCCESS_CANONICAL" in result.stdout

def test_package_lock_rejection(monkeypatch):
    env = get_base_env()
    # Write a temporary lock file
    with tempfile.TemporaryDirectory() as td:
        bad_lock = os.path.join(td, "ml_runtime_package_lock_v3.json")
        with open(bad_lock, "w") as f:
            json.dump({"sympy": "99.99.99"}, f)
            
        code = f"""
import sys, os
import importlib.metadata
import json
import pathlib
# Mock the JSON loading right before configure_runtime
old_load = json.load
def mock_load(f):
    if 'ml_runtime_package_lock_v3.json' in getattr(f, 'name', ''):
        return {{"sympy": "99.99.99", "torch": "2.13.0"}}
    return old_load(f)
json.load = mock_load

try:
    from chessheat.ml_runtime import configure_runtime
    configure_runtime(1729)
    sys.exit(0)
except Exception as e:
    print(str(e))
    sys.exit(1)
"""
        result = subprocess.run([sys.executable, "-c", code], env=env, capture_output=True, text=True)
        assert result.returncode != 0
        assert "Package sympy version mismatch" in result.stdout or "missing" in result.stdout

def test_code_lock_rejection():
    env = get_base_env()
    code = f"""
import sys, os
import json
# Mock the JSON loading right before configure_runtime
old_load = json.load
def mock_load(f):
    if 'ml_runtime_code_lock_v3.json' in getattr(f, 'name', ''):
        return {{"scripts/run_ml_runtime_v3.sh": "00000000000000000"}}
    return old_load(f)
json.load = mock_load

try:
    from chessheat.ml_runtime import configure_runtime
    configure_runtime(1729)
    sys.exit(0)
except Exception as e:
    print(str(e))
    sys.exit(1)
"""
    result = subprocess.run([sys.executable, "-c", code], env=env, capture_output=True, text=True)
    assert result.returncode != 0
    assert "Code lock mismatch" in result.stdout

def test_validator_negative():
    # Provide bad hashes to the validator's validation helper
    env = get_base_env()
    code = """
import sys, os
from scripts.validate_ml_runtime_v3 import validate_triplicate_hashes, validate_v1_baseline

bad_records = [
    {"MODEL": "a"*64, "OPT": "b"*64, "CPU": "c"*64, "MPS": "d"*64},
    {"MODEL": "a"*64, "OPT": "x"*64, "CPU": "c"*64, "MPS": "d"*64},
    {"MODEL": "a"*64, "OPT": "b"*64, "CPU": "c"*64, "MPS": "d"*64}
]
try:
    validate_triplicate_hashes(bad_records, "test")
    sys.exit(0)
except ValueError as e:
    print(str(e))
    sys.exit(1)
"""
    result = subprocess.run([sys.executable, "-c", code], env=env, capture_output=True, text=True)
    assert result.returncode != 0
    assert "Mismatch in OPT across 3 runs" in result.stdout

def test_deterministic_flags():
    env = get_base_env()
    code = """
import sys, os
from chessheat.ml_runtime import configure_runtime
ctx = configure_runtime(1729)
torch = ctx.torch
assert torch.are_deterministic_algorithms_enabled() == True
assert torch.is_deterministic_algorithms_warn_only_enabled() == False
assert torch.get_deterministic_debug_mode() == 2
assert torch.get_default_dtype() == torch.float32
assert torch.get_float32_matmul_precision() == "highest"
print("OK")
sys.exit(0)
"""
    result = subprocess.run([sys.executable, "-c", code], env=env, capture_output=True, text=True)
    assert result.returncode == 0
    assert "OK" in result.stdout

