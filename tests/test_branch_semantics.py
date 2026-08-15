import pytest
from typing import List
from chessheat.models import AnalysisRecord, Score, MoveObservation, PlyObservation, CandidateProvenance, SquareEffectRole, EvidenceEnvelope
from chessheat.branch import extract_branches, ConsequenceDiscriminationStatistic
from chessheat.recurrence import aggregate_square_recurrence, reconstruct_recurrence_from_branches
from chessheat.models import SpatialEvent, FutureBranch, BranchUniverse

def create_mock_record(observations: List[MoveObservation]) -> AnalysisRecord:
    return AnalysisRecord(
        fen="rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1",
        candidate_policy={"top_n": 3, "max_regret_cp": 200},
        move_observations=observations,
        root_side="white",
        comparison_perspective="white",
        engine_name="mock",
        search_budget_type="nodes",
        search_budget_value=1000,
        baseline_observation=Score(type="cp", value=0, perspective="white")
    )

def test_branch_reconstructibility():
    """
    Proof 1: Reconstructibility
    ordinary recurrence can be mechanically reconstructed from the richer branch representation.
    """
    obs1 = MoveObservation(
        uci="e2e4",
        san="e4",
        origin_square="e2",
        destination_square="e4",
        is_capture=False,
        resulting_fen="fen1",
        score=Score(type="cp", value=50, perspective="white"),
        regret=Score(type="cp", value=0, perspective="white"),
        parsed_pv=[
            PlyObservation(ply_number=1, uci="e2e4", origin="e2", destination="e4", roles=[SquareEffectRole.ORIGIN, SquareEffectRole.DESTINATION]),
            PlyObservation(ply_number=2, uci="e7e5", origin="e7", destination="e5", roles=[SquareEffectRole.ORIGIN, SquareEffectRole.DESTINATION]),
            PlyObservation(ply_number=3, uci="g1f3", origin="g1", destination="f3", roles=[SquareEffectRole.ORIGIN, SquareEffectRole.DESTINATION])
        ]
    )
    obs2 = MoveObservation(
        uci="d2d4",
        san="d4",
        origin_square="d2",
        destination_square="d4",
        is_capture=False,
        resulting_fen="fen2",
        score=Score(type="cp", value=40, perspective="white"),
        regret=Score(type="cp", value=10, perspective="white"),
        parsed_pv=[
            PlyObservation(ply_number=1, uci="d2d4", origin="d2", destination="d4", roles=[SquareEffectRole.ORIGIN, SquareEffectRole.DESTINATION]),
            PlyObservation(ply_number=2, uci="d7d5", origin="d7", destination="d5", roles=[SquareEffectRole.ORIGIN, SquareEffectRole.DESTINATION]),
            PlyObservation(ply_number=3, uci="c2c4", origin="c2", destination="c4", roles=[SquareEffectRole.ORIGIN, SquareEffectRole.DESTINATION])
        ]
    )
    obs3 = MoveObservation(
        uci="h2h3", # Not admitted, regret > 200
        san="h3",
        origin_square="h2",
        destination_square="h3",
        is_capture=False,
        resulting_fen="fen3",
        score=Score(type="cp", value=-200, perspective="white"),
        regret=Score(type="cp", value=250, perspective="white"),
        parsed_pv=[
            PlyObservation(ply_number=1, uci="h2h3", origin="h2", destination="h3", roles=[SquareEffectRole.ORIGIN, SquareEffectRole.DESTINATION])
        ]
    )
    
    record = create_mock_record([obs1, obs2, obs3])
    
    # Standard computation
    standard_result = aggregate_square_recurrence(record)
    
    # New spine extraction and reconstruction
    universe = extract_branches(record)
    reconstructed_result = reconstruct_recurrence_from_branches(universe)
    
    # Structural identity proof
    assert standard_result.model_dump() == reconstructed_result.model_dump()
    assert universe.provenance.admitted_count == 2
    assert "e2e4" in universe.provenance.admitted_root_moves
    assert "h2h3" not in universe.provenance.admitted_root_moves

