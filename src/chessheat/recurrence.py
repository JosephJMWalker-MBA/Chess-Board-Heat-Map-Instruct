from typing import Dict, Any
from .models import AnalysisRecord, SquareRecurrence, RecurrenceMetric, CandidateProvenance, RecurrenceResult

def aggregate_square_recurrence(record: AnalysisRecord) -> RecurrenceResult:
    """
    Computes PV Recurrence metrics for each square based on the candidate policy.
    """
    policy = record.candidate_policy
    top_n = policy.get("top_n")
    max_regret_cp = policy.get("max_regret_cp")

    # Sort move observations by regret
    def regret_sort_key(obs):
        r = obs.regret
        if not r:
            return float('inf')
        if r.type == "mate":
            return r.value if r.value is not None else float('inf')
        return r.value if r.value is not None else float('inf')

    # All legal root moves
    all_observations = sorted(record.move_observations, key=regret_sort_key)
    candidate_lines = all_observations

    # Filter by max_regret_cp if provided
    if max_regret_cp is not None:
        candidate_lines = [
            obs for obs in candidate_lines
            if obs.regret and obs.regret.type == "cp" and obs.regret.value is not None and obs.regret.value <= max_regret_cp
        ]

    # Then apply top_n if provided
    if top_n is not None:
        candidate_lines = candidate_lines[:top_n]

    num_candidates = len(candidate_lines)

    candidate_scores = {obs.uci: obs.score for obs in candidate_lines}
    candidate_regrets = {obs.uci: obs.regret for obs in candidate_lines if obs.regret}

    provenance = CandidateProvenance(
        total_legal_moves=len(all_observations),
        candidate_policy=policy,
        admitted_count=num_candidates,
        admitted_root_moves=[obs.uci for obs in candidate_lines],
        candidate_scores=candidate_scores,
        candidate_regrets=candidate_regrets,
        aggregated_pvs=0 # will be updated
    )

    if num_candidates == 0:
        return RecurrenceResult(provenance=provenance, squares={})

    # 2. Aggregate Recurrence
    # Data structure: square -> role -> { lines_visited: set(uci), visit_count: int, earliest_ply: int }
    # role "overall" means across any role.

    agg = {}

    def init_sq(sq):
        if sq not in agg:
            agg[sq] = {
                "overall": {"lines": set(), "visits": 0, "earliest": None},
                "roles": {}
            }

    def init_role(sq, r):
        init_sq(sq)
        if r not in agg[sq]["roles"]:
            agg[sq]["roles"][r] = {"lines": set(), "visits": 0, "earliest": None}

    for root_uci in [obs.uci for obs in candidate_lines]:
        obs = next(o for o in candidate_lines if o.uci == root_uci)
        if obs.parsed_pv:
            provenance.aggregated_pvs += 1

        for ply_obs in obs.parsed_pv:
            sqs = set()
            roles_map = []

            roles_map.append((ply_obs.origin, "origin"))
            sqs.add(ply_obs.origin)

            roles_map.append((ply_obs.destination, "destination"))
            sqs.add(ply_obs.destination)

            if ply_obs.capture:
                roles_map.append((ply_obs.capture, "capture"))
                sqs.add(ply_obs.capture)

            ply = ply_obs.ply_number

            # Update overall
            for sq in sqs:
                init_sq(sq)
                agg[sq]["overall"]["lines"].add(root_uci)
                agg[sq]["overall"]["visits"] += 1
                if agg[sq]["overall"]["earliest"] is None or ply < agg[sq]["overall"]["earliest"]:
                    agg[sq]["overall"]["earliest"] = ply

            # Update roles
            for sq, r in roles_map:
                init_role(sq, r)
                agg[sq]["roles"][r]["lines"].add(root_uci)
                agg[sq]["roles"][r]["visits"] += 1
                if agg[sq]["roles"][r]["earliest"] is None or ply < agg[sq]["roles"][r]["earliest"]:
                    agg[sq]["roles"][r]["earliest"] = ply

    # 3. Format output
    result = {}
    for sq, data in agg.items():
        overall_metric = RecurrenceMetric(
            distinct_line_count=len(data["overall"]["lines"]),
            line_fraction=len(data["overall"]["lines"]) / num_candidates,
            visit_count=data["overall"]["visits"],
            earliest_ply=data["overall"]["earliest"]
        )

        by_role = {}
        for r, r_data in data["roles"].items():
            by_role[r] = RecurrenceMetric(
                distinct_line_count=len(r_data["lines"]),
                line_fraction=len(r_data["lines"]) / num_candidates,
                visit_count=r_data["visits"],
                earliest_ply=r_data["earliest"]
            )

        result[sq] = SquareRecurrence(
            square=sq,
            overall=overall_metric,
            by_role=by_role
        )

    return RecurrenceResult(provenance=provenance, squares=result)
