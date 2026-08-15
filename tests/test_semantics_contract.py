import pytest
from chessheat.semantics import (
    EpistemicGuarantee, SubjectKind, EvidenceLevel, RelationState,
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
    sig1 = SemanticSignatureV1()
    sig2 = SemanticSignatureV1()
    
    assert sig1.signature_hash() == sig2.signature_hash()
    
    # Verify it actually returns a 64-char sha256 hex string
    assert len(sig1.signature_hash()) == 64

def test_serialization_round_trip():
    """
    Verify that SemanticSignatureV1 round-trips via JSON without loss.
    """
    sig = SemanticSignatureV1()
    serialized = sig.model_dump_json()
    deserialized = SemanticSignatureV1.model_validate_json(serialized)
    
    assert deserialized.signature_hash() == sig.signature_hash()