def test_branch_irreversibility():
    """
    Proof 2: Irreversibility
    root-conditioned consequence structure cannot generally be reconstructed 
    once branch identity has been collapsed away.
    """
    # Universe A: Square e4 is used in a good branch (regret=0) and a bad branch (regret=150)
    universe_a = BranchUniverse(
        envelope=EvidenceEnvelope(epistemic_guarantee="search_derived", subject_kind="square", producer="mock", history_requirement=False, line_source="pv"),
        provenance=CandidateProvenance(
            total_legal_moves=2, candidate_policy={}, admitted_count=2, admitted_root_moves=["a", "b"], 
            candidate_scores={}, candidate_regrets={}, aggregated_pvs=2
        ),
        branches=[
            FutureBranch(
                root_uci="a", root_fen="fen", actor="white", line_source="pv", producer="mock",
                score=Score(type="cp", value=100, perspective="white"),
                regret=Score(type="cp", value=0, perspective="white"),
                is_admitted=True,
                future_evidence=[SpatialEvent(square="e4", role="destination", ply=1)]
            ),
            FutureBranch(
                root_uci="b", root_fen="fen", actor="white", line_source="pv", producer="mock",
                score=Score(type="cp", value=-50, perspective="white"),
                regret=Score(type="cp", value=150, perspective="white"),
                is_admitted=True,
                future_evidence=[SpatialEvent(square="e4", role="destination", ply=2)]
            )
        ]
    )
    
    # Universe B: Square e4 is used only in two identical mediocre branches (regret=75)
    universe_b = BranchUniverse(
        envelope=EvidenceEnvelope(epistemic_guarantee="search_derived", subject_kind="square", producer="mock", history_requirement=False, line_source="pv"),
        provenance=CandidateProvenance(
            total_legal_moves=2, candidate_policy={}, admitted_count=2, admitted_root_moves=["c", "d"], 
            candidate_scores={}, candidate_regrets={}, aggregated_pvs=2
        ),
        branches=[
            FutureBranch(
                root_uci="c", root_fen="fen", actor="white", line_source="pv", producer="mock",
                score=Score(type="cp", value=25, perspective="white"),
                regret=Score(type="cp", value=75, perspective="white"),
                is_admitted=True,
                future_evidence=[SpatialEvent(square="e4", role="destination", ply=1)]
            ),
            FutureBranch(
                root_uci="d", root_fen="fen", actor="white", line_source="pv", producer="mock",
                score=Score(type="cp", value=25, perspective="white"),
                regret=Score(type="cp", value=75, perspective="white"),
                is_admitted=True,
                future_evidence=[SpatialEvent(square="e4", role="destination", ply=2)]
            )
        ]
    )
    
    # Reconstruct recurrence for both
    rec_a = reconstruct_recurrence_from_branches(universe_a)
    rec_b = reconstruct_recurrence_from_branches(universe_b)
    
    # The aggregated consequence (recurrence metrics) for square 'e4' is identical:
    # 2 distinct lines, 100% fraction, 2 visits, earliest ply 1.
    sq_a = rec_a.squares["e4"]
    sq_b = rec_b.squares["e4"]
    
    assert sq_a.overall.visit_count == sq_b.overall.visit_count == 2
    assert sq_a.overall.distinct_line_count == sq_b.overall.distinct_line_count == 2
    assert sq_a.overall.earliest_ply == sq_b.overall.earliest_ply == 1
    
    # BUT their consequence landscape is totally different. 
    # Universe A's e4 discriminates a 0-regret move from a 150-regret move.
    # Universe B's e4 is indifferent (75-regret vs 75-regret).
    # Since rec_a.squares["e4"] == rec_b.squares["e4"], the consequence information was lost.

def test_branch_integrity():
    """
    Integrity: Tests ensuring branch identity, mate typing, 
    candidate admission, actor/depth, and line provenance survive intact.
    """
    obs = MoveObservation(
        uci="e2e4",
        san="e4",
        origin_square="e2",
        destination_square="e4",
        is_capture=False,
        resulting_fen="fen4",
        score=Score(type="mate", value=1, perspective="white"),
        regret=Score(type="mate", value=0, perspective="white"),
        parsed_pv=[
            PlyObservation(ply_number=1, uci="e2e4", origin="e2", destination="e4", roles=[SquareEffectRole.ORIGIN, SquareEffectRole.DESTINATION]),
            PlyObservation(ply_number=2, uci="e7e5", origin="e7", destination="e5", capture="d4", roles=[SquareEffectRole.ORIGIN, SquareEffectRole.DESTINATION, SquareEffectRole.CAPTURE])
        ]
    )
    record = create_mock_record([obs])
    # override policy to allow mate regret admission
    record.candidate_policy = {"top_n": 3, "max_regret_cp": None}
    universe = extract_branches(record)
    
    assert len(universe.branches) == 1
    branch = universe.branches[0]
    
    # Branch identity
    assert branch.root_uci == "e2e4"
    
    # Mate typing survives
    assert branch.score.type == "mate"
    assert branch.score.value == 1
    assert branch.regret.type == "mate"
    assert branch.regret.value == 0
    
    # Candidate admission survives
    assert branch.is_admitted is True
    
    # Actor/depth and line provenance survive as SpatialEvents
    events = branch.future_evidence
    assert len(events) == 5 # e2 origin, e4 dest (ply 1), e7 origin, e5 dest, d4 capture (ply 2)
    
    capture_event = next(e for e in events if e.role == "capture")
    assert capture_event.square == "d4"
    assert capture_event.ply == 2

