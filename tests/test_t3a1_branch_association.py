import json
import math
import statistics
import pytest
import chess
import hashlib
from typing import List, Dict, Any

from chessheat.models import AnalysisRecord, Score, MoveObservation, FutureBranch
from chessheat.branch import extract_branches
from chessheat.experiment import ExperimentSpec, ExperimentResult, SuiteManifest, SuiteKind
from chessheat.semantics import SemanticSignatureV1, SufficientPosition
from chessheat.consequence import compute_regrets

def evaluate_t3a1(branches: List[FutureBranch]) -> Dict[str, Any]:
    event_sq = "e4"
    event_role = "capture"
    
    partition_1 = []
    partition_0 = []
    
    short_roots = {}
    
    all_regrets = {}
    
    observed_event_occurrence_count = 0
    
    classification = None
    failure_reason = None
    
    for b in branches:
        if b.regret.type != "cp":
            classification = "INCONCLUSIVE"
            failure_reason = "MIXED_MATE_CP"
            break
            
        all_regrets[b.root_uci] = {"type": b.regret.type, "value": b.regret.value}
        
        # future_moves excludes ply 1 root move. Horizon is ply 2-5 inclusive (4 plies)
        if len(b.future_moves) < 4:
            short_roots[b.root_uci] = len(b.future_moves)
            classification = "INCONCLUSIVE"
            failure_reason = "INSUFFICIENT_OBSERVED_PV_LENGTH"
            # Do not break immediately; we want to gather all short roots and all occurrences
            
        x = 0
        for ev in b.future_evidence:
            if 2 <= ev.ply <= 5:
                if ev.square == event_sq and ev.role == event_role:
                    x = 1
                    observed_event_occurrence_count += 1
                    
        if x == 1:
            partition_1.append(b)
        else:
            partition_0.append(b)
            
    if classification is None:
        if len(partition_1) < 2 or len(partition_0) < 2:
            classification = "INCONCLUSIVE"
            failure_reason = "PARTITIONS_TOO_SMALL"
            
    r_1 = [b.regret.value for b in partition_1]
    r_0 = [b.regret.value for b in partition_0]
    
    D = None
    M = None
    
    if classification is None:
        median_1 = statistics.median(r_1)
        median_0 = statistics.median(r_0)
        D = median_1 - median_0
        
        min_1 = min(r_1)
        max_0 = max(r_0)
        M = min_1 - max_0
        
        if D > 0 and M > 0:
            classification = "SUPPORTED"
        elif D > 0 and M <= 0:
            classification = "WEAK_SUPPORT"
        else:
            classification = "FALSIFIED"
            
    # For incomplete horizon, we cannot know X_i for all branches
    # So the true full-root aggregate membership count is unavailable
    if short_roots:
        full_root_aggregate_membership_count = "UNAVAILABLE_DUE_TO_INCOMPLETE_HORIZON"
    else:
        full_root_aggregate_membership_count = len(partition_1)
        
    return {
        "classification": classification,
        "failure_reason": failure_reason,
        "event": {"square": event_sq, "role": event_role},
        "horizon_plies": [2, 3, 4, 5],
        "short_roots": short_roots,
        "typed_root_regrets": all_regrets,
        "evaluable_event_present_roots": sorted([b.root_uci for b in partition_1]),
        "evaluable_event_absent_roots": sorted([b.root_uci for b in partition_0]),
        "is_evaluable_set_incomplete": len(short_roots) > 0,
        "D": D,
        "M": M,
        "full_root_aggregate_membership_count": full_root_aggregate_membership_count,
        "observed_event_occurrence_count": observed_event_occurrence_count,
        "preregistration_commit": "748fb141450ae14ca489120900a520027c21ffc6"
    }

