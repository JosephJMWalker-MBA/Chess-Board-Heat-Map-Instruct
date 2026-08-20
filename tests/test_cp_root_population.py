import pytest
import chess
import chess.pgn
import io
from chessheat.cp_root_population import process_game, reconstruct_root_board

def make_game(fen=None, moves=None, site="https://lichess.org/dummy", setup="0"):
    pgn_str = f'[Event "?"]\n[Site "site"]\n[GameURL "{site}"]\n'
    if fen:
        pgn_str += f'[FEN "{fen}"]\n'
    if setup:
        pgn_str += f'[SetUp "{setup}"]\n'
    pgn_str += '\n'
    if moves:
        pgn_str += moves
    return chess.pgn.read_game(io.StringIO(pgn_str))

def test_missing_game_url():
    game = make_game(site="?")
    res = process_game(game)
    assert res["error"] == "MISSING_CANONICAL_GAME_ID"
    
def test_variant():
    pgn_str = '[Event "?"]\n[Site "site"]\n[GameURL "url"]\n[Variant "Chess960"]\n\n'
    game = chess.pgn.read_game(io.StringIO(pgn_str))
    res = process_game(game)
    assert res["error"] == "VARIANT_EXCLUDED"

def test_setup_no_fen():
    game = make_game(setup="1")
    res = process_game(game)
    assert res["error"] == "MALFORMED_INITIAL_STATE"

def test_game_errors():
    pgn_str = '[Event "?"]\n[Site "site"]\n[GameURL "url"]\n\n1. e4 e5 2. e6'
    game = chess.pgn.read_game(io.StringIO(pgn_str))
    res = process_game(game)
    assert res["error"] == "MALFORMED_REPLAY"

def test_illegal_move():
    # E.g. king into check
    pgn_str = '[Event "?"]\n[Site "site"]\n[GameURL "url"]\n\n1. f3 e6 2. g4 Qh4+ 3. Nc3'
    game = chess.pgn.read_game(io.StringIO(pgn_str))
    res = process_game(game)
    assert res["error"] == "MALFORMED_REPLAY"

def test_zero_eligible():
    pgn_str = '[Event "?"]\n[Site "site"]\n[GameURL "url"]\n[FEN "8/8/8/8/8/8/8/K7 w - - 0 1"]\n[SetUp "1"]\n\n'
    game = chess.pgn.read_game(io.StringIO(pgn_str))
    res = process_game(game)
    assert res["error"] == "NO_RULE_ELIGIBLE_ROOT"

def test_reconstruction():
    game = make_game(site="url1", moves="1. e4 e5 2. Nf3 Nc6")
    res = process_game(game)
    assert res["success"]
    
    board = reconstruct_root_board(res)
    assert len(board.move_stack) == res["selected_ply"]
    
    # Check history identity and full identity
    assert board.fen(en_passant="fen").split(" ")[0] == res["sufficient_position"]["board_arrangement_fen"]
