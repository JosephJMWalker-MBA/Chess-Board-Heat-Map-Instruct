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
    def __init__(self, engine_path: str = "stockfish", budget_nodes: int = 500000, threads: int = 1, hash_mb: int = 16, comparison_perspective: str = "white"):
        self.engine_path = engine_path
        self.budget_nodes = budget_nodes
        self.threads = threads
        self.hash_mb = hash_mb
        if comparison_perspective not in ("white", "black"):
            raise ValueError("comparison_perspective must be 'white' or 'black'")
        self.comparison_perspective = comparison_perspective
        self.engine = None
        self.engine_version = "Unknown"

    def __enter__(self):
        self.engine = chess.engine.SimpleEngine.popen_uci(self.engine_path)
        try:
            self.engine.configure({"Hash": self.hash_mb, "Threads": self.threads})
            # Try to get engine name/version
            self.engine_version = self.engine.id.get('name', 'Unknown')
        except Exception:
            self.engine.quit()
            raise
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.engine:
            self.engine.quit()

    def create_seal(self, manifest_path: str, protocol_path: str, output_dir: str) -> Dict[str, Any]:
        """Implement a serializable pre-execution seal tied to harness configuration."""
        import os, hashlib
        result = subprocess.run(["git", "status", "--porcelain"], capture_output=True, text=True)
        if result.returncode != 0:
            raise RuntimeError("Failed to check git status")
        is_clean = (result.stdout.strip() == "")
        if not is_clean:
            raise RuntimeError(f"Seal broken: Working tree is not clean.\n{result.stdout}")
            
        sha_result = subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True, text=True)
        if sha_result.returncode != 0:
            raise RuntimeError(f"Seal broken: Failed to resolve HEAD SHA.\n{sha_result.stderr}")
        commit_sha = sha_result.stdout.strip()
        
        if getattr(self, 'engine_version', 'Unknown') == 'Unknown':
            raise RuntimeError("Seal broken: Engine must be successfully initialized to obtain its true version.")
        
        # Hash harness itself for identity
        harness_hash = hashlib.sha256(open(__file__, "rb").read()).hexdigest()
        
        # Hash inputs
        def file_sha256(path: str) -> str:
            if not os.path.exists(path):
                raise RuntimeError(f"Seal broken: Required file missing: {path}")
            return hashlib.sha256(open(path, "rb").read()).hexdigest()
            
        manifest_hash = file_sha256(manifest_path)
        protocol_hash = file_sha256(protocol_path)
        
        # Ensure output directory exists
        os.makedirs(output_dir, exist_ok=True)
        
        return {
            "git_commit_sha": commit_sha,
            "working_tree_clean": is_clean,
            "harness_identity": harness_hash,
            "manifest_hash": manifest_hash,
            "protocol_hash": protocol_hash,
            "engine_path": self.engine_path,
            "engine_version": self.engine_version,
            "engine_threads": self.threads,
            "engine_hash_mb": self.hash_mb,
            "engine_node_budget": self.budget_nodes,
            "comparison_perspective": self.comparison_perspective,
            "output_directory_identity": os.path.abspath(output_dir)
        }

    def evaluate_move(self, board: chess.Board, move: chess.Move) -> Score:
        board.push(move)
        try:
            info = self.engine.analyse(board, chess.engine.Limit(nodes=self.budget_nodes))
            if self.comparison_perspective == "white":
                s = info["score"].white()
            else:
                s = info["score"].black()
                
            if s.is_mate():
                return Score(type='mate', value=s.mate(), perspective=self.comparison_perspective)
            else:
                return Score(type='cp', value=s.score(), perspective=self.comparison_perspective)
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
        bundle: Any = None,
        required_evidence_families: List[str] = None
    ) -> Dict[str, Any]:
        if required_evidence_families is None:
            required_evidence_families = []
            
        if "temporal" in required_evidence_families and not transition_evidence:
            raise ValueError("Preflight failed: Hypothesis requires temporal evidence, but none was provided.")
            
        if "bundle" in required_evidence_families and not bundle:
            raise ValueError("Preflight failed: Hypothesis requires bundle evidence, but none was provided.")
            
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

        from chessheat.temporal import extract_implicated_squares
        
        sq_pred = extract_implicated_squares(predecessor_sig)
        sq_succ = extract_implicated_squares(successor_sig)
        shared_squares = list(sq_pred & sq_succ)

        bundle_ev = None
        if bundle:
            import hashlib
            candidates_data = []
            for c in bundle.candidates:
                candidates_data.append({
                    "predecessor": str(c.structural_evidence.predecessor_signature),
                    "successor": str(c.structural_evidence.successor_signature),
                    "m11": c.structural_evidence.m_11,
                    "m10": c.structural_evidence.m_10,
                    "m01": c.structural_evidence.m_01,
                    "m00": c.structural_evidence.m_00,
                })
            
            # Deterministic canonical serialization + SHA-256
            import json
            canonical_str = json.dumps(candidates_data, sort_keys=True)
            bundle_id = hashlib.sha256(canonical_str.encode('utf-8')).hexdigest()
            
            bundle_ev = {
                "bundle_identity": bundle_id,
                "bundle_constituent_candidate_pairs": candidates_data
            }

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
            "bundle_evidence": bundle_ev
        }

    def compare_transpositions(self, initial_fen: str, moves_a: List[str], moves_b: List[str]) -> Dict[str, Any]:
        board_a = chess.Board(initial_fen)
        for move_san in moves_a:
            board_a.push_san(move_san)
            
        board_b = chess.Board(initial_fen)
        for move_san in moves_b:
            board_b.push_san(move_san)
            
        fen_a = board_a.fen()
        fen_b = board_b.fen()
        
        # Check structural equality
        from chessheat.validation.harness import extract_all_signatures
        geom_a = extract_all_signatures(board_a)
        geom_b = extract_all_signatures(board_b)
        
        legal_roots_a = set(board_a.legal_moves)
        legal_roots_b = set(board_b.legal_moves)
        
        from chessheat.temporal import build_temporal_ledger_from_pgn
        import chess as python_chess
        import chess.pgn as python_chess_pgn
        
        def make_pgn(moves: List[str], fen: str) -> str:
            game = python_chess_pgn.Game()
            game.setup(python_chess.Board(fen))
            node = game
            board = python_chess.Board(fen)
            for m in moves:
                move = board.parse_san(m)
                node = node.add_variation(move)
                board.push(move)
            return str(game)
            
        pgn_a = make_pgn(moves_a, initial_fen)
        pgn_b = make_pgn(moves_b, initial_fen)
        
        ledger_a = build_temporal_ledger_from_pgn(pgn_a)
        ledger_b = build_temporal_ledger_from_pgn(pgn_b)
        
        # Compare actual ledger events
        events_a = {str(e.event_identity): e for e in ledger_a.events}
        events_b = {str(e.event_identity): e for e in ledger_b.events}
        
        ledger_inequality_evidence = {}
        for ev_id, ev_a in events_a.items():
            ev_b = events_b.get(ev_id)
            if not ev_b:
                ledger_inequality_evidence[ev_id] = {"a": ev_a.active_intervals, "b": None}
            elif ev_a.active_intervals != ev_b.active_intervals:
                ledger_inequality_evidence[ev_id] = {"a": ev_a.active_intervals, "b": ev_b.active_intervals}
                
        for ev_id, ev_b in events_b.items():
            if ev_id not in events_a:
                ledger_inequality_evidence[ev_id] = {"a": None, "b": ev_b.active_intervals}
        
        return {
            "history_a": moves_a,
            "history_b": moves_b,
            "terminal_fen_a": fen_a,
            "terminal_fen_b": fen_b,
            "terminal_fen_equality": fen_a == fen_b,
            "geometry_equality": geom_a == geom_b,
            "legal_root_equality": legal_roots_a == legal_roots_b,
            "temporal_ledger_differences": ledger_inequality_evidence
        }
