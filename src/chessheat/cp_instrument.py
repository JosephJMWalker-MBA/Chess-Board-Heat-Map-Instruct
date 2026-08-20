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

@dataclass(frozen=True)
class ExecutableIdentity:
    resolved_path: str
    sha256: str

def verify_executable(executable_path: str) -> ExecutableIdentity:
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
        
    return ExecutableIdentity(resolved_path=resolved, sha256=digest)

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

def get_canonical_instrument_config(role: InstrumentRole) -> dict:
    return {
        "instrument_id": SOURCE_INSTRUMENT_ID if role == InstrumentRole.SOURCE else TARGET_INSTRUMENT_ID,
        "producer_identity": STOCKFISH_UCI_NAME,
        "binary_sha256": STOCKFISH_BINARY_SHA256,
        "Threads": 1,
        "Hash": 16,
        "Ponder": False,
        "MultiPV": 1,
        "Skill Level": 20,
        "UCI_LimitStrength": False,
        "UCI_Chess960": False,
        "UCI_ShowWDL": False,
        "SyzygyProbeLimit": 0,
        "tablebase_policy": "NO_EXTERNAL_TABLEBASE",
        "network_policy": "BINARY_DEFAULT_NNUE",
        "reset_policy": "FRESH_GAME_TOKEN_PER_CHILD",
        "process_policy": "ONE_LONG_LIVED_PROCESS_PER_ROLE"
    }

