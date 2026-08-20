import pytest
import chess
import chess.engine
import os
import hashlib
import json
from unittest.mock import patch, MagicMock

import chessheat.cp_instrument as cpi
from chessheat.experiment import ExperimentSpec, ExperimentResult
from chessheat.semantics import SufficientPosition

def create_real_options():
    opts = {}
    opts["Threads"] = chess.engine.Option("Threads", "spin", 1, 1, 512, [])
    opts["Hash"] = chess.engine.Option("Hash", "spin", 16, 1, 33554432, [])
    opts["Skill Level"] = chess.engine.Option("Skill Level", "spin", 20, 0, 20, [])
    opts["UCI_LimitStrength"] = chess.engine.Option("UCI_LimitStrength", "check", False, None, None, [])
    opts["UCI_ShowWDL"] = chess.engine.Option("UCI_ShowWDL", "check", False, None, None, [])
    opts["SyzygyProbeLimit"] = chess.engine.Option("SyzygyProbeLimit", "spin", 0, 0, 7, [])
    opts["SyzygyPath"] = chess.engine.Option("SyzygyPath", "string", "<empty>", None, None, [])
    
    opts["MultiPV"] = chess.engine.Option("MultiPV", "spin", 1, 1, 500, [])
    opts["Ponder"] = chess.engine.Option("Ponder", "check", False, None, None, [])
    opts["UCI_Chess960"] = chess.engine.Option("UCI_Chess960", "check", False, None, None, [])
        
    opts["EvalFile"] = chess.engine.Option("EvalFile", "string", "nn-default.nnue", None, None, [])
    opts["EvalFileSmall"] = chess.engine.Option("EvalFileSmall", "string", "nn-default-small.nnue", None, None, [])
    return opts

def test_source_role():
    session = cpi.InstrumentSession("dummy", cpi.InstrumentRole.SOURCE)
    assert session.nodes == cpi.SOURCE_NODES
    assert session.instrument_id == cpi.SOURCE_INSTRUMENT_ID

def test_target_role():
    session = cpi.InstrumentSession("dummy", cpi.InstrumentRole.TARGET)
    assert session.nodes == cpi.TARGET_NODES

def test_invalid_role():
    with pytest.raises(cpi.ProtocolError, match="Invalid role"):
        cpi.InstrumentSession("dummy", "NOT_A_ROLE")

def test_role_immutability():
    session = cpi.InstrumentSession("dummy", cpi.InstrumentRole.SOURCE)
    with pytest.raises(AttributeError):
        session.role = cpi.InstrumentRole.TARGET

@patch('chessheat.cp_instrument.os.path.exists')
@patch('chessheat.cp_instrument.os.path.isfile')
@patch('chessheat.cp_instrument.os.access')
@patch('builtins.open')
def test_verify_executable_resolved_path(mock_open, mock_access, mock_isfile, mock_exists):
    mock_exists.return_value = True
    mock_isfile.return_value = True
    mock_access.return_value = True
    mock_open.return_value.__enter__.return_value.read.return_value = b"fake"
    with patch('chessheat.cp_instrument.hashlib.sha256') as mock_sha:
        mock_sha.return_value.hexdigest.return_value = cpi.STOCKFISH_BINARY_SHA256
        res = cpi.verify_executable("~/bin/stockfish")
        assert res.resolved_path == os.path.realpath(os.path.expanduser("~/bin/stockfish"))
        assert res.sha256 == cpi.STOCKFISH_BINARY_SHA256

@patch('chessheat.cp_instrument.verify_executable')
def test_start_fails_if_not_file(mock_verify):
    mock_verify.side_effect = cpi.ProtocolError("Not a regular file")
    session = cpi.InstrumentSession("dummy", cpi.InstrumentRole.SOURCE)
    with pytest.raises(cpi.ProtocolError, match="Not a regular file"):
        session.start()

@patch('chessheat.cp_instrument.verify_executable')
@patch('chess.engine.SimpleEngine.popen_uci')
def test_pre_and_post_spawn_sha(mock_popen, mock_verify):
    ident = cpi.ExecutableIdentity("/bin/stockfish", cpi.STOCKFISH_BINARY_SHA256)
    mock_verify.return_value = ident
    
    mock_engine = MagicMock()
    mock_engine.id = {"name": cpi.STOCKFISH_UCI_NAME}
    mock_engine.options = create_real_options()
    mock_popen.return_value = mock_engine
    
    session = cpi.InstrumentSession("dummy", cpi.InstrumentRole.SOURCE)
    session.start()
    assert mock_verify.call_count == 2
    
@patch('chessheat.cp_instrument.verify_executable')
@patch('chess.engine.SimpleEngine.popen_uci')
def test_post_spawn_sha_mismatch(mock_popen, mock_verify):
    ident1 = cpi.ExecutableIdentity("/bin/stockfish", cpi.STOCKFISH_BINARY_SHA256)
    ident2 = cpi.ExecutableIdentity("/bin/stockfish", "different_sha")
    mock_verify.side_effect = [ident1, ident2]
    
    mock_engine = MagicMock()
    mock_engine.id = {"name": cpi.STOCKFISH_UCI_NAME}
    mock_engine.options = create_real_options()
    mock_popen.return_value = mock_engine
    
    session = cpi.InstrumentSession("dummy", cpi.InstrumentRole.SOURCE)
    with pytest.raises(cpi.ProtocolError, match="Executable digest mutated"):
        session.start()
    mock_engine.quit.assert_called_once()

