from typing import List, Protocol
from .models import AnalysisRecord, BranchUniverse, FutureBranch, SpatialEvent

def extract_branches(record: AnalysisRecord) -> BranchUniverse:
    """
    Extracts admitted future branches from an AnalysisRecord.
    Constructs the BranchUniverse which preserves branch identity,
    typed regret, and spatially ordered events before aggregation.
    """
    policy = record.candidate_policy
    top_n = policy.get("top_n")
    max_regret_cp = policy.get("max_regret_cp")

    # Recreate the filtering logic from recurrence.py
    def regret_sort_key(obs):
        r = obs.regret
        if not r:
            return float('inf')
        if r.type == "mate":
            return r.value if r.value is not None else float('inf')
        return r.value if r.value is not None else float('inf')

    all_observations = sorted(record.move_observations, key=regret_sort_key)
    admitted_lines = list(all_observations)

    if max_regret_cp is not None:
        admitted_lines = [
            obs for obs in admitted_lines
            if obs.regret and obs.regret.type == "cp" and obs.regret.value is not None and obs.regret.value <= max_regret_cp
        ]
    
    if top_n is not None:
        admitted_lines = admitted_lines[:top_n]

    admitted_ucis = {obs.uci for obs in admitted_lines}
    
    candidate_scores = {obs.uci: obs.score for obs in admitted_lines}
    candidate_regrets = {obs.uci: obs.regret for obs in admitted_lines if obs.regret}
    
    from .models import CandidateProvenance, EvidenceEnvelope

    envelope = EvidenceEnvelope(
        epistemic_guarantee="search_derived",
        subject_kind="square",
        producer=record.engine_name,
        history_requirement=False,
        line_source="pv"
    )

    branches = []
    aggregated_pvs = 0
    for obs in all_observations:
        is_admitted = obs.uci in admitted_ucis
        
        events = []
        future_moves = []
        if obs.parsed_pv and is_admitted:
            aggregated_pvs += 1
            for ply_obs in obs.parsed_pv:
                ply = ply_obs.ply_number
                future_moves.append(ply_obs.uci)
                events.append(SpatialEvent(square=ply_obs.origin, role="origin", ply=ply))
                events.append(SpatialEvent(square=ply_obs.destination, role="destination", ply=ply))
                if ply_obs.capture:
                    events.append(SpatialEvent(square=ply_obs.capture, role="capture", ply=ply))
        
        branches.append(FutureBranch(
            root_uci=obs.uci,
            root_fen=record.fen,
            actor=record.root_side,
            line_source="pv",
            producer=record.engine_name,
            score=obs.score,
            regret=obs.regret,
            is_admitted=is_admitted,
            future_moves=future_moves,
            future_evidence=events
        ))
        
    provenance = CandidateProvenance(
        total_legal_moves=len(all_observations),
        candidate_policy=policy,
        admitted_count=len(admitted_lines),
        admitted_root_moves=[obs.uci for obs in admitted_lines],
        candidate_scores=candidate_scores,
        candidate_regrets=candidate_regrets,
        aggregated_pvs=aggregated_pvs
    )
    
    return BranchUniverse(
        envelope=envelope,
        provenance=provenance,
        branches=branches
    )


class ConsequenceDiscriminationStatistic(Protocol):
    """
    Specification for a future statistic that evaluates how strongly a 
    specific spatial event partitions good vs. bad branches.
    This enables evaluation of regional/spatial consequence without
    discarding the branch identity.
    """
    def evaluate(self, branches: List[FutureBranch], event_square: str, event_role: str) -> float:
        ...