def get_canonical_budget_config(role: InstrumentRole) -> dict:
    return {
        "type": "nodes",
        "value": SOURCE_NODES if role == InstrumentRole.SOURCE else TARGET_NODES
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
        self._pre_identity = None
        self._post_identity = None
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
        if self._engine is not None:
            raise ProtocolError("Session already started")
            
        self._pre_identity = verify_executable(self._executable_path)
        
        try:
            engine = chess.engine.SimpleEngine.popen_uci(self._pre_identity.resolved_path)
        except Exception as e:
            raise ProtocolError(f"Failed to spawn engine: {e}")
            
        self._engine = engine
        
        try:
            if self._engine.id.get("name") != STOCKFISH_UCI_NAME:
                raise ProtocolError(f"Wrong UCI name. Expected {STOCKFISH_UCI_NAME}")

            self._post_identity = verify_executable(self._pre_identity.resolved_path)
            
            if self._pre_identity.resolved_path != self._post_identity.resolved_path:
                raise ProtocolError("Resolved path changed during spawn")
            if self._pre_identity.sha256 != self._post_identity.sha256:
                raise ProtocolError("Executable digest mutated during spawn")
                
            options = self._engine.options
            
            # Managed options enforcement
            for k in MANAGED_OPTIONS:
                if k not in options:
                    raise ProtocolError(f"Missing managed option: {k}")
                if not options[k].is_managed():
                    raise ProtocolError(f"Required managed option {k} is not managed by python-chess")
            
            # Unmanaged static options enforcement and parseability
            for k, expected_val in STATIC_UCI_CONFIG.items():
                if k not in options:
                    raise ProtocolError(f"Missing static option: {k}")
                if options[k].is_managed():
                    raise ProtocolError(f"Static option {k} must not be managed")
                try:
                    options[k].parse(expected_val)
                except Exception as e:
                    raise ProtocolError(f"Static option {k} rejects configured value {expected_val}: {e}")

            # EvalFile / EvalFileSmall
            for k in ["EvalFile", "EvalFileSmall"]:
                if k not in options:
                    raise ProtocolError(f"Missing network option: {k}")
                    
            # SyzygyPath emptiness check
            syzygy_path_opt = options.get("SyzygyPath")
            if not syzygy_path_opt:
                raise ProtocolError("Missing SyzygyPath option")
            if syzygy_path_opt.default not in ["<empty>", ""]:
                raise ProtocolError(f"SyzygyPath default is not empty: {syzygy_path_opt.default}")

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
            sorted_managed = sorted(list(MANAGED_OPTIONS))

            self._provenance = {
                "producer": STOCKFISH_UCI_NAME,
                "pre_spawn_sha256": self._pre_identity.sha256,
                "post_spawn_sha256": self._post_identity.sha256,
                "role": self.role.value,
                "instrument_id": self.instrument_id,
                "resolved_path": self._pre_identity.resolved_path,
                "static_config_applied": STATIC_UCI_CONFIG.copy(),
                "managed_semantics_enforced": sorted_managed,
                "eval_file_default": options["EvalFile"].default,
                "eval_file_small_default": options["EvalFileSmall"].default,
                "observed_syzygy_path_default": syzygy_path_opt.default,
                "normalized_tablebase_policy": "NO_EXTERNAL_TABLEBASE",
                "options_surface": sorted_opts
            }
        except ProtocolError:
            self.close()
            raise
        except Exception as e:
            self.close()
            raise ProtocolError(f"Unexpected start error: {e}")

    def acquire(self, spec: ExperimentSpec, root_board: chess.Board) -> ExperimentResult:
        if not self._engine:
            raise ProtocolError("Session not started")
            
        if spec.spec_version != 2:
            raise ProtocolError("spec_version must be 2")
        if spec.producer_identity != STOCKFISH_UCI_NAME:
            raise ProtocolError("producer_identity mismatch")
            
        if spec.budget_config != get_canonical_budget_config(self.role):
            raise ProtocolError("budget_config does not exactly match canonical shape")
            
        if spec.instrument_config != get_canonical_instrument_config(self.role):
            raise ProtocolError("instrument_config does not exactly match canonical shape")
            
        if spec.comparison_perspective != ("white" if root_board.turn == chess.WHITE else "black"):
            raise ProtocolError("comparison_perspective mismatch")
            
        if spec.sufficient_position.variant != "standard":
            raise ProtocolError("sufficient_position.variant must be standard")
            
        # Root board validation
        if not root_board.is_valid():
            raise ProtocolError("Root board is invalid")
        if root_board.chess960:
            raise ProtocolError("Chess960 is not permitted")
        if root_board.is_game_over(claim_draw=False):
            raise ProtocolError("Terminal root board")
        legal_moves = list(root_board.legal_moves)
        if len(legal_moves) < 2:
            raise ProtocolError("Root board must have at least 2 legal moves")
            
        sp = spec.sufficient_position
        observed_ep = None if root_board.ep_square is None else chess.square_name(root_board.ep_square)
        
        if sp.board_arrangement_fen != root_board.board_fen() or \
           sp.side_to_move != ("w" if root_board.turn else "b") or \
           sp.castling_rights != root_board.castling_xfen() or \
           sp.en_passant_square != observed_ep or \
           sp.halfmove_clock != root_board.halfmove_clock or \
           sp.fullmove_number != root_board.fullmove_number:
            raise ProtocolError("SufficientPosition derivable fields mismatch with root_board")
            
        if sp.history_available is not True:
            raise ProtocolError("history_available must be True for CP instrument")
        if not sp.history_identity:
            raise ProtocolError("history_identity must be a non-empty string for CP instrument")
            
        # Verify candidate policy
        sorted_moves = sorted(legal_moves, key=lambda m: m.uci())
        sorted_ucis = [m.uci() for m in sorted_moves]
        
        expected_policy = {
            "scope": "cp_all_legal_root_moves_v1",
            "ordered_legal_root_ucis": sorted_ucis,
            "required_search_count": len(sorted_ucis)
        }
        
        if spec.candidate_policy != expected_policy:
            raise ProtocolError("candidate_policy does not exactly match canonical expected policy")
            
        observations = []
        
        try:
            for idx, move in enumerate(sorted_moves):
                child_board = root_board.copy(stack=True)
                parent_stack_len = len(child_board.move_stack)
                child_board.push(move)
                child_stack_len = len(child_board.move_stack)
                
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
                if reported_nodes is not None:
                    if type(reported_nodes) is not int:
                        raise ProtocolError(f"Malformed reported nodes: expected int, got {type(reported_nodes)}")
                    if reported_nodes < 0:
                        raise ProtocolError("Negative reported nodes")
                    
                obs = {
                    "canonical_acquisition_index": idx,
                    "root_move_uci": move.uci(),
                    "child_fen": child_board.fen(shredder=False, en_passant="fen"),
                    "history_derivation_version": "S0_CHILD_PUSH_V1",
                    "parent_history_identity": sp.history_identity,
                    "parent_move_stack_length": parent_stack_len,
                    "child_move_stack_length": child_stack_len,
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
            "observed_syzygy_path_default": self._provenance["observed_syzygy_path_default"],
            "normalized_tablebase_policy": self._provenance["normalized_tablebase_policy"],
            "comparison_perspective": "white" if root_board.turn == chess.WHITE else "black",
            "canonical_acquisition_order": sorted_ucis,
            "root_sufficient_position": sp.model_dump(),
            "parent_history_available": sp.history_available,
            "parent_history_identity": sp.history_identity,
            "history_binding_source": "FROZEN_ROOT_MANIFEST",
            "observations": observations
        }
        
        return ExperimentResult.create(spec_digest=spec.spec_digest(), data=data)

    def close(self):
        if self._engine:
            try:
                self._engine.quit()
            except Exception:
                pass
            self._engine = None

