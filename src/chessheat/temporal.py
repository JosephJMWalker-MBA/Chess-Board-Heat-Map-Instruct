import chess
import chess.pgn
import io
from pydantic import BaseModel, Field, model_validator
from typing import List, Tuple, Optional, Dict, Any, Union, Set

from chessheat.geometry import (
    BoardGeometry,
    extract_geometry,
    compute_geometry_delta,
    AttackRelationship,
    SlidingRay,
    PieceRef
)

class TemporalEvent(BaseModel):
    """
    Tracks the lifetime of a specific geometry event over the course of a game history.
    
    TemporalEvent identity means persistent identity of a structural geometry signature,
    not physical-piece identity or causal continuity. If an identical geometric 
    relation disappears and later returns, it is tracked as the same TemporalEvent 
    reappearing.
    
    Active-interval boundary semantics:
    - Intervals are represented as `(start_ply, end_ply)`.
    - `start_ply` (inclusive): The exact ply at which the event first appeared (or ply 0 if present initially).
    - `end_ply` (exclusive): The exact ply at which the event was removed. If None, the event is active at the current end of history.
    - Thus, a lifetime for a closed interval is `end_ply - start_ply`.
    """
    event_identity: Any  # AttackRelationship, SlidingRay, or Tuple[PieceRef, str] for mobility
    event_type: str      # 'attack', 'defense', 'ray', 'mobility'
    active_intervals: List[Tuple[int, Optional[int]]] = Field(default_factory=list)
    is_left_censored: bool = False
    
    def episode_count(self) -> int:
        return len(self.active_intervals)
        
    def per_episode_durations(self, history_end_ply: int) -> List[int]:
        durations = []
        for start, end in self.active_intervals:
            effective_end = end if end is not None else history_end_ply
            durations.append(effective_end - start)
        return durations
        
    def observed_total_active_plies(self, history_end_ply: int) -> int:
        return sum(self.per_episode_durations(history_end_ply))
        
    def observed_max_continuous_active_plies(self, history_end_ply: int) -> int:
        durations = self.per_episode_durations(history_end_ply)
        return max(durations) if durations else 0
        
    def absence_gap_durations(self) -> List[int]:
        gaps = []
        for i in range(len(self.active_intervals) - 1):
            end_prev = self.active_intervals[i][1]
            start_next = self.active_intervals[i+1][0]
            if end_prev is not None:
                gaps.append(start_next - end_prev)
        return gaps
        
    def reappearance_count(self) -> int:
        count = self.episode_count()
        return count - 1 if count > 0 else 0
        
    def is_currently_active(self) -> bool:
        if not self.active_intervals:
            return False
        return self.active_intervals[-1][1] is None
        
    def is_right_censored(self) -> bool:
        return self.is_currently_active()

def extract_implicated_squares(event_identity: Any) -> Set[str]:
    """Extracts the set of squares structurally implicated by the geometric event signature."""
    if isinstance(event_identity, AttackRelationship):
        return {event_identity.attacker.square, event_identity.target_square}
    elif isinstance(event_identity, SlidingRay):
        sqs = {event_identity.source.square, event_identity.target_square}
        sqs.update(event_identity.path)
        return sqs
    elif isinstance(event_identity, tuple) and len(event_identity) == 2 and isinstance(event_identity[0], PieceRef):
        return {event_identity[0].square, event_identity[1]}
    return set()

class CoTransitionRelation(BaseModel):
    removed_event_signature: Any
    born_event_signature: Any
    shared_squares: Set[str] = Field(default_factory=set)
    overlaps: bool = False
    ply: int
    move_san: str
    observed_age_of_removed_episode: Optional[int] = None
    observed_duration_of_born_episode: Optional[int] = None
    is_removed_left_censored: Optional[bool] = None
    is_born_right_censored: Optional[bool] = None
    is_born_reappearance: Optional[bool] = None

