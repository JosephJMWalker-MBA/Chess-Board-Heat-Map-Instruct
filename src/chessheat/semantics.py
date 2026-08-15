from enum import Enum
from typing import List, Optional, Any, Dict
from pydantic import BaseModel, Field

class EpistemicGuarantee(str, Enum):
    RULE_EXACT = "rule_exact"
    ENGINE_DERIVED = "engine_derived"
    SEARCH_DERIVED = "search_derived"
    EMPIRICAL = "empirical"
    HEURISTIC = "heuristic"

class SubjectKind(str, Enum):
    SQUARE = "square"
    PIECE = "piece"
    MOVE = "move"
    RELATION = "relation"
    PATH = "path"
    REGION = "region"
    INTERACTION_COMPONENT = "interaction_component"
    GLOBAL_STATE = "global_state"

class EvidenceLevel(str, Enum):
    OCCURRENCE = "occurrence"
    RECURRENCE = "recurrence"
    BRANCH_DISCRIMINATION = "branch_discrimination"
    CONSEQUENCE_ASSOCIATION = "consequence_association"
    INTERVENTION_SENSITIVITY = "intervention_sensitivity"
    CAUSAL_VALIDATION = "causal_validation"

class RelationState(str, Enum):
    LATENT = "latent"
    ENABLED = "enabled"
    REALIZED = "realized"

class SufficientPosition(BaseModel):
    """
    Sufficient legal chess state (P).
    Distinguishes history and availability over and above simple board arrangement.
    """
    board_arrangement_fen: str
    side_to_move: str
    castling_rights: str
    en_passant_square: Optional[str]
    halfmove_clock: int
    fullmove_number: int
    history_available: bool
    variant: str = "standard"

class ParticipantRole(BaseModel):
    subject: str # e.g., square or piece identifier
    kind: SubjectKind
    role: str # e.g., 'origin', 'target', 'mediator'

class RelationContainer(BaseModel):
    """
    Semantic container for relations (not strictly pairwise edges).
    """
    relation_type: str
    participants: List[ParticipantRole]
    geometry_path: Optional[List[str]] = None
    state: RelationState
    provenance: str

class ObservationIdentity(BaseModel):
    """
    Observation vs. Instrument Semantics.
    Independent observations intended for comparison must originate 
    from equivalent instrument states to prevent instrument contamination.
    """
    producer: str
    configuration: Dict[str, Any]
    search_epoch_state: str
    candidate_scope: str
    budget: Dict[str, int]
    line_source: str
    provenance: str

class SemanticSignatureV1(BaseModel):
    """
    A tiny deterministic semantic fixture/signature mechanism.
    This serves as a semantic regression sentinel.
    """
    version: str = "1.0"
    epistemic_types: List[str] = [e.value for e in EpistemicGuarantee]
    subject_kinds: List[str] = [s.value for s in SubjectKind]
    evidence_levels: List[str] = [e.value for e in EvidenceLevel]
    relation_states: List[str] = [r.value for r in RelationState]
    
    def signature_hash(self) -> str:
        import hashlib
        import json
        payload = self.model_dump()
        payload_str = json.dumps(payload, sort_keys=True)
        return hashlib.sha256(payload_str.encode('utf-8')).hexdigest()
