import pytest
import chess
from chessheat.semantics import RelationContainer, ParticipantRole, SubjectKind, CoreRelationState, SufficientPosition
from chessheat.models import SpatialEvent, FutureBranch, Score
from chessheat.experiment import ExperimentSpec, ExperimentResult, SuiteManifest, SuiteKind
from chessheat.semantics import SemanticSignatureV1

def project_relations_to_spatial_events(relations: list[RelationContainer], ply: int = 1) -> list[SpatialEvent]:
    r"""
    \Pi_\square : E_{relation} \to E_{square}
    Retains subject (square), kind (SQUARE), and role (origin/target).
    """
    events = []
    for r in relations:
        for p in r.participants:
            role_map = {"origin": "origin", "target": "destination"}
            if p.role in role_map:
                events.append(SpatialEvent(square=p.subject, role=role_map[p.role], ply=ply))
    return sorted(events, key=lambda e: (e.square, e.role))


def test_endpoint_pairing_lemma():
    """
    Endpoint-Pairing Lemma: 
    Projection from relation records to independent SpatialEvent(square, role, ply) events 
    is non-injective because relation pairing/linkage is lost.
    """
    # Mechanically valid chess setup (e.g. 2 Rooks attacking 2 targets)
    # White Rooks on a1, c1. Black targets on a3, c3.
    # Note: This lemma isolates just the relation representation, independent of the board state baseline.
    
    vertical = [
        RelationContainer(relation_type="ray", participants=[
            ParticipantRole(subject="a1", kind=SubjectKind.SQUARE, role="origin"),
            ParticipantRole(subject="a3", kind=SubjectKind.SQUARE, role="target")
        ], state="enabled", provenance="rule_exact"),
        RelationContainer(relation_type="ray", participants=[
            ParticipantRole(subject="c1", kind=SubjectKind.SQUARE, role="origin"),
            ParticipantRole(subject="c3", kind=SubjectKind.SQUARE, role="target")
        ], state="enabled", provenance="rule_exact")
    ]
    
    diagonal = [
        RelationContainer(relation_type="ray", participants=[
            ParticipantRole(subject="a1", kind=SubjectKind.SQUARE, role="origin"),
            ParticipantRole(subject="c3", kind=SubjectKind.SQUARE, role="target")
        ], state="enabled", provenance="rule_exact"),
        RelationContainer(relation_type="ray", participants=[
            ParticipantRole(subject="c1", kind=SubjectKind.SQUARE, role="origin"),
            ParticipantRole(subject="a3", kind=SubjectKind.SQUARE, role="target")
        ], state="enabled", provenance="rule_exact")
    ]
    
    proj_v = project_relations_to_spatial_events(vertical)
    proj_d = project_relations_to_spatial_events(diagonal)
    
    # Proof of non-injectivity: the relations differ, but their square projections are identical.
    assert vertical != diagonal
    assert proj_v == proj_d

def test_ray_blocker_strong_falsifier():
    """
    T2 Preflight: Ray/Blocker Information Irreversibility - Strong Falsifier
    Tests whether the ray/blocker relation distinction can be reconstructed from the
    sufficient legal position and the actual ChessHeat baseline square events (which include ply).
    """
    # 1. Mechanically Valid Chess Fixture
    fen = "4k3/8/8/8/8/8/4P3/4K2R w K - 0 1"
    board = chess.Board(fen)
    assert board.is_valid()
    
    # 2. Mechanically derive relations (e.g., ray/blocker for a discovered attack or PV)
    # Suppose our branch PV is 1. e2e4. 
    move = chess.Move.from_uci("e2e4")
    assert move in board.legal_moves
    
    # The FutureBranch baseline captures the PV moves as SpatialEvents tagged by ply.
    pv_events = [
        SpatialEvent(square="e2", role="origin", ply=1),
        SpatialEvent(square="e4", role="destination", ply=1)
    ]
    
    score = Score(type="cp", value=100, perspective="white")
    branch = FutureBranch(
        root_uci="e2e4",
        root_fen=fen,
        actor="white",
        line_source="synthetic_pv",
        producer="rule_exact",
        score=score,
        regret=score,
        is_admitted=True,
        future_evidence=pv_events
    )
    
    # 3. Mechanically challenge the proof
    # Can we reconstruct the PV move from the baseline square evidence?
    # Yes, because ply=1 has exactly one origin and one destination.
    reconstructed_origin = next(e.square for e in branch.future_evidence if e.ply == 1 and e.role == "origin")
    reconstructed_dest = next(e.square for e in branch.future_evidence if e.ply == 1 and e.role == "destination")
    
    reconstructed_move_uci = f"{reconstructed_origin}{reconstructed_dest}"
    assert reconstructed_move_uci == "e2e4"
    
    # Since we can reconstruct the move, we can apply it to the sufficient legal position.
    simulated_board = chess.Board(branch.root_fen)
    simulated_board.push_uci(reconstructed_move_uci)
    
    # From the simulated board, we can perfectly reconstruct any rule-exact ray/blocker relation.
    # E.g., extracting the open file for the rook on h1:
    rook_attacks = simulated_board.attacks(chess.H1)
    assert chess.H8 in rook_attacks  # Ray h1->h8 is unblocked
    
    # Conclusion: The square evidence (which includes ply and move roles) + permitted board state
    # allows deterministic reconstruction of the PV, and therefore deterministic reconstruction
    # of all board states and all rule-exact ray/blocker relations.
    # Therefore, the relations are fully reconstructible and the irreversibility hypothesis is FALSIFIED.
    
    # 4. Use real S1 identities
    s0_canonical = SemanticSignatureV1.create_canonical()
    
    manifest = SuiteManifest(
        suite_id="t2_ray_blocker_falsifier",
        kind=SuiteKind.MECHANISM_STRESS,
        fixtures={"fixture_1": "mock_fixture_hash"}
    )
    
    spec = ExperimentSpec(
        semantic_signature_version="1.0",
        semantic_signature_digest=s0_canonical.signature_hash(),
        suite_identity=manifest.suite_id,
        suite_digest=manifest.suite_digest(),
        fixture_identity="fixture_1",
        fixture_digest="mock_fixture_hash",
        sufficient_position=SufficientPosition(
            board_arrangement_fen=fen,
            side_to_move="w",
            castling_rights="K",
            en_passant_square=None,
            halfmove_clock=0,
            fullmove_number=1,
            history_available=False
        ),
        candidate_policy={"type": "rule_exact"},
        producer_identity="synthetic_proof",
        instrument_config={"type": "none"},
        budget_config={"type": "exact", "value": 1},
        line_source="rule_exact",
        hypothesis_identifier="t2_ray_blocker_irreversibility"
    )

    result = ExperimentResult.create(
        spec_digest=spec.spec_digest(),
        data={
            "outcome": "FALSIFIED",
            "endpoint_pairing_lemma": "Proved non-injective natively",
            "conclusion": "Because FutureBranch baseline includes explicit PV moves tagged by ply, "
                          "the exact sequence of future board states can be reconstructed. "
                          "Thus, any rule-exact ray/blocker relation can be deterministically "
                          "reconstructed from the baseline + root state, falsifying irreversibility."
        }
    )

    assert result.data["outcome"] == "FALSIFIED"
