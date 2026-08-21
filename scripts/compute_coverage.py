import json
import math
from collections import Counter
from typing import Dict, Any, List
from chessheat.cp_source_feasibility import SourceFeasibilityRunnerV2, build_source_v2_spec

def percentile_nearest_rank(values: List[int], p: float) -> int:
    if not values:
        return 0
    values = sorted(values)
    rank = math.ceil(p * len(values))
    rank = max(1, min(rank, len(values)))
    return values[rank - 1]

def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", default="artifacts/research/cp_source_feasibility_2026_07/cp_root_population_manifest_v2.jsonl.zst")
    parser.add_argument("--output", default="artifacts/research/cp_source_feasibility_2026_07/raw/cp_source_root_results_v2.jsonl")
    parser.add_argument("--meta", default="artifacts/research/cp_source_feasibility_2026_07/cp_root_population_manifest_v2.meta.json")
    args = parser.parse_args()

    # Reuse runner's envelope validations
    # The runner validates EVERYTHING if we pass it the output path.
    # It parses the manifest, meta, and the existing jsonl entirely, verifying all envelope rules.
    try:
        runner = SourceFeasibilityRunnerV2(args.manifest, args.output, "dummy_stockfish", args.meta)
    except Exception as e:
        print(f"Validation failed: {e}")
        raise
        
    roots_attempted = 0
    roots_successful = 0
    roots_failed = 0
    
    total_legal_alternatives = 0
    total_successful_child_observations = 0
    total_cp_alternatives = 0
    total_mate_alternatives = 0
    
    roots_ge_2_cp = 0
    roots_lt_2_cp = 0
    roots_zero_cp = 0
    total_cp_pairs = 0
    
    legal_alts_per_root = []
    cp_alts_per_root = []
    pairs_per_root = []
    
    options_digests = set()
    
    with open(args.output, "r", encoding="utf-8") as f:
        for i, line in enumerate(f):
            if not line.strip():
                raise ValueError("Blank line in result artifact")
            roots_attempted += 1
            record = json.loads(line)
            
            if record["status"] == "FAILURE":
                roots_failed += 1
                continue
                
            roots_successful += 1
            
            er_dump = record["experiment_result"]
            payload = json.loads(er_dump["data_payload"])
            
            expected_r = runner.admitted_roots[i]
            expected_spec = build_source_v2_spec(expected_r, runner.manifest_digest, record["producer_uci_name"])
            req_count = expected_spec.candidate_policy["required_search_count"]
            
            observations = payload["observations"]
            canonical_order = payload["canonical_acquisition_order"]
            
            L = len(observations)
            if L != len(canonical_order):
                raise ValueError("Observations length != canonical_acquisition_order length")
                
            if L != req_count:
                raise ValueError("Observations length != expected required_search_count")
                
            obs_ucis = [o["root_move_uci"] for o in observations]
            if obs_ucis != canonical_order:
                raise ValueError("Observation ucis do not match canonical_order exactly")
                
            c_count = 0
            m_count = 0
            for o in observations:
                st = o["score_type"]
                if st == "cp":
                    c_count += 1
                elif st == "mate":
                    m_count += 1
                else:
                    raise ValueError(f"Invalid score_type: {st}")
                    
            if c_count + m_count != L:
                raise ValueError("CP + Mate count does not equal L")
                
            pairs = c_count * (c_count - 1) // 2
            
            total_legal_alternatives += req_count
            total_successful_child_observations += L
            total_cp_alternatives += c_count
            total_mate_alternatives += m_count
            
            if c_count >= 2:
                roots_ge_2_cp += 1
            else:
                roots_lt_2_cp += 1
            if pairs == 0:
                roots_zero_cp += 1
                
            total_cp_pairs += pairs
            
            legal_alts_per_root.append(req_count)
            cp_alts_per_root.append(c_count)
            pairs_per_root.append(pairs)
            
            from chessheat.cp_root_population import canonical_json_digest
            if "options_surface" not in payload:
                raise ValueError("Provenance error: missing options_surface")
            if not payload["options_surface"]:
                raise ValueError("Provenance error: empty options_surface")
            opt_digest = canonical_json_digest(payload["options_surface"])
            options_digests.add(opt_digest)

    if len(options_digests) > 1:
        raise ValueError(f"Provenance inconsistency: Multiple options_surface digests found: {options_digests}")
        
    print(f"roots attempted: {roots_attempted}")
    print(f"roots successful: {roots_successful}")
    print(f"roots failed: {roots_failed}")
    print(f"total legal alternatives: {total_legal_alternatives}")
    print(f"total successful child observations: {total_successful_child_observations}")
    print(f"CP alternatives: {total_cp_alternatives}")
    print(f"mate alternatives: {total_mate_alternatives}")
    
    cp_frac = total_cp_alternatives / total_successful_child_observations if total_successful_child_observations > 0 else 0
    print(f"CP fraction: {cp_frac:.4f}")
    
    print(f"roots with >=2 CP alternatives: {roots_ge_2_cp}")
    print(f"roots with <2 CP alternatives: {roots_lt_2_cp}")
    print(f"roots with zero CP/CP pairs: {roots_zero_cp}")
    print(f"total CP/CP unordered pairs: {total_cp_pairs}")
    
    report_dist("legal alternatives/root", legal_alts_per_root)
    report_dist("CP alternatives/root", cp_alts_per_root)
    report_dist("CP/CP pairs/root", pairs_per_root)
    
    if options_digests:
        print(f"Options surface SHA256: {list(options_digests)[0]}")

def get_median(vals):
    n = len(vals)
    if n % 2 == 1:
        return vals[n//2]
    return (vals[n//2 - 1] + vals[n//2]) / 2.0

def report_dist(name, vals):
    if not vals:
        print(f"{name}: N/A")
        return
    vals_sorted = sorted(vals)
    print(f"{name}:")
    print(f"  min: {vals_sorted[0]}")
    print(f"  median: {get_median(vals_sorted)}")
    print(f"  nearest-rank p90: {percentile_nearest_rank(vals, 0.90)}")
    print(f"  nearest-rank p95: {percentile_nearest_rank(vals, 0.95)}")
    print(f"  max: {vals_sorted[-1]}")

if __name__ == "__main__":
    main()
