import pytest
import chess
from unittest.mock import MagicMock, patch
from chessheat.engine import Score
from chessheat.validation.harness import ValidationHarness

def test_best_cp_root_has_regret_zero():
    h = ValidationHarness()
    scores = {
        "e4": Score(type="cp", value=50, perspective="white"),
        "d4": Score(type="cp", value=30, perspective="white"),
        "Nf3": Score(type="cp", value=45, perspective="white")
    }
    regrets = h.calculate_consequence(scores)
    assert regrets["e4"].value == 0
    assert regrets["d4"].value == 20
    assert regrets["Nf3"].value == 5

def test_no_cp_regret_is_negative():
    h = ValidationHarness()
    scores = {
        "e4": Score(type="cp", value=-10, perspective="white"),
        "d4": Score(type="cp", value=-50, perspective="white")
    }
    regrets = h.calculate_consequence(scores)
    assert regrets["e4"].value == 0
    assert regrets["d4"].value == 40
    assert all(r.value >= 0 for r in regrets.values() if r.type == 'cp')

def test_mixed_cp_mate_groups():
    h = ValidationHarness()
    scores = {
        "e4": Score(type="cp", value=100, perspective="white"),
        "Qxf7#": Score(type="mate", value=1, perspective="white"),
        "d4": Score(type="cp", value=50, perspective="white")
    }
    regrets = h.calculate_consequence(scores)
    assert regrets["e4"].value == 0
    assert regrets["d4"].value == 50
    assert regrets["Qxf7#"].type == "mate"
    assert regrets["Qxf7#"].value == 1

def test_all_mate_partition():
    h = ValidationHarness()
    scores = {
        "Qxf7#": Score(type="mate", value=1, perspective="white"),
        "Qh5#": Score(type="mate", value=2, perspective="white")
    }
    regrets = h.calculate_consequence(scores)
    assert regrets["Qxf7#"].type == "mate"
    assert regrets["Qh5#"].type == "mate"

def test_one_root_position():
    h = ValidationHarness()
    scores = {
        "Kxg2": Score(type="cp", value=-300, perspective="white")
    }
    regrets = h.calculate_consequence(scores)
    assert regrets["Kxg2"].value == 0

def test_lifecycle_cleanup_on_exception():
    class FakeEngine:
        def __init__(self):
            self.quit_called = False
            
        def configure(self, opts):
            pass
            
        def quit(self):
            self.quit_called = True
            
        def analyse(self, board, limit):
            raise RuntimeError("Engine crashed mid-analysis!")

    h = ValidationHarness("fake_path")
    fake = FakeEngine()
    
    with patch("chess.engine.SimpleEngine.popen_uci", return_value=fake):
        try:
            with h:
                h.evaluate_move(chess.Board(), list(chess.Board().legal_moves)[0])
        except RuntimeError as e:
            assert str(e) == "Engine crashed mid-analysis!"
            
        assert fake.quit_called == True

def test_evidence_completeness_contract():
    h = ValidationHarness("fake_path")
    
    # We will mock evaluate_move to return a dummy CP score
    with patch.object(h, "evaluate_move", return_value=Score(type="cp", value=10, perspective="white")):
        res = h.process_position("rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1", "dummy_e", "dummy_f")
        
        # Verify the structure satisfies the completeness contract
        assert "fen" in res
        assert "predecessor" in res
        assert "successor" in res
        assert "partitions" in res
        
        # Exactly 4 partitions
        assert list(res["partitions"].keys()) == ["11", "10", "01", "00"]
        
        # Complete memberships (20 legal moves from start position)
        total_moves = sum(len(p["moves"]) for p in res["partitions"].values())
        assert total_moves == 20
        
        # Valid CP regret distributions
        assert "raw_scores" in res
        assert "regrets" in res
        assert len(res["regrets"]) == 20
        for r in res["regrets"].values():
            assert r["value"] >= 0
            
        # Extract per-partition cp count and mate count
        for p in res["partitions"].values():
            assert "cp_count" in p
            assert "mate_count" in p
            assert "median_cp_regret" in p