@patch('chessheat.cp_instrument.verify_executable')
@patch('chess.engine.SimpleEngine.popen_uci')
def test_missing_evalfile(mock_popen, mock_verify):
    ident = cpi.ExecutableIdentity("/bin/stockfish", cpi.STOCKFISH_BINARY_SHA256)
    mock_verify.return_value = ident
    
    mock_engine = MagicMock()
    mock_engine.id = {"name": cpi.STOCKFISH_UCI_NAME}
    opts = create_real_options()
    del opts["EvalFile"]
    mock_engine.options = opts
    mock_popen.return_value = mock_engine
    
    session = cpi.InstrumentSession("dummy", cpi.InstrumentRole.SOURCE)
    with pytest.raises(cpi.ProtocolError, match="Missing network option: EvalFile"):
        session.start()
    mock_engine.quit.assert_called_once()

@patch('chessheat.cp_instrument.verify_executable')
@patch('chess.engine.SimpleEngine.popen_uci')
def test_missing_evalfilesmall(mock_popen, mock_verify):
    ident = cpi.ExecutableIdentity("/bin/stockfish", cpi.STOCKFISH_BINARY_SHA256)
    mock_verify.return_value = ident
    
    mock_engine = MagicMock()
    mock_engine.id = {"name": cpi.STOCKFISH_UCI_NAME}
    opts = create_real_options()
    del opts["EvalFileSmall"]
    mock_engine.options = opts
    mock_popen.return_value = mock_engine
    
    session = cpi.InstrumentSession("dummy", cpi.InstrumentRole.SOURCE)
    with pytest.raises(cpi.ProtocolError, match="Missing network option: EvalFileSmall"):
        session.start()
    mock_engine.quit.assert_called_once()

@patch('chessheat.cp_instrument.verify_executable')
@patch('chess.engine.SimpleEngine.popen_uci')
def test_wrong_uci_name(mock_popen, mock_verify):
    ident = cpi.ExecutableIdentity("/bin/stockfish", cpi.STOCKFISH_BINARY_SHA256)
    mock_verify.return_value = ident
    
    mock_engine = MagicMock()
    mock_engine.id = {"name": "WrongEngine"}
    mock_engine.options = create_real_options()
    mock_popen.return_value = mock_engine
    
    session = cpi.InstrumentSession("dummy", cpi.InstrumentRole.SOURCE)
    with pytest.raises(cpi.ProtocolError, match="Wrong UCI name"):
        session.start()
    mock_engine.quit.assert_called_once()

@patch('chessheat.cp_instrument.verify_executable')
@patch('chess.engine.SimpleEngine.popen_uci')
def test_non_empty_syzygy_default(mock_popen, mock_verify):
    ident = cpi.ExecutableIdentity("/bin/stockfish", cpi.STOCKFISH_BINARY_SHA256)
    mock_verify.return_value = ident
    
    mock_engine = MagicMock()
    mock_engine.id = {"name": cpi.STOCKFISH_UCI_NAME}
    opts = create_real_options()
    opts["SyzygyPath"] = chess.engine.Option("SyzygyPath", "string", "/var/lib/syzygy", None, None, [])
    mock_engine.options = opts
    mock_popen.return_value = mock_engine
    
    session = cpi.InstrumentSession("dummy", cpi.InstrumentRole.SOURCE)
    with pytest.raises(cpi.ProtocolError, match="SyzygyPath default is not empty"):
        session.start()
    mock_engine.quit.assert_called_once()

@patch('chessheat.cp_instrument.verify_executable')
@patch('chess.engine.SimpleEngine.popen_uci')
def test_real_option_is_managed(mock_popen, mock_verify):
    ident = cpi.ExecutableIdentity("/bin/stockfish", cpi.STOCKFISH_BINARY_SHA256)
    mock_verify.return_value = ident
    
    mock_engine = MagicMock()
    mock_engine.id = {"name": cpi.STOCKFISH_UCI_NAME}
    
    # Real python-chess logic!
    opts = create_real_options()
    assert opts["MultiPV"].is_managed() is True
    assert opts["Ponder"].is_managed() is True
    assert opts["UCI_Chess960"].is_managed() is True
    
    assert opts["Threads"].is_managed() is False
    assert opts["Hash"].is_managed() is False
    assert opts["Skill Level"].is_managed() is False
    assert opts["UCI_LimitStrength"].is_managed() is False
    assert opts["UCI_ShowWDL"].is_managed() is False
    assert opts["SyzygyProbeLimit"].is_managed() is False
    assert opts["SyzygyPath"].is_managed() is False
    assert opts["EvalFile"].is_managed() is False
    assert opts["EvalFileSmall"].is_managed() is False
    
    mock_engine.options = opts
    mock_popen.return_value = mock_engine
    
    session = cpi.InstrumentSession("dummy", cpi.InstrumentRole.SOURCE)
    session.start()