def test_t3a1_branch_conditioned_association():
    with open("tests/fixtures/t3a1_fixture.json", "r") as f:
        fixture = json.load(f)
        
    fen = fixture["fen"]
    preregistration_commit = fixture["preregistration_commit"]
    
    move_observations = [MoveObservation(**obs) for obs in fixture["observations"]]
    scores_dict = {obs.uci: obs.score for obs in move_observations}
    regrets_dict = compute_regrets(scores_dict)
    
    for obs in move_observations:
        if obs.uci in regrets_dict:
            obs.regret = regrets_dict[obs.uci]
            
    record = AnalysisRecord(
        fen=fen,
        root_side="white",
        comparison_perspective="white",
        engine_name="stockfish",
        search_budget_type="nodes",
        search_budget_value=100000,
        candidate_policy={},
        baseline_observation=Score(type="cp", value=0, perspective="white"),
        move_observations=move_observations
    )
    
    universe = extract_branches(record)
    branches = universe.branches
    
    board = chess.Board(fen)
    legal_ucis = {m.uci() for m in board.legal_moves}
    obs_ucis = {b.root_uci for b in branches}
    assert legal_ucis == obs_ucis, "Missing legal roots in observations"
    
    # 2. Permutation Invariance
    res_orig = evaluate_t3a1(branches)
    res_rev = evaluate_t3a1(branches[::-1])
    res_sort = evaluate_t3a1(sorted(branches, key=lambda b: b.root_uci))
    
    assert res_orig == res_rev == res_sort, "Permutation invariance violated"
    
    assert res_orig["classification"] == "INCONCLUSIVE"
    assert res_orig["failure_reason"] == "INSUFFICIENT_OBSERVED_PV_LENGTH"
    assert "e4c5" in res_orig["short_roots"]
    
    # 5. Restore Exact S1 Artifact Inputs
    signature = SemanticSignatureV1.create_canonical()
    fix_digest = hashlib.sha256(json.dumps(fixture, sort_keys=True).encode("utf-8")).hexdigest()
    
    manifest = SuiteManifest(
        suite_id="t3a1-branch-association",
        kind=SuiteKind.MECHANISM_STRESS,
        fixtures={fen.replace(" ", "_"): fix_digest}
    )
    
    spec = ExperimentSpec(
        semantic_signature_version=signature.version,
        semantic_signature_digest=signature.signature_hash(),
        suite_identity=manifest.suite_id,
        suite_digest=manifest.suite_digest(),
        fixture_identity=fen.replace(" ", "_"),
        fixture_digest=fix_digest,
        sufficient_position=SufficientPosition(
            board_arrangement_fen=fen.split()[0],
            side_to_move="w",
            castling_rights="-",
            en_passant_square=None,
            halfmove_clock=0,
            fullmove_number=1,
            history_available=False,
            variant="standard"
        ),
        candidate_policy={},
        producer_identity="Stockfish 18",
        instrument_config={"Threads": 1, "Hash": 16},
        budget_config={"type": "nodes", "value": 100000},
        line_source="pv",
        hypothesis_identifier="T3a-1-Branch-Association"
    )
    
    # 6. Expand deterministic result payload
    res_orig["exact_producer"] = "Stockfish 18"
    res_orig["exact_options"] = {"Threads": 1, "Hash": 16}
    res_orig["exact_budget"] = {"nodes": 100000}
    
    res = ExperimentResult.create(spec_digest=spec.spec_digest(), data=res_orig)
    
    with open("tests/fixtures/t3a1_result.json", "w") as f:
        json.dump(res.model_dump(mode="json"), f, indent=2)

def test_aggregation_irreversibility_lemma():
    # Synthetic test to mechanically preserve the aggregation irreversibility lemma
    # 4 roots with regrets [10, 10, 0, 0]
    regrets = [10, 10, 0, 0]
    
    # Assignment A: X = [1, 1, 0, 0]
    xa = [1, 1, 0, 0]
    agg_a = sum(xa)
    
    r_1_a = [r for r, x in zip(regrets, xa) if x == 1]
    r_0_a = [r for r, x in zip(regrets, xa) if x == 0]
    D_a = statistics.median(r_1_a) - statistics.median(r_0_a)
    M_a = min(r_1_a) - max(r_0_a)
    
    # Assignment B: X = [0, 1, 1, 0]
    xb = [0, 1, 1, 0]
    agg_b = sum(xb)
    
    r_1_b = [r for r, x in zip(regrets, xb) if x == 1]
    r_0_b = [r for r, x in zip(regrets, xb) if x == 0]
    D_b = statistics.median(r_1_b) - statistics.median(r_0_b)
    M_b = min(r_1_b) - max(r_0_b)
    
    assert agg_a == agg_b == 2
    assert D_a == 10.0
    assert M_a == 10
    
    assert D_b == 0.0
    assert M_b == -10
    
    assert D_a != D_b
    assert M_a != M_b
