import os
import json
import hashlib
import subprocess
import statistics
import tempfile
from typing import Dict, Any, List

import chess

from chessheat.validation.harness import ValidationHarness
from chessheat.validation.t1_11_preflight import run_preflight

T1_11_CONFIG = {
    "threads": 1,
    "hash_mb": 16,
    "node_budget": 500000,
    "comparison_perspective": "root_side"
}

def get_git_info() -> Dict[str, str]:
    try:
        status = subprocess.check_output(["git", "status", "--porcelain"], text=True).strip()
        if status:
            raise ValueError("Git working directory is not clean. Commit all changes before running the execution seal.")
        commit_sha = subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip()
        return {"commit_sha": commit_sha}
    except Exception as e:
        if isinstance(e, ValueError):
            raise e
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
        
        if version == "Unknown":
            raise ValueError("Engine version is Unknown")
            
        return {
            "engine_path_resolved": abs_path,
            "engine_version": version
        }
    except Exception as e:
        if isinstance(e, ValueError):
            raise e
        raise RuntimeError(f"Failed to execute engine {engine_path}: {e}")

def validate_preflight_and_manifest(manifest_path: str, preflight_path: str):
    with open(manifest_path, "r") as f:
        manifest_data = json.load(f)
    with open(preflight_path, "r") as f:
        preflight_data = json.load(f)
        
    m_ids = [item["fixture_id"] for item in manifest_data]
    p_ids = [item["fixture_id"] for item in preflight_data.get("fixtures", [])]
    
    if m_ids != p_ids:
        raise ValueError("Manifest and preflight fixture IDs do not match exactly.")
        
    for fix in preflight_data.get("fixtures", []):
        if fix.get("eligibility_status") == "FAIL":
            raise ValueError(f"Preflight has FAIL eligibility for {fix.get('fixture_id')}")
        if fix.get("dimension_preflight_status") == "FAIL":
            raise ValueError(f"Preflight has FAIL dimension status for {fix.get('fixture_id')}")
        if fix.get("dimension_preflight_status") not in ["PASS", "PRECONDITIONS_PASS_PENDING_ENGINE"]:
            raise ValueError(f"Unknown status for {fix.get('fixture_id')}: {fix.get('dimension_preflight_status')}")
            
    pending = [f["fixture_id"] for f in preflight_data["fixtures"] if f["dimension_preflight_status"] == "PRECONDITIONS_PASS_PENDING_ENGINE"]
    if sorted(pending) != ["Q11", "Q14", "Q4"]:
        raise ValueError(f"Expected exactly Q4, Q11, Q14 to be pending engine. Got: {pending}")

def verify_preflight_reproducibility(frozen_preflight_path: str):
    with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as tmp:
        tmp_path = tmp.name
        
    try:
        from unittest.mock import patch
        with patch("chessheat.validation.t1_11_preflight.open") as mock_open:
            original_open = open
            def fake_open(file, mode="r", *args, **kwargs):
                if mode == "w" and "t1_11_structural_preflight.json" in str(file):
                    return original_open(tmp_path, "w", *args, **kwargs)
                return original_open(file, mode, *args, **kwargs)
            mock_open.side_effect = fake_open
            
            run_preflight()
            
        frozen_hash = hash_file(frozen_preflight_path)
        regen_hash = hash_file(tmp_path)
        
        if frozen_hash != regen_hash:
            raise ValueError("Regenerated preflight SHA does not match frozen preflight SHA.")
    finally:
        os.remove(tmp_path)

def create_execution_seal(
    manifest_path: str,
    protocol_path: str,
    preflight_path: str,
    engine_path: str,
    output_dir: str
) -> Dict[str, Any]:
    
    validate_preflight_and_manifest(manifest_path, preflight_path)
    verify_preflight_reproducibility(preflight_path)
            
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
        "engine_threads": T1_11_CONFIG["threads"],
        "engine_hash_mb": T1_11_CONFIG["hash_mb"],
        "engine_node_budget": T1_11_CONFIG["node_budget"],
        "comparison_perspective": T1_11_CONFIG["comparison_perspective"],
        "output_directory_identity": os.path.abspath(output_dir)
    }
    
    seal_path = os.path.join(output_dir, "t1_11_execution_seal.json")
    with open(seal_path, "w") as f:
        json.dump(seal, f, indent=2)
        
    return seal

def median_regret_cp(regrets: Dict[str, Any], m_partition: List[str]):
    vals = []
    for m in m_partition:
        if m in regrets:
            regret = regrets[m]
            if regret.type == "cp":
                vals.append(regret.value)
    
    if not vals:
        return None
    return statistics.median(vals)

