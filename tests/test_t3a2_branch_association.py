import json
import chess
import hashlib
from chessheat.models import AnalysisRecord, MoveObservation, Score, SpatialEvent
from chessheat.consequence import compute_regrets
from chessheat.branch import extract_branches

def evaluate_t3a2(branches):
    event_sq = "d4"
    event_role = "capture"
    
    partition_1 = []
    partition_0 = []
    
    classification = "UNCLASSIFIED"
    failure_reason = None
    
    short_roots = {}
    all_regrets = {}
    
    # Pre-check all horizons to ensure observational completeness
    is_evaluable_set_incomplete = False
    
    for b in branches:
        if b.regret.type != "cp":
            classification = "INCONCLUSIVE"
            failure_reason = "MIXED_MATE_CP"
            break
            
        all_regrets[b.root_uci] = {"type": b.regret.type, "value": b.regret.value}
        
        # Check if ply 2 is present in future_evidence
        # future_moves excludes ply 1 (root). We just need ply 2 to be there.
        has_ply_2 = False
        for ev in b.future_evidence:
            if ev.ply == 2:
                has_ply_2 = True
                break
                
        if not has_ply_2:
            short_roots[b.root_uci] = len(b.future_moves) # length might be 0
            classification = "INCONCLUSIVE"
            failure_reason = "INSUFFICIENT_OBSERVED_PV_LENGTH"
            is_evaluable_set_incomplete = True
            
        if not is_evaluable_set_incomplete:
            # We only evaluate X_i if all roots pass the completeness gate
            x = 0
            for ev in b.future_evidence:
                if ev.ply == 2:
                    if ev.square == event_sq and ev.role == event_role:
                        x = 1
            if x == 1:
                partition_1.append(b)
            else:
                partition_0.append(b)

    d = None
    m = None
    ax = None
    
    if not is_evaluable_set_incomplete and classification != "INCONCLUSIVE":
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
                
            ax = len(partition_1)
            
    return {
        "classification": classification,
        "failure_reason": failure_reason,
        "D": d,
        "M": m,
        "A_x": ax,
        "horizon_plies": [2],
        "short_roots": short_roots,
        "typed_root_regrets": all_regrets,
        "unevaluable_roots": sorted(list(short_roots.keys())),
        "evaluable_event_present_roots": sorted([b.root_uci for b in partition_1]),
        "evaluable_event_absent_roots": sorted([b.root_uci for b in partition_0]),
        "is_evaluable_set_incomplete": is_evaluable_set_incomplete
    }

def test_t3a2_branch_conditioned_association():
    with open("tests/fixtures/t3a2_fixture.json", "r") as f:
        fixture = json.load(f)
        
    fen = fixture["fen"]
    preregistration_commit = fixture["preregistration_commit"]
    
    # Assert fixture values against preregistration invariants
    assert fen == "4k3/8/1b6/8/3R4/8/8/4K3 w - - 0 1"
    assert fixture["engine_name"].startswith("Stockfish")
    assert "18" in fixture["engine_name"]
    assert fixture["engine_options"] == {"Threads": 1, "Hash": 16}
    assert fixture["search_budget_type"] == "nodes"
    assert fixture["search_budget_value"] == 100000
    assert fixture["candidate_policy"] == {}
    assert fixture["comparison_perspective"] == "white"

    move_observations = [MoveObservation(**obs) for obs in fixture["observations"]]
    scores_dict = {obs.uci: obs.score for obs in move_observations}
    
    # 4. Compute typed regret exactly once from the complete root universe
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
    
    # 3. Mechanical provenance gates before statistics
    assert legal_ucis == obs_ucis, "Missing legal roots in observations"
    assert len(obs_ucis) == 19, "Legal root count must be exactly 19"

    # 10. Mechanical permutation invariance
    res_orig = evaluate_t3a2(branches)
    res_rev = evaluate_t3a2(branches[::-1])
    res_sort = evaluate_t3a2(sorted(branches, key=lambda b: b.root_uci))
    
    assert res_orig == res_rev == res_sort, "Permutation invariance violated"
    
    res = res_orig
    
    # Save the result artifact
    with open("tests/fixtures/t3a2_fixture.json", "rb") as f:
        fixture_bytes = f.read()
    fixture_digest = hashlib.sha256(fixture_bytes).hexdigest()
    
    # Ensure S0 digest exists
    try:
        from test_semantics_audit import current_semantic_digest
        s0_digest = current_semantic_digest()
    except Exception:
        s0_digest = "S0_DIGEST_UNAVAILABLE"
        
    result_payload = {
        "suite_identity": "SuiteManifest(kind=MECHANISM_STRESS)",
        "preregistration_commit": preregistration_commit,
        "classification": res["classification"],
        "failure_reason": res["failure_reason"],
        "fen": fen,
        "event": {"square": "d4", "role": "capture", "ply": 2},
        "expected_direction": "BAD / HIGHER_REGRET",
        "engine_identity": fixture["engine_name"],
        "engine_options": fixture["engine_options"],
        "search_budget": {"type": "nodes", "value": 100000},
        "candidate_policy": {},
        "line_source": "pv",
        "legal_root_count": 19,
        "typed_scores": {k: {"type": v.type, "value": v.value} for k,v in scores_dict.items()},
        "typed_regrets": res["typed_root_regrets"],
        "evaluable_event_present_roots": res["evaluable_event_present_roots"],
        "evaluable_event_absent_roots": res["evaluable_event_absent_roots"],
        "unevaluable_roots": res["unevaluable_roots"],
        "D": res["D"],
        "M": res["M"],
        "aggregate_membership_count": res["A_x"],
        "fixture_digest": fixture_digest,
        "semantic_signature_digest": s0_digest
    }
    
    with open("tests/fixtures/t3a2_result.json", "w") as f:
        json.dump(result_payload, f, indent=2)
        
    # The actual result logic doesn't assert a specific classification in the test itself
    # because the classification is determined by the data. The experiment result is preserved.
    # The test passes if all provenance and constraints held, and it didn't crash.
    print(f"\n[T3a-2 Execution Result]")
    print(f"Classification: {res['classification']}")
    if res['failure_reason']:
        print(f"Failure Reason: {res['failure_reason']}")
    else:
        print(f"|X=1| = {len(res['evaluable_event_present_roots'])}")
        print(f"|X=0| = {len(res['evaluable_event_absent_roots'])}")
        print(f"D = {res['D']}")
        print(f"M = {res['M']}")
        print(f"A(x) = {res['A_x']}")
        
    assert True
