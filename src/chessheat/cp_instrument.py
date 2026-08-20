import hashlib
import os
import copy
import chess
import chess.engine
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from enum import Enum

from .experiment import ExperimentSpec, ExperimentResult
from .semantics import SufficientPosition

STOCKFISH_UCI_NAME = "Stockfish 18"
STOCKFISH_BINARY_SHA256 = "ae4c93fa9676ca7750d0714342fd8a5b1d018000fc6e0f6cedf112067b5ef374"

SOURCE_INSTRUMENT_ID = "CP_SOURCE_SF18_50K_ISOLATED_V1"
SOURCE_NODES = 50000

TARGET_INSTRUMENT_ID = "CP_TARGET_SF18_250K_ISOLATED_V1"
TARGET_NODES = 250000

STATIC_UCI_CONFIG = {
    "Threads": 1,
    "Hash": 16,
    "Skill Level": 20,
    "UCI_LimitStrength": False,
    "UCI_ShowWDL": False,
    "SyzygyProbeLimit": 0,
    "SyzygyPath": "<empty>"
}

MANAGED_OPTIONS = {"MultiPV", "Ponder", "UCI_Chess960"}

class InstrumentRole(str, Enum):
    SOURCE = "SOURCE"
    TARGET = "TARGET"

class ProtocolError(Exception):
    pass

def verify_executable(executable_path: str) -> str:
    expanded = os.path.expanduser(executable_path)
    resolved = os.path.realpath(expanded)
    
    if not os.path.exists(resolved):
        raise ProtocolError(f"Executable does not exist: {resolved}")
    if not os.path.isfile(resolved):
        raise ProtocolError("Executable is not a regular file")
    if not os.access(resolved, os.X_OK):
        raise ProtocolError("Executable lacks execution permissions")
        
    with open(resolved, "rb") as f:
        digest = hashlib.sha256(f.read()).hexdigest()
        
    if digest != STOCKFISH_BINARY_SHA256:
        raise ProtocolError(f"Binary SHA mismatch. Expected {STOCKFISH_BINARY_SHA256}, got {digest}")
        
    return resolved

def serialize_option(opt: chess.engine.Option) -> dict:
    return {
        "name": opt.name,
        "type": opt.type,
        "default": opt.default,
        "min": opt.min,
        "max": opt.max,
        "var": opt.var,
        "managed": opt.is_managed()
    }

