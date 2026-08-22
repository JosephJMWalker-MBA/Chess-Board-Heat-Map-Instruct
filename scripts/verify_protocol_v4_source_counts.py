import sys
import json
from src.chessheat.protocol_freeze import get_partition, canonical_protocol_payload_v4

def main():
    print("Verifying SOURCE protocol V4 counts...")
    
    all_counts = {"TRAIN": 0, "VALIDATION": 0, "TEST": 0}
    eligible_counts = {"TRAIN": 0, "VALIDATION": 0, "TEST": 0}

    with open("artifacts/research/cp_source_feasibility_2026_07/raw/cp_source_root_results_v2.jsonl") as f:
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
    
    v4_payload = canonical_protocol_payload_v4()
    p_all = v4_payload["split"]["expected_all_root_counts"]
    p_el = v4_payload["split"]["expected_eligible_counts"]
    p_z = v4_payload["split"]["expected_zero_counts"]
    
    print(f"Measured All Counts: {all_counts}")
    print(f"Payload All Counts: {p_all}")
    if all_counts != p_all:
        sys.exit(f"Mismatch in all_root counts: {all_counts} != {p_all}")
        
    print(f"Measured Eligible Counts: {eligible_counts}")
    print(f"Payload Eligible Counts: {p_el}")
    if eligible_counts != p_el:
        sys.exit(f"Mismatch in eligible counts: {eligible_counts} != {p_el}")
        
    print(f"Measured Zero Counts: {zero_counts}")
    print(f"Payload Zero Counts: {p_z}")
    if zero_counts != p_z:
        sys.exit(f"Mismatch in zero counts: {zero_counts} != {p_z}")

    total_all = sum(all_counts.values())
    total_eligible = sum(eligible_counts.values())
    print(f"Total All: {total_all}, Total Eligible: {total_eligible}")
    if total_all != 33859 or total_eligible != 33444:
        sys.exit(f"Totals mismatch: {total_all}, {total_eligible}")
        
    print("SOURCE counts exactly match V4 payload.")
    sys.exit(0)

if __name__ == "__main__":
    main()
