from typing import List, Literal, Optional, Union, Dict, Any, Set
from pydantic import BaseModel, Field
from enum import Enum

class Score(BaseModel):
    type: Literal["cp", "mate"]
    value: int
    perspective: Literal["white", "black"]



class SquareEffectRole(str, Enum):
    ORIGIN = "origin"
    DESTINATION = "destination"
    CAPTURE = "capture"
    KING_ORIGIN = "king_origin"
    KING_DESTINATION = "king_destination"
    ROOK_ORIGIN = "rook_origin"
    ROOK_DESTINATION = "rook_destination"
    EN_PASSANT_CAPTURE = "en_passant_capture"

class MoveSquareEffect(BaseModel):
    uci: str
    roles: List[SquareEffectRole]

class ImplicatedMove(BaseModel):
    uci: str
    roles: List[SquareEffectRole]
    outcome: Score
    regret: Optional[Score] = None
    promotion: Optional[str] = None

class SquareAttribution(BaseModel):
    square: str
    move_count: int = 0
    as_origin: int = 0
    as_destination: int = 0
    as_capture: int = 0

    best_move: Optional[str] = None
    worst_move: Optional[str] = None

    # Aggregates for CP only
    best_outcome_cp: Optional[int] = None
    worst_outcome_cp: Optional[int] = None
    mean_cp_outcome: Optional[float] = None

    min_cp_regret: Optional[int] = None
    max_cp_regret: Optional[int] = None
    mean_cp_regret: Optional[float] = None

    # Tally for mates
    mate_outcomes: int = 0

    implicated_moves: List[ImplicatedMove] = Field(default_factory=list)

class PlyObservation(BaseModel):
    ply_number: int
    uci: str
    origin: str
    destination: str
    capture: Optional[str] = None
    roles: List[SquareEffectRole]

class MoveObservation(BaseModel):
    uci: str
    san: str
    origin_square: str
    destination_square: str
    is_capture: bool
    captured_square: Optional[str] = None
    promotion: Optional[str] = None
    is_castling: bool = False
    is_en_passant: bool = False
    resulting_fen: str
    score: Score
    regret: Optional[Score] = None
    principal_variation: Optional[List[str]] = None
    parsed_pv: List[PlyObservation] = Field(default_factory=list)

class AnalysisRecord(BaseModel):
    schema_version: str = "1.0"
    fen: str
    root_side: Literal["white", "black"]
    comparison_perspective: Literal["white", "black"]
    engine_name: str
    engine_options: Dict[str, Any] = Field(default_factory=dict)
    candidate_policy: Dict[str, Any] = Field(default_factory=dict)
    search_budget_type: str
    search_budget_value: int
    baseline_observation: Score
    move_observations: List[MoveObservation]

class MetricDelta(BaseModel):
    state: Literal["persisted", "appeared", "disappeared", "absent_both"]
    before: Optional[Union[float, int]] = None
    after: Optional[Union[float, int]] = None
    delta: Optional[Union[float, int]] = None

class SquareRoleDeltas(BaseModel):
    metrics: Dict[str, MetricDelta]

class SquareDeltaSummary(BaseModel):
    roles: Dict[str, SquareRoleDeltas]

class PairedAnalysisRecord(BaseModel):
    schema_version: str = "1.0"
    source_fen: str
    transition_move: str
    resulting_fen: str
    before_side_to_move: Literal["white", "black"]
    after_side_to_move: Literal["white", "black"]
    comparison_perspective: Literal["white", "black"]

    before_record: AnalysisRecord
    after_record: AnalysisRecord

    before_attributions: Dict[str, SquareAttribution]
    after_attributions: Dict[str, SquareAttribution]

    deltas: Dict[str, SquareDeltaSummary]

class RecurrenceMetric(BaseModel):
    distinct_line_count: int
    line_fraction: float
    visit_count: int
    earliest_ply: Optional[int]

class SquareRecurrence(BaseModel):
    square: str
    overall: RecurrenceMetric
    by_role: Dict[str, RecurrenceMetric]

class CandidateProvenance(BaseModel):
    total_legal_moves: int
    candidate_policy: Dict[str, Any]
    admitted_count: int
    admitted_root_moves: List[str]
    candidate_scores: Dict[str, Score]
    candidate_regrets: Dict[str, Score]
    aggregated_pvs: int

class RecurrenceResult(BaseModel):
    provenance: CandidateProvenance
    squares: Dict[str, SquareRecurrence]

class EventSignature(BaseModel):
    event_type: str
    source_square: str
    target_square: str
    path: List[str] = Field(default_factory=list)
    piece_symbol: Optional[str] = None
    target_symbol: Optional[str] = None

    # We must allow hashing in sets
    def __hash__(self):
        return hash((self.event_type, self.source_square, self.target_square, tuple(self.path), self.piece_symbol, self.target_symbol))

class MetricDistribution(BaseModel):
    min_val: Optional[float] = None
    max_val: Optional[float] = None
    mean_val: Optional[float] = None
    median_val: Optional[float] = None
    q1_val: Optional[float] = None
    q3_val: Optional[float] = None
    best_move: Optional[str] = None
    worst_move: Optional[str] = None

class EventBundle(BaseModel):
    constituent_events: List[EventSignature]
    producing_moves: List[str]
    non_producing_moves: List[str]
    candidate_fraction: float
    regret_with_bundle: MetricDistribution
    regret_without_bundle: MetricDistribution
    outcome_with_bundle: MetricDistribution
    outcome_without_bundle: MetricDistribution
    mean_regret_diff: float
    median_regret_diff: float
    implicated_squares: List[str]
    is_perfectly_confounded: bool