def evaluate_structural(q_id: str, q_ev: Dict[str, Any]):
    n11 = len(q_ev.get("m_11", []))
    n10 = len(q_ev.get("m_10", []))
    n01 = len(q_ev.get("m_01", []))
    n00 = len(q_ev.get("m_00", []))
    total_roots = n11 + n10 + n01 + n00
    
    if q_id == "Q1":
        return "SUPPORTED" if (n11 > 0 and (n10 > 0 or n01 > 0)) else "FALSIFIED"
    elif q_id == "Q2":
        return "SUPPORTED" if n01 > 0 else "FALSIFIED"
    elif q_id == "Q3":
        return "SUPPORTED" if (n01 == 0 and n00 > 0) else "FALSIFIED"
    elif q_id == "Q5":
        dur = q_ev["dimension_evidence"]["computed_duration"]
        rc = q_ev["dimension_evidence"]["right_censored"]
        if rc: return "AMBIGUOUS"
        return "SUPPORTED" if dur == 1 else "FALSIFIED"
    elif q_id == "Q6":
        return "SUPPORTED" if (n01 == 0 and n00 == 0 and total_roots > 1) else "FALSIFIED"
    elif q_id == "Q7":
        c1_m11 = set(q_ev["dimension_evidence"]["bundle_equality_1"]["m11"])
        c2_m11 = set(q_ev["dimension_evidence"]["bundle_equality_2"]["m11"])
        c1_m10 = set(q_ev["dimension_evidence"]["bundle_equality_1"]["m10"])
        c2_m10 = set(q_ev["dimension_evidence"]["bundle_equality_2"]["m10"])
        c1_m01 = set(q_ev["dimension_evidence"]["bundle_equality_1"]["m01"])
        c2_m01 = set(q_ev["dimension_evidence"]["bundle_equality_2"]["m01"])
        c1_m00 = set(q_ev["dimension_evidence"]["bundle_equality_1"]["m00"])
        c2_m00 = set(q_ev["dimension_evidence"]["bundle_equality_2"]["m00"])
        
        constituents = len(q_ev["dimension_evidence"]["constituent_pairs"])
        if constituents >= 2 and c1_m11 == c2_m11 and c1_m10 == c2_m10 and c1_m01 == c2_m01 and c1_m00 == c2_m00:
            return "SUPPORTED"
        return "FALSIFIED"
    elif q_id == "Q8":
        return "SUPPORTED" if len(q_ev["dimension_evidence"]["intersection"]) > 0 else "FALSIFIED"
    elif q_id == "Q9":
        return "SUPPORTED" if len(q_ev["dimension_evidence"]["intersection"]) == 0 else "FALSIFIED"
    elif q_id == "Q10":
        return "SUPPORTED" if len(q_ev["dimension_evidence"]["intervals"]) > 1 else "FALSIFIED"
    elif q_id == "Q12":
        return "SUPPORTED" if total_roots == 1 else "FALSIFIED"
    elif q_id == "Q13":
        fa = q_ev["dimension_evidence"]["fen_a"]
        fb = q_ev["dimension_evidence"]["fen_b"]
        ia = q_ev["dimension_evidence"]["intervals_a"]
        ib = q_ev["dimension_evidence"]["intervals_b"]
        if fa == fb and ia != ib:
            return "SUPPORTED"
        return "FALSIFIED"
    elif q_id == "Q15":
        return "SUPPORTED" if q_ev["dimension_evidence"]["tuple_present_when_white_to_move"] != q_ev["dimension_evidence"]["tuple_present_when_black_to_move"] else "FALSIFIED"
    
    return "AMBIGUOUS"