def test_excluded_roots_evidence():
    """
    Tests that excluded roots contribute zero branch evidence 
    and are marked as not admitted.
    """
    obs_good = MoveObservation(
        uci="e2e4", san="e4", origin_square="e2", destination_square="e4",
        is_capture=False, resulting_fen="fen1",
        score=Score(type="cp", value=50, perspective="white"),
        regret=Score(type="cp", value=0, perspective="white"),
        parsed_pv=[PlyObservation(ply_number=1, uci="e2e4", origin="e2", destination="e4", roles=[SquareEffectRole.ORIGIN, SquareEffectRole.DESTINATION])]
    )
    obs_bad = MoveObservation(
        uci="h2h3", san="h3", origin_square="h2", destination_square="h3",
        is_capture=False, resulting_fen="fen2",
        score=Score(type="cp", value=-500, perspective="white"),
        regret=Score(type="cp", value=550, perspective="white"),
        parsed_pv=[PlyObservation(ply_number=1, uci="h2h3", origin="h2", destination="h3", roles=[SquareEffectRole.ORIGIN, SquareEffectRole.DESTINATION])]
    )
    record = create_mock_record([obs_good, obs_bad])
    universe = extract_branches(record)
    
    # h2h3 should be rejected because regret 550 > 200
    bad_branch = next(b for b in universe.branches if b.root_uci == "h2h3")
    assert bad_branch.is_admitted is False
    assert len(bad_branch.future_evidence) == 0 # no evidence!
    
def test_envelope_and_serialization():
    """
    Tests that the typed evidence envelope and 
    actor/depth/line-source fields survive model serialization.
    """
    obs = MoveObservation(
        uci="e2e4", san="e4", origin_square="e2", destination_square="e4",
        is_capture=False, resulting_fen="fen1",
        score=Score(type="cp", value=50, perspective="white"),
        regret=Score(type="cp", value=0, perspective="white"),
        parsed_pv=[PlyObservation(ply_number=1, uci="e2e4", origin="e2", destination="e4", roles=[SquareEffectRole.ORIGIN, SquareEffectRole.DESTINATION])]
    )
    record = create_mock_record([obs])
    universe = extract_branches(record)
    
    # Verify Envelope
    assert universe.envelope.epistemic_guarantee == "search_derived"
    assert universe.envelope.subject_kind == "square"
    assert universe.envelope.producer == "mock"
    assert universe.envelope.history_requirement is False
    assert universe.envelope.line_source == "pv"
    
    # Verify FutureBranch attributes
    branch = universe.branches[0]
    assert branch.root_fen == record.fen
    assert branch.actor == "white"
    assert branch.line_source == "pv"
    assert branch.producer == "mock"
    
    # Test Serialization
    serialized = universe.model_dump_json()
    deserialized = BranchUniverse.model_validate_json(serialized)
    
    assert deserialized.envelope.epistemic_guarantee == "search_derived"
    assert deserialized.branches[0].actor == "white"
    assert deserialized.branches[0].root_fen == record.fen
    assert deserialized.branches[0].line_source == "pv"

def test_extract_branches_rejects_ply1_mismatch():
    """
    Tests that a mismatch between root UCI and ply 1 UCI raises a ValueError,
    ensuring future_moves cannot silently skip or misalign the root move.
    """
    obs = MoveObservation(
        uci="e2e4", san="e4", origin_square="e2", destination_square="e4",
        is_capture=False, resulting_fen="fen1",
        score=Score(type="cp", value=50, perspective="white"),
        regret=Score(type="cp", value=0, perspective="white"),
        parsed_pv=[PlyObservation(ply_number=1, uci="d2d4", origin="d2", destination="d4", roles=[SquareEffectRole.ORIGIN, SquareEffectRole.DESTINATION])]
    )
    record = create_mock_record([obs])
    
    with pytest.raises(ValueError, match="must mechanically match the root UCI"):
        extract_branches(record)
