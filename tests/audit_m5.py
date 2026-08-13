import json
import os
import glob
from collections import defaultdict
import math

FIXTURES_FILE = "tests/fixtures/validation_m5.json"
RESULTS_DIR = "tests/fixtures/results"
AUDIT_REPORT_JSON = "tests/fixtures/m5_audit.json"
AUDIT_REPORT_MD = "tests/fixtures/m5_audit_summary.md"

def get_valence(metric_name):
    if "regret" in metric_name:
        return "inverse"
    elif "cp" in metric_name:
        return "positive"
    return "neutral"

def calculate_metric(moves, metric_filter):
    if not moves:
        return None
    if metric_filter == "move_count":
        return len(moves)
    if metric_filter == "mate_count":
        return sum(1 for m in moves if m.get("outcome", {}).get("type") == "mate")

    cp_outcomes = [m["outcome"]["value"] for m in moves if m.get("outcome", {}).get("type") == "cp"]
    cp_regrets = [m["regret"]["value"] for m in moves if m.get("regret") and m["regret"].get("type") == "cp" and m["regret"].get("value") is not None]

    if "outcome" in metric_filter:
        if not cp_outcomes: return None
        if metric_filter == "best_cp": return max(cp_outcomes)
        if metric_filter == "worst_cp": return min(cp_outcomes)
        if metric_filter == "mean_cp": return sum(cp_outcomes) / len(cp_outcomes)

    if "regret" in metric_filter:
        if not cp_regrets: return None
        if metric_filter == "min_cp_regret": return min(cp_regrets)
        if metric_filter == "max_cp_regret": return max(cp_regrets)
        if metric_filter == "mean_cp_regret": return sum(cp_regrets) / len(cp_regrets)
    return None

def extract_values(record, expected_layer):
    # expected_layer e.g. "destination + min_cp_regret", "delta outcome"
    values = {}
    if "delta" in expected_layer:
        # Paired record
        deltas = record.get("deltas", {})
        # For simplicity, extract destination mean_cp delta, or just a default if not fully specified
        role = "destination"
        metric = "mean_cp" # fallback
        if "outcome" in expected_layer: metric = "mean_cp"
        for sq, delta_data in deltas.items():
            val = delta_data["roles"].get(role, {}).get("metrics", {}).get(metric, {}).get("delta")
            if val is not None:
                values[sq] = val
    else:
        # Normal record
        parts = expected_layer.split("+")
        role = parts[0].strip() if len(parts) > 0 else "all"
        metric = parts[1].strip() if len(parts) > 1 else "move_count"

        attributions = record.get("attributions", {})
        for sq, attr in attributions.items():
            moves = attr.get("implicated_moves", [])
            if role != "all":
                moves = [m for m in moves if role in m.get("roles", [])]
            val = calculate_metric(moves, metric)
            if val is not None:
                values[sq] = val

    return values, expected_layer.split("+")[-1].strip() if "+" in expected_layer else "mean_cp"

def rank_squares(values, metric_name):
    # Sort squares. If valence is positive, highest is best. Inverse, lowest is best.
    valence = get_valence(metric_name)
    reverse = True if valence == "positive" else False

    sorted_items = sorted(values.items(), key=lambda x: x[1], reverse=reverse)
    ranks = {}
    for i, (sq, val) in enumerate(sorted_items):
        ranks[sq] = i + 1
    return sorted_items, ranks

def jaccard(set_a, set_b):
    if not set_a and not set_b:
        return 1.0
    return len(set_a.intersection(set_b)) / len(set_a.union(set_b))

def run_audit():
    with open(FIXTURES_FILE, "r") as f:
        fixtures = json.load(f)

    budgets = [50000, 100000, 250000]
    audit_results = {}

    for fixture in fixtures:
        fid = fixture["fixture_id"]
        expected_layer = fixture["hypothesis"].get("expected_best_layer", "all + move_count")
        if expected_layer == "None":
            expected_layer = "destination + mean_cp" # fallback for F6

        expected_hot = set(fixture["hypothesis"].get("expected_hot_region", []))
        expected_quiet = set(fixture["hypothesis"].get("expected_quiet_region", []))

        fixture_audit = {
            "hypothesis": fixture["hypothesis"],
            "budgets": {}
        }

        top5_sets = {}

        for b in budgets:
            fpath = os.path.join(RESULTS_DIR, f"{fid}_{b}.json")
            if not os.path.exists(fpath):
                continue
            with open(fpath, "r") as f:
                record = json.load(f)

            values, metric_name = extract_values(record, expected_layer)
            sorted_items, ranks = rank_squares(values, metric_name)

            top5 = [sq for sq, val in sorted_items[:5]]
            top5_sets[b] = set(top5)

            hot_ranks = {sq: ranks.get(sq, -1) for sq in expected_hot}
            quiet_ranks = {sq: ranks.get(sq, -1) for sq in expected_quiet}

            fixture_audit["budgets"][str(b)] = {
                "top_5": top5,
                "hot_region_ranks": hot_ranks,
                "quiet_region_ranks": quiet_ranks,
                "values_distribution": {
                    "min": min(values.values()) if values else None,
                    "max": max(values.values()) if values else None,
                    "count": len(values)
                }
            }

        # Cross-budget stability
        stability = {}
        if 50000 in top5_sets and 100000 in top5_sets:
            stability["jaccard_50k_100k"] = jaccard(top5_sets[50000], top5_sets[100000])
        if 100000 in top5_sets and 250000 in top5_sets:
            stability["jaccard_100k_250k"] = jaccard(top5_sets[100000], top5_sets[250000])
        if 50000 in top5_sets and 250000 in top5_sets:
            stability["jaccard_50k_250k"] = jaccard(top5_sets[50000], top5_sets[250000])

        fixture_audit["stability"] = stability
        audit_results[fid] = fixture_audit

    with open(AUDIT_REPORT_JSON, "w") as f:
        json.dump(audit_results, f, indent=2)

    # Generate MD summary
    with open(AUDIT_REPORT_MD, "w") as f:
        f.write("# Milestone 5.5: Machine-Auditable Validation Summary\n\n")
        for fid, data in audit_results.items():
            f.write(f"## {fid}\n")
            f.write(f"**Target Layer:** {data['hypothesis'].get('expected_best_layer')}\n")
            f.write(f"**Expected Hot:** {', '.join(data['hypothesis'].get('expected_hot_region', []))}\n")
            f.write(f"**Expected Quiet:** {', '.join(data['hypothesis'].get('expected_quiet_region', []))}\n\n")

            f.write("### Budget Ranks\n")
            for b in budgets:
                bs = str(b)
                if bs not in data["budgets"]: continue
                b_data = data["budgets"][bs]
                f.write(f"- **{b} nodes:**\n")
                f.write(f"  - Top 5: {', '.join(b_data['top_5'])}\n")
                f.write(f"  - Expected Hot Ranks: {b_data['hot_region_ranks']}\n")

            f.write("\n### Top-5 Stability (Jaccard Index)\n")
            stab = data.get("stability", {})
            f.write(f"- 50k vs 100k: {stab.get('jaccard_50k_100k', 0):.2f}\n")
            f.write(f"- 100k vs 250k: {stab.get('jaccard_100k_250k', 0):.2f}\n\n")

if __name__ == "__main__":
    run_audit()