class SuccessionCounterfactualEvidence(BaseModel):
    fen_before: str
    side_to_move: str
    legal_root_count: int
    predecessor_signature: Any
    successor_signature: Any
    played_move_san: str
    played_move_is_joint: bool
    m_11: List[str] = Field(default_factory=list)
    m_10: List[str] = Field(default_factory=list)
    m_01: List[str] = Field(default_factory=list)
    m_00: List[str] = Field(default_factory=list)
    n_11: int = 0
    n_10: int = 0
    n_01: int = 0
    n_00: int = 0
    p_b_given_d: Optional[float] = None
    p_b_given_not_d: Optional[float] = None
    delta_assoc: Optional[float] = None
    
    # Temporal/Spatial Evidence
    spatial_overlap: bool = False
    observed_age_of_removed_episode: Optional[int] = None
    observed_duration_of_born_episode: Optional[int] = None
    is_removed_left_censored: Optional[bool] = None
    is_born_right_censored: Optional[bool] = None
    is_born_reappearance: Optional[bool] = None

    @model_validator(mode='after')
    def assert_integrity(self) -> 'SuccessionCounterfactualEvidence':
        s_11, s_10, s_01, s_00 = set(self.m_11), set(self.m_10), set(self.m_01), set(self.m_00)
        
        # 1. Mutually exclusive
        assert s_11.isdisjoint(s_10), "M_11 and M_10 are not disjoint"
        assert s_11.isdisjoint(s_01), "M_11 and M_01 are not disjoint"
        assert s_11.isdisjoint(s_00), "M_11 and M_00 are not disjoint"
        assert s_10.isdisjoint(s_01), "M_10 and M_01 are not disjoint"
        assert s_10.isdisjoint(s_00), "M_10 and M_00 are not disjoint"
        assert s_01.isdisjoint(s_00), "M_01 and M_00 are not disjoint"
        
        # 2. Exhaustive and counts match
        assert self.n_11 + self.n_10 + self.n_01 + self.n_00 == self.legal_root_count, "Counts do not sum to legal root count"
        assert len(self.m_11) == self.n_11
        assert len(self.m_10) == self.n_10
        assert len(self.m_01) == self.n_01
        assert len(self.m_00) == self.n_00
        
        # 3. Played move belongs to M_11
        assert self.played_move_san in s_11, "Played move is not in M_11"
        assert self.played_move_is_joint, "Played move must be marked as joint"
        
        # 4. Conditional probabilities are None when denominators are zero
        denom_d = self.n_11 + self.n_10
        if denom_d > 0:
            assert self.p_b_given_d == self.n_11 / denom_d
        else:
            assert self.p_b_given_d is None
            
        denom_not_d = self.n_01 + self.n_00
        if denom_not_d > 0:
            assert self.p_b_given_not_d == self.n_01 / denom_not_d
        else:
            assert self.p_b_given_not_d is None
            
        if self.p_b_given_d is not None and self.p_b_given_not_d is not None:
            assert self.delta_assoc == self.p_b_given_d - self.p_b_given_not_d
        else:
            assert self.delta_assoc is None
            
        return self

class StructuralTransition(BaseModel):
    ply: int
    side: str
    move_san: str
    move_uci: str
    fen_before: str
    fen_after: str
    legal_optionality_before: int
    legal_optionality_after: int
    born_events: Set[Any] = Field(default_factory=set)
    removed_events: Set[Any] = Field(default_factory=set)
    persisting_events: Set[Any] = Field(default_factory=set)
    reappearing_events: Set[Any] = Field(default_factory=set)
    co_transitions: List[CoTransitionRelation] = Field(default_factory=list)
    counterfactual_evidence: List[SuccessionCounterfactualEvidence] = Field(default_factory=list)

class TemporalLedger(BaseModel):
    final_fen: str
    transitions: List[StructuralTransition] = Field(default_factory=list)
    events: List[TemporalEvent] = Field(default_factory=list)
    total_plies: int = 0