@patch('chessheat.cp_instrument.verify_executable')
@patch('chess.engine.SimpleEngine.popen_uci')
def test_start_twice(mock_popen, mock_verify):
    ident = cpi.ExecutableIdentity("/bin/stockfish", cpi.STOCKFISH_BINARY_SHA256)
    mock_verify.return_value = ident
    
    mock_engine = MagicMock()
    mock_engine.id = {"name": cpi.STOCKFISH_UCI_NAME}
    mock_engine.options = create_real_options()
    mock_popen.return_value = mock_engine
    
    session = cpi.InstrumentSession("dummy", cpi.InstrumentRole.SOURCE)
    session.start()
    with pytest.raises(cpi.ProtocolError, match="Session already started"):
        session.start()

@patch('chessheat.cp_instrument.verify_executable')
@patch('chess.engine.SimpleEngine.popen_uci')
def test_acquire_before_start_and_after_close(mock_popen, mock_verify):
    ident = cpi.ExecutableIdentity("/bin/stockfish", cpi.STOCKFISH_BINARY_SHA256)
    mock_verify.return_value = ident
    
    mock_engine = MagicMock()
    mock_engine.id = {"name": cpi.STOCKFISH_UCI_NAME}
    mock_engine.options = create_real_options()
    mock_popen.return_value = mock_engine
    
    session = cpi.InstrumentSession("dummy", cpi.InstrumentRole.SOURCE)
    
    board = chess.Board()
    
    # A. acquire before start -> ProtocolError
    with pytest.raises(cpi.ProtocolError, match="Session not started"):
        session.acquire(MagicMock(), board)
        
    # B. close before start -> no exception
    session.close()
    
    # Start the session
    session.start()
    
    # C. successful start then close -> quit called once
    session.close()
    mock_engine.quit.assert_called_once()
    
    # D. close twice -> no second quit, no exception
    session.close()
    mock_engine.quit.assert_called_once()
    
    # E. acquire after close -> ProtocolError
    with pytest.raises(cpi.ProtocolError, match="Session not started"):
        session.acquire(MagicMock(), board)

def get_valid_spec(board, role=cpi.InstrumentRole.SOURCE):
    return ExperimentSpec(
        semantic_signature_version="1",
        semantic_signature_digest="a"*64,
        suite_identity="test",
        suite_digest="b"*64,
        fixture_identity="test",
        fixture_digest="c"*64,
        sufficient_position=SufficientPosition(
            variant="standard",
            board_arrangement_fen=board.board_fen(),
            side_to_move="w" if board.turn else "b",
            castling_rights=board.castling_xfen(),
            en_passant_square=chess.square_name(board.ep_square) if board.ep_square else None,
            halfmove_clock=board.halfmove_clock,
            fullmove_number=board.fullmove_number,
            history_available=True,
            history_identity="frozen_history_123"
        ),
        candidate_policy={
            "scope": "cp_all_legal_root_moves_v1",
            "ordered_legal_root_ucis": [m.uci() for m in sorted(list(board.legal_moves), key=lambda x: x.uci())],
            "required_search_count": len(list(board.legal_moves))
        },
        producer_identity=cpi.STOCKFISH_UCI_NAME,
        instrument_config=cpi.get_canonical_instrument_config(role),
        budget_config=cpi.get_canonical_budget_config(role),
        line_source="test",
        hypothesis_identifier="test",
        spec_version=2,
        comparison_perspective="white" if board.turn else "black"
    )

@patch('chessheat.cp_instrument.verify_executable')
@patch('chess.engine.SimpleEngine.popen_uci')
def test_budget_mismatch_rejection(mock_popen, mock_verify):
    ident = cpi.ExecutableIdentity("/bin/stockfish", cpi.STOCKFISH_BINARY_SHA256)
    mock_verify.return_value = ident
    mock_engine = MagicMock()
    mock_engine.id = {"name": cpi.STOCKFISH_UCI_NAME}
    mock_engine.options = create_real_options()
    mock_popen.return_value = mock_engine
    
    session = cpi.InstrumentSession("dummy", cpi.InstrumentRole.SOURCE)
    session.start()
    
    board = chess.Board()
    
    # Valid canonical
    spec = get_valid_spec(board)
    assert spec.budget_config == {"type": "nodes", "value": 50000}
    
    # wrong type
    spec.budget_config["type"] = "depth"
    with pytest.raises(cpi.ProtocolError):
        session.acquire(spec, board)
        
    # wrong value
    spec.budget_config = {"type": "nodes", "value": 999}
    with pytest.raises(cpi.ProtocolError):
        session.acquire(spec, board)
        
    # old shape
    spec.budget_config = {"nodes": 50000}
    with pytest.raises(cpi.ProtocolError):
        session.acquire(spec, board)
        
    # extra key
    spec.budget_config = {"type": "nodes", "value": 50000, "extra": True}
    with pytest.raises(cpi.ProtocolError):
        session.acquire(spec, board)

