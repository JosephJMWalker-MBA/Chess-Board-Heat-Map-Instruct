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
    assert opts["Hash"].is_managed() is False
    
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
    spec = get_valid_spec(board)
    spec.budget_config["value"] = 999
    with pytest.raises(cpi.ProtocolError, match="budget_config does not exactly match"):
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
    with pytest.raises(cpi.ProtocolError, match="instrument_config does not exactly match"):
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

@patch('chessheat.cp_instrument.verify_executable')
@patch('chess.engine.SimpleEngine.popen_uci')
def test_candidate_policy_mismatch(mock_popen, mock_verify):
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
    with pytest.raises(cpi.ProtocolError, match="candidate_policy does not exactly match"):
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

@patch('chessheat.cp_instrument.verify_executable')
@patch('chess.engine.SimpleEngine.popen_uci')
def test_boolean_nodes_handling(mock_popen, mock_verify):
    ident = cpi.ExecutableIdentity("/bin/stockfish", cpi.STOCKFISH_BINARY_SHA256)
    mock_verify.return_value = ident
    mock_engine = MagicMock()
    mock_engine.id = {"name": cpi.STOCKFISH_UCI_NAME}
    mock_engine.options = create_real_options()
    
    def fake_analyse(*args, **kwargs):
        return {"score": chess.engine.PovScore(chess.engine.Cp(100), chess.WHITE), "nodes": True}
    mock_engine.analyse.side_effect = fake_analyse
    mock_popen.return_value = mock_engine
    
    session = cpi.InstrumentSession("dummy", cpi.InstrumentRole.SOURCE)
    session.start()
    board = chess.Board()
    spec = get_valid_spec(board)
    
    with pytest.raises(cpi.ProtocolError, match="Malformed reported nodes"):
        session.acquire(spec, board)

@patch('chessheat.cp_instrument.verify_executable')
@patch('chess.engine.SimpleEngine.popen_uci')
def test_list_pv_result_rejected(mock_popen, mock_verify):
    ident = cpi.ExecutableIdentity("/bin/stockfish", cpi.STOCKFISH_BINARY_SHA256)
    mock_verify.return_value = ident
    mock_engine = MagicMock()
    mock_engine.id = {"name": cpi.STOCKFISH_UCI_NAME}
    mock_engine.options = create_real_options()
    
    def fake_analyse(*args, **kwargs):
        return [{"score": chess.engine.PovScore(chess.engine.Cp(100), chess.WHITE)}]
    mock_engine.analyse.side_effect = fake_analyse
    mock_popen.return_value = mock_engine
    
    session = cpi.InstrumentSession("dummy", cpi.InstrumentRole.SOURCE)
    session.start()
    board = chess.Board()
    spec = get_valid_spec(board)
    
    with pytest.raises(cpi.ProtocolError, match="Expected single-PV result dict"):
        session.acquire(spec, board)

@patch('chessheat.cp_instrument.verify_executable')
@patch('chess.engine.SimpleEngine.popen_uci')
def test_deterministic_provenance(mock_popen, mock_verify):
    ident = cpi.ExecutableIdentity("/bin/stockfish", cpi.STOCKFISH_BINARY_SHA256)
    mock_verify.return_value = ident
    mock_engine = MagicMock()
    mock_engine.id = {"name": cpi.STOCKFISH_UCI_NAME}
    mock_engine.options = create_real_options()
    mock_engine.analyse.return_value = {"score": chess.engine.PovScore(chess.engine.Cp(100), chess.WHITE), "nodes": 100}
    mock_popen.return_value = mock_engine
    
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

