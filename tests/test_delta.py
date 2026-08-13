import pytest
import chess
from unittest.mock import MagicMock
from chessheat.models import AnalysisRecord, Score, MoveObservation, PairedAnalysisRecord
from chessheat.engine import EngineAdapter, analyze
from chessheat.delta import analyze_transition, compute_square_deltas, filter_moves, calculate_metric

class MockAdapter(EngineAdapter):
    def get_name(self) -> str:
        return "Mock"

    def get_options(self) -> dict:
        return {}

    def analyze_position(self, board: chess.Board, budget_type: str, budget_value: int) -> dict:
        # Just return dummy +10 score for whichever side is to move
        return {
            "score": chess.engine.PovScore(chess.engine.Cp(10), board.turn),
            "pv": []
        }

    def close(self):
        pass

def test_analyze_transition_validates_move():
    adapter = MockAdapter()

    # invalid uci
    with pytest.raises(ValueError, match="Invalid transition move format"):
        analyze_transition(chess.STARTING_FEN, "invalid", adapter, "nodes", 1)

    # illegal move
    with pytest.raises(ValueError, match="Transition move is illegal"):
        analyze_transition(chess.STARTING_FEN, "e2e5", adapter, "nodes", 1)

    # legal transition
    paired = analyze_transition(chess.STARTING_FEN, "e2e4", adapter, "nodes", 1)

    assert paired.source_fen == chess.STARTING_FEN
    assert paired.transition_move == "e2e4"
    assert paired.before_side_to_move == "white"
    assert paired.after_side_to_move == "black"
    assert paired.comparison_perspective == "white"

def test_analyze_transition_perspectives():
    adapter = MockAdapter()
    # Let's test a transition from Black's perspective
    black_fen = "rnbqkbnr/pppppppp/8/8/4P3/8/PPPP1PPP/RNBQKBNR b KQkq e3 0 1"
    paired = analyze_transition(black_fen, "e7e5", adapter, "nodes", 1)

    assert paired.before_side_to_move == "black"
    assert paired.after_side_to_move == "white"
    assert paired.comparison_perspective == "black"

    # Both records should be evaluated from the black perspective
    assert paired.before_record.comparison_perspective == "black"
    assert paired.after_record.comparison_perspective == "black"

def test_compute_square_deltas_states():
    # Setup some mock attributions
    from chessheat.models import SquareAttribution, ImplicatedMove, Score, SquareEffectRole

    m1 = ImplicatedMove(uci="e2e4", roles=[SquareEffectRole.DESTINATION], outcome=Score(type="cp", value=10, perspective="white"), regret=Score(type="cp", value=0, perspective="white"))
    m2 = ImplicatedMove(uci="d2d4", roles=[SquareEffectRole.DESTINATION], outcome=Score(type="cp", value=5, perspective="white"), regret=Score(type="cp", value=5, perspective="white"))

    # e4 was present before and after -> persisted
    before_e4 = SquareAttribution(square="e4", implicated_moves=[m1, m2])
    after_e4 = SquareAttribution(square="e4", implicated_moves=[m1])

    summary_e4 = compute_square_deltas(before_e4, after_e4)
    dest_deltas = summary_e4.roles["destination"]

    assert dest_deltas.metrics["move_count"].state == "persisted"
    assert dest_deltas.metrics["move_count"].before == 2
    assert dest_deltas.metrics["move_count"].after == 1
    assert dest_deltas.metrics["move_count"].delta == -1

    # e5 was present before, disappeared after -> disappeared
    summary_disappeared = compute_square_deltas(before_e4, None)
    assert summary_disappeared.roles["destination"].metrics["move_count"].state == "disappeared"
    assert summary_disappeared.roles["destination"].metrics["move_count"].before == 2
    assert summary_disappeared.roles["destination"].metrics["move_count"].after is None
    assert summary_disappeared.roles["destination"].metrics["move_count"].delta is None

    # e6 was absent before, appeared after -> appeared
    summary_appeared = compute_square_deltas(None, after_e4)
    assert summary_appeared.roles["destination"].metrics["move_count"].state == "appeared"
    assert summary_appeared.roles["destination"].metrics["move_count"].before is None
    assert summary_appeared.roles["destination"].metrics["move_count"].after == 1
    assert summary_appeared.roles["destination"].metrics["move_count"].delta is None

    # a1 was absent before, absent after -> absent_both
    summary_absent = compute_square_deltas(None, None)
    assert summary_absent.roles["destination"].metrics["move_count"].state == "absent_both"
    assert summary_absent.roles["destination"].metrics["move_count"].delta is None
