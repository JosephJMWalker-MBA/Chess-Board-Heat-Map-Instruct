import pytest
from chessheat.models import MoveObservation, Score, SquareEffectRole, AnalysisRecord
from chessheat.attribution import calculate_regret, extract_direct_effects, compare_scores, aggregate_square_attributions

def test_compare_scores():
    # white perspective
    s1 = Score(type="cp", value=100, perspective="white")
    s2 = Score(type="cp", value=50, perspective="white")
    assert compare_scores(s1, s2) == 1

    # mate vs cp
    s3 = Score(type="mate", value=2, perspective="white") # mate in 2 for white
    assert compare_scores(s3, s1) == 1

    s4 = Score(type="mate", value=-2, perspective="white") # mate in 2 against white
    assert compare_scores(s1, s4) == 1

    # mate vs mate
    s5 = Score(type="mate", value=1, perspective="white")
    assert compare_scores(s5, s3) == 1 # mate in 1 is better than mate in 2

def test_calculate_regret():
    best = Score(type="cp", value=50, perspective="white")
    move = Score(type="cp", value=10, perspective="white")

    r = calculate_regret(best, move)
    assert r.type == "cp"
    assert r.value == 40

    # mixed
    best_m = Score(type="mate", value=3, perspective="white")
    r2 = calculate_regret(best_m, move)
    assert r2.type == "mixed"
    assert r2.value is None

def test_extract_direct_effects():
    # normal move
    obs_normal = MoveObservation(
        uci="e2e4", san="e4", origin_square="e2", destination_square="e4",
        is_capture=False, is_castling=False, is_en_passant=False, resulting_fen="",
        score=Score(type="cp", value=0, perspective="white")
    )
    eff = extract_direct_effects(obs_normal)
    assert SquareEffectRole.ORIGIN in eff["e2"]
    assert SquareEffectRole.DESTINATION in eff["e4"]

    # capture
    obs_cap = MoveObservation(
        uci="f3e5", san="Nxe5", origin_square="f3", destination_square="e5",
        is_capture=True, captured_square="e5", is_castling=False, is_en_passant=False, resulting_fen="",
        score=Score(type="cp", value=0, perspective="white")
    )
    eff2 = extract_direct_effects(obs_cap)
    assert SquareEffectRole.ORIGIN in eff2["f3"]
    assert SquareEffectRole.DESTINATION in eff2["e5"]
    assert SquareEffectRole.CAPTURE in eff2["e5"]

    # castling
    obs_castle = MoveObservation(
        uci="e1g1", san="O-O", origin_square="e1", destination_square="g1",
        is_capture=False, is_castling=True, is_en_passant=False, resulting_fen="",
        score=Score(type="cp", value=0, perspective="white")
    )
    eff3 = extract_direct_effects(obs_castle)
    assert SquareEffectRole.KING_ORIGIN in eff3["e1"]
    assert SquareEffectRole.KING_DESTINATION in eff3["g1"]
    assert SquareEffectRole.ROOK_ORIGIN in eff3["h1"]
    assert SquareEffectRole.ROOK_DESTINATION in eff3["f1"]

    # en passant
    obs_ep = MoveObservation(
        uci="d5e6", san="dxe6", origin_square="d5", destination_square="e6",
        is_capture=True, captured_square="e5", is_castling=False, is_en_passant=True, resulting_fen="",
        score=Score(type="cp", value=0, perspective="white")
    )
    eff4 = extract_direct_effects(obs_ep)
    assert SquareEffectRole.ORIGIN in eff4["d5"]
    assert SquareEffectRole.DESTINATION in eff4["e6"]
    assert SquareEffectRole.EN_PASSANT_CAPTURE in eff4["e5"]

def test_aggregate_square_attributions():
    best = MoveObservation(
        uci="e2e4", san="e4", origin_square="e2", destination_square="e4",
        is_capture=False, is_castling=False, is_en_passant=False, resulting_fen="",
        score=Score(type="cp", value=100, perspective="white"),
        promotion=None
    )
    worst = MoveObservation(
        uci="a2a3", san="a3", origin_square="a2", destination_square="a3",
        is_capture=False, is_castling=False, is_en_passant=False, resulting_fen="",
        score=Score(type="cp", value=-50, perspective="white"),
        promotion=None
    )

    # Add a promotion move
    promo = MoveObservation(
        uci="h7h8q", san="h8=Q", origin_square="h7", destination_square="h8",
        is_capture=False, is_castling=False, is_en_passant=False, resulting_fen="",
        score=Score(type="cp", value=200, perspective="white"),
        promotion="q"
    )

    record = AnalysisRecord(
        fen="start",
        root_side="white",
        comparison_perspective="white",
        engine_name="test",
        search_budget_type="nodes",
        search_budget_value=1,
        baseline_observation=Score(type="cp", value=0, perspective="white"),
        move_observations=[best, worst, promo]
    )

    attrs = aggregate_square_attributions(record)

    e4 = attrs["e4"]
    assert e4.as_destination == 1
    assert e4.best_move == "e2e4"
    assert e4.implicated_moves[0].uci == "e2e4"
    assert e4.implicated_moves[0].roles == [SquareEffectRole.DESTINATION]

    h8 = attrs["h8"]
    assert h8.implicated_moves[0].uci == "h7h8q"
    assert h8.implicated_moves[0].promotion == "q"

    e2 = attrs["e2"]
    assert e2.implicated_moves[0].roles == [SquareEffectRole.ORIGIN]
    assert e4.best_outcome_cp == 100
    assert e4.min_cp_regret == 100

    a3 = attrs["a3"]
    assert a3.worst_move == "a2a3"
    assert a3.worst_outcome_cp == -50
    assert a3.min_cp_regret == 250 # 200 - (-50)
