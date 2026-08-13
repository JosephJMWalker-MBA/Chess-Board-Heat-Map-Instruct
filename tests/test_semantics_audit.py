import pytest
from chessheat.models import MoveObservation, Score, SquareEffectRole, AnalysisRecord
from chessheat.attribution import aggregate_square_attributions

def test_singleton_destination_regret_preserved():
    # Simulate a scenario where d4 is a singleton destination (e.g. only d2d4 played there)
    # and e4 is another move. The best move is e2e4 with +38. d2d4 has +34.

    e4_move = MoveObservation(
        uci="e2e4", san="e4", origin_square="e2", destination_square="e4",
        is_capture=False, is_castling=False, is_en_passant=False, resulting_fen="",
        score=Score(type="cp", value=38, perspective="white")
    )

    d4_move = MoveObservation(
        uci="d2d4", san="d4", origin_square="d2", destination_square="d4",
        is_capture=False, is_castling=False, is_en_passant=False, resulting_fen="",
        score=Score(type="cp", value=34, perspective="white")
    )

    record = AnalysisRecord(
        fen="start",
        root_side="white",
        engine_name="test",
        search_budget_type="nodes",
        search_budget_value=1,
        baseline_observation=Score(type="cp", value=47, perspective="white"),
        move_observations=[e4_move, d4_move]
    )

    attrs = aggregate_square_attributions(record)

    # 1. "a singleton destination square preserves the move's global regret rather than becoming zero"
    assert attrs["d4"].min_cp_regret == 4

    # 2. "the same move has identical regret when referenced from its origin and destination squares"
    # For d2d4: origin is d2, dest is d4. Both should have regret 4 for this move.
    d2_move_ref = next(m for m in attrs["d2"].implicated_moves if m.uci == "d2d4")
    d4_move_ref = next(m for m in attrs["d4"].implicated_moves if m.uci == "d2d4")

    assert d2_move_ref.regret.value == 4
    assert d4_move_ref.regret.value == 4
    assert d2_move_ref.regret == d4_move_ref.regret

def test_black_perspective_regret():
    # 3. "root-side perspective remains correct for Black as well as White."
    # If it is Black's turn, the scores are from Black's perspective.
    # So a score of +100 means Black is winning by a pawn. A score of +50 means Black is winning by half a pawn.
    # The best move is +100.

    best_move = MoveObservation(
        uci="e7e5", san="e5", origin_square="e7", destination_square="e5",
        is_capture=False, is_castling=False, is_en_passant=False, resulting_fen="",
        score=Score(type="cp", value=100, perspective="black")
    )

    other_move = MoveObservation(
        uci="d7d5", san="d5", origin_square="d7", destination_square="d5",
        is_capture=False, is_castling=False, is_en_passant=False, resulting_fen="",
        score=Score(type="cp", value=50, perspective="black")
    )

    record = AnalysisRecord(
        fen="start",
        root_side="black",
        engine_name="test",
        search_budget_type="nodes",
        search_budget_value=1,
        baseline_observation=Score(type="cp", value=80, perspective="black"),
        move_observations=[best_move, other_move]
    )

    attrs = aggregate_square_attributions(record)

    # Best move should have regret 0
    assert attrs["e5"].min_cp_regret == 0

    # Other move should have regret 50 (100 - 50)
    assert attrs["d5"].min_cp_regret == 50