def build_temporal_ledger_from_pgn(pgn_string: str) -> TemporalLedger:
    """
    Parses a PGN and builds a descriptive temporal ledger of geometry events.
    """
    game = chess.pgn.read_game(io.StringIO(pgn_string))
    if not game:
        raise ValueError("Invalid PGN")

    board = game.board()
    
    # Check for left censoring (PGN starts from a custom position, not the standard initial position)
    is_custom_start = board.fen() != chess.STARTING_FEN
    
    # State tracking
    ply = 0
    transitions = []
    active_events_dict: Dict[Any, TemporalEvent] = {}
    previously_observed_signatures: Set[Any] = set()

    # Extract initial geometry
    current_geometry = extract_geometry(board)
    current_legal_count = board.legal_moves.count()
    
    def _add_event(event_id: Any, evt_type: str, current_ply: int):
        if event_id not in active_events_dict:
            left_censored = is_custom_start and current_ply == 0
            active_events_dict[event_id] = TemporalEvent(
                event_identity=event_id, 
                event_type=evt_type, 
                active_intervals=[(current_ply, None)],
                is_left_censored=left_censored
            )
        else:
            active_events_dict[event_id].active_intervals.append((current_ply, None))
        previously_observed_signatures.add(event_id)

    # Initialize all initial geometry at ply 0
    for attack in current_geometry.attacks:
        _add_event(attack, "attack", 0)
    for defense in current_geometry.defenses:
        _add_event(defense, "defense", 0)
    for ray in current_geometry.rays:
        _add_event(ray, "ray", 0)
    for mobility in current_geometry.mobility:
        for dest in mobility.legal_destinations:
            identity = (mobility.piece, dest)
            _add_event(identity, "mobility", 0)

    # Traverse moves
    for move in game.mainline_moves():
        side = "white" if board.turn == chess.WHITE else "black"
        move_san = board.san(move)
        move_uci = move.uci()
        fen_before = board.fen()
        
        board.push(move)
        ply += 1
        
        next_legal_count = board.legal_moves.count()
        fen_after = board.fen()

        next_geometry = extract_geometry(board)
        delta = compute_geometry_delta(current_geometry, next_geometry)
        
        # Pop the played move to evaluate counterfactuals at the pre-move position
        board.pop()
        
        # Pre-compute structural changes for all legal moves
        candidate_deltas: Dict[str, Tuple[Set[Any], Set[Any]]] = {}
        for m in board.legal_moves:
            m_san = board.san(m)
            board.push(m)
            cand_geom = extract_geometry(board)
            cand_delta = compute_geometry_delta(current_geometry, cand_geom)
            
            cand_D = set()
            for d in cand_delta.disappeared_attacks: cand_D.add(d)
            for d in cand_delta.disappeared_defenses: cand_D.add(d)
            for d in cand_delta.disappeared_rays: cand_D.add(d)
            for d in cand_delta.mobility_lost: cand_D.add(d)
                
            cand_B = set()
            for b in cand_delta.appeared_attacks: cand_B.add(b)
            for b in cand_delta.appeared_defenses: cand_B.add(b)
            for b in cand_delta.appeared_rays: cand_B.add(b)
            for b in cand_delta.mobility_gained: cand_B.add(b)
                
            candidate_deltas[m_san] = (cand_D, cand_B)
            board.pop()
            
        # Re-apply the played move to advance the state
        board.push(move)

        next_geometry = extract_geometry(board)
        delta = compute_geometry_delta(current_geometry, next_geometry)

        # Calculate born and removed sets for this transition
        B_t = set()
        D_t = set()
        
        # Handle disappearances
        for disappeared in delta.disappeared_attacks:
            if disappeared in active_events_dict:
                active_events_dict[disappeared].active_intervals[-1] = (active_events_dict[disappeared].active_intervals[-1][0], ply)
                D_t.add(disappeared)
        for disappeared in delta.disappeared_defenses:
            if disappeared in active_events_dict:
                active_events_dict[disappeared].active_intervals[-1] = (active_events_dict[disappeared].active_intervals[-1][0], ply)
                D_t.add(disappeared)
        for disappeared in delta.disappeared_rays:
            if disappeared in active_events_dict:
                active_events_dict[disappeared].active_intervals[-1] = (active_events_dict[disappeared].active_intervals[-1][0], ply)
                D_t.add(disappeared)
        for disappeared in delta.mobility_lost:
            if disappeared in active_events_dict:
                active_events_dict[disappeared].active_intervals[-1] = (active_events_dict[disappeared].active_intervals[-1][0], ply)
                D_t.add(disappeared)

        # Handle appearances (or reappearances)
        for appeared in delta.appeared_attacks:
            _add_event(appeared, "attack", ply)
            B_t.add(appeared)
                
        for appeared in delta.appeared_defenses:
            _add_event(appeared, "defense", ply)
            B_t.add(appeared)
                
        for appeared in delta.appeared_rays:
            _add_event(appeared, "ray", ply)
            B_t.add(appeared)
                
        for appeared in delta.mobility_gained:
            _add_event(appeared, "mobility", ply)
            B_t.add(appeared)
            
        # P_t is everything that was active before and not removed
        P_t = set()
        for identity, evt in active_events_dict.items():
            if evt.is_currently_active() and identity not in B_t:
                P_t.add(identity)
                
        R_t = {b for b in B_t if b in previously_observed_signatures and active_events_dict[b].episode_count() > 1}
        
        # Build co-transitions and counterfactual evidence
        co_transitions = []
        cf_evidence = []
        for d in D_t:
            for b in B_t:
                sq_d = extract_implicated_squares(d)
                sq_b = extract_implicated_squares(b)
                shared = sq_d.intersection(sq_b)
                overlaps = len(shared) > 0
                co_transitions.append(CoTransitionRelation(
                    removed_event_signature=d,
                    born_event_signature=b,
                    shared_squares=shared,
                    overlaps=overlaps,
                    ply=ply,
                    move_san=move_san
                ))
                
                # Build counterfactual evidence
                m_11, m_10, m_01, m_00 = [], [], [], []
                for m_san, (cand_D, cand_B) in candidate_deltas.items():
                    removes_d = d in cand_D
                    births_b = b in cand_B
                    if removes_d and births_b: m_11.append(m_san)
                    elif removes_d and not births_b: m_10.append(m_san)
                    elif not removes_d and births_b: m_01.append(m_san)
                    else: m_00.append(m_san)
                    
                n_11, n_10, n_01, n_00 = len(m_11), len(m_10), len(m_01), len(m_00)
                
                p_b_given_d = None
                if (n_11 + n_10) > 0:
                    p_b_given_d = n_11 / (n_11 + n_10)
                    
                p_b_given_not_d = None
                if (n_01 + n_00) > 0:
                    p_b_given_not_d = n_01 / (n_01 + n_00)
                    
                delta_assoc = None
                if p_b_given_d is not None and p_b_given_not_d is not None:
                    delta_assoc = p_b_given_d - p_b_given_not_d
                
                played_move_is_joint = (move_san in m_11)
                
                cf_evidence.append(SuccessionCounterfactualEvidence(
                    fen_before=fen_before,
                    side_to_move=side,
                    legal_root_count=current_legal_count,
                    predecessor_signature=d,
                    successor_signature=b,
                    played_move_san=move_san,
                    played_move_is_joint=played_move_is_joint,
                    m_11=m_11,
                    m_10=m_10,
                    m_01=m_01,
                    m_00=m_00,
                    n_11=n_11,
                    n_10=n_10,
                    n_01=n_01,
                    n_00=n_00,
                    p_b_given_d=p_b_given_d,
                    p_b_given_not_d=p_b_given_not_d,
                    delta_assoc=delta_assoc,
                    spatial_overlap=overlaps
                ))
                
        transitions.append(StructuralTransition(
            ply=ply,
            side=side,
            move_san=move_san,
            move_uci=move_uci,
            fen_before=fen_before,
            fen_after=fen_after,
            legal_optionality_before=current_legal_count,
            legal_optionality_after=next_legal_count,
            born_events=B_t,
            removed_events=D_t,
            persisting_events=P_t,
            reappearing_events=R_t,
            co_transitions=co_transitions,
            counterfactual_evidence=cf_evidence
        ))

        current_geometry = next_geometry
        current_legal_count = next_legal_count

    # Two-pass attachment of lifecycle metrics to CoTransitionRelation objects
    for transition in transitions:
        for co in transition.co_transitions:
            rem_event = active_events_dict.get(co.removed_event_signature)
            born_event = active_events_dict.get(co.born_event_signature)
            
            if rem_event:
                # Find the interval that ended at this transition ply
                for (start, end) in rem_event.active_intervals:
                    if end == co.ply:
                        co.observed_age_of_removed_episode = co.ply - start
                        co.is_removed_left_censored = rem_event.is_left_censored and start == 0
                        break
            
            if born_event:
                # Find the interval that started at this transition ply
                for (start, end) in born_event.active_intervals:
                    if start == co.ply:
                        effective_end = end if end is not None else ply
                        co.observed_duration_of_born_episode = effective_end - start
                        co.is_born_right_censored = (end is None)
                        break
                co.is_born_reappearance = born_event.episode_count() > 1 and co.born_event_signature in previously_observed_signatures
                
        for cf in transition.counterfactual_evidence:
            rem_event = active_events_dict.get(cf.predecessor_signature)
            born_event = active_events_dict.get(cf.successor_signature)
            
            if rem_event:
                for (start, end) in rem_event.active_intervals:
                    if end == transition.ply:
                        cf.observed_age_of_removed_episode = transition.ply - start
                        cf.is_removed_left_censored = rem_event.is_left_censored and start == 0
                        break
                        
            if born_event:
                for (start, end) in born_event.active_intervals:
                    if start == transition.ply:
                        effective_end = end if end is not None else ply
                        cf.observed_duration_of_born_episode = effective_end - start
                        cf.is_born_right_censored = (end is None)
                        break
                cf.is_born_reappearance = born_event.episode_count() > 1 and cf.successor_signature in previously_observed_signatures

    return TemporalLedger(
        final_fen=board.fen(),
        transitions=transitions,
        events=list(active_events_dict.values()),
        total_plies=ply
    )