@patch('chessheat.cp_instrument.verify_executable')
@patch('chess.engine.SimpleEngine.popen_uci')
def test_instrument_config_mismatch_rejection(mock_popen, mock_verify):
    ident = cpi.ExecutableIdentity("/bin/stockfish", cpi.STOCKFISH_BINARY_SHA256)
    mock_verify.return_value = ident
    mock_engine = MagicMock()
    mock_engine.id = {"name": cpi.STOCKFISH_UCI_NAME}
    mock_engine.options = create_real_options()
    mock_popen.return_value = mock_engine
    
    session = cpi.InstrumentSession("dummy", cpi.InstrumentRole.SOURCE)
    session.start()
    
    board = chess.Board()
    spec = get_valid_spec(board)
    spec.instrument_config["Threads"] = 999
    with pytest.raises(cpi.ProtocolError):
        session.acquire(spec, board)
        
    spec = get_valid_spec(board)
    spec.instrument_config["Hash"] = 999
    with pytest.raises(cpi.ProtocolError):
        session.acquire(spec, board)
        
    spec = get_valid_spec(board)
    spec.instrument_config["Ponder"] = True
    with pytest.raises(cpi.ProtocolError):
        session.acquire(spec, board)
        
    spec = get_valid_spec(board)
    spec.instrument_config["MultiPV"] = 5
    with pytest.raises(cpi.ProtocolError):
        session.acquire(spec, board)
        
    spec = get_valid_spec(board)
    spec.instrument_config["UCI_Chess960"] = True
    with pytest.raises(cpi.ProtocolError):
        session.acquire(spec, board)
        
    spec = get_valid_spec(board)
    spec.instrument_config["SyzygyProbeLimit"] = 5
    with pytest.raises(cpi.ProtocolError):
        session.acquire(spec, board)
        
    spec = get_valid_spec(board)
    spec.instrument_config["tablebase_policy"] = "CUSTOM"
    with pytest.raises(cpi.ProtocolError):
        session.acquire(spec, board)
        
    spec = get_valid_spec(board)
    spec.instrument_config["network_policy"] = "CUSTOM"
    with pytest.raises(cpi.ProtocolError):
        session.acquire(spec, board)

    spec = get_valid_spec(board)
    spec.instrument_config["reset_policy"] = "CUSTOM"
    with pytest.raises(cpi.ProtocolError):
        session.acquire(spec, board)

    spec = get_valid_spec(board)
    spec.instrument_config["process_policy"] = "CUSTOM"
    with pytest.raises(cpi.ProtocolError):
        session.acquire(spec, board)

    spec = get_valid_spec(board)
    spec.instrument_config["binary_sha256"] = "CUSTOM"
    with pytest.raises(cpi.ProtocolError):
        session.acquire(spec, board)

    spec = get_valid_spec(board)
    spec.instrument_config["producer_identity"] = "CUSTOM"
    with pytest.raises(cpi.ProtocolError):
        session.acquire(spec, board)

@patch('chessheat.cp_instrument.verify_executable')
@patch('chess.engine.SimpleEngine.popen_uci')
def test_en_passant_canonicalization(mock_popen, mock_verify):
    ident = cpi.ExecutableIdentity("/bin/stockfish", cpi.STOCKFISH_BINARY_SHA256)
    mock_verify.return_value = ident
    mock_engine = MagicMock()
    mock_engine.id = {"name": cpi.STOCKFISH_UCI_NAME}
    mock_engine.options = create_real_options()
    mock_engine.analyse.return_value = {"score": chess.engine.PovScore(chess.engine.Cp(10), chess.WHITE), "nodes": 100}
    mock_popen.return_value = mock_engine
    
    session = cpi.InstrumentSession("dummy", cpi.InstrumentRole.SOURCE)
    session.start()
    
    board = chess.Board("rnbqkbnr/pppppppp/8/8/4P3/8/PPPP1PPP/RNBQKBNR b KQkq e3 0 1")
    spec = get_valid_spec(board)
    assert spec.sufficient_position.en_passant_square == "e3"
    
    # Modify spec to use "-" instead of "e3" -> should fail
    spec.sufficient_position.en_passant_square = "-"
    with pytest.raises(cpi.ProtocolError, match="SufficientPosition derivable fields mismatch"):
        session.acquire(spec, board)
        
    board2 = chess.Board()
    spec2 = get_valid_spec(board2)
    assert spec2.sufficient_position.en_passant_square is None
    spec2.sufficient_position.en_passant_square = "-"
    with pytest.raises(cpi.ProtocolError, match="SufficientPosition derivable fields mismatch"):
        session.acquire(spec2, board2)

