import pytest
import chess
import chess.engine
import os
import hashlib
from unittest.mock import patch, MagicMock

import chessheat.cp_instrument as cpi
from chessheat.experiment import ExperimentSpec
from chessheat.semantics import SufficientPosition

class FakeOption(chess.engine.Option):
    def __init__(self, name, type, default, min, max, var, managed):
        super().__init__(name, type, default, min, max, var)
        self._managed = managed
    def is_managed(self):
        return self._managed

def create_fake_options():
    opts = {}
    for k in cpi.STATIC_UCI_CONFIG:
        opts[k] = FakeOption(k, "string", "", None, None, [], False)
    
    for k in cpi.MANAGED_OPTIONS:
        opts[k] = FakeOption(k, "check", False, None, None, [], True)
        
    opts["EvalFile"] = FakeOption("EvalFile", "string", "default.nnue", None, None, [], False)
    opts["EvalFileSmall"] = FakeOption("EvalFileSmall", "string", "default_small.nnue", None, None, [], False)
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
    with pytest.raises(AttributeError):
        session.nodes = 100
    with pytest.raises(AttributeError):
        session.instrument_id = "foo"

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
        assert res == os.path.realpath(os.path.expanduser("~/bin/stockfish"))

@patch('chessheat.cp_instrument.verify_executable')
def test_start_fails_if_not_file(mock_verify):
    mock_verify.side_effect = cpi.ProtocolError("Not a regular file")
    session = cpi.InstrumentSession("dummy", cpi.InstrumentRole.SOURCE)
    with pytest.raises(cpi.ProtocolError, match="Not a regular file"):
        session.start()

@patch('chessheat.cp_instrument.verify_executable')
@patch('chess.engine.SimpleEngine.popen_uci')
def test_pre_and_post_spawn_sha(mock_popen, mock_verify):
    mock_verify.return_value = "/bin/stockfish"
    
    mock_engine = MagicMock()
    mock_engine.id = {"name": cpi.STOCKFISH_UCI_NAME}
    mock_engine.options = create_fake_options()
    mock_popen.return_value = mock_engine
    
    session = cpi.InstrumentSession("dummy", cpi.InstrumentRole.SOURCE)
    session.start()
    assert mock_verify.call_count == 2 # Pre and post

@patch('chessheat.cp_instrument.verify_executable')
@patch('chess.engine.SimpleEngine.popen_uci')
def test_wrong_uci_name(mock_popen, mock_verify):
    mock_engine = MagicMock()
    mock_engine.id = {"name": "Stockfish 16"}
    mock_popen.return_value = mock_engine
    
    session = cpi.InstrumentSession("dummy", cpi.InstrumentRole.SOURCE)
    with pytest.raises(cpi.ProtocolError, match="Wrong UCI name"):
        session.start()
    mock_engine.quit.assert_called_once()

@patch('chessheat.cp_instrument.verify_executable')
@patch('chess.engine.SimpleEngine.popen_uci')
def test_network_options_exist_but_not_configured(mock_popen, mock_verify):
    mock_engine = MagicMock()
    mock_engine.id = {"name": cpi.STOCKFISH_UCI_NAME}
    opts = create_fake_options()
    mock_engine.options = opts
    mock_popen.return_value = mock_engine
    
    session = cpi.InstrumentSession("dummy", cpi.InstrumentRole.SOURCE)
    session.start()
    
    # Check configure was called only with static options
    mock_engine.configure.assert_called_once_with(cpi.STATIC_UCI_CONFIG)
    
@patch('chessheat.cp_instrument.verify_executable')
@patch('chess.engine.SimpleEngine.popen_uci')
def test_managed_options_semantics(mock_popen, mock_verify):
    mock_engine = MagicMock()
    mock_engine.id = {"name": cpi.STOCKFISH_UCI_NAME}
    opts = create_fake_options()
    opts["MultiPV"] = FakeOption("MultiPV", "spin", 1, None, None, [], False) # Not managed!
    mock_engine.options = opts
    mock_popen.return_value = mock_engine
    
    session = cpi.InstrumentSession("dummy", cpi.InstrumentRole.SOURCE)
    with pytest.raises(cpi.ProtocolError, match="is not managed"):
        session.start()

