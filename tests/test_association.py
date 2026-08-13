import pytest
from chessheat.models import AnalysisRecord, MoveObservation, Score, EventBundle
from chessheat.geometry import GeometryDelta, AttackRelationship, PieceRef
from chessheat.association import aggregate_bundle_leverage, _compute_distribution

def test_compute_distribution():
    dist = _compute_distribution([("e2e4", 10), ("d2d4", 20), ("g1f3", 30)])
    assert dist.min_val == 10
    assert dist.max_val == 30
    assert dist.mean_val == 20
    assert dist.best_move == "e2e4"
    assert dist.worst_move == "g1f3"
    assert dist.median_val == 20

    dist_empty = _compute_distribution([])
    assert dist_empty.min_val is None
    assert dist_empty.max_val is None
    assert dist_empty.mean_val is None

def test_bundle_leverage():
    # Setup moves
    obs1 = MoveObservation(
        uci="e2e4", san="e4", origin_square="e2", destination_square="e4",
        is_capture=False, resulting_fen="f1",
        score=Score(type="cp", value=100, perspective="white"),
        regret=Score(type="cp", value=0, perspective="white"),
    )
    obs2 = MoveObservation(
        uci="d2d4", san="d4", origin_square="d2", destination_square="d4",
        is_capture=False, resulting_fen="f2",
        score=Score(type="cp", value=80, perspective="white"),
        regret=Score(type="cp", value=20, perspective="white")
    )
    obs3 = MoveObservation(
        uci="g1f3", san="Nf3", origin_square="g1", destination_square="f3",
        is_capture=False, resulting_fen="f3",
        score=Score(type="cp", value=50, perspective="white"),
        regret=Score(type="cp", value=50, perspective="white"),
    )

    record = AnalysisRecord(
        fen="fake", root_side="white", comparison_perspective="white",
        engine_name="fake", search_budget_type="depth", search_budget_value=1,
        baseline_observation=Score(type="cp", value=0, perspective="white"),
        move_observations=[obs1, obs2, obs3]
    )

    # Delta for e2e4 and d2d4 has event A (they share it)
    d1 = GeometryDelta(appeared_attacks=[], disappeared_attacks=[], appeared_defenses=[], disappeared_defenses=[], appeared_rays=[], disappeared_rays=[], mobility_gained=[], mobility_lost=[])
    d1.appeared_attacks.append(AttackRelationship(
        attacker=PieceRef(symbol="P", square="e4"), target_square="d5", target_piece=None
    ))
    # Add a second event to d1 only
    d1.appeared_attacks.append(AttackRelationship(
        attacker=PieceRef(symbol="P", square="e4"), target_square="f5", target_piece=None
    ))

    d2 = GeometryDelta(appeared_attacks=[], disappeared_attacks=[], appeared_defenses=[], disappeared_defenses=[], appeared_rays=[], disappeared_rays=[], mobility_gained=[], mobility_lost=[])
    d2.appeared_attacks.append(AttackRelationship(
        attacker=PieceRef(symbol="P", square="e4"), target_square="d5", target_piece=None
    ))

    d3 = GeometryDelta(appeared_attacks=[], disappeared_attacks=[], appeared_defenses=[], disappeared_defenses=[], appeared_rays=[], disappeared_rays=[], mobility_gained=[], mobility_lost=[])

    deltas = {
        "e2e4": d1,
        "d2d4": d2,
        "g1f3": d3
    }

    bundles = aggregate_bundle_leverage(record, deltas)

    # e4->d5 is shared by e2e4 and d2d4.
    # e4->f5 is only e2e4.
    # So they should form TWO separate bundles because their producing move sets differ!
    assert len(bundles) == 2

    # Find the bundle for e4->d5
    b_shared = next(b for b in bundles if "d2d4" in b.producing_moves)
    assert b_shared.producing_moves == ["d2d4", "e2e4"]
    assert b_shared.non_producing_moves == ["g1f3"]
    assert len(b_shared.constituent_events) == 1
    assert not b_shared.is_perfectly_confounded

    assert b_shared.regret_with_bundle.min_val == 0
    assert b_shared.regret_with_bundle.max_val == 20
    assert b_shared.regret_without_bundle.mean_val == 50

    # Find the bundle for e4->f5
    b_solo = next(b for b in bundles if b.producing_moves == ["e2e4"])
    assert b_solo.producing_moves == ["e2e4"]
    assert len(b_solo.constituent_events) == 1
    assert not b_solo.is_perfectly_confounded

    assert "e4" in b_shared.implicated_squares
    assert "d5" in b_shared.implicated_squares
