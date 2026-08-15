import pytest
from chessheat.semantics import (
    EpistemicGuarantee, SubjectKind, EvidenceLevel, CoreRelationState,
    SemanticSignatureV1
)

def test_epistemic_guarantee_constraints():
    """
    Ensure the epistemic types strictly conform to the frozen vocabulary.
    """
    valid_types = {"rule_exact", "engine_derived", "search_derived", "empirical", "heuristic"}
    enum_values = {e.value for e in EpistemicGuarantee}
    assert enum_values == valid_types

def test_subject_kind_constraints():
    """
    Ensure the subject kinds cover the required domain.
    """
    required_types = {"square", "piece", "move", "relation", "path", "region", "interaction_component", "global_state"}
    enum_values = {e.value for e in SubjectKind}
    # Allow extensibility by asserting subset relationship
    # UPDATE: SubjectKind is now a closed V1 ontology protected by the SemanticSignatureV1 digest.
    # The digest will fail if a new top-level kind is added without an explicit version update.
    assert required_types.issubset(enum_values)

def test_evidence_level_ladder():
    """
    Ensure evidence levels cover the required hierarchy.
    """
    required_levels = {
        "occurrence", "recurrence", "branch_discrimination",
        "consequence_association", "intervention_sensitivity", "causal_validation"
    }
    enum_values = {e.value for e in EvidenceLevel}
    assert required_levels.issubset(enum_values)

def test_frozen_semantic_signature_digest():
    """
    Verify that SemanticSignatureV1 equals the exact expected digest.
    If this fails, a meaningful semantic definition has changed (e.g. new SubjectKind added,
    fields altered) and requires an explicit semantic-version bump.
    """
    EXPECTED_DIGEST = "5fa4d57cf43c673fa31874ce5d19e777acf0ea695fd032412b193c2123461080"
    
    sig = SemanticSignatureV1.create_canonical()
    assert sig.signature_hash() == EXPECTED_DIGEST

def test_semantic_signature_mutation():
    """
    Prove that a meaningful semantic change alters the signature digest.
    """
    sig = SemanticSignatureV1.create_canonical()
    original_hash = sig.signature_hash()
    
    # Mutate relation state
    sig.relation.state = CoreRelationState.REALIZED.value
    assert sig.signature_hash() != original_hash
    
    # Reset and mutate relation type
    sig.relation.state = CoreRelationState.ENABLED.value
    assert sig.signature_hash() == original_hash
    
    sig.relation.relation_type = "defends"
    assert sig.signature_hash() != original_hash

def test_serialization_round_trip():
    """
    Verify that SemanticSignatureV1 round-trips via JSON without loss.
    """
    sig = SemanticSignatureV1.create_canonical()
    serialized = sig.model_dump_json()
    deserialized = SemanticSignatureV1.model_validate_json(serialized)
    
    assert deserialized.signature_hash() == sig.signature_hash()

def test_relation_state_extensibility():
    """
    Ensure the relation state allows core states, admits custom namespaced states,
    but rejects malformed or arbitrary unconstrained strings.
    """
    from chessheat.semantics import RelationContainer, ParticipantRole, SubjectKind
    from pydantic import ValidationError

    def make_container(state: str):
        return RelationContainer(
            relation_type="attacks",
            participants=[ParticipantRole(subject="e2", kind=SubjectKind.SQUARE, role="origin")],
            state=state,
            provenance="test"
        )
    
    # 1. Core states round-trip correctly
    c1 = make_container(CoreRelationState.ENABLED.value)
    assert c1.state == "enabled"
    
    # 2. Valid future/custom states can be represented intentionally
    c2 = make_container("example:pinned")
    assert c2.state == "example:pinned"
    
    # 3. Malformed/empty/unstructured state identifiers are rejected
    with pytest.raises(ValidationError):
        make_container("banana")  # Unconstrained text
        
    with pytest.raises(ValidationError):
        make_container("   ")  # Empty/whitespace
        
    with pytest.raises(ValidationError):
        make_container("custom_without_colon")  # Missing namespace delimiter

def test_relation_state_assignment_validation():
    """
    Ensure RelationContainer.state validation cannot be bypassed by post-construction assignment.
    """
    from chessheat.semantics import RelationContainer, ParticipantRole, SubjectKind
    from pydantic import ValidationError

    relation = RelationContainer(
        relation_type="attacks",
        participants=[ParticipantRole(subject="e2", kind=SubjectKind.SQUARE, role="origin")],
        state=CoreRelationState.ENABLED.value,
        provenance="test"
    )

    with pytest.raises(ValidationError):
        relation.state = "banana"

def test_history_distinction():
    """
    Ensure two otherwise identical sufficient positions with distinct available
    history identities remain distinguishable.
    """
    from chessheat.semantics import SufficientPosition
    
    base_kwargs = dict(
        board_arrangement_fen="fen",
        side_to_move="w",
        castling_rights="-",
        en_passant_square=None,
        halfmove_clock=0,
        fullmove_number=1,
        variant="standard"
    )

    p1 = SufficientPosition(**base_kwargs, history_available=True, history_identity="hash_A")
    p2 = SufficientPosition(**base_kwargs, history_available=True, history_identity="hash_B")
    
    assert p1.model_dump_json() != p2.model_dump_json()

def test_unavailable_history():
    """
    Ensure unavailable history remains explicitly representable.
    """
    from chessheat.semantics import SufficientPosition
    
    p = SufficientPosition(
        board_arrangement_fen="fen",
        side_to_move="w",
        castling_rights="-",
        en_passant_square=None,
        halfmove_clock=0,
        fullmove_number=1,
        history_available=False,
        history_identity=None
    )
    assert p.history_available is False
    assert p.history_identity is None
