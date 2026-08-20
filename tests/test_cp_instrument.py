import pytest
import chess
import chess.engine
from unittest.mock import patch, MagicMock

from chessheat.cp_instrument import (
    construct_acquisition_plan,
    InstrumentSession,
    ProtocolError,
    verify_executable,
    STOCKFISH_UCI_NAME,
    STOCKFISH_BINARY_SHA256,
    SOURCE_NODES,
    TARGET_NODES
)

@pytest.fixture
def fake_board():
    return chess.Board("rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1")

def test_plan_generation(fake_board):
    plan = construct_acquisition_plan(fake_board)
    assert len(plan) == 20
    # verify canonical order
    ucis = [p.root_move_uci for p in plan]
    assert ucis == sorted(ucis)
    # verify perspective
    assert all(p.comparison_perspective == chess.WHITE for p in plan)

def test_plan_generation_invalid():
    b = chess.Board()
    b.clear() # invalid, kings missing
    with pytest.raises(ProtocolError, match="invalid"):
        construct_acquisition_plan(b)
        
def test_plan_generation_chess960():
    b = chess.Board(chess960=True)
    with pytest.raises(ProtocolError, match="Chess960"):
        construct_acquisition_plan(b)

def test_session_role_validation():
    with pytest.raises(ProtocolError, match="Invalid role"):
        InstrumentSession("dummy_path", "INVALID")

@patch("chessheat.cp_instrument.verify_executable")
@patch("chess.engine.SimpleEngine.popen_uci")
def test_session_start_and_acquire(mock_popen, mock_verify, fake_board):
    mock_engine = MagicMock()
    mock_engine.id = {"name": STOCKFISH_UCI_NAME}
    
    mock_opt_eval = MagicMock()
    mock_opt_eval.value = "default.nnue"
    mock_opt_eval.default = "default.nnue"
    
    mock_opt_eval_small = MagicMock()
    mock_opt_eval_small.value = "default_small.nnue"
    mock_opt_eval_small.default = "default_small.nnue"

    mock_opt_syzygy = MagicMock()
    mock_opt_syzygy.value = "<empty>"
    
    mock_engine.options = {
        "Threads": MagicMock(),
        "Hash": MagicMock(),
        "Skill Level": MagicMock(),
        "UCI_LimitStrength": MagicMock(),
        "UCI_ShowWDL": MagicMock(),
        "SyzygyProbeLimit": MagicMock(),
        "SyzygyPath": mock_opt_syzygy,
        "MultiPV": MagicMock(),
        "Ponder": MagicMock(),
        "UCI_Chess960": MagicMock(),
        "EvalFile": mock_opt_eval,
        "EvalFileSmall": mock_opt_eval_small,
    }
    
    # Mock analyse response
    mock_engine.analyse.return_value = {
        "score": chess.engine.PovScore(chess.engine.Cp(100), chess.WHITE),
        "nodes": 50000
    }
    
    mock_popen.return_value = mock_engine
    
    session = InstrumentSession("dummy", "SOURCE")
    session.start()
    
    # Configure called with unmanaged
    mock_engine.configure.assert_called_once()
    config_call = mock_engine.configure.call_args[0][0]
    assert "MultiPV" not in config_call
    assert "Hash" in config_call
    
    obs = session.acquire(fake_board)
    assert len(obs) == 20
    assert mock_engine.analyse.call_count == 20
    
    # Check analyse kwargs
    call_args = mock_engine.analyse.call_args[0]
    call_kwargs = mock_engine.analyse.call_args[1]
    assert "game" in call_kwargs
    assert call_kwargs["multipv"] is None
    assert call_kwargs["root_moves"] is None
    assert call_args[1].nodes == SOURCE_NODES
    
    assert obs[0].score_type == "cp"
    assert obs[0].score_value == 100
    assert obs[0].perspective == chess.WHITE
    
    session.close()