@patch('chessheat.cp_instrument.verify_executable')
@patch('chess.engine.SimpleEngine.popen_uci')
def test_candidate_policy_boundaries(mock_popen, mock_verify):
    ident = cpi.ExecutableIdentity("/bin/stockfish", cpi.STOCKFISH_BINARY_SHA256)
    mock_verify.return_value = ident
    mock_engine = MagicMock()
    mock_engine.id = {"name": cpi.STOCKFISH_UCI_NAME}
    mock_engine.options = create_real_options()
    mock_popen.return_value = mock_engine
    
    session = cpi.InstrumentSession("dummy", cpi.InstrumentRole.SOURCE)
    session.start()
    
    board = chess.Board()
    spec = get_valid_spec(board)
    spec.candidate_policy["scope"] = "wrong_scope"
    with pytest.raises(cpi.ProtocolError):
        session.acquire(spec, board)
        
    # Omitted move
    spec = get_valid_spec(board)
    spec.candidate_policy["ordered_legal_root_ucis"] = spec.candidate_policy["ordered_legal_root_ucis"][1:]
    with pytest.raises(cpi.ProtocolError):
        session.acquire(spec, board)
        
    # Extra impossible move
    spec = get_valid_spec(board)
    spec.candidate_policy["ordered_legal_root_ucis"].append("e2e5")
    with pytest.raises(cpi.ProtocolError):
        session.acquire(spec, board)
        
    # Duplicated move
    spec = get_valid_spec(board)
    spec.candidate_policy["ordered_legal_root_ucis"].append(spec.candidate_policy["ordered_legal_root_ucis"][0])
    with pytest.raises(cpi.ProtocolError):
        session.acquire(spec, board)
        
    # Wrong ordering
    spec = get_valid_spec(board)
    ucis = spec.candidate_policy["ordered_legal_root_ucis"].copy()
    ucis.reverse()
    spec.candidate_policy["ordered_legal_root_ucis"] = ucis
    with pytest.raises(cpi.ProtocolError):
        session.acquire(spec, board)
        
    # Wrong count
    spec = get_valid_spec(board)
    spec.candidate_policy["required_search_count"] = 999
    with pytest.raises(cpi.ProtocolError):
        session.acquire(spec, board)
        
    # Extra contradictory key
    spec = get_valid_spec(board)
    spec.candidate_policy["extra"] = True
    with pytest.raises(cpi.ProtocolError):
        session.acquire(spec, board)

@patch('chessheat.cp_instrument.verify_executable')
@patch('chess.engine.SimpleEngine.popen_uci')
def test_root_validity(mock_popen, mock_verify):
    ident = cpi.ExecutableIdentity("/bin/stockfish", cpi.STOCKFISH_BINARY_SHA256)
    mock_verify.return_value = ident
    mock_engine = MagicMock()
    mock_engine.id = {"name": cpi.STOCKFISH_UCI_NAME}
    mock_engine.options = create_real_options()
    mock_popen.return_value = mock_engine
    
    session = cpi.InstrumentSession("dummy", cpi.InstrumentRole.SOURCE)
    session.start()
    
    # Invalid board: 3 kings
    board = chess.Board("3k4/8/8/8/8/8/8/K1K5 w - - 0 1")
    spec = get_valid_spec(board)
    with pytest.raises(cpi.ProtocolError, match="Root board is invalid"):
        session.acquire(spec, board)
    
    # Valid but 1 legal move
    board = chess.Board("1r6/8/8/8/8/7k/p7/K7 w - - 0 1")
    spec = get_valid_spec(board)
    with pytest.raises(cpi.ProtocolError, match="at least 2 legal moves"):
        session.acquire(spec, board)
        
    # Checkmate (terminal)
    board = chess.Board("rnb1kbnr/pppp1ppp/8/4p3/6Pq/5P2/PPPPP2P/RNBQKBNR w KQkq - 1 3")
    spec = get_valid_spec(board)
    with pytest.raises(cpi.ProtocolError, match="Terminal root board"):
        session.acquire(spec, board)
        
    # Chess960
    board = chess.Board(chess960=True)
    spec = get_valid_spec(board)
    with pytest.raises(cpi.ProtocolError, match="Chess960 is not permitted"):
        session.acquire(spec, board)

@patch('chessheat.cp_instrument.verify_executable')
@patch('chess.engine.SimpleEngine.popen_uci')
def test_history_boundaries(mock_popen, mock_verify):
    ident = cpi.ExecutableIdentity("/bin/stockfish", cpi.STOCKFISH_BINARY_SHA256)
    mock_verify.return_value = ident
    mock_engine = MagicMock()
    mock_engine.id = {"name": cpi.STOCKFISH_UCI_NAME}
    mock_engine.options = create_real_options()
    mock_popen.return_value = mock_engine
    
    session = cpi.InstrumentSession("dummy", cpi.InstrumentRole.SOURCE)
    session.start()
    
    board = chess.Board()
    spec = get_valid_spec(board)
    spec.sufficient_position.history_available = False
    with pytest.raises(cpi.ProtocolError, match="history_available must be True"):
        session.acquire(spec, board)
        
    spec = get_valid_spec(board)
    spec.sufficient_position.history_identity = None
    with pytest.raises(cpi.ProtocolError, match="history_identity must be a non-empty string"):
        session.acquire(spec, board)
        
    spec = get_valid_spec(board)
    spec.sufficient_position.history_identity = ""
    with pytest.raises(cpi.ProtocolError, match="history_identity must be a non-empty string"):
        session.acquire(spec, board)

