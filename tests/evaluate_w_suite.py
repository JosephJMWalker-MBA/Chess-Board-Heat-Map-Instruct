import json
from typing import Dict, Any, List, Set

def compute_recall(expected: Set[str], selected: Set[str]) -> float:
    if not expected: return 1.0
    intersection = expected.intersection(selected)
    return len(intersection) / len(expected)

def compute_precision(expected: Set[str], selected: Set[str]) -> float:
    if not selected: return 1.0
    intersection = expected.intersection(selected)
    return len(intersection) / len(selected)

def evaluate_w_suite(results_path: str):
    with open(results_path) as f:
        data = json.load(f)
        
    for fid, d in data.items():
        print(f"--- Evaluating {fid} ---")
        
        all_expected = set()
        for region in d.get("expected_regions", []):
            sqs = set(region["squares"])
            all_expected.update(sqs)
            
        selected_squares = set(d.get("selected_squares", []))
        
        # Region Level
        for region in d.get("expected_regions", []):
            sqs = set(region["squares"])
            r_recall = compute_recall(sqs, selected_squares)
            print(f"Region '{region['id']}' Recall: {r_recall:.2f}")
            
        # Global Level
        g_recall = compute_recall(all_expected, selected_squares)
        g_precision = compute_precision(all_expected, selected_squares)
        
        print(f"Global Recall: {g_recall:.2f}")
        print(f"Global Precision: {g_precision:.2f}")
        print(f"Selected Count: {len(selected_squares)}")
        print(f"False Positive Area: {len(selected_squares - all_expected)}")
        
        # Breakdown by Channel / Rejections
        print("Channel Sources:", d.get("channel_sources", {}))
        print("Observed-but-Rejected Count:", d.get("rejected_count", 0))
        print("Rejection Reasons:", d.get("rejection_reasons", {}))
        print(f"Amplitude (A_cp): {d.get('a_cp')}, Amplitude (A_mate): {d.get('a_mate')}")
        print(f"Zero-Optionality State: {d.get('zero_optionality')}")
        print()

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        evaluate_w_suite(sys.argv[1])