def get_valid_spec(board):
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
            en_passant_square=chess.square_name(board.ep_square) if board.ep_square else "-",
            halfmove_clock=board.halfmove_clock,
            fullmove_number=board.fullmove_number,
            history_available=False,
            history_identity="none"
        ),
        candidate_policy={
            "scope": "cp_all",
            "ordered_legal_root_ucis": [m.uci() for m in sorted(list(board.legal_moves), key=lambda x: x.uci())],
            "required_search_count": len(list(board.legal_moves))
        },
        producer_identity=cpi.STOCKFISH_UCI_NAME,
        instrument_config={"instrument_id": cpi.SOURCE_INSTRUMENT_ID},
        budget_config={"nodes": cpi.SOURCE_NODES},
        line_source="test",
        hypothesis_identifier="test",
        spec_version=2,
        comparison_perspective="white" if board.turn else "black"
    )

@patch('chessheat.cp_instrument.verify_executable')
@patch('chess.engine.SimpleEngine.popen_uci')
def test_acquisition_mechanics(mock_popen, mock_verify):
    mock_verify.return_value = "/bin/stockfish"
    mock_engine = MagicMock()
    mock_engine.id = {"name": cpi.STOCKFISH_UCI_NAME}
    mock_engine.options = create_fake_options()
    
    # Mock analyse responses
    def fake_analyse(board, limit, **kwargs):
        return {"score": chess.engine.PovScore(chess.engine.Cp(100), chess.WHITE), "nodes": 123}
    mock_engine.analyse.side_effect = fake_analyse
    mock_popen.return_value = mock_engine
    
    session = cpi.InstrumentSession("dummy", cpi.InstrumentRole.SOURCE)
    session.start()
    
    board = chess.Board()
    spec = get_valid_spec(board)
    
    res = session.acquire(spec, board)
    
    # Validate token uniqueness and parameters
    analyse_calls = mock_engine.analyse.call_args_list
    assert len(analyse_calls) == 20
    
    tokens = [call.kwargs['game'] for call in analyse_calls]
    assert len(set(id(t) for t in tokens)) == 20 # all distinct
    
    for call in analyse_calls:
        assert call.kwargs['multipv'] is None
        assert call.kwargs['root_moves'] is None
        assert call.args[1].nodes == cpi.SOURCE_NODES
        
    assert res.spec_digest == spec.spec_digest()
    
@patch('chessheat.cp_instrument.verify_executable')
@patch('chess.engine.SimpleEngine.popen_uci')
def test_history_preservation_regression(mock_popen, mock_verify):
    mock_verify.return_value = "/bin/stockfish"
    mock_engine = MagicMock()
    mock_engine.id = {"name": cpi.STOCKFISH_UCI_NAME}
    mock_engine.options = create_fake_options()
    mock_engine.analyse.return_value = {"score": chess.engine.PovScore(chess.engine.Cp(100), chess.WHITE)}
    mock_popen.return_value = mock_engine
    
    session = cpi.InstrumentSession("dummy", cpi.InstrumentRole.SOURCE)
    session.start()
    
    board = chess.Board()
    board.push_san("e4")
    board.push_san("e5")
    
    spec = get_valid_spec(board)
    session.acquire(spec, board)
    
    analyse_calls = mock_engine.analyse.call_args_list
    child_board = analyse_calls[0].args[0]
    
    assert len(child_board.move_stack) == 3 # root has 2, child has 1 more

@patch('chessheat.cp_instrument.verify_executable')
@patch('chess.engine.SimpleEngine.popen_uci')
def test_missing_nodes(mock_popen, mock_verify):
    mock_verify.return_value = "/bin/stockfish"
    mock_engine = MagicMock()
    mock_engine.id = {"name": cpi.STOCKFISH_UCI_NAME}
    mock_engine.options = create_fake_options()
    mock_engine.analyse.return_value = {"score": chess.engine.PovScore(chess.engine.Cp(100), chess.WHITE)} # no nodes!
    mock_popen.return_value = mock_engine
    
    session = cpi.InstrumentSession("dummy", cpi.InstrumentRole.SOURCE)
    session.start()
    
    board = chess.Board()
    board.clear_board()
    board.set_piece_at(chess.E1, chess.Piece(chess.KING, chess.WHITE))
    board.set_piece_at(chess.E8, chess.Piece(chess.KING, chess.BLACK))
    
    spec = get_valid_spec(board)
    res = session.acquire(spec, board)
    
    obs = res.data["observations"]
    assert obs[0]["reported_nodes"] is None