def run_t1_11_execution(preflight_path: str, manifest_path: str, output_dir: str, engine_path: str):
    validate_preflight_and_manifest(manifest_path, preflight_path)
    
    with open(preflight_path, "r") as f:
        preflight_data = json.load(f)
    with open(manifest_path, "r") as f:
        manifest_data = json.load(f)
        
    manifest_dict = {item["fixture_id"]: item for item in manifest_data}
    
    results = []
    
    with ValidationHarness(
        engine_path=engine_path,
        budget_nodes=T1_11_CONFIG["node_budget"],
        threads=T1_11_CONFIG["threads"],
        hash_mb=T1_11_CONFIG["hash_mb"],
        comparison_perspective=T1_11_CONFIG["comparison_perspective"]
    ) as harness:
        
        for fix in preflight_data["fixtures"]:
            q_id = fix["fixture_id"]
            man_item = manifest_dict[q_id]
            
            status = fix["dimension_preflight_status"]
            
            m_11 = fix.get("m_11", [])
            m_10 = fix.get("m_10", [])
            m_01 = fix.get("m_01", [])
            m_00 = fix.get("m_00", [])
            
            n01 = len(m_01)
            
            record = {
                "fixture_id": q_id,
                "hypothesis": man_item["human_hypothesis"],
                "classification": "AMBIGUOUS",
                "criterion_applied": man_item["mechanical_support_condition"],
                "structural_evidence": fix,
                "raw_typed_scores": {},
                "typed_regrets": {},
                "partition_summaries": {
                    "m_11": m_11,
                    "m_10": m_10,
                    "m_01": m_01,
                    "m_00": m_00
                },
                "comparison_perspective": T1_11_CONFIG["comparison_perspective"],
                "engine_invoked": False,
                "engine_provenance": {}
            }
            
            if status == "PASS":
                record["classification"] = evaluate_structural(q_id, fix)
            elif status == "PRECONDITIONS_PASS_PENDING_ENGINE":
                record["engine_invoked"] = True
                
                board = chess.Board(man_item["pre_move_fen"])
                
                if q_id.startswith("Q4"):
                    scores, regrets = harness.evaluate_root_position(board)
                    
                    record["raw_typed_scores"] = {m: {"type": s.type, "value": s.value} for m, s in scores.items()}
                    record["typed_regrets"] = {m: {"type": r.type, "value": r.value} for m, r in regrets.items()}
                    
                    if n01 <= 0:
                        record["classification"] = "FALSIFIED"
                    else:
                        med_11 = median_regret_cp(regrets, m_11)
                        med_10 = median_regret_cp(regrets, m_10)
                        
                        if med_11 is None or med_10 is None:
                            record["classification"] = "AMBIGUOUS"
                        elif med_11 < med_10:
                            record["classification"] = "SUPPORTED"
                        else:
                            record["classification"] = "FALSIFIED"
                elif q_id.startswith("Q11"):
                    scores, regrets = harness.evaluate_root_position(board)
                    
                    record["raw_typed_scores"] = {m: {"type": s.type, "value": s.value} for m, s in scores.items()}
                    record["typed_regrets"] = {m: {"type": r.type, "value": r.value} for m, r in regrets.items()}
                    
                    if not scores:
                        record["classification"] = "AMBIGUOUS"
                    else:
                        has_mate = any(s.type == "mate" for s in scores.values())
                        if has_mate:
                            record["classification"] = "SUPPORTED"
                        else:
                            record["classification"] = "FALSIFIED"
                elif q_id.startswith("Q14"):
                    scores_primary, regrets_primary = harness.evaluate_root_position(board)
                    
                    twin_fen = man_item["twin_fixture"]["fen"]
                    twin_board = chess.Board(twin_fen)
                    scores_twin, regrets_twin = harness.evaluate_root_position(twin_board)
                    
                    record["raw_typed_scores"] = {
                        "primary": {m: {"type": s.type, "value": s.value} for m, s in scores_primary.items()},
                        "twin": {m: {"type": s.type, "value": s.value} for m, s in scores_twin.items()}
                    }
                    record["typed_regrets"] = {
                        "primary": {m: {"type": r.type, "value": r.value} for m, r in regrets_primary.items()},
                        "twin": {m: {"type": r.type, "value": r.value} for m, r in regrets_twin.items()}
                    }
                    
                    m_11_twin = fix["dimension_evidence"]["twin_partitions"]["m11"]
                    
                    med_11_p = median_regret_cp(regrets_primary, m_11)
                    med_11_t = median_regret_cp(regrets_twin, m_11_twin)
                    
                    if med_11_p is None or med_11_t is None:
                        record["classification"] = "AMBIGUOUS"
                    elif med_11_p != med_11_t:
                        record["classification"] = "SUPPORTED"
                    else:
                        record["classification"] = "FALSIFIED"
            
            if record["engine_invoked"]:
                record["engine_provenance"] = {
                    "threads": T1_11_CONFIG["threads"],
                    "hash_mb": T1_11_CONFIG["hash_mb"],
                    "nodes": T1_11_CONFIG["node_budget"]
                }
                
            results.append(record)
        
    os.makedirs(output_dir, exist_ok=True)
    
    for r in results:
        with open(os.path.join(output_dir, f"{r['fixture_id']}.json"), "w") as f:
            json.dump(r, f, indent=2)
            
    summary = {
        "total_fixtures": len(results),
        "classifications": {
            "SUPPORTED": len([r for r in results if r["classification"] == "SUPPORTED"]),
            "FALSIFIED": len([r for r in results if r["classification"] == "FALSIFIED"]),
            "AMBIGUOUS": len([r for r in results if r["classification"] == "AMBIGUOUS"])
        }
    }
    
    with open(os.path.join(output_dir, "aggregate_summary.json"), "w") as f:
        json.dump(summary, f, indent=2)

if __name__ == "__main__":
    pass
