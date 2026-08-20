import pytest
import chess
import chess.pgn
import io
from chessheat.cp_root_population import (
    process_game, get_history_identity, get_selected_ply, get_conservative_transposition_group,
    is_eligible, RootPopulationError
)

def test_missing_game_url():
    game = chess.pgn.Game()
    res = process_game(game)
    assert res["error"] == "MISSING_CANONICAL_GAME_ID"

def test_variant_exclusion():
    game = chess.pgn.Game()
    game.headers["Site"] = "https://lichess.org/XYZ"
    game.headers["Variant"] = "Crazyhouse"
    res = process_game(game)
    assert res["error"] == "VARIANT_EXCLUDED"

def test_malformed_initial_state():
    game = chess.pgn.Game()
    game.headers["Site"] = "https://lichess.org/XYZ"
    game.headers["FEN"] = "invalid fen"
    res = process_game(game)
    assert res["error"] == "MALFORMED_INITIAL_STATE"

def test_no_rule_eligible_root():
    game = chess.pgn.Game()
    game.headers["Site"] = "https://lichess.org/XYZ"
    game.headers["FEN"] = "8/8/8/8/8/8/8/K7 w - - 0 1"
    res = process_game(game)
    assert res["error"] == "NO_RULE_ELIGIBLE_ROOT"

def test_successful_game_process():
    pgn_text = """[Event "test"]
[Site "https://lichess.org/ABC"]
[Result "1-0"]

1. e4 e5"""
    game = chess.pgn.read_game(io.StringIO(pgn_text))
    res = process_game(game)
    assert "error" not in res
    assert res["game_url"] == "https://lichess.org/ABC"
    assert res["eligible_ply_count"] > 0
    assert "root_identity" in res

def test_history_identity():
    id1 = get_history_identity(chess.STARTING_FEN, ["e2e4"])
    id2 = get_history_identity(chess.STARTING_FEN, ["e2e4"])
    assert id1 == id2
    
    id3 = get_history_identity(chess.STARTING_FEN, ["d2d4"])
    assert id1 != id3

def test_selected_ply_deterministic():
    ply1 = get_selected_ply("url1", [0, 1, 2])
    ply2 = get_selected_ply("url1", [0, 1, 2])
    assert ply1 == ply2

def test_conservative_key():
    board = chess.Board()
    k1 = get_conservative_transposition_group(board)
    k2 = get_conservative_transposition_group(board)
    assert k1 == k2

def test_is_eligible():
    board = chess.Board()
    assert is_eligible(board) == True
    board.clear()
    board.set_piece_at(chess.A1, chess.Piece(chess.KING, chess.WHITE))
    assert is_eligible(board) == False