class TemporalSuccessionGraph:
    def __init__(self, ledger: TemporalLedger):
        self.ledger = ledger
        # Multigraph edges: List of CoTransitionRelation
        self.edges: List[CoTransitionRelation] = []
        for transition in ledger.transitions:
            self.edges.extend(transition.co_transitions)
            
    def get_predecessors(self, signature: Any) -> List[CoTransitionRelation]:
        return [e for e in self.edges if e.born_event_signature == signature]
        
    def get_successors(self, signature: Any) -> List[CoTransitionRelation]:
        return [e for e in self.edges if e.removed_event_signature == signature]
        
    def transition_count(self, removed_sig: Any, born_sig: Any) -> int:
        return sum(1 for e in self.edges if e.removed_event_signature == removed_sig and e.born_event_signature == born_sig)
        
    def branching_degree(self, removed_sig: Any) -> int:
        return len({e.born_event_signature for e in self.edges if e.removed_event_signature == removed_sig})
        
    def convergence_degree(self, born_sig: Any) -> int:
        return len({e.removed_event_signature for e in self.edges if e.born_event_signature == born_sig})
        
    def get_succession_chain(self, signature_list: List[Any]) -> bool:
        if len(signature_list) < 2:
            return False
        
        for i in range(len(signature_list) - 1):
            a = signature_list[i]
            b = signature_list[i + 1]
            if not any(e for e in self.edges if e.removed_event_signature == a and e.born_event_signature == b):
                return False
        return True
        
    def had_spatial_overlap(self, removed_sig: Any, born_sig: Any) -> bool:
        return any(e.overlaps for e in self.edges if e.removed_event_signature == removed_sig and e.born_event_signature == born_sig)

def build_temporal_succession_graph(ledger: TemporalLedger) -> TemporalSuccessionGraph:
    return TemporalSuccessionGraph(ledger)
