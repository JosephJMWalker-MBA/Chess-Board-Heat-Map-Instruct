import chess
import chess.pgn
import hashlib
import json
from typing import Dict, Any, List, Optional, Tuple
from chessheat.semantics import SufficientPosition

ROOT_SELECTOR_VERSION = "ChessHeat-root-v1"
HISTORY_IDENTITY_VERSION = "CHESSHEAT_HISTORY_IDENTITY_V1"
TRANSPOSITION_GROUP_VERSION = "CP_TRANSPOSE_GROUP_S0_RULESTATE_V1"
ROOT_MANIFEST_SCHEMA_V2 = "CP_ROOT_POPULATION_JULY_2026_MANIFEST_V2"
DUPLICATE_RESOLUTION_VERSION = "CP_EXACT_DUPLICATE_GAMEURL_LEX_V1"

class RootPopulationError(Exception):
    pass

class ReconstructRootError(Exception):
    pass

def canonical_json_digest(payload: Dict[str, Any]) -> str:
    canonical_json = json.dumps(payload, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(canonical_json.encode('utf-8')).hexdigest()

def get_history_identity(initial_fen: str, move_prefix_ucis: List[str]) -> str:
    payload = {
        "version": HISTORY_IDENTITY_VERSION,
        "declared_initial_fen": initial_fen,
        "mainline_uci_prefix": move_prefix_ucis
    }
    return canonical_json_digest(payload)

def get_selected_ply(game_url: str, eligible_plies: List[int]) -> int:
    if not eligible_plies:
        raise RootPopulationError("NO_RULE_ELIGIBLE_ROOT")
    
    h_input = f"{ROOT_SELECTOR_VERSION}|{game_url}".encode("utf-8")
    h = hashlib.sha256(h_input).digest()
    j = int.from_bytes(h, byteorder='big') % len(eligible_plies)
    return eligible_plies[j]

def get_conservative_transposition_group(board: chess.Board) -> str:
    parts = [
        board.board_fen(),
        "w" if board.turn == chess.WHITE else "b",
        board.castling_xfen(),
        chess.square_name(board.ep_square) if board.ep_square is not None else "None"
    ]
    payload = {
        "version": TRANSPOSITION_GROUP_VERSION,
        "components": parts
    }
    return canonical_json_digest(payload)

def is_eligible(board: chess.Board) -> bool:
    if not board.is_valid():
        return False
    if board.is_variant_end():
        return False
    if board.is_game_over(claim_draw=False):
        return False
    if len(list(board.legal_moves)) < 2:
        return False
    return True

def process_game(game: chess.pgn.Game) -> Dict[str, Any]:
    game_url = game.headers.get("GameURL", "").strip()
    if not game_url or game_url == "?":
        return {"error": "MISSING_CANONICAL_GAME_ID"}
        
    variant = game.headers.get("Variant", "Standard")
    if variant.lower() != "standard":
        return {"error": "VARIANT_EXCLUDED", "variant": variant}
        
    initial_fen = game.headers.get("FEN")
    
    try:
        if initial_fen:
            board = chess.Board(initial_fen)
        else:
            if game.headers.get("SetUp", "0") == "1":
                return {"error": "MALFORMED_INITIAL_STATE"}
            board = chess.Board()
            initial_fen = chess.STARTING_FEN
    except ValueError:
        return {"error": "MALFORMED_INITIAL_STATE"}

    initial_fen_canon = board.fen(en_passant="fen")

    eligible_plies = []
    current_board = board.copy(stack=True)
    if is_eligible(current_board):
        eligible_plies.append(0)
        
    ply = 0
    move_ucis = []
    
    # Must reject if game.errors is non-empty
    if game.errors:
        return {"error": "MALFORMED_REPLAY"}

    for move in game.mainline_moves():
        if move not in current_board.legal_moves:
            return {"error": "MALFORMED_REPLAY"}
        try:
            current_board.push(move)
        except Exception:
            return {"error": "MALFORMED_REPLAY"}
            
        ply += 1
        move_ucis.append(move.uci())
        if is_eligible(current_board):
            eligible_plies.append(ply)

    if not eligible_plies:
        return {"error": "NO_RULE_ELIGIBLE_ROOT"}
        
    selected_ply = get_selected_ply(game_url, eligible_plies)
    
    selected_board = board.copy(stack=True)
    selected_ucis = move_ucis[:selected_ply]
    for m_uci in selected_ucis:
        selected_board.push(chess.Move.from_uci(m_uci))
        
    hist_id = get_history_identity(initial_fen_canon, selected_ucis)
    
    suff = SufficientPosition(
        board_arrangement_fen=selected_board.board_fen(),
        side_to_move="w" if selected_board.turn == chess.WHITE else "b",
        castling_rights=selected_board.castling_xfen(),
        en_passant_square=chess.square_name(selected_board.ep_square) if selected_board.ep_square is not None else None,
        halfmove_clock=selected_board.halfmove_clock,
        fullmove_number=selected_board.fullmove_number,
        history_available=True,
        history_identity=hist_id,
        variant="standard"
    )
    
    canonical_suff_digest = canonical_json_digest(suff.model_dump())
    trans_group = get_conservative_transposition_group(selected_board)
    
    return {
        "success": True,
        "game_url": game_url,
        "site": game.headers.get("Site", ""),
        "declared_initial_fen": initial_fen_canon,
        "mainline_uci_prefix": selected_ucis,
        "eligible_ply_count": len(eligible_plies),
        "selected_ply": selected_ply,
        "sufficient_position": suff.model_dump(),
        "root_identity": canonical_suff_digest,
        "transposition_group": trans_group,
        "history_identity": hist_id
    }

def reconstruct_root_board(record: Dict[str, Any]) -> chess.Board:
    initial_fen = record["declared_initial_fen"]
    ucis = record["mainline_uci_prefix"]
    
    board = chess.Board(initial_fen)
    for uci in ucis:
        move = chess.Move.from_uci(uci)
        if move not in board.legal_moves:
            raise ReconstructRootError("Illegal move in prefix")
        board.push(move)
        
    if len(board.move_stack) != record["selected_ply"]:
        raise ReconstructRootError("Move stack length does not match selected_ply")
        
    hist_id = get_history_identity(initial_fen, ucis)
    
    suff = SufficientPosition(
        board_arrangement_fen=board.board_fen(),
        side_to_move="w" if board.turn == chess.WHITE else "b",
        castling_rights=board.castling_xfen(),
        en_passant_square=chess.square_name(board.ep_square) if board.ep_square is not None else None,
        halfmove_clock=board.halfmove_clock,
        fullmove_number=board.fullmove_number,
        history_available=True,
        history_identity=hist_id,
        variant="standard"
    )
    
    canonical_suff_digest = canonical_json_digest(suff.model_dump())
    
    if hist_id != record["history_identity"]:
        raise ReconstructRootError("history_identity mismatch")
    if canonical_suff_digest != record["root_identity"]:
        raise ReconstructRootError("root_identity mismatch")
    if suff.model_dump() != record["sufficient_position"]:
        raise ReconstructRootError("sufficient_position mismatch")
        
    return board
