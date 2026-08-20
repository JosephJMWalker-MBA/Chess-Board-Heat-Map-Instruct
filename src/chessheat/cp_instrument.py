import hashlib
import os
import chess
import chess.engine
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass

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

@dataclass
class AcquisitionPlanEntry:
    root_move_uci: str
    child_fen: str
    comparison_perspective: chess.Color
    canonical_acquisition_index: int

@dataclass
class Observation:
    root_move_uci: str
    child_fen: str
    score_type: str
    score_value: int
    perspective: chess.Color
    nodes: int
    
class ProtocolError(Exception):
    pass

def construct_acquisition_plan(root_board: chess.Board) -> List[AcquisitionPlanEntry]:
    if not root_board.is_valid():
        raise ProtocolError("Root board is invalid")
    if root_board.chess960:
        raise ProtocolError("Chess960 is not permitted")
    
    perspective = root_board.turn
    legal_moves = list(root_board.legal_moves)
    if not legal_moves:
        raise ProtocolError("Zero legal moves")
        
    sorted_moves = sorted(legal_moves, key=lambda m: m.uci())
    seen_moves = set()
    
    plan = []
    for idx, move in enumerate(sorted_moves):
        uci = move.uci()
        if uci in seen_moves:
            raise ProtocolError(f"Duplicate legal move: {uci}")
        seen_moves.add(uci)
        
        child_board = root_board.copy()
        child_board.push(move)
        plan.append(AcquisitionPlanEntry(
            root_move_uci=uci,
            child_fen=child_board.fen(),
            comparison_perspective=perspective,
            canonical_acquisition_index=idx
        ))
        
    return plan

def verify_executable(executable_path: str):
    if not os.path.isfile(executable_path):
        raise ProtocolError("Executable is not a file")
    
    with open(executable_path, "rb") as f:
        digest = hashlib.sha256(f.read()).hexdigest()
        
    if digest != STOCKFISH_BINARY_SHA256:
        raise ProtocolError(f"Binary SHA mismatch. Expected {STOCKFISH_BINARY_SHA256}, got {digest}")

class InstrumentSession:
    def __init__(self, executable_path: str, role: str):
        self.executable_path = executable_path
        if role not in ("SOURCE", "TARGET"):
            raise ProtocolError(f"Invalid role: {role}")
            
        self.role = role
        self.instrument_id = SOURCE_INSTRUMENT_ID if role == "SOURCE" else TARGET_INSTRUMENT_ID
        self.nodes = SOURCE_NODES if role == "SOURCE" else TARGET_NODES
        self._engine = None
        self._provenance = {}

    def start(self):
        verify_executable(self.executable_path)
        
        engine = chess.engine.SimpleEngine.popen_uci(self.executable_path)
        self._engine = engine
        
        if self._engine.id.get("name") != STOCKFISH_UCI_NAME:
            self.close()
            raise ProtocolError(f"Wrong UCI name. Expected {STOCKFISH_UCI_NAME}")
            
        options = self._engine.options
        for k in STATIC_UCI_CONFIG:
            if k not in options:
                self.close()
                raise ProtocolError(f"Missing required option: {k}")
                
        for k in MANAGED_OPTIONS:
            if k not in options:
                self.close()
                raise ProtocolError(f"Missing managed option: {k}")
                
        # Validate EvalFile and EvalFileSmall are default
        for k in ["EvalFile", "EvalFileSmall"]:
            if k in options:
                val = options[k].value
                default = options[k].default
                if val != default:
                    self.close()
                    raise ProtocolError(f"Attempted network override for {k}")
                self._provenance[f"{k}_default"] = default
                
        # SyzygyPath check
        if "SyzygyPath" in options and options["SyzygyPath"].value != "<empty>":
            self.close()
            raise ProtocolError("Tablebase path is active")

        # Configure unmanaged static options
        config_to_apply = {}
        for k, v in STATIC_UCI_CONFIG.items():
            if k not in MANAGED_OPTIONS:
                config_to_apply[k] = v
                
        try:
            self._engine.configure(config_to_apply)
        except Exception as e:
            self.close()
            raise ProtocolError(f"Configuration mismatch: {e}")

        # Provenance
        self._provenance["producer"] = STOCKFISH_UCI_NAME
        self._provenance["sha256"] = STOCKFISH_BINARY_SHA256
        self._provenance["role"] = self.role
        self._provenance["instrument_id"] = self.instrument_id
        self._provenance["nodes"] = self.nodes
        self._provenance["resolved_path"] = self.executable_path
        self._provenance["static_config"] = STATIC_UCI_CONFIG.copy()

    def acquire(self, root_board: chess.Board) -> List[Observation]:
        if not self._engine:
            raise ProtocolError("Session not started")
            
        plan = construct_acquisition_plan(root_board)
        observations = []
        
        for entry in plan:
            child_board = chess.Board(entry.child_fen)
            game_token = object() # Fresh token
            
            result = self._engine.analyse(
                child_board,
                chess.engine.Limit(nodes=self.nodes),
                game=game_token,
                multipv=None,
                root_moves=None
            )
            
            if "score" not in result:
                raise ProtocolError("Missing score")
                
            pov_score = result["score"]
            root_score = pov_score.pov(entry.comparison_perspective)
            
            if root_score.is_mate():
                s_type = "mate"
                s_val = root_score.mate()
            else:
                s_type = "cp"
                s_val = root_score.score()
                
            nodes_searched = result.get("nodes", self.nodes)
            
            obs = Observation(
                root_move_uci=entry.root_move_uci,
                child_fen=entry.child_fen,
                score_type=s_type,
                score_value=s_val,
                perspective=entry.comparison_perspective,
                nodes=nodes_searched
            )
            observations.append(obs)
            
        return observations

    def get_provenance(self):
        return self._provenance.copy()

    def close(self):
        if self._engine:
            self._engine.quit()
            self._engine = None
