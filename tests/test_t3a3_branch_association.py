import json
import chess
import hashlib
from chessheat.models import AnalysisRecord, MoveObservation, Score, SpatialEvent
from chessheat.consequence import compute_regrets
from chessheat.branch import extract_branches

def evaluate_t3a3(branches):
    event_sq = "c4"
    event_role = "capture"
    
    classification = "UNCLASSIFIED"
    failure_reason = None
    
    short_roots = {}
    all_regrets = {}
    
    # Pass A: Pre-check all horizons to ensure observational completeness and typed-consequence validity
    is_evaluable_set_incomplete = False
    for b in branches:
        if b.regret.type != "cp":
            classification = "INCONCLUSIVE"
            failure_reason = "MIXED_MATE_CP"
            break
            
        all_regrets[b.root_uci] = {"type": b.regret.type, "value": b.regret.value}
        
        has_ply_2 = False
        for ev in b.future_evidence:
            if ev.ply == 2:
                has_ply_2 = True
                break
                
        if not has_ply_2:
            short_roots[b.root_uci] = len(b.future_moves)
            classification = "INCONCLUSIVE"
            failure_reason = "INSUFFICIENT_OBSERVED_PV_LENGTH"
            is_evaluable_set_incomplete = True

    root_event_membership = {}
    partition_1 = []
    partition_0 = []
    d = None
    m = None
    ax = None
    
    if not is_evaluable_set_incomplete and classification != "INCONCLUSIVE":
        # Pass B: assign X_i for every root
        for b in branches:
            x = 0
            for ev in b.future_evidence:
                if ev.ply == 2:
                    if ev.square == event_sq and ev.role == event_role:
                        x = 1
            root_event_membership[b.root_uci] = x
            if x == 1:
                partition_1.append(b)
            else:
                partition_0.append(b)
        
        ax = sum(root_event_membership.values())
        
        if len(partition_1) < 2 or len(partition_0) < 2:
            classification = "INCONCLUSIVE"
            failure_reason = "INSUFFICIENT_PARTITION_CARDINALITY"
        else:
            # Compute statistics
            r_1 = sorted([b.regret.value for b in partition_1])
            r_0 = sorted([b.regret.value for b in partition_0])
            
            def median(l):
                n = len(l)
                if n % 2 == 1:
                    return l[n // 2]
                else:
                    return (l[n // 2 - 1] + l[n // 2]) / 2.0
                    
            median_1 = median(r_1)
            median_0 = median(r_0)
            d = median_1 - median_0
            m = min(r_1) - max(r_0)
            
            if d > 0 and m > 0:
                classification = "SUPPORTED"
            elif d > 0 and m <= 0:
                classification = "WEAK_SUPPORT"
            else:
                classification = "FALSIFIED"
            
    return {
        "classification": classification,
        "failure_reason": failure_reason,
        "D": d,
        "M": m,
        "A_x": ax,
        "horizon_plies": [2],
        "short_roots": short_roots,
        "typed_root_regrets": all_regrets,
        "root_event_membership": root_event_membership,
        "legal_root_ucis": sorted([b.root_uci for b in branches]),
        "unevaluable_roots": sorted(list(short_roots.keys())),
        "evaluable_event_present_roots": sorted([b.root_uci for b in partition_1]),
        "evaluable_event_absent_roots": sorted([b.root_uci for b in partition_0]),
        "is_evaluable_set_incomplete": is_evaluable_set_incomplete
    }

def test_t3a3_branch_conditioned_association():
    fixture_path = "tests/fixtures/t3a3_fixture.json"
    
    # Preserve observation invariant
    with open(fixture_path, "rb") as f:
        raw_fixture_bytes = f.read()
    raw_fixture_digest = hashlib.sha256(raw_fixture_bytes).hexdigest()
    
    with open(fixture_path, "r") as f:
        fixture = json.load(f)
        
    fen = fixture["fen"]
    
    # 1. Exact producer gate
    assert fen == "4k3/8/1n6/8/2B5/8/8/4K3 w - - 0 1"
    assert fixture["engine_name"] == "Stockfish 18", "Engine identity must be exactly Stockfish 18"
    assert fixture["engine_options"] == {"Threads": 1, "Hash": 16}
    assert fixture["search_budget_type"] == "nodes"
    assert fixture["search_budget_value"] == 100000
    assert fixture["candidate_policy"] == {}
    assert fixture["comparison_perspective"] == "white"

    move_observations = [MoveObservation(**obs) for obs in fixture["move_observations"]]
    scores_dict = {obs.uci: obs.score for obs in move_observations}
    
    # Compute typed regret exactly once from the complete root universe
    regrets_dict = compute_regrets(scores_dict)
    
    for obs in move_observations:
        if obs.uci in regrets_dict:
            obs.regret = regrets_dict[obs.uci]

    # 2. Reconstruct AnalysisRecord with exact observed metadata
    record = AnalysisRecord(
        fen=fen,
        root_side="white",
        comparison_perspective=fixture["comparison_perspective"],
        engine_name=fixture["engine_name"],
        engine_options=fixture["engine_options"],
        search_budget_type=fixture["search_budget_type"],
        search_budget_value=fixture["search_budget_value"],
        candidate_policy=fixture["candidate_policy"],
        baseline_observation=Score(**fixture["baseline_observation"]),
        move_observations=move_observations
    )

    universe = extract_branches(record)
    branches = universe.branches
    
    board = chess.Board(fen)
    legal_ucis = {m.uci() for m in board.legal_moves}
    obs_ucis = {b.root_uci for b in branches}
    
    # Mechanical provenance gates before statistics
    assert legal_ucis == obs_ucis, "Missing legal roots in observations"
    assert len(obs_ucis) == 16, "Legal root count must be exactly 16"

    # Mechanical permutation invariance
    res_orig = evaluate_t3a3(branches)
    res_rev = evaluate_t3a3(branches[::-1])
    res_sort = evaluate_t3a3(sorted(branches, key=lambda b: b.root_uci))
    
    assert res_orig == res_rev == res_sort, "Permutation invariance violated"
    
    res = res_orig
    
    from chessheat.semantics import SemanticSignatureV1
    canonical_sig = SemanticSignatureV1.create_canonical()
    s0_digest = canonical_sig.signature_hash()
    
    # 4. Construct an actual SuiteManifest
    from chessheat.experiment import SuiteManifest, SuiteKind
    suite = SuiteManifest(
        suite_id="t3a3_suite",
        kind=SuiteKind.MECHANISM_STRESS,
        fixtures={
            "t3a3_independent_replication": raw_fixture_digest
        }
    )
    
    # 5. Construct the exact SufficientPosition
    from chessheat.semantics import SufficientPosition
    sp = SufficientPosition(
        board_arrangement_fen="4k3/8/1n6/8/2B5/8/8/4K3",
        side_to_move="w",
        castling_rights="-",
        en_passant_square=None,
        halfmove_clock=0,
        fullmove_number=1,
        history_available=False,
        history_identity=None,
        variant="standard"
    )
    
    # 6. Construct a real ExperimentSpec (Version 2)
    from chessheat.experiment import ExperimentSpec
    from pydantic import ValidationError
    
    # Assert missing perspective fails
    try:
        ExperimentSpec(
            semantic_signature_version=canonical_sig.version,
            semantic_signature_digest=s0_digest,
            suite_identity="t3a3_suite",
            suite_digest=suite.suite_digest(),
            fixture_identity="t3a3_independent_replication",
            fixture_digest=raw_fixture_digest,
            sufficient_position=sp,
            candidate_policy={},
            producer_identity=fixture["engine_name"],
            instrument_config=fixture["engine_options"],
            budget_config={"type": fixture["search_budget_type"], "value": fixture["search_budget_value"]},
            line_source="pv",
            hypothesis_identifier="T3a-3",
            spec_version=2
        )
        assert False, "Should have failed v2 perspective validation"
    except ValidationError:
        pass
        
    spec = ExperimentSpec(
        semantic_signature_version=canonical_sig.version,
        semantic_signature_digest=s0_digest,
        suite_identity="t3a3_suite",
        suite_digest=suite.suite_digest(),
        fixture_identity="t3a3_independent_replication",
        fixture_digest=raw_fixture_digest,
        sufficient_position=sp,
        candidate_policy={},
        producer_identity=fixture["engine_name"],
        instrument_config=fixture["engine_options"],
        budget_config={"type": fixture["search_budget_type"], "value": fixture["search_budget_value"]},
        line_source="pv",
        hypothesis_identifier="T3a-3",
        spec_version=2,
        comparison_perspective="white"
    )
    
    # 7. Preserve fully typed scores and regrets (including perspective)
    fully_typed_scores = {k: {"type": v.type, "value": v.value, "perspective": v.perspective} for k,v in scores_dict.items()}
    fully_typed_regrets = {k: {"type": v.type, "value": v.value, "perspective": v.perspective} for k,v in regrets_dict.items()}

    # 8. Create a real immutable ExperimentResult
    payload = {
        "classification": res["classification"],
        "failure_reason": res["failure_reason"],
        "preregistration_commit": "fff7954531407e95ae9ed89a59a8e753b82aebc0",
        "fen": fen,
        "event": {"square": "c4", "role": "capture", "ply": 2},
        "expected_direction": "BAD / HIGHER_REGRET",
        "legal_root_count": 16,
        "evaluable_event_present_roots": res["evaluable_event_present_roots"],
        "evaluable_event_absent_roots": res["evaluable_event_absent_roots"],
        "unevaluable_roots": res["unevaluable_roots"],
        "root_event_membership": res["root_event_membership"],
        "legal_root_ucis": res["legal_root_ucis"],
        "typed_scores": fully_typed_scores,
        "typed_regrets": fully_typed_regrets,
        "D": res["D"],
        "M": res["M"],
        "A_x": res["A_x"],
        "fixture_digest": raw_fixture_digest,
        "semantic_signature_digest": s0_digest,
        "suite_identity": "t3a3_suite",
        "suite_digest": suite.suite_digest(),
        "spec_digest": spec.spec_digest(),
        "spec_version": 2,
        "comparison_perspective": "white",
        "exact_producer": fixture["engine_name"],
        "exact_options": fixture["engine_options"],
        "exact_budget": {"type": fixture["search_budget_type"], "value": fixture["search_budget_value"]}
    }
    
    from chessheat.experiment import ExperimentResult
    result_obj = ExperimentResult.create(spec_digest=spec.spec_digest(), data=payload)
    
    with open("tests/fixtures/t3a3_result.json", "w") as f:
        json.dump(result_obj.model_dump(mode="json"), f, indent=2)
        
    # 9. Mechanical reload/integrity test
    with open("tests/fixtures/t3a3_result.json", "r") as f:
        serialized_data = json.load(f)
        
    loaded_result = ExperimentResult(**serialized_data)
    assert loaded_result.spec_digest == spec.spec_digest()
    
    # 10. Preserve the observation
    with open(fixture_path, "rb") as f:
        final_fixture_bytes = f.read()
    final_fixture_digest = hashlib.sha256(final_fixture_bytes).hexdigest()
    assert raw_fixture_digest == final_fixture_digest, "Fixture was illegally modified"
    
    print(f"Classification: {loaded_result.data['classification']}")
    print(f"Failure Reason: {loaded_result.data['failure_reason']}")
    print(f"|X=1|: {len(loaded_result.data['evaluable_event_present_roots'])}")
    print(f"|X=0|: {len(loaded_result.data['evaluable_event_absent_roots'])}")
    print(f"Event-present roots: {loaded_result.data['evaluable_event_present_roots']}")
    print(f"Event-absent roots: {loaded_result.data['evaluable_event_absent_roots']}")
    print(f"D: {loaded_result.data['D']}")
    print(f"M: {loaded_result.data['M']}")
    print(f"A(x): {loaded_result.data['A_x']}")
    print(f"Artifact Digest: {loaded_result.artifact_digest}")
    print(f"Spec Digest: {spec.spec_digest()}")
    print(f"S0 Digest: {s0_digest}")
    print(f"Raw Fixture SHA unchanged: {raw_fixture_digest == final_fixture_digest}")
