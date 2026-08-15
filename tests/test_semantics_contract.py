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

def test_semantic_signature_determinism():
    """
    Verify that SemanticSignatureV1 generates a deterministic hash for the same definition.
    """
    sig1 = SemanticSignatureV1.create_canonical()
    sig2 = SemanticSignatureV1.create_canonical()
    
    assert sig1.signature_hash() == sig2.signature_hash()
    
    # Verify it actually returns a 64-char sha256 hex string
    assert len(sig1.signature_hash()) == 64

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