@patch('chessheat.cp_instrument.verify_executable')
@patch('chess.engine.SimpleEngine.popen_uci')
def test_configure_call_proof(mock_popen, mock_verify):
    ident = cpi.ExecutableIdentity("/bin/stockfish", cpi.STOCKFISH_BINARY_SHA256)
    mock_verify.return_value = ident
    mock_engine = MagicMock()
    mock_engine.id = {"name": cpi.STOCKFISH_UCI_NAME}
    mock_engine.options = create_real_options()
    mock_popen.return_value = mock_engine
    
    session = cpi.InstrumentSession("dummy", cpi.InstrumentRole.SOURCE)
    session.start()
    
    mock_engine.configure.assert_called_once_with(cpi.STATIC_UCI_CONFIG)
    
    cfg = mock_engine.configure.call_args[0][0]
    assert "MultiPV" not in cfg
    assert "Ponder" not in cfg
    assert "UCI_Chess960" not in cfg
    assert "EvalFile" not in cfg
    assert "EvalFileSmall" not in cfg

@patch('chessheat.cp_instrument.verify_executable')
@patch('chess.engine.SimpleEngine.popen_uci')
def test_acquisition_mechanics_and_child_proofs(mock_popen, mock_verify):
    ident = cpi.ExecutableIdentity("/bin/stockfish", cpi.STOCKFISH_BINARY_SHA256)
    mock_verify.return_value = ident
    mock_engine = MagicMock()
    mock_engine.id = {"name": cpi.STOCKFISH_UCI_NAME}
    mock_engine.options = create_real_options()
    mock_engine.analyse.return_value = {"score": chess.engine.PovScore(chess.engine.Cp(100), chess.WHITE), "nodes": 100}
    mock_popen.return_value = mock_engine
    
    session = cpi.InstrumentSession("dummy", cpi.InstrumentRole.SOURCE)
    session.start()
    
    # Create history-bearing root
    root_board = chess.Board()
    root_board.push(chess.Move.from_uci("e2e4"))
    root_board.push(chess.Move.from_uci("e7e5"))
    
    original_fen = root_board.fen()
    original_stack = list(root_board.move_stack)
    
    spec = get_valid_spec(root_board)
    
    res = session.acquire(spec, root_board)
    
    # Caller board unchanged
    assert root_board.fen() == original_fen
    assert list(root_board.move_stack) == original_stack
    
    legal_moves = list(root_board.legal_moves)
    expected_ucis = [m.uci() for m in sorted(legal_moves, key=lambda x: x.uci())]
    
    # Analyse call count
    assert mock_engine.analyse.call_count == len(expected_ucis)
    
    game_tokens = []
    
    for i, call in enumerate(mock_engine.analyse.call_args_list):
        args, kwargs = call
        child_board = args[0]
        limit = args[1]
        
        # 1. First positional arg is child
        assert child_board is not root_board
        
        # 2. Limit nodes
        assert limit.nodes == cpi.SOURCE_NODES
        
        # 3. game present and distinct
        game = kwargs["game"]
        assert game is not None
        game_tokens.append(game)
        
        # 4. multipv and root_moves
        assert kwargs["multipv"] is None
        assert kwargs["root_moves"] is None
        
        # Canonical order proof
        assert child_board.move_stack[-1].uci() == expected_ucis[i]
        assert len(child_board.move_stack) == len(original_stack) + 1
        assert child_board.move_stack[:-1] == original_stack
        
        # Child FEN / Result provenance
        obs = json.loads(res.data_payload)["observations"][i]
        assert obs["canonical_acquisition_index"] == i
        assert obs["root_move_uci"] == expected_ucis[i]
        assert obs["child_fen"] == child_board.fen(shredder=False, en_passant="fen")
        assert obs["parent_move_stack_length"] == len(original_stack)
        assert obs["child_move_stack_length"] == len(original_stack) + 1
        assert obs["history_derivation_version"] == "S0_CHILD_PUSH_V1"
        assert obs["parent_history_identity"] == spec.sufficient_position.history_identity
        assert obs["isolation_sequence_index"] == i
        assert obs["requested_nodes"] == cpi.SOURCE_NODES

    # Distinct tokens
    assert len(game_tokens) == len(expected_ucis)
    assert len({id(t) for t in game_tokens}) == len(expected_ucis)
    
    # History identity survived
    assert json.loads(res.data_payload)["parent_history_identity"] == spec.sufficient_position.history_identity
    
    # ExperimentResult Binding / Integrity
    assert res.spec_digest == spec.spec_digest()
    assert json.loads(res.data_payload)["spec_digest"] == res.spec_digest
    
    # Tampering test
    payload = json.loads(res.data_payload)
    payload["instrument_id"] = "TAMPERED"
    tampered_data = json.dumps(payload, sort_keys=True)
    with pytest.raises(ValueError):
        ExperimentResult(spec_digest=res.spec_digest, artifact_digest=res.artifact_digest, data_payload=tampered_data)

