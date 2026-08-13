import pytest
import chess
from unittest.mock import MagicMock, patch
from chessheat.engine import Score
from chessheat.consequence import compute_regrets
from chessheat.validation.harness import ValidationHarness

def test_best_cp_root_has_regret_zero():
    scores = {
        "e4": Score(type="cp", value=50, perspective="white"),
        "d4": Score(type="cp", value=30, perspective="white"),
        "Nf3": Score(type="cp", value=45, perspective="white")
    }
    regrets = compute_regrets(scores)
    assert regrets["e4"].value == 0
    assert regrets["d4"].value == 20
    assert regrets["Nf3"].value == 5

def test_no_cp_regret_is_negative():
    scores = {
        "e4": Score(type="cp", value=-10, perspective="white"),
        "d4": Score(type="cp", value=-50, perspective="white")
    }
    regrets = compute_regrets(scores)
    assert regrets["e4"].value == 0
    assert regrets["d4"].value == 40
    assert all(r.value >= 0 for r in regrets.values() if r.type == 'cp')

def test_mixed_cp_mate_groups():
    scores = {
        "e4": Score(type="cp", value=100, perspective="white"),
        "Qxf7#": Score(type="mate", value=1, perspective="white"),
        "d4": Score(type="cp", value=50, perspective="white")
    }
    regrets = compute_regrets(scores)
    assert regrets["e4"].value == 0
    assert regrets["d4"].value == 50
    assert regrets["Qxf7#"].type == "mate"
    assert regrets["Qxf7#"].value == 1

def test_all_mate_partition():
    scores = {
        "Qxf7#": Score(type="mate", value=1, perspective="white"),
        "Qh5#": Score(type="mate", value=2, perspective="white")
    }
    regrets = compute_regrets(scores)
    assert regrets["Qxf7#"].type == "mate"
    assert regrets["Qh5#"].type == "mate"

def test_one_root_position():
    scores = {
        "Kxg2": Score(type="cp", value=-300, perspective="white")
    }
    regrets = compute_regrets(scores)
    assert regrets["Kxg2"].value == 0

def test_lifecycle_cleanup_on_configure_exception():
    h = ValidationHarness("fake_path")
    
    mock_engine = MagicMock()
    mock_engine.configure.side_effect = Exception("Configuration crashed")
    
    with patch("chess.engine.SimpleEngine.popen_uci", return_value=mock_engine):
        with pytest.raises(Exception, match="Configuration crashed"):
            with h:
                pass
                
    # Ensure quit was called because configure raised an exception
    mock_engine.quit.assert_called_once()

def test_lifecycle_cleanup_on_exception():
    class FakeEngine:
        def __init__(self):
            self.quit_called = False
            self.id = {"name": "Fake Engine"}
            
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
    from chessheat.geometry import PieceRef
    from unittest.mock import patch
    from chessheat.engine import Score
    
    h = ValidationHarness("fake_path")
    
    # We will mock evaluate_move to avoid needing stockfish, but we will run the real preflight
    # Predecessor: e2 pawn can move to e4 (removed because e2 pawn moves to e4)
    e = (PieceRef(square='e2', symbol='P'), 'e4')
    # Successor: e7 pawn can move to e5 (born because after e4 it's black's turn and e5 is empty)
    f = (PieceRef(square='e7', symbol='p'), 'e5')
    
    with patch.object(h, "evaluate_move", return_value=Score(type="cp", value=10, perspective="white")):
        # We pass dummy temporal and bundle evidence to verify they are wired up
        # The prompt says: "For optional evidence families, explicitly distinguish not_applicable from missing_required_evidence"
        # We don't have to define complex mocks here, just passing None to show they can be omitted.
        res = h.process_position(chess.STARTING_FEN, "e4", e, f)
        
        # Verify the structure satisfies the completeness contract
        assert "fen" in res
        assert "played_move" in res
        assert "predecessor" in res
        assert "successor" in res
        assert "legal_root_count" in res
        assert res["legal_root_count"] == 20
        assert "partitions" in res
        
        # Exactly 4 partitions
        assert list(res["partitions"].keys()) == ["11", "10", "01", "00"]
        
        # e4 should be in M11 since it removes e and creates f
        assert "e4" in res["partitions"]["11"]["moves"]
        
        # Complete memberships (20 legal moves from start position)
        total_moves = sum(len(p["moves"]) for p in res["partitions"].values())
        assert total_moves == 20
        
        # Valid CP regret distributions
        assert "raw_scores" in res
        assert "regrets" in res
        assert "temporal_evidence" in res
        assert "bundle_evidence" in res
        assert len(res["regrets"]) == 20
        for r in res["regrets"].values():
            assert r["value"] >= 0
            
        # Extract per-partition cp count and mate count
        for p in res["partitions"].values():
            assert "cp_count" in p
            assert "mate_count" in p
            assert "median_cp_regret" in p

