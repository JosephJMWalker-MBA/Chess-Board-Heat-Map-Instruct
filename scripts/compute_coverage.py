import json
import hashlib
from typing import Dict, Any, Tuple
from collections import Counter
from chessheat.experiment import ExperimentResult
from chessheat.cp_root_population import canonical_json_digest

def validate_and_extract_coverage(record: Dict[str, Any]) -> Tuple[Dict[str, int], str]:
    if record["status"] != "SUCCESS":
        return None, None
        
    er = ExperimentResult(**record["experiment_result"])
    payload = json.loads(er.data_payload)
    observations = payload.get("observations", [])
    
    cp_count = sum(1 for o in observations if o["score_type"] == "cp")
    mate_count = sum(1 for o in observations if o["score_type"] == "mate")
    total_count = len(observations)
    
    if cp_count + mate_count != total_count:
        raise ValueError("Non-cp/mate score_type found")
        
    policy = payload.get("candidate_policy", {})
    required = policy.get("required_search_count")
    if total_count != required:
        raise ValueError("Observation count mismatch with required_search_count")
        
    options_surface = payload.get("options_surface", [])
    options_digest = canonical_json_digest(options_surface)
    
    counts = {
        "cp": cp_count,
        "mate": mate_count,
        "total": total_count,
        "pairs": (cp_count * (cp_count - 1)) // 2
    }
    return counts, options_digest

def main():
    path = "artifacts/research/cp_source_feasibility_2026_07/raw/cp_source_root_results_v2.jsonl"
    
    total_roots = 0
    success_roots = 0
    total_cp = 0
    total_mate = 0
    total_pairs = 0
    options_digests = set()
    
    try:
        with open(path, "r", encoding="utf-8") as f:
            for line in f:
                if not line.strip(): continue
                total_roots += 1
                record = json.loads(line)
                
                counts, digest = validate_and_extract_coverage(record)
                if counts is None:
                    continue
                    
                success_roots += 1
                total_cp += counts["cp"]
                total_mate += counts["mate"]
                total_pairs += counts["pairs"]
                options_digests.add(digest)
    except FileNotFoundError:
        print("No results file found.")
        return
        
    if len(options_digests) > 1:
        raise ValueError(f"Multiple options surface digests found: {options_digests}")
        
    print(f"Total Roots: {total_roots}")
    print(f"Success Roots: {success_roots}")
    print(f"Total CP Options: {total_cp}")
    print(f"Total Mate Options: {total_mate}")
    print(f"Total CP Pairs: {total_pairs}")
    
    if options_digests:
        print(f"Unique Options Digest: {list(options_digests)[0]}")

if __name__ == "__main__":
    main()