@patch('chessheat.cp_instrument.verify_executable')
@patch('chess.engine.SimpleEngine.popen_uci')
def test_failed_child_acquisition(mock_popen, mock_verify):
    ident = cpi.ExecutableIdentity("/bin/stockfish", cpi.STOCKFISH_BINARY_SHA256)
    mock_verify.return_value = ident
    mock_engine = MagicMock()
    mock_engine.id = {"name": cpi.STOCKFISH_UCI_NAME}
    mock_engine.options = create_real_options()
    
    call_counts = [0]
    def fake_analyse(*args, **kwargs):
        call_counts[0] += 1
        if call_counts[0] == 3:
            raise Exception("Simulated crash")
        return {"score": chess.engine.PovScore(chess.engine.Cp(100), chess.WHITE), "nodes": 100}
        
    mock_engine.analyse.side_effect = fake_analyse
    mock_popen.return_value = mock_engine
    
    session = cpi.InstrumentSession("dummy", cpi.InstrumentRole.SOURCE)
    session.start()
    
    board = chess.Board()
    spec = get_valid_spec(board)
    
    with pytest.raises(cpi.ProtocolError, match="Analysis failed"):
        session.acquire(spec, board)
        
    # No result returned, no partial data

@patch('chessheat.cp_instrument.verify_executable')
@patch('chess.engine.SimpleEngine.popen_uci')
def test_score_output_proofs(mock_popen, mock_verify):
    ident = cpi.ExecutableIdentity("/bin/stockfish", cpi.STOCKFISH_BINARY_SHA256)
    mock_verify.return_value = ident
    mock_engine = MagicMock()
    mock_engine.id = {"name": cpi.STOCKFISH_UCI_NAME}
    mock_engine.options = create_real_options()
    
    scores = [
        {"score": chess.engine.PovScore(chess.engine.Cp(150), chess.WHITE), "nodes": 100}, # valid CP
        {"score": chess.engine.PovScore(chess.engine.Mate(3), chess.WHITE), "nodes": 100}, # valid mate
        {"nodes": 100}, # missing score
        {"score": None, "nodes": 100}, # None score
        {"score": "not_a_score", "nodes": 100}, # non-PovScore
        [{"score": chess.engine.PovScore(chess.engine.Cp(150), chess.WHITE), "nodes": 100}], # list/MultiPV
        {"score": chess.engine.PovScore(chess.engine.Cp(-50), chess.BLACK), "nodes": 100} # perspective inversion
    ]
    
    idx = [0]
    def fake_analyse(*args, **kwargs):
        s = scores[idx[0]]
        idx[0] += 1
        return s
        
    mock_engine.analyse.side_effect = fake_analyse
    mock_popen.return_value = mock_engine
    
    session = cpi.InstrumentSession("dummy", cpi.InstrumentRole.SOURCE)
    session.start()
    board = chess.Board('k7/8/8/8/8/8/p7/K7 w - - 0 1') # 2 legal moves
    
    # 1. Valid CP
    idx[0] = 0
    spec = get_valid_spec(board)
    res = session.acquire(spec, board)
    assert json.loads(res.data_payload)["observations"][0]["score_type"] == "cp"
    assert json.loads(res.data_payload)["observations"][0]["score_value"] == 150
    assert json.loads(res.data_payload)["observations"][0]["perspective"] == "white"
    
    assert json.loads(res.data_payload)["observations"][1]["score_type"] == "mate"
    assert json.loads(res.data_payload)["observations"][1]["score_value"] == 3
        
    # 2. Missing score
    idx[0] = 2
    spec = get_valid_spec(board)
    with pytest.raises(cpi.ProtocolError, match="Missing score"):
        session.acquire(spec, board)
            
    # 3. None score
    idx[0] = 3
    spec = get_valid_spec(board)
    with pytest.raises(cpi.ProtocolError, match="Score is not a PovScore"):
        session.acquire(spec, board)
            
    # 4. non-PovScore
    idx[0] = 4
    spec = get_valid_spec(board)
    with pytest.raises(cpi.ProtocolError, match="Score is not a PovScore"):
        session.acquire(spec, board)
            
    # 5. list/MultiPV
    idx[0] = 5
    spec = get_valid_spec(board)
    with pytest.raises(cpi.ProtocolError, match="Expected single-PV result dict from analyse"):
        session.acquire(spec, board)
            
    # 6. Perspective inversion
    idx[0] = 6
    spec = get_valid_spec(board)
    def fake_analyse_2(*args, **kwargs):
        if kwargs["game"]:
            pass
        return scores[6]
    mock_engine.analyse.side_effect = fake_analyse_2
    res = session.acquire(spec, board)
    assert json.loads(res.data_payload)["observations"][0]["score_type"] == "cp"
    assert json.loads(res.data_payload)["observations"][0]["score_value"] == 50