def test_paired_history_evidence():
    # Test compare_transpositions
    h = ValidationHarness("fake_path")
    # Same endpoint, different histories, ending with knight moves to avoid en passant FEN differences
    # History A: 1. e4 e5 2. Nf3 Nc6
    # History B: 1. e4 e5 2. Nc3 Nf6 (wait, endpoints must be the same!)
    # Let's just do:
    # A: 1. Nf3 Nf6 2. Nc3 Nc6
    # B: 1. Nc3 Nc6 2. Nf3 Nf6
    moves_a = ["Nf3", "Nf6", "Nc3", "Nc6"]
    moves_b = ["Nc3", "Nc6", "Nf3", "Nf6"]
    
    res = h.compare_transpositions(chess.STARTING_FEN, moves_a, moves_b)
    
    assert res["history_a"] == moves_a
    assert res["history_b"] == moves_b
    assert res["terminal_fen_equality"] is True
    assert res["geometry_equality"] is True
    assert res["legal_root_equality"] is True
    assert res["temporal_ledger_inequality"] is True

def test_preflight_invalid_fen():
    with pytest.raises(ValueError, match="is not a valid chess state"):
        ValidationHarness.preflight_fixture("invalid_fen", "e4", "dummy_e", "dummy_f")

def test_preflight_invalid_move():
    with pytest.raises(ValueError, match="is not legal in this FEN"):
        # e5 is illegal from starting position
        ValidationHarness.preflight_fixture(chess.STARTING_FEN, "e5", "dummy_e", "dummy_f")

def test_preflight_missing_predecessor():
    from chessheat.geometry import AttackRelationship, PieceRef
    with pytest.raises(ValueError, match="not present in root"):
        ValidationHarness.preflight_fixture(
            chess.STARTING_FEN, 
            "e4", 
            AttackRelationship(attacker=PieceRef(symbol="N", square="a1"), target_square="h8", target_piece=None), # dummy
            "dummy_f"
        )

def test_create_seal(tmp_path):
    from unittest.mock import patch, MagicMock
    with patch("subprocess.run") as mock_run:
        # First call is status, second is rev-parse
        mock_run.side_effect = [
            MagicMock(returncode=0, stdout=" M some_file.py\n"),
            MagicMock(returncode=0, stdout="abc1234\n")
        ]
        
        manifest_path = tmp_path / "manifest.txt"
        manifest_path.write_text("dummy manifest")
        protocol_path = tmp_path / "protocol.txt"
        protocol_path.write_text("dummy protocol")
        out_dir = tmp_path / "out"
        
        harness = ValidationHarness(threads=2, hash_mb=32, comparison_perspective="black")
        harness.engine_version = "TestEngine 1.0"
        
        import pytest
        with pytest.raises(RuntimeError, match="Seal broken"):
            harness.create_seal(str(manifest_path), str(protocol_path), str(out_dir))
            
        mock_run.side_effect = [
            MagicMock(returncode=0, stdout=""),
            MagicMock(returncode=0, stdout="abc1234\n")
        ]
        seal = harness.create_seal(str(manifest_path), str(protocol_path), str(out_dir))
        assert seal["working_tree_clean"] is True
        assert seal["git_commit_sha"] == "abc1234"
        assert seal["engine_threads"] == 2
        assert seal["engine_hash_mb"] == 32
        assert seal["comparison_perspective"] == "black"
        assert seal["engine_version"] == "TestEngine 1.0"
        assert "harness_identity" in seal
        assert "manifest_hash" in seal
        assert "protocol_hash" in seal
        import os
        assert os.path.exists(str(out_dir))

def test_preflight_played_move_not_in_m11():
    from chessheat.geometry import PieceRef
    with pytest.raises(ValueError, match="does not belong to M_11"):
        # e4 is played, but we assert e4 must remove an attack that it doesn't remove.
        # Starting position: g1 knight can move to f3. 
        # e4 does not remove this mobility.
        ValidationHarness.preflight_fixture(
            chess.STARTING_FEN, 
            "e4", 
            (PieceRef(square='g1', symbol='N'), 'f3'), 
            "dummy_f" # e4 doesn't create dummy_f either.
        )

def test_compute_regrets_mixed_perspective():
    from chessheat.consequence import compute_regrets
    from chessheat.engine import Score
    scores = {
        "move_a": Score(type="cp", value=100, perspective="white"),
        "move_b": Score(type="cp", value=80, perspective="black"),
    }
    with pytest.raises(ValueError, match="Mixed comparison perspectives found"):
        compute_regrets(scores)
