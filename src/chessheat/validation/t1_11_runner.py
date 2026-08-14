import os
import json
import hashlib
import subprocess
from typing import Dict, Any

def get_git_info() -> Dict[str, str]:
    try:
        status = subprocess.check_output(["git", "status", "--porcelain"], text=True).strip()
        if status:
            raise ValueError("Git working directory is not clean. Commit all changes before running the execution seal.")
        commit_sha = subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip()
        return {"commit_sha": commit_sha}
    except Exception as e:
        raise RuntimeError(f"Failed to verify Git state: {e}")

def hash_file(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        h.update(f.read())
    return h.hexdigest()

def get_engine_info(engine_path: str) -> Dict[str, str]:
    try:
        abs_path = subprocess.check_output(["which", engine_path], text=True).strip()
        if not abs_path:
            abs_path = os.path.abspath(engine_path)
            
        version_out = subprocess.check_output([abs_path], input="uci\nquit\n", text=True)
        version_lines = [line for line in version_out.split('\n') if "id name" in line]
        version = version_lines[0].replace("id name", "").strip() if version_lines else "Unknown"
        
        return {
            "engine_path_resolved": abs_path,
            "engine_version": version
        }
    except Exception as e:
        raise RuntimeError(f"Failed to execute engine {engine_path}: {e}")

def create_execution_seal(
    manifest_path: str,
    protocol_path: str,
    preflight_path: str,
    engine_path: str,
    engine_threads: int,
    engine_hash_mb: int,
    engine_node_budget: int,
    comparison_perspective: str,
    output_dir: str
) -> Dict[str, Any]:
    
    # Programmatically verify preflight is free of FAIL states before generation
    with open(preflight_path, "r") as f:
        preflight_data = json.load(f)
        
    for fix in preflight_data.get("fixtures", []):
        if fix.get("eligibility_status") == "FAIL":
            raise ValueError(f"Preflight has FAIL eligibility for {fix.get('fixture_id')}")
            
        if fix.get("dimension_preflight_status") == "FAIL":
            raise ValueError(f"Preflight has FAIL dimension status for {fix.get('fixture_id')}")
            
    # Verify empty dir
    if os.path.exists(output_dir):
        if len(os.listdir(output_dir)) > 0:
            raise ValueError(f"Output directory {output_dir} is not empty.")
    else:
        os.makedirs(output_dir)
        
    git_info = get_git_info()
    engine_info = get_engine_info(engine_path)
    
    manifest_hash = hash_file(manifest_path)
    protocol_hash = hash_file(protocol_path)
    preflight_hash = hash_file(preflight_path)
    
    runner_path = os.path.abspath(__file__)
    harness_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "harness.py"))
    
    runner_hash = hash_file(runner_path)
    harness_hash = hash_file(harness_path)
    
    seal = {
        "git_commit_sha": git_info["commit_sha"],
        "harness_identity": harness_hash,
        "runner_identity": runner_hash,
        "manifest_hash": manifest_hash,
        "protocol_hash": protocol_hash,
        "preflight_hash": preflight_hash,
        "engine_path": engine_info["engine_path_resolved"],
        "engine_version": engine_info["engine_version"],
        "engine_threads": engine_threads,
        "engine_hash_mb": engine_hash_mb,
        "engine_node_budget": engine_node_budget,
        "comparison_perspective": comparison_perspective,
        "output_directory_identity": os.path.abspath(output_dir)
    }
    
    seal_path = os.path.join(output_dir, "t1_11_execution_seal.json")
    with open(seal_path, "w") as f:
        json.dump(seal, f, indent=2)
        
    return seal

def run_t1_11_execution(preflight_path: str, manifest_path: str, output_dir: str, engine_path: str):
    with open(preflight_path, "r") as f:
        preflight_data = json.load(f)
        
    with open(manifest_path, "r") as f:
        manifest_data = json.load(f)
        
    manifest_dict = {item["fixture_id"]: item for item in manifest_data}
        
    for fix in preflight_data.get("fixtures", []):
        if fix.get("eligibility_status") == "FAIL":
            raise ValueError(f"Preflight has FAIL for {fix.get('fixture_id')}")
            
        if fix.get("dimension_preflight_status") == "FAIL":
            raise ValueError(f"Preflight has FAIL dimension for {fix.get('fixture_id')}")
            
        status = fix.get("dimension_preflight_status")
        # Ensure structural fixtures do not call the engine
        if status == "PASS":
            pass # No engine call needed
        elif status == "PRECONDITIONS_PASS_PENDING_ENGINE":
            # Harness engine eval would happen here
            pass
            
    pass

if __name__ == "__main__":
    pass
