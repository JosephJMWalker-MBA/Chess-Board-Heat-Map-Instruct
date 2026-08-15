from enum import Enum
from typing import List, Optional, Any, Dict
from pydantic import BaseModel, Field, field_validator
import re

class EpistemicGuarantee(str, Enum):
    RULE_EXACT = "rule_exact"
    ENGINE_DERIVED = "engine_derived"
    SEARCH_DERIVED = "search_derived"
    EMPIRICAL = "empirical"
    HEURISTIC = "heuristic"

class SubjectKind(str, Enum):
    """
    Extensibility rule: SubjectKind is a closed enum. Adding a new top-level
    subject kind requires a semantic-version bump in the semantic ontology.
    """
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

class CoreRelationState(str, Enum):
    """
    Core examples of relation states. The semantic ontology allows future typed 
    relation states (as strings) without rewriting the ontology.
    """
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
    state: str  # CoreRelationState or a namespaced string (e.g., "domain:state")
    provenance: str

    @field_validator('state')
    @classmethod
    def validate_state_format(cls, v: str) -> str:
        if v in {e.value for e in CoreRelationState}:
            return v
        # Reject unconstrained text, require explicit namespace for future states
        if not re.match(r'^[a-z0-9_]+:[a-z0-9_]+$', v):
            raise ValueError(
                f"Custom relation state '{v}' is rejected. "
                "Non-core states must be explicitly namespaced (e.g., 'domain:state')."
            )
        return v

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
    Hashes canonical serialized semantic records, including sufficient position identity,
    a multi-participant relation/mediator example, and relation-state/transition semantics.
    """
    version: str = "1.0"
    position: SufficientPosition
    relation: RelationContainer
    
    @classmethod
    def create_canonical(cls) -> "SemanticSignatureV1":
        return cls(
            position=SufficientPosition(
                board_arrangement_fen="rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR",
                side_to_move="w",
                castling_rights="KQkq",
                en_passant_square=None,
                halfmove_clock=0,
                fullmove_number=1,
                history_available=False,
                variant="standard"
            ),
            relation=RelationContainer(
                relation_type="attacks",
                participants=[
                    ParticipantRole(subject="e2", kind=SubjectKind.SQUARE, role="origin"),
                    ParticipantRole(subject="e4", kind=SubjectKind.SQUARE, role="mediator"),
                    ParticipantRole(subject="e7", kind=SubjectKind.SQUARE, role="target")
                ],
                geometry_path=["e2", "e3", "e4", "e5", "e6", "e7"],
                state=CoreRelationState.ENABLED.value,
                provenance="rule_exact"
            )
        )
    
    def signature_hash(self) -> str:
        import hashlib
        import json
        payload = self.model_dump()
        payload_str = json.dumps(payload, sort_keys=True)
        return hashlib.sha256(payload_str.encode('utf-8')).hexdigest()
