import chess
import chess.engine
import asyncio
from typing import Optional, List, Dict, Any, Tuple
from abc import ABC, abstractmethod

from .models import AnalysisRecord, MoveObservation, Score, PlyObservation, SquareEffectRole

class EngineAdapter(ABC):
    @abstractmethod
    def get_name(self) -> str:
        pass

    @abstractmethod
    def get_options(self) -> Dict[str, Any]:
        pass

    @abstractmethod
    def analyze_position(self, board: chess.Board, budget_type: str, budget_value: int) -> dict:
        """Returns a dict containing 'score' (pov Score obj) and 'pv' (list of uci moves)"""
        pass

    @abstractmethod
    def close(self):
        pass

class StockfishAdapter(EngineAdapter):
    def __init__(self, stockfish_path: str, options: Optional[Dict[str, Any]] = None):
        self.engine = chess.engine.SimpleEngine.popen_uci(stockfish_path)
        self.options = options or {"Threads": 1, "Hash": 16}
        try:
            self.engine.configure(self.options)
        except Exception:
            self.engine.quit()
            raise

    def get_name(self) -> str:
        return self.engine.id.get("name", "Stockfish")

    def get_options(self) -> Dict[str, Any]:
        return self.options

    def analyze_position(self, board: chess.Board, budget_type: str, budget_value: int) -> dict:
        limit_args = {}
        if budget_type == "nodes":
            limit_args["nodes"] = budget_value
        elif budget_type == "depth":
            limit_args["depth"] = budget_value
        elif budget_type == "time":
            limit_args["time"] = budget_value / 1000.0
        else:
            limit_args["nodes"] = budget_value # fallback

        limit = chess.engine.Limit(**limit_args)
        result = self.engine.analyse(board, limit)

        # We must preserve the score from the root perspective.
        # But this function just returns the raw pov score of the side to move for the given board.
        # We'll normalize it in the main harness.
        return {
            "score": result["score"], # this is a PovScore
            "pv": [move.uci() for move in result.get("pv", [])]
        }

    def close(self):
        self.engine.quit()

def _convert_pov_score(pov_score: chess.engine.PovScore, perspective: chess.Color) -> Score:
    """Convert chess.engine.PovScore to our Score model from the specified perspective."""
    score = pov_score.pov(perspective)
    if score.is_mate():
        return Score(type="mate", value=score.mate(), perspective="white" if perspective == chess.WHITE else "black")
    else:
        return Score(type="cp", value=score.score(), perspective="white" if perspective == chess.WHITE else "black")

def analyze(fen: str, adapter: EngineAdapter, budget_type: str, budget_value: int, comparison_perspective: Optional[str] = None, candidate_policy: Optional[Dict[str, Any]] = None) -> AnalysisRecord:
    board = chess.Board(fen)
    if not board.is_valid():
        raise ValueError("Invalid FEN position")

    root_color = board.turn
    root_side_str = "white" if root_color == chess.WHITE else "black"

    comp_color = root_color
    if comparison_perspective:
        comp_color = chess.WHITE if comparison_perspective == "white" else chess.BLACK
    comp_side_str = "white" if comp_color == chess.WHITE else "black"

    # Baseline evaluation
    baseline_result = adapter.analyze_position(board, budget_type, budget_value)
    baseline_score = _convert_pov_score(baseline_result["score"], comp_color)

    move_observations = []

    for move in board.legal_moves:
        is_capture = board.is_capture(move)
        is_en_passant = board.is_en_passant(move)

        captured_square = None
        if is_capture:
            if is_en_passant:
                # If en passant, the captured pawn is on the rank of the origin square, file of destination
                captured_square = chess.square_name(chess.square(chess.square_file(move.to_square), chess.square_rank(move.from_square)))
            else:
                captured_square = chess.square_name(move.to_square)

        is_castling = board.is_castling(move)

        san = board.san(move)

        # Apply move
        board.push(move)
        resulting_fen = board.fen()

        # Analyze resulting position
        result = adapter.analyze_position(board, budget_type, budget_value)
        move_score = _convert_pov_score(result["score"], comp_color)

        board.pop()

        # Parse PV
        parsed_pv = []
        current_board = board.copy()

        # Ply 1 is the root move
        cap_sq = captured_square
        r = [SquareEffectRole.ORIGIN, SquareEffectRole.DESTINATION]
        if cap_sq: r.append(SquareEffectRole.CAPTURE)

        parsed_pv.append(PlyObservation(
            ply_number=1,
            uci=move.uci(),
            origin=chess.square_name(move.from_square),
            destination=chess.square_name(move.to_square),
            capture=cap_sq,
            roles=r
        ))
        current_board.push(move)

        pv_uci = result.get("pv", [])

        # In multi-pv responses from Stockfish via python-chess, the first move in the PV list
        # is the root move itself. We must avoid duplicating it since we manually inserted the
        # root move at ply_number=1 above.
        if pv_uci and pv_uci[0] == move.uci():
            pv_uci = pv_uci[1:]

        for i, move_uci in enumerate(pv_uci):
            ply_num = i + 2
            try:
                m = chess.Move.from_uci(move_uci)
                is_cap = current_board.is_capture(m)
                is_ep = current_board.is_en_passant(m)
                c_sq = None
                if is_cap:
                    if is_ep:
                        c_sq = chess.square_name(chess.square(chess.square_file(m.to_square), chess.square_rank(m.from_square)))
                    else:
                        c_sq = chess.square_name(m.to_square)

                r2 = [SquareEffectRole.ORIGIN, SquareEffectRole.DESTINATION]
                if c_sq: r2.append(SquareEffectRole.CAPTURE)

                parsed_pv.append(PlyObservation(
                    ply_number=ply_num,
                    uci=move_uci,
                    origin=chess.square_name(m.from_square),
                    destination=chess.square_name(m.to_square),
                    capture=c_sq,
                    roles=r2
                ))
                current_board.push(m)
            except Exception:
                break

        obs = MoveObservation(
            uci=move.uci(),
            san=san,
            origin_square=chess.square_name(move.from_square),
            destination_square=chess.square_name(move.to_square),
            is_capture=is_capture,
            captured_square=captured_square,
            promotion=chess.piece_symbol(move.promotion).upper() if move.promotion else None,
            is_castling=is_castling,
            is_en_passant=is_en_passant,
            resulting_fen=resulting_fen,
            score=move_score,
            principal_variation=result.get("pv"),
            parsed_pv=parsed_pv
        )
        move_observations.append(obs)

    return AnalysisRecord(
        fen=fen,
        root_side=root_side_str,
        comparison_perspective=comp_side_str,
        engine_name=adapter.get_name(),
        engine_options=adapter.get_options(),
        candidate_policy=candidate_policy or {},
        search_budget_type=budget_type,
        search_budget_value=budget_value,
        baseline_observation=baseline_score,
        move_observations=move_observations
    )
