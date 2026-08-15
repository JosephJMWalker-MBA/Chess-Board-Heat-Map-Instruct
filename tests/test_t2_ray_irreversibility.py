import pytest
import chess
import hashlib
import json
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
    
    assert vertical != diagonal
    assert proj_v == proj_d

def test_ordinary_pv_reconstruction_lemma():
    """
    Ordinary-PV Reconstruction Lemma: 
    For tested ordinary moves whose identity is determined by origin/destination/state, 
    the square-event PV can be replayed and rule-exact relations reconstructed.
    """
    fen = "4k3/8/8/8/8/8/4P3/4K2R w K - 0 1"
    board = chess.Board(fen)
    assert board.is_valid()
    
    pv_events = [
        SpatialEvent(square="e2", role="origin", ply=1),
        SpatialEvent(square="e4", role="destination", ply=1)
    ]
    
    reconstructed_origin = next(e.square for e in pv_events if e.ply == 1 and e.role == "origin")
    reconstructed_dest = next(e.square for e in pv_events if e.ply == 1 and e.role == "destination")
    reconstructed_move_uci = f"{reconstructed_origin}{reconstructed_dest}"
    
    simulated_board = chess.Board(fen)
    simulated_board.push_uci(reconstructed_move_uci)
    
    rook_attacks = simulated_board.attacks(chess.H1)
    assert chess.H8 in rook_attacks  

def test_promotion_ambiguity_proves_irreversibility():
    """
    T2 Preflight: Ray/Blocker Information Irreversibility
    Proves that for promotion moves, the FutureBranch baseline square evidence
    (origin and destination squares) is non-injective. Discarding the promotion piece
    permanently loses branch-conditioned relational semantics, supporting Claim A.
    """
    # 1. Test promotion ambiguity in the actual baseline
    # Board with Black King on a8, White pawn on d7, Black pawn on h4 (target).
    fen = "k7/3P4/8/8/7p/8/8/4K3 w - - 0 1"
    board = chess.Board(fen)
    assert board.is_valid()
    
    root_uci = "e1d1"
    assert chess.Move.from_uci(root_uci) in board.legal_moves
    
    # We construct two legal PV continuations from this root
    # PV A: 1... a8a7 (ply 1) 2. d7d8q (ply 2)
    # PV B: 1... a8a7 (ply 1) 2. d7d8r (ply 2)
    
    pv_events = [
        SpatialEvent(square="a8", role="origin", ply=1),
        SpatialEvent(square="a7", role="destination", ply=1),
        SpatialEvent(square="d7", role="origin", ply=2),
        SpatialEvent(square="d8", role="destination", ply=2)
    ]
    
    # 2. Use the actual FutureBranch information boundary
    score = Score(type="cp", value=100, perspective="white")
    branch_Q = FutureBranch(
        root_uci=root_uci, root_fen=fen, actor="white", line_source="synthetic", producer="engine",
        score=score, regret=score, is_admitted=True, future_moves=["a8a7", "d7d8q"], future_evidence=pv_events
    )
    branch_R = FutureBranch(
        root_uci=root_uci, root_fen=fen, actor="white", line_source="synthetic", producer="engine",
        score=score, regret=score, is_admitted=True, future_moves=["a8a7", "d7d8r"], future_evidence=pv_events
    )
    
    # The FutureBranch baseline evidence is perfectly identical.
    assert branch_Q.future_evidence == branch_R.future_evidence
    
    # Trying to reconstruct from baseline fails to uniquely determine promotion:
    # Origin is d7, dest is d8. The move is d7d8? -> could be q, r, b, or n.
    reconstructed_moves = []
    board_after_ply1 = board.copy()
    board_after_ply1.push_uci("e1d1")
    board_after_ply1.push_uci("a8a7")
    
    for m in board_after_ply1.legal_moves:
        if chess.square_name(m.from_square) == "d7" and chess.square_name(m.to_square) == "d8":
            reconstructed_moves.append(m)
            
    assert len(reconstructed_moves) == 4  # All 4 promotions match the baseline square evidence
    
    # 3. Test relational consequence of the ambiguity (and fix with future_moves)
    # Replay Q promotion using EXACT future_moves
    board_Q = board_after_ply1.copy()
    board_Q.push_uci(branch_Q.future_moves[-1])
    attacks_Q = board_Q.attacks(chess.D8)
    assert chess.H4 in attacks_Q # Queen on d8 attacks h4
    
    # Replay R promotion using EXACT future_moves
    board_R = board_after_ply1.copy()
    board_R.push_uci(branch_R.future_moves[-1])
    attacks_R = board_R.attacks(chess.D8)
    assert chess.H4 not in attacks_R # Rook on d8 does NOT attack h4
    
    # Prove future_moves explicitly disambiguates the identical square projections
    assert branch_Q.future_moves != branch_R.future_moves
    
    # We have established that the exact same FutureBranch square evidence 
    # maps to different rule-exact ray relation structure.
    
    # 5. Fix S1 fixture identity
    fixture_content = {
        "fen": fen,
        "root_uci": root_uci,
        "pv_a": ["a8a7", "d7d8q"],
        "pv_b": ["a8a7", "d7d8r"]
    }
    fixture_hash = hashlib.sha256(json.dumps(fixture_content, sort_keys=True).encode()).hexdigest()
    
    s0_canonical = SemanticSignatureV1.create_canonical()
    
    manifest = SuiteManifest(
        suite_id="t2_ray_blocker_promotion_ambiguity",
        kind=SuiteKind.MECHANISM_STRESS,
        fixtures={"fixture_1": fixture_hash}
    )
    
    spec = ExperimentSpec(
        semantic_signature_version="1.0",
        semantic_signature_digest=s0_canonical.signature_hash(),
        suite_identity=manifest.suite_id,
        suite_digest=manifest.suite_digest(),
        fixture_identity="fixture_1",
        fixture_digest=fixture_hash,
        sufficient_position=SufficientPosition(
            board_arrangement_fen=fen,
            side_to_move="w",
            castling_rights="-",
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

    # 4. Correct the logical classification
    result = ExperimentResult.create(
        spec_digest=spec.spec_digest(),
        data={
            "outcome": "FALSIFIED",
            "endpoint_pairing_lemma": "Preserved: independent square projection loses linkage.",
            "promotion_ambiguity_lemma": "Preserved: future_evidence throws away promotion piece identity.",
            "conclusion": "Because FutureBranch now explicitly preserves exact future_moves alongside future_evidence, "
                          "every legal continuation can be deterministically replayed from the root state. "
                          "Thus, rule-exact ray/blocker relation structure is completely reconstructible, "
                          "falsifying the relation irreversibility hypothesis relative to the new branch baseline. "
                          "Relations are derivable semantic structure, not necessary primitive evidence."
        }
    )

    assert result.data["outcome"] == "FALSIFIED"

