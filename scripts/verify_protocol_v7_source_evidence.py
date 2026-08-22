import sys
import json
import hashlib
from src.chessheat.protocol_freeze import get_partition, canonical_protocol_payload_v7

def main():
    print("Verifying SOURCE protocol V7 counts and SHA...")
    
    expected_sha = "7eb640c572dad4c6607cfb1b5ccf99597672042e5c516f131feab02223ccfa6b"
    raw_path = "artifacts/research/cp_source_feasibility_2026_07/raw/cp_source_root_results_v2.jsonl"
    
    sha256_hash = hashlib.sha256()
    with open(raw_path, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    
    actual_sha = sha256_hash.hexdigest()
    print(f"RAW SOURCE SHA256:\n{actual_sha}")
    if actual_sha != expected_sha:
        print("MATCH: FAIL")
        sys.exit(f"SHA mismatch! Expected {expected_sha}, got {actual_sha}")
    else:
        print("MATCH: PASS\n")
    
    all_counts = {"TRAIN": 0, "VALIDATION": 0, "TEST": 0}
    eligible_counts = {"TRAIN": 0, "VALIDATION": 0, "TEST": 0}

    with open(raw_path) as f:
        for line in f:
            data = json.loads(line)
            payload = json.loads(data['experiment_result']['data_payload'])
            sp = payload['root_sufficient_position']
            part = get_partition(sp)
            all_counts[part] += 1
            
            finite = 0
            if 'observations' in payload:
                for obs in payload['observations']:
                    if 'score_value' in obs and obs['score_type'] == 'cp':
                        finite += 1
            
            if finite >= 2:
                eligible_counts[part] += 1

    zero_counts = {
        "TRAIN": all_counts["TRAIN"] - eligible_counts["TRAIN"],
        "VALIDATION": all_counts["VALIDATION"] - eligible_counts["VALIDATION"],
        "TEST": all_counts["TEST"] - eligible_counts["TEST"]
    }
    
    v5_payload = canonical_protocol_payload_v7()
    p_all = v5_payload["split"]["expected_all_root_counts"]
    p_el = v5_payload["split"]["expected_eligible_counts"]
    p_z = v5_payload["split"]["expected_zero_counts"]
    
    if all_counts != p_all:
        sys.exit(f"Mismatch in all_root counts: {all_counts} != {p_all}")
        
    if eligible_counts != p_el:
        sys.exit(f"Mismatch in eligible counts: {eligible_counts} != {p_el}")
        
    if zero_counts != p_z:
        sys.exit(f"Mismatch in zero counts: {zero_counts} != {p_z}")

    total_all = sum(all_counts.values())
    total_eligible = sum(eligible_counts.values())
    if total_all != 33859 or total_eligible != 33444:
        sys.exit(f"Totals mismatch: {total_all}, {total_eligible}")
        
    print("ALL COUNTS:")
    print(f"{all_counts['TRAIN']} / {all_counts['VALIDATION']} / {all_counts['TEST']}\n")
    print("ELIGIBLE:")
    print(f"{eligible_counts['TRAIN']} / {eligible_counts['VALIDATION']} / {eligible_counts['TEST']}\n")
    print("ZERO:")
    print(f"{zero_counts['TRAIN']} / {zero_counts['VALIDATION']} / {zero_counts['TEST']}\n")
    print("TOTALS:")
    print(f"{total_all} / {total_eligible} / {sum(zero_counts.values())}\n")
    print("PASS.")
    sys.exit(0)

if __name__ == "__main__":
    main()