class InstrumentSession:
    def __init__(self, executable_path: str, role: InstrumentRole):
        self._executable_path = executable_path
        if not isinstance(role, InstrumentRole):
            raise ProtocolError(f"Invalid role: {role}")
            
        self._role = role
        self._instrument_id = SOURCE_INSTRUMENT_ID if role == InstrumentRole.SOURCE else TARGET_INSTRUMENT_ID
        self._nodes = SOURCE_NODES if role == InstrumentRole.SOURCE else TARGET_NODES
        self._engine = None
        self._resolved_path = None
        self._provenance = {}

    @property
    def role(self) -> InstrumentRole:
        return self._role

    @property
    def instrument_id(self) -> str:
        return self._instrument_id

    @property
    def nodes(self) -> int:
        return self._nodes

    def start(self):
        self._resolved_path = verify_executable(self._executable_path)
        
        try:
            engine = chess.engine.SimpleEngine.popen_uci(self._resolved_path)
        except Exception as e:
            raise ProtocolError(f"Failed to spawn engine: {e}")
            
        self._engine = engine
        
        try:
            # 8. require observed UCI name exactly: Stockfish 18
            if self._engine.id.get("name") != STOCKFISH_UCI_NAME:
                raise ProtocolError(f"Wrong UCI name. Expected {STOCKFISH_UCI_NAME}")

            # 9. calculate executable SHA-256 AGAIN from the resolved path
            post_spawn_sha = verify_executable(self._resolved_path)
            
            options = self._engine.options
            
            # Managed options enforcement
            for k in MANAGED_OPTIONS:
                if k not in options:
                    raise ProtocolError(f"Missing managed option: {k}")
                if not options[k].is_managed():
                    raise ProtocolError(f"Required managed option {k} is not managed by python-chess")
            
            # Unmanaged static options enforcement
            for k in STATIC_UCI_CONFIG:
                if k not in options:
                    raise ProtocolError(f"Missing static option: {k}")
                if options[k].is_managed():
                    raise ProtocolError(f"Static option {k} must not be managed")

            # EvalFile / EvalFileSmall
            for k in ["EvalFile", "EvalFileSmall"]:
                if k not in options:
                    raise ProtocolError(f"Missing network option: {k}")

            # Configure unmanaged static options ONLY
            try:
                self._engine.configure(STATIC_UCI_CONFIG)
            except Exception as e:
                raise ProtocolError(f"Configuration mismatch: {e}")

            # Serialize entire option surface
            serialized_options = {}
            for name, opt in options.items():
                serialized_options[name] = serialize_option(opt)
            
            # Sort for deterministic provenance
            sorted_opts = {k: serialized_options[k] for k in sorted(serialized_options)}

            self._provenance = {
                "producer": STOCKFISH_UCI_NAME,
                "pre_spawn_sha256": STOCKFISH_BINARY_SHA256,
                "post_spawn_sha256": STOCKFISH_BINARY_SHA256,
                "role": self.role.value,
                "instrument_id": self.instrument_id,
                "resolved_path": self._resolved_path,
                "static_config_applied": STATIC_UCI_CONFIG.copy(),
                "managed_semantics_enforced": list(MANAGED_OPTIONS),
                "eval_file_default": options["EvalFile"].default,
                "eval_file_small_default": options["EvalFileSmall"].default,
                "options_surface": sorted_opts
            }
        except ProtocolError:
            self.close()
            raise

    def acquire(self, spec: ExperimentSpec, root_board: chess.Board) -> ExperimentResult:
        if not self._engine:
            raise ProtocolError("Session not started")
            
        if spec.spec_version != 2:
            raise ProtocolError("spec_version must be 2")
        if spec.producer_identity != STOCKFISH_UCI_NAME:
            raise ProtocolError("producer_identity mismatch")
        if spec.comparison_perspective != ("white" if root_board.turn == chess.WHITE else "black"):
            raise ProtocolError("comparison_perspective mismatch")
            
        expected_budget = SOURCE_NODES if self.role == InstrumentRole.SOURCE else TARGET_NODES
        if spec.budget_config.get("nodes") != expected_budget:
            raise ProtocolError("budget_config nodes mismatch")
            
        if spec.instrument_config.get("instrument_id") != self.instrument_id:
            raise ProtocolError("instrument_config mismatch")
            
        if spec.sufficient_position.variant != "standard":
            raise ProtocolError("sufficient_position.variant must be standard")
            
        if root_board.chess960:
            raise ProtocolError("Chess960 is not permitted")

        sp = spec.sufficient_position
        if sp.board_arrangement_fen != root_board.board_fen() or \
           sp.side_to_move != ("w" if root_board.turn else "b") or \
           sp.castling_rights != root_board.castling_xfen() or \
           sp.en_passant_square != (chess.square_name(root_board.ep_square) if root_board.ep_square else "-") or \
           sp.halfmove_clock != root_board.halfmove_clock or \
           sp.fullmove_number != root_board.fullmove_number:
            raise ProtocolError("SufficientPosition derivable fields mismatch with root_board")
            
        # Verify candidate policy
        legal_moves = list(root_board.legal_moves)
        if not legal_moves:
            raise ProtocolError("Zero legal moves")
        sorted_moves = sorted(legal_moves, key=lambda m: m.uci())
        sorted_ucis = [m.uci() for m in sorted_moves]
        
        cp_ucis = spec.candidate_policy.get("ordered_legal_root_ucis")
        if cp_ucis != sorted_ucis:
            raise ProtocolError("ordered_legal_root_ucis does not exactly match canonical legal root moves")
        if spec.candidate_policy.get("required_search_count") != len(sorted_ucis):
            raise ProtocolError("required_search_count mismatch")
            
        observations = []
        
        try:
            for idx, move in enumerate(sorted_moves):
                child_board = root_board.copy(stack=True)
                child_board.push(move)
                
                game_token = object() # Fresh token
                
                result = self._engine.analyse(
                    child_board,
                    chess.engine.Limit(nodes=self.nodes),
                    game=game_token,
                    multipv=None,
                    root_moves=None
                )
                
                if type(result) is not dict:
                    raise ProtocolError("Expected single-PV result dict from analyse")
                if "score" not in result:
                    raise ProtocolError("Missing score")
                
                pov_score = result["score"]
                if not isinstance(pov_score, chess.engine.PovScore):
                    raise ProtocolError("Score is not a PovScore")
                    
                root_score = pov_score.pov(root_board.turn)
                
                if root_score.is_mate():
                    if root_score.mate() is None:
                        raise ProtocolError("Malformed mate score")
                    s_type = "mate"
                    s_val = root_score.mate()
                else:
                    if root_score.score() is None:
                        raise ProtocolError("Malformed cp score")
                    s_type = "cp"
                    s_val = root_score.score()
                    
                reported_nodes = result.get("nodes")
                if reported_nodes is not None and not isinstance(reported_nodes, int):
                    raise ProtocolError("Malformed reported nodes")
                if reported_nodes is not None and reported_nodes < 0:
                    raise ProtocolError("Negative reported nodes")
                    
                obs = {
                    "canonical_acquisition_index": idx,
                    "root_move_uci": move.uci(),
                    "child_fen": child_board.fen(shredder=False, en_passant="fen"),
                    "parent_history_identity": sp.history_identity,
                    "child_derivation": "child_history derives from parent + root_move",
                    "requested_nodes": self.nodes,
                    "reported_nodes": reported_nodes,
                    "score_type": s_type,
                    "score_value": s_val,
                    "perspective": "white" if root_board.turn == chess.WHITE else "black",
                    "isolation_sequence_index": idx
                }
                observations.append(obs)
        except ProtocolError:
            raise
        except Exception as e:
            raise ProtocolError(f"Analysis failed: {e}")
            
        data = {
            "spec_digest": spec.spec_digest(),
            "instrument_role": self.role.value,
            "instrument_id": self.instrument_id,
            "producer_uci_name": self._provenance["producer"],
            "resolved_executable_path": self._provenance["resolved_path"],
            "pre_spawn_sha256": self._provenance["pre_spawn_sha256"],
            "post_spawn_sha256": self._provenance["post_spawn_sha256"],
            "options_surface": self._provenance["options_surface"],
            "static_config_applied": self._provenance["static_config_applied"],
            "managed_semantics_enforced": self._provenance["managed_semantics_enforced"],
            "eval_file_default": self._provenance["eval_file_default"],
            "eval_file_small_default": self._provenance["eval_file_small_default"],
            "comparison_perspective": "white" if root_board.turn == chess.WHITE else "black",
            "canonical_acquisition_order": sorted_ucis,
            "root_sufficient_position": sp.model_dump(),
            "observations": observations
        }
        
        return ExperimentResult.create(spec_digest=spec.spec_digest(), data=data)

    def close(self):
        if self._engine:
            self._engine.quit()
            self._engine = None