@patch('chessheat.cp_instrument.verify_executable')
@patch('chess.engine.SimpleEngine.popen_uci')
def test_node_provenance_matrix(mock_popen, mock_verify):
    ident = cpi.ExecutableIdentity("/bin/stockfish", cpi.STOCKFISH_BINARY_SHA256)
    mock_verify.return_value = ident
    mock_engine = MagicMock()
    mock_engine.id = {"name": cpi.STOCKFISH_UCI_NAME}
    mock_engine.options = create_real_options()
    
    nodes_to_test = [
        None,
        0,
        100,
        -10,
        True,
        False,
        3.14,
        "100"
    ]
    
    idx = [0]
    def fake_analyse(*args, **kwargs):
        n = nodes_to_test[idx[0]]
        res = {"score": chess.engine.PovScore(chess.engine.Cp(100), chess.WHITE)}
        if n is not None:
            res["nodes"] = n
        return res
        
    mock_engine.analyse.side_effect = fake_analyse
    mock_popen.return_value = mock_engine
    
    session = cpi.InstrumentSession("dummy", cpi.InstrumentRole.SOURCE)
    session.start()
    board = chess.Board('k7/8/8/8/8/8/p7/K7 w - - 0 1')
    
    # 1. None -> accepted
    idx[0] = 0
    spec = get_valid_spec(board)
    res = session.acquire(spec, board)
    assert json.loads(res.data_payload)["observations"][0]["reported_nodes"] is None
    assert json.loads(res.data_payload)["observations"][0]["requested_nodes"] == cpi.SOURCE_NODES
    
    # 2. 0 -> accepted
    idx[0] = 1
    res = session.acquire(spec, board)
    assert json.loads(res.data_payload)["observations"][0]["reported_nodes"] == 0
    
    # 3. 100 -> accepted
    idx[0] = 2
    res = session.acquire(spec, board)
    assert json.loads(res.data_payload)["observations"][0]["reported_nodes"] == 100
    
    # 4. -10 -> rejected
    idx[0] = 3
    with pytest.raises(cpi.ProtocolError, match="Negative reported nodes"):
        session.acquire(spec, board)
        
    # 5. True -> rejected
    idx[0] = 4
    with pytest.raises(cpi.ProtocolError, match="expected int"):
        session.acquire(spec, board)
        
    # 6. False -> rejected
    idx[0] = 5
    with pytest.raises(cpi.ProtocolError, match="expected int"):
        session.acquire(spec, board)
        
    # 7. 3.14 -> rejected
    idx[0] = 6
    with pytest.raises(cpi.ProtocolError, match="expected int"):
        session.acquire(spec, board)
        
    # 8. "100" -> rejected
    idx[0] = 7
    with pytest.raises(cpi.ProtocolError, match="expected int"):
        session.acquire(spec, board)

@patch('chessheat.cp_instrument.verify_executable')
@patch('chess.engine.SimpleEngine.popen_uci')
def test_source_target_process_independence(mock_popen, mock_verify):
    ident = cpi.ExecutableIdentity("/bin/stockfish", cpi.STOCKFISH_BINARY_SHA256)
    mock_verify.return_value = ident
    
    source_engine = MagicMock()
    source_engine.id = {"name": cpi.STOCKFISH_UCI_NAME}
    source_engine.options = create_real_options()
    
    target_engine = MagicMock()
    target_engine.id = {"name": cpi.STOCKFISH_UCI_NAME}
    target_engine.options = create_real_options()
    
    mock_popen.side_effect = [source_engine, target_engine]
    
    source_session = cpi.InstrumentSession("dummy", cpi.InstrumentRole.SOURCE)
    source_session.start()
    
    target_session = cpi.InstrumentSession("dummy", cpi.InstrumentRole.TARGET)
    target_session.start()
    
    assert mock_popen.call_count == 2
    
    assert source_session._engine is source_engine
    assert target_session._engine is target_engine
    assert source_session._engine is not target_session._engine
    
    assert source_session.nodes == 50000
    assert source_session.instrument_id == cpi.SOURCE_INSTRUMENT_ID
    
    assert target_session.nodes == 250000
    assert target_session.instrument_id == cpi.TARGET_INSTRUMENT_ID

@patch('chessheat.cp_instrument.verify_executable')
@patch('chess.engine.SimpleEngine.popen_uci')
def test_deterministic_provenance(mock_popen, mock_verify):
    ident = cpi.ExecutableIdentity("/bin/stockfish", cpi.STOCKFISH_BINARY_SHA256)
    mock_verify.return_value = ident
    
    # Use two genuinely distinct fake engine objects
    engine1 = MagicMock()
    engine1.id = {"name": cpi.STOCKFISH_UCI_NAME}
    engine1.options = create_real_options()
    engine1.analyse.return_value = {"score": chess.engine.PovScore(chess.engine.Cp(100), chess.WHITE), "nodes": 100}
    
    engine2 = MagicMock()
    engine2.id = {"name": cpi.STOCKFISH_UCI_NAME}
    engine2.options = create_real_options()
    engine2.analyse.return_value = {"score": chess.engine.PovScore(chess.engine.Cp(100), chess.WHITE), "nodes": 100}
    
    mock_popen.side_effect = [engine1, engine2]
    
    session1 = cpi.InstrumentSession("dummy", cpi.InstrumentRole.SOURCE)
    session1.start()
    
    session2 = cpi.InstrumentSession("dummy", cpi.InstrumentRole.SOURCE)
    session2.start()
    
    board = chess.Board()
    spec = get_valid_spec(board)
    
    res1 = session1.acquire(spec, board)
    res2 = session2.acquire(spec, board)
    
    assert res1.data_payload == res2.data_payload
    assert res1.artifact_digest == res2.artifact_digest

