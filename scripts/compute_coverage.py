import json
import math
from pathlib import Path
from chessheat.experiment import ExperimentResult

def main():
    result_path = Path("artifacts/research/cp_source_feasibility_2026_07/raw/cp_source_root_results_v2.jsonl")
    if not result_path.exists():
        print("No results to compute")
        return
        
    legal_alts_dist = []
    cp_alts_dist = []
    pairs_dist = []
    
    roots_attempted = 0
    roots_success = 0
    roots_failed = 0
    
    total_legal = 0
    total_cp = 0
    total_mate = 0
    roots_ge2_cp = 0
    roots_lt2_cp = 0
    total_pairs = 0
    
    options_digest_set = set()
    
    with open(result_path, "r", encoding="utf-8") as f:
        for line in f:
            if not line.strip(): continue
            rec = json.loads(line)
            roots_attempted += 1
            if rec["status"] == "SUCCESS":
                roots_success += 1
                er = ExperimentResult(**rec["experiment_result"])
                payload = json.loads(er.data_payload)
                
                # Options digest
                opts = payload["options_surface"]
                opt_str = json.dumps(opts, sort_keys=True, separators=(",", ":")).encode("utf-8")
                import hashlib
                opts_digest = hashlib.sha256(opt_str).hexdigest()
                options_digest_set.add(opts_digest)
                
                obs = payload["observations"]
                L = len(obs)
                C = sum(1 for o in obs if o["score_type"] == "cp")
                M = sum(1 for o in obs if o["score_type"] == "mate")
                
                if C + M != L:
                    raise ValueError("Observation count mismatch")
                
                pairs = C * (C - 1) // 2
                
                total_legal += L
                total_cp += C
                total_mate += M
                total_pairs += pairs
                
                if C >= 2:
                    roots_ge2_cp += 1
                else:
                    roots_lt2_cp += 1
                    
                legal_alts_dist.append(L)
                cp_alts_dist.append(C)
                pairs_dist.append(pairs)
                
            else:
                roots_failed += 1

    print(f"Attempted: {roots_attempted}, Success: {roots_success}, Failed: {roots_failed}")
    print(f"Total legal: {total_legal}, Total CP: {total_cp}, Total Mate: {total_mate}")
    print(f"Roots >=2 CP: {roots_ge2_cp}, Roots <2 CP: {roots_lt2_cp}, Total pairs: {total_pairs}")
    
    if len(options_digest_set) > 1:
        print("WARNING: Multiple options digests observed:", options_digest_set)
        
    def get_dist(arr):
        if not arr: return {}
        arr = sorted(arr)
        N = len(arr)
        def nearest_rank(p):
            rank = math.ceil(p * N)
            return arr[max(0, rank - 1)]
        return {
            "min": arr[0],
            "median": arr[N//2] if N % 2 != 0 else (arr[N//2 - 1] + arr[N//2]) / 2.0,
            "p90": nearest_rank(0.90),
            "p95": nearest_rank(0.95),
            "max": arr[-1]
        }
        
    print("Legal dist:", get_dist(legal_alts_dist))
    print("CP dist:", get_dist(cp_alts_dist))
    print("Pairs dist:", get_dist(pairs_dist))
    print("Options digest:", list(options_digest_set))

if __name__ == "__main__":
    main()
