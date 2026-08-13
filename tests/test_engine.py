import pytest
import chess
import chess.engine
from chessheat.engine import EngineAdapter, analyze
from chessheat.models import AnalysisRecord

class FakeEngineAdapter(EngineAdapter):
    def __init__(self, forced_score_cp=None, forced_score_mate=None):
        self.forced_score_cp = forced_score_cp
        self.forced_score_mate = forced_score_mate

    def get_name(self) -> str:
        return "FakeEngine 1.0"

    def get_options(self) -> dict:
        return {"Threads": 1, "Hash": 16}

    def analyze_position(self, board: chess.Board, budget_type: str, budget_value: int) -> dict:
        # Evaluate randomly or use forced values
        # Since we just want to test pipeline, return a stable mock score.
        if self.forced_score_mate is not None:
            score = chess.engine.Mate(self.forced_score_mate)
        else:
            cp = self.forced_score_cp if self.forced_score_cp is not None else 15
            score = chess.engine.Cp(cp)

        pov_score = chess.engine.PovScore(score, board.turn)

        return {
            "score": pov_score,
            "pv": ["e2e4"] if board.legal_moves else []
        }

    def close(self):
        pass


def test_invalid_fen():
    adapter = FakeEngineAdapter()
    with pytest.raises(ValueError):
        analyze("invalid fen", adapter, "nodes", 100)

def test_starting_position_legal_moves():
    adapter = FakeEngineAdapter()
    record = analyze(chess.STARTING_FEN, adapter, "nodes", 100)

    assert record.root_side == "white"
    assert len(record.move_observations) == 20
    assert record.search_budget_type == "nodes"
    assert record.search_budget_value == 100

def test_score_perspective():
    # Board where black is to move
    fen = "rnbqkbnr/pppppppp/8/8/4P3/8/PPPP1PPP/RNBQKBNR b KQkq - 0 1"

    # If the board evaluation is +50 cp for black, it should be -50 cp for white?
    # Actually pov score in FakeEngine is relative to board.turn.
    # Let's say FakeEngine always evaluates board.turn as +50.
    # So Black is +50.
    # The root perspective is Black.
    # Therefore the baseline score should be +50 cp for black.

    adapter = FakeEngineAdapter(forced_score_cp=50)
    record = analyze(fen, adapter, "nodes", 100)

    assert record.root_side == "black"
    assert record.baseline_observation.perspective == "black"
    assert record.baseline_observation.value == 50
    assert record.baseline_observation.type == "cp"

    # Now look at a move observation (after black plays, it's white's turn)
    # The resulting board has board.turn == chess.WHITE
    # FakeEngine will evaluate it as +50 cp for White.
    # But since root_perspective is Black, it should be converted to -50 cp for Black.

    obs = record.move_observations[0]
    assert obs.score.perspective == "black"
    assert obs.score.value == -50
    assert obs.score.type == "cp"

def test_mate_score():
    adapter = FakeEngineAdapter(forced_score_mate=2)
    record = analyze(chess.STARTING_FEN, adapter, "nodes", 100)
    assert record.baseline_observation.type == "mate"
    assert record.baseline_observation.value == 2

def test_special_moves():
    # Set up a position with castling, en passant, and promotion available.
    # White to move.
    fen = "r3k2r/p1ppqpb1/bn2pnp1/3PN3/1p2P3/2N2Q1p/PPPBBPPP/R3K2R w KQkq - 0 1"

    adapter = FakeEngineAdapter()
    record = analyze(fen, adapter, "nodes", 100)

    castling_moves = [m for m in record.move_observations if m.is_castling]
    assert len(castling_moves) > 0
    assert any(m.uci == "e1g1" for m in castling_moves)
    assert any(m.uci == "e1c1" for m in castling_moves)

    # En passant setup
    fen_ep = "rnbqkbnr/pppp1ppp/8/3Pp3/8/8/PPP1PPPP/RNBQKBNR w KQkq e6 0 1"
    record_ep = analyze(fen_ep, adapter, "nodes", 100)
    ep_moves = [m for m in record_ep.move_observations if m.is_en_passant]
    assert len(ep_moves) == 1
    assert ep_moves[0].uci == "d5e6"
    assert ep_moves[0].captured_square == "e5"

    # Promotion setup
    fen_prom = "8/P7/8/8/8/8/8/4K2k w - - 0 1"
    record_prom = analyze(fen_prom, adapter, "nodes", 100)
    prom_moves = [m for m in record_prom.move_observations if m.promotion]
    assert len(prom_moves) == 4
    assert any(m.promotion == "Q" for m in prom_moves)
