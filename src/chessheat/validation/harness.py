import chess
import chess.engine
import subprocess
import typing
from typing import Optional, List, Dict, Any, Set, Tuple

from chessheat.engine import Score

def extract_all_signatures(board: chess.Board) -> Set[Any]:
    from chessheat.geometry import extract_geometry
    geom = extract_geometry(board)
    sigs = set()
    for a in geom.attacks: sigs.add(a)
    for d in geom.defenses: sigs.add(d)
    for r in geom.rays: sigs.add(r)
    for m in geom.mobility:
        for dest in m.legal_destinations:
            sigs.add((m.piece, dest))
    return sigs

class ValidationHarness:
    def __init__(self, engine_path: str = "stockfish", budget_nodes: int = 500000):
        self.engine_path = engine_path
        self.budget_nodes = budget_nodes
        self.engine = None

    def __enter__(self):
        self.engine = chess.engine.SimpleEngine.popen_uci(self.engine_path)
        self.engine.configure({"Hash": 16, "Threads": 1})
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.engine:
            self.engine.quit()

    @staticmethod
    def assert_seal():
        """Ensure git status --porcelain is empty."""
        result = subprocess.run(["git", "status", "--porcelain"], capture_output=True, text=True)
        if result.returncode != 0:
            raise RuntimeError("Failed to check git status")
        if result.stdout.strip() != "":
            raise RuntimeError(f"Seal broken: Working tree is not clean.\n{result.stdout}")

    def evaluate_move(self, board: chess.Board, move: chess.Move) -> Score:
        board.push(move)
        try:
            info = self.engine.analyse(board, chess.engine.Limit(nodes=self.budget_nodes))
            played_color = not board.turn
            if played_color == chess.WHITE:
                s = info["score"].white()
            else:
                s = info["score"].black()
                
            if s.is_mate():
                return Score(type='mate', value=s.mate(), perspective='white' if played_color == chess.WHITE else 'black')
            else:
                return Score(type='cp', value=s.score(), perspective='white' if played_color == chess.WHITE else 'black')
        finally:
            board.pop()

    def calculate_consequence(self, scores: Dict[str, Score]) -> Dict[str, Score]:
        cp_scores = [s.value for s in scores.values() if s.type == 'cp']
        
        if cp_scores:
            e_star = max(cp_scores)
        else:
            e_star = None

        regrets = {}
        for m_san, s in scores.items():
            if s.type == 'mate':
                regrets[m_san] = s
            else:
                if e_star is None:
                    raise RuntimeError("No CP scores found but processing a CP move.")
                r = e_star - s.value
                if r < 0:
                    raise ValueError(f"Regret invariant violated! R(m)={r} < 0 for {m_san}")
                regrets[m_san] = Score(type='cp', value=r, perspective=s.perspective)
        
        return regrets

    def process_position(self, fen: str, predecessor_sig: Any, successor_sig: Any) -> Dict[str, Any]:
        board = chess.Board(fen)
        legal_moves = list(board.legal_moves)
        
        current_sigs = extract_all_signatures(board)
        
        m_11, m_10, m_01, m_00 = [], [], [], []
        scores = {}
        
        for m in legal_moves:
            m_san = board.san(m)
            scores[m_san] = self.evaluate_move(board, m)
            
            board.push(m)
            next_sigs = extract_all_signatures(board)
            board.pop()
            
            e_removed = predecessor_sig in (current_sigs - next_sigs)
            f_born = successor_sig in (next_sigs - current_sigs)
            
            if e_removed and f_born: m_11.append(m_san)
            elif e_removed and not f_born: m_10.append(m_san)
            elif not e_removed and f_born: m_01.append(m_san)
            else: m_00.append(m_san)
            
        assert len(m_11) + len(m_10) + len(m_01) + len(m_00) == len(legal_moves)
        
        regrets = self.calculate_consequence(scores)
        
        def summarize_partition(moves: List[str]):
            cp_count = sum(1 for m in moves if regrets[m].type == 'cp')
            mate_count = sum(1 for m in moves if regrets[m].type == 'mate')
            
            cprs = [regrets[m].value for m in moves if regrets[m].type == 'cp']
            if cprs:
                cprs.sort()
                n = len(cprs)
                median_cp = float(cprs[n//2] if n % 2 != 0 else (cprs[n//2 - 1] + cprs[n//2]) / 2)
            else:
                median_cp = None
                
            return {
                "moves": moves,
                "cp_count": cp_count,
                "mate_count": mate_count,
                "median_cp_regret": median_cp
            }

        return {
            "fen": fen,
            "predecessor": str(predecessor_sig),
            "successor": str(successor_sig),
            "partitions": {
                "11": summarize_partition(m_11),
                "10": summarize_partition(m_10),
                "01": summarize_partition(m_01),
                "00": summarize_partition(m_00),
            },
            "raw_scores": {m: {"type": s.type, "value": s.value} for m, s in scores.items()},
            "regrets": {m: {"type": r.type, "value": r.value} for m, r in regrets.items()}
        }