@patch("chessheat.cp_instrument.verify_executable")
@patch("chess.engine.SimpleEngine.popen_uci")
def test_mate_score_handling(mock_popen, mock_verify, fake_board):
    mock_engine = MagicMock()
    mock_engine.id = {"name": STOCKFISH_UCI_NAME}
    
    mock_opt_eval = MagicMock()
    mock_opt_eval.value = "default.nnue"
    mock_opt_eval.default = "default.nnue"
    
    mock_opt_syzygy = MagicMock()
    mock_opt_syzygy.value = "<empty>"
    
    mock_engine.options = {
        "Threads": MagicMock(),
        "Hash": MagicMock(),
        "Skill Level": MagicMock(),
        "UCI_LimitStrength": MagicMock(),
        "UCI_ShowWDL": MagicMock(),
        "SyzygyProbeLimit": MagicMock(),
        "SyzygyPath": mock_opt_syzygy,
        "MultiPV": MagicMock(),
        "Ponder": MagicMock(),
        "UCI_Chess960": MagicMock(),
        "EvalFile": mock_opt_eval,
    }
    
    # Mock analyse response mate in 3 from black's pov, but root is white
    mock_engine.analyse.return_value = {
        "score": chess.engine.PovScore(chess.engine.Mate(3), chess.BLACK),
        "nodes": 250000
    }
    mock_popen.return_value = mock_engine
    
    session = InstrumentSession("dummy", "TARGET")
    session.start()
    obs = session.acquire(fake_board)
    assert obs[0].score_type == "mate"
    # white to move, black has mate in 3, so score for white is -3 mate
    assert obs[0].score_value == -3
    assert obs[0].perspective == chess.WHITE
    
@patch("chessheat.cp_instrument.verify_executable")
@patch("chess.engine.SimpleEngine.popen_uci")
def test_network_override_rejected(mock_popen, mock_verify):
    mock_engine = MagicMock()
    mock_engine.id = {"name": STOCKFISH_UCI_NAME}
    
    mock_opt_eval = MagicMock()
    mock_opt_eval.value = "custom.nnue"
    mock_opt_eval.default = "default.nnue"
    
    mock_engine.options = {
        "EvalFile": mock_opt_eval,
        # other options missing will also raise, but network override should fail
        "Threads": MagicMock(), "Hash": MagicMock(), "Skill Level": MagicMock(),
        "UCI_LimitStrength": MagicMock(), "UCI_ShowWDL": MagicMock(),
        "SyzygyProbeLimit": MagicMock(), "SyzygyPath": MagicMock(),
        "MultiPV": MagicMock(), "Ponder": MagicMock(), "UCI_Chess960": MagicMock()
    }
    mock_popen.return_value = mock_engine
    
    session = InstrumentSession("dummy", "SOURCE")
    with pytest.raises(ProtocolError, match="network override"):
        session.start()

@patch("chessheat.cp_instrument.verify_executable")
@patch("chess.engine.SimpleEngine.popen_uci")
def test_syzygy_path_rejected(mock_popen, mock_verify):
    mock_engine = MagicMock()
    mock_engine.id = {"name": STOCKFISH_UCI_NAME}
    
    mock_opt_syzygy = MagicMock()
    mock_opt_syzygy.value = "/path/to/tablebases"
    
    mock_engine.options = {
        "SyzygyPath": mock_opt_syzygy,
        "Threads": MagicMock(), "Hash": MagicMock(), "Skill Level": MagicMock(),
        "UCI_LimitStrength": MagicMock(), "UCI_ShowWDL": MagicMock(),
        "SyzygyProbeLimit": MagicMock(), "MultiPV": MagicMock(),
        "Ponder": MagicMock(), "UCI_Chess960": MagicMock()
    }
    mock_popen.return_value = mock_engine
    
    session = InstrumentSession("dummy", "SOURCE")
    with pytest.raises(ProtocolError, match="Tablebase path is active"):
        session.start()

def test_verify_executable_not_file(tmp_path):
    d = tmp_path / "dir"
    d.mkdir()
    with pytest.raises(ProtocolError, match="not a file"):
        verify_executable(str(d))

def test_verify_executable_sha_mismatch(tmp_path):
    f = tmp_path / "stockfish"
    f.write_bytes(b"wrong contents")
    with pytest.raises(ProtocolError, match="Binary SHA mismatch"):
        verify_executable(str(f))