@patch('chessheat.cp_instrument.verify_executable')
@patch('chess.engine.SimpleEngine.popen_uci')
def test_mate_score(mock_popen, mock_verify):
    mock_verify.return_value = "/bin/stockfish"
    mock_engine = MagicMock()
    mock_engine.id = {"name": cpi.STOCKFISH_UCI_NAME}
    mock_engine.options = create_fake_options()
    mock_engine.analyse.return_value = {"score": chess.engine.PovScore(chess.engine.Mate(2), chess.WHITE)}
    mock_popen.return_value = mock_engine
    
    session = cpi.InstrumentSession("dummy", cpi.InstrumentRole.SOURCE)
    session.start()
    
    board = chess.Board()
    board.clear_board()
    board.set_piece_at(chess.E1, chess.Piece(chess.KING, chess.WHITE))
    board.set_piece_at(chess.E8, chess.Piece(chess.KING, chess.BLACK))
    
    spec = get_valid_spec(board)
    res = session.acquire(spec, board)
    
    obs = res.data["observations"]
    assert obs[0]["score_type"] == "mate"
    assert obs[0]["score_value"] == 2

@patch('chessheat.cp_instrument.verify_executable')
@patch('chess.engine.SimpleEngine.popen_uci')
def test_malformed_score(mock_popen, mock_verify):
    mock_verify.return_value = "/bin/stockfish"
    mock_engine = MagicMock()
    mock_engine.id = {"name": cpi.STOCKFISH_UCI_NAME}
    mock_engine.options = create_fake_options()
    mock_engine.analyse.return_value = {"score": None} # None score
    mock_popen.return_value = mock_engine
    
    session = cpi.InstrumentSession("dummy", cpi.InstrumentRole.SOURCE)
    session.start()
    
    board = chess.Board()
    board.clear_board()
    board.set_piece_at(chess.E1, chess.Piece(chess.KING, chess.WHITE))
    board.set_piece_at(chess.E8, chess.Piece(chess.KING, chess.BLACK))
    
    spec = get_valid_spec(board)
    with pytest.raises(cpi.ProtocolError, match="Score is not a PovScore"):
        session.acquire(spec, board)

@patch('chessheat.cp_instrument.verify_executable')
@patch('chess.engine.SimpleEngine.popen_uci')
def test_separate_processes(mock_popen, mock_verify):
    mock_verify.return_value = "/bin/stockfish"
    # Two separate sessions should call popen_uci independently
    session1 = cpi.InstrumentSession("dummy", cpi.InstrumentRole.SOURCE)
    session2 = cpi.InstrumentSession("dummy", cpi.InstrumentRole.TARGET)
    
    mock_engine1 = MagicMock()
    mock_engine1.id = {"name": cpi.STOCKFISH_UCI_NAME}
    mock_engine1.options = create_fake_options()
    
    mock_engine2 = MagicMock()
    mock_engine2.id = {"name": cpi.STOCKFISH_UCI_NAME}
    mock_engine2.options = create_fake_options()
    
    mock_popen.side_effect = [mock_engine1, mock_engine2]
    
    session1.start()
    session2.start()
    
    assert mock_popen.call_count == 2
    
@patch('chessheat.cp_instrument.verify_executable')
@patch('chess.engine.SimpleEngine.popen_uci')
def test_failed_child_produces_no_result(mock_popen, mock_verify):
    mock_verify.return_value = "/bin/stockfish"
    mock_engine = MagicMock()
    mock_engine.id = {"name": cpi.STOCKFISH_UCI_NAME}
    mock_engine.options = create_fake_options()
    
    def fake_analyse(board, limit, **kwargs):
        if board.move_stack[-1].uci() == "a2a3":
            raise Exception("Crash")
        return {"score": chess.engine.PovScore(chess.engine.Cp(100), chess.WHITE), "nodes": 123}
        
    mock_engine.analyse.side_effect = fake_analyse
    mock_popen.return_value = mock_engine
    
    session = cpi.InstrumentSession("dummy", cpi.InstrumentRole.SOURCE)
    session.start()
    
    board = chess.Board()
    spec = get_valid_spec(board)
    
    with pytest.raises(cpi.ProtocolError, match="Analysis failed"):
        session.acquire(spec, board)

