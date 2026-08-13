import chess
import chess.engine
import subprocess
import typing
from typing import Optional, List, Dict, Any, Set, Tuple

from chessheat.consequence import compute_regrets
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
        try:
            self.engine.configure({"Hash": 16, "Threads": 1})
        except Exception:
            self.engine.quit()
            raise
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.engine:
            self.engine.quit()

    @staticmethod
    def create_seal(manifest_hash: str, protocol_hash: str, engine_path: str, engine_version: str, threads: int, hash_mb: int, nodes: int, comparison_perspective: str, output_dir: str) -> Dict[str, Any]:
        """Implement a serializable pre-execution seal."""
        result = subprocess.run(["git", "status", "--porcelain"], capture_output=True, text=True)
        if result.returncode != 0:
            raise RuntimeError("Failed to check git status")
        is_clean = (result.stdout.strip() == "")
        if not is_clean:
            raise RuntimeError(f"Seal broken: Working tree is not clean.\n{result.stdout}")
            
        sha_result = subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True, text=True)
        commit_sha = sha_result.stdout.strip()
        
        return {
            "git_commit_sha": commit_sha,
            "working_tree_clean": is_clean,
            "harness_identity": "ValidationHarness_v2",
            "manifest_hash": manifest_hash,
            "protocol_hash": protocol_hash,
            "engine_path": engine_path,
            "engine_version": engine_version,
            "engine_threads": threads,
            "engine_hash_mb": hash_mb,
            "engine_node_budget": nodes,
            "comparison_perspective": comparison_perspective,
            "output_directory_identity": output_dir
        }

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

    @staticmethod
    def preflight_fixture(fen: str, played_move_san: str, predecessor_sig: Any, successor_sig: Any):
        try:
            board = chess.Board(fen)
            if not board.is_valid():
                raise ValueError(f"Preflight failed: FEN {fen} is not a valid chess state.")
        except ValueError:
            raise ValueError(f"Preflight failed: FEN {fen} is not a valid chess state.")
            
        try:
            played_move = board.parse_san(played_move_san)
        except ValueError:
            raise ValueError(f"Preflight failed: Played move {played_move_san} is not legal in this FEN.")
            
        legal_moves = list(board.legal_moves)
        current_sigs = extract_all_signatures(board)
        
        m_11, m_10, m_01, m_00 = [], [], [], []
        
        for m in legal_moves:
            m_san = board.san(m)
            
            board.push(m)
            next_sigs = extract_all_signatures(board)
            board.pop()
            
            e_removed = predecessor_sig in (current_sigs - next_sigs)
            f_born = successor_sig in (next_sigs - current_sigs)
            
            if e_removed and f_born: m_11.append(m_san)
            elif e_removed and not f_born: m_10.append(m_san)
            elif not e_removed and f_born: m_01.append(m_san)
            else: m_00.append(m_san)
            
        if predecessor_sig not in current_sigs:
            raise ValueError(f"Preflight failed: Predecessor signature {predecessor_sig} not present in root.")
            
        # Successor signature f should technically be present after played move, but D_t and B_t check is implied by partition structure.
        # Wait, the prompt says "proof e in D_t; proof f in B_t; proof played move in M_11".
        # D_t = signatures that disappear. B_t = signatures that appear.
        if played_move_san not in m_11:
            raise ValueError(f"Preflight failed: Played move {played_move_san} does not belong to M_11 (it does not simultaneously remove e and create f).")
            
        total_partition_size = len(m_11) + len(m_10) + len(m_01) + len(m_00)
        if total_partition_size != len(legal_moves):
            raise ValueError(f"Preflight failed: Partition sizes ({total_partition_size}) do not match legal move count ({len(legal_moves)}).")
            
        return m_11, m_10, m_01, m_00

    def process_position(
        self, 
        fen: str, 
        played_move_san: str, 
        predecessor_sig: Any, 
        successor_sig: Any,
        transition_evidence: Any = None,
        bundle: Any = None
    ) -> Dict[str, Any]:
        # Engine-free preflight before doing any expensive engine work
        m_11, m_10, m_01, m_00 = self.preflight_fixture(fen, played_move_san, predecessor_sig, successor_sig)
        
        board = chess.Board(fen)
        legal_moves = list(board.legal_moves)
        
        scores = {}
        
        for m in legal_moves:
            m_san = board.san(m)
            scores[m_san] = self.evaluate_move(board, m)
            
        regrets = compute_regrets(scores)
        
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

        def get_squares(sig):
            if hasattr(sig, "implicated_squares"):
                return sig.implicated_squares()
            if hasattr(sig, "source_square") and hasattr(sig, "target_square"):
                return {sig.source_square, sig.target_square}
            return set()
            
        shared_squares = list(get_squares(predecessor_sig) & get_squares(successor_sig))

        return {
            "fen": fen,
            "played_move": played_move_san,
            "predecessor": str(predecessor_sig),
            "successor": str(successor_sig),
            "legal_root_count": len(legal_moves),
            "partitions": {
                "11": summarize_partition(m_11),
                "10": summarize_partition(m_10),
                "01": summarize_partition(m_01),
                "00": summarize_partition(m_00),
            },
            "raw_scores": {m: {"type": s.type, "value": s.value} for m, s in scores.items()},
            "regrets": {m: {"type": r.type, "value": r.value} for m, r in regrets.items()},
            "temporal_evidence": {
                "spatial_overlap": transition_evidence.spatial_overlap if transition_evidence else None,
                "observed_age_of_removed_episode": transition_evidence.observed_age_of_removed_episode if transition_evidence else None,
                "observed_duration_of_born_episode": transition_evidence.observed_duration_of_born_episode if transition_evidence else None,
                "is_removed_left_censored": transition_evidence.is_removed_left_censored if transition_evidence else None,
                "is_born_right_censored": transition_evidence.is_born_right_censored if transition_evidence else None,
                "is_born_reappearance": transition_evidence.is_born_reappearance if transition_evidence else None,
                "p_b_given_d": transition_evidence.p_b_given_d if transition_evidence else None,
                "p_b_given_not_d": transition_evidence.p_b_given_not_d if transition_evidence else None,
                "delta_assoc": transition_evidence.delta_assoc if transition_evidence else None,
                "shared_squares": shared_squares,
                "exact_support_partition_equality": (
                    set(transition_evidence.m_11) == set(m_11) and 
                    set(transition_evidence.m_10) == set(m_10) and 
                    set(transition_evidence.m_01) == set(m_01) and 
                    set(transition_evidence.m_00) == set(m_00)
                ) if transition_evidence else None
            },
            "bundle_evidence": {
                "bundle_identity": hash(frozenset(bundle.constituent_events)) if bundle else None,
                "bundle_constituent_candidate_pairs": [{"e": str(e), "f": str(f)} for e in bundle.constituent_events for f in bundle.constituent_events] if bundle else None,
            },
            "paired_history_evidence": None # Placeholder for terminal-state vs current-state comparison
        }
