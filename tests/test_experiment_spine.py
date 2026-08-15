import pytest
from pydantic import ValidationError
from chessheat.semantics import SufficientPosition
from chessheat.experiment import (
    SuiteKind, SuiteManifest, ExperimentSpec, ExperimentResult, ComparisonResult
)

@pytest.fixture
def base_position():
    return SufficientPosition(
        board_arrangement_fen="fen",
        side_to_move="w",
        castling_rights="-",
        en_passant_square=None,
        halfmove_clock=0,
        fullmove_number=1,
        history_available=False
    )

@pytest.fixture
def base_spec(base_position):
    return ExperimentSpec(
        semantic_signature_version="1.0",
        semantic_signature_digest="fake_s0_digest",
        suite_identity="test_suite",
        suite_digest="fake_suite_digest",
        fixture_identity="fixture_1",
        fixture_digest="fake_fixture_digest",
        sufficient_position=base_position,
        candidate_policy={"top_n": 5},
        producer_identity="stockfish_18",
        instrument_config={"threads": 1},
        budget_config={"nodes": 500000},
        line_source="pv",
        hypothesis_identifier="test_hyp"
    )

def test_experiment_identity_determinism(base_spec):
    """
    Identical frozen inputs/configs produce identical experiment identity (digest).
    """
    spec2 = base_spec.model_copy(deep=True)
    assert base_spec.spec_digest() == spec2.spec_digest()

def test_experiment_identity_mutation(base_spec):
    """
    Changing a meaningful input/config changes the identity.
    """
    orig_digest = base_spec.spec_digest()
    
    # Mutate budget
    mutated_budget = base_spec.model_copy(deep=True)
    mutated_budget.budget_config["nodes"] = 1000000
    assert mutated_budget.spec_digest() != orig_digest

    # Mutate policy
    mutated_policy = base_spec.model_copy(deep=True)
    mutated_policy.candidate_policy["top_n"] = 3
    assert mutated_policy.spec_digest() != orig_digest
    
    # Mutate position
    mutated_pos = base_spec.model_copy(deep=True)
    mutated_pos.sufficient_position.side_to_move = "b"
    assert mutated_pos.spec_digest() != orig_digest

    # Changed semantic-signature digest => different spec identity
    mutated_sem = base_spec.model_copy(deep=True)
    mutated_sem.semantic_signature_digest = "changed_s0_digest"
    assert mutated_sem.spec_digest() != orig_digest

def test_suite_and_fixture_identity_changes(base_spec):
    """
    same suite label + changed fixture content => different suite/spec identity;
    same fixture label + changed fixture content => different fixture/spec identity;
    """
    manifest_a = SuiteManifest(suite_id="suite1", kind=SuiteKind.NATURAL_REPRESENTATIVE, fixtures={"f1": "content_hash_1"})
    manifest_b = SuiteManifest(suite_id="suite1", kind=SuiteKind.NATURAL_REPRESENTATIVE, fixtures={"f1": "content_hash_2"})
    
    # Same suite label, changed fixture content -> different suite digest
    assert manifest_a.suite_digest() != manifest_b.suite_digest()

    orig_digest = base_spec.spec_digest()
    
    # Same fixture label, changed fixture content -> different spec digest
    mutated_fix = base_spec.model_copy(deep=True)
    mutated_fix.fixture_digest = "changed_fixture_digest"
    assert mutated_fix.spec_digest() != orig_digest

    # Same suite label, changed suite content (digest) -> different spec digest
    mutated_suite = base_spec.model_copy(deep=True)
    mutated_suite.suite_digest = manifest_b.suite_digest()
    assert mutated_suite.spec_digest() != orig_digest

def test_experiment_serialization(base_spec):
    """
    Fixture identity and semantic-signature version survive round-trip JSON serialization.
    """
    serialized = base_spec.model_dump_json()
    deserialized = ExperimentSpec.model_validate_json(serialized)
    
    assert deserialized.fixture_identity == "fixture_1"
    assert deserialized.semantic_signature_version == "1.0"
    assert deserialized.spec_digest() == base_spec.spec_digest()

def test_result_provenance_immutability(base_spec):
    """
    Experiment results cannot silently replace or mutate their source specification.
    They are frozen and refer to the spec by digest. Later mutation of the spec
    does not alter the result's represented provenance.
    """
    orig_digest = base_spec.spec_digest()
    result = ExperimentResult.create(
        spec_digest=orig_digest,
        data={"heat": 100}
    )
    
    with pytest.raises(ValidationError):
        result.spec_digest = "new_digest"
        
    # Result payload cannot silently mutate under an unchanged artifact digest
    # Result payload is accessible via throwing dictionary
    result.data["heat"] = 999
    
    # The actual payload was unmutated
    assert result.data["heat"] == 100
    # Artifact digest mechanically derived
    assert result.artifact_digest != result.spec_digest

    # Mutate the source spec's nested dictionary
    base_spec.candidate_policy["top_n"] = 999
    
    # The result's provenance remains the original, distinct from the mutated spec
    assert result.spec_digest == orig_digest
    assert result.spec_digest != base_spec.spec_digest()

def test_result_artifact_validation(base_spec):
    """
    Ensure direct construction or JSON deserialization rigorously validates the payload and digest.
    """
    import json
    orig_digest = base_spec.spec_digest()
    
    # .create() round-trips successfully (proven by construction)
    valid_result = ExperimentResult.create(spec_digest=orig_digest, data={"heat": 100})
    
    # direct construction with a fake digest fails
    with pytest.raises(ValidationError):
        ExperimentResult(
            spec_digest=orig_digest,
            artifact_digest="fake_digest",
            data_payload=json.dumps({"heat": 100})
        )

    # JSON deserialization with a tampered payload but old digest fails
    tampered_payload_json = valid_result.model_dump()
    tampered_payload_json["data_payload"] = json.dumps({"heat": 999})
    with pytest.raises(ValidationError):
        ExperimentResult.model_validate(tampered_payload_json)

    # JSON deserialization with a tampered digest fails
    tampered_digest_json = valid_result.model_dump()
    tampered_digest_json["artifact_digest"] = "tampered"
    with pytest.raises(ValidationError):
        ExperimentResult.model_validate(tampered_digest_json)

    # Non-canonical payload (e.g. unsorted keys or extra whitespace) fails
    with pytest.raises(ValidationError):
        ExperimentResult(
            spec_digest=orig_digest,
            artifact_digest=valid_result.artifact_digest, # Using valid digest but padded payload
            data_payload='{"heat": 100 }'
        )

def test_digest_order_stability(base_spec):
    """
    Digest canonicalization is order-stable for mappings where ordering is not semantically meaningful.
    """
    spec_a = base_spec.model_copy(deep=True)
    spec_a.instrument_config = {"a": 1, "b": 2}
    
    spec_b = base_spec.model_copy(deep=True)
    spec_b.instrument_config = {"b": 2, "a": 1}
    
    assert spec_a.spec_digest() == spec_b.spec_digest()

def test_suite_distinction():
    """
    Natural/representative suites and mechanism-stress suites are explicitly distinguishable.
    """
    natural = SuiteManifest(suite_id="s1", kind=SuiteKind.NATURAL_REPRESENTATIVE, fixtures={"f1": "d1"})
    stress = SuiteManifest(suite_id="s2", kind=SuiteKind.MECHANISM_STRESS, fixtures={"f2": "d2"})
    
    assert natural.kind == SuiteKind.NATURAL_REPRESENTATIVE
    assert stress.kind == SuiteKind.MECHANISM_STRESS
    assert natural.kind != stress.kind
