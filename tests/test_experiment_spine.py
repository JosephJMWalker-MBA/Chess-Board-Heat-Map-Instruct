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
        suite_identity="test_suite",
        fixture_identity="fixture_1",
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
    result = ExperimentResult(
        spec_digest=orig_digest,
        artifact_digest="artifact_hash",
        data={"heat": 100}
    )
    
    with pytest.raises(ValidationError):
        result.spec_digest = "new_digest"
        
    with pytest.raises(ValidationError):
        result.data = {}

    # Mutate the source spec's nested dictionary
    base_spec.candidate_policy["top_n"] = 999
    
    # The result's provenance remains the original, distinct from the mutated spec
    assert result.spec_digest == orig_digest
    assert result.spec_digest != base_spec.spec_digest()

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
    natural = SuiteManifest(suite_id="s1", kind=SuiteKind.NATURAL_REPRESENTATIVE, fixtures=["f1"])
    stress = SuiteManifest(suite_id="s2", kind=SuiteKind.MECHANISM_STRESS, fixtures=["f2"])
    
    assert natural.kind == SuiteKind.NATURAL_REPRESENTATIVE
    assert stress.kind == SuiteKind.MECHANISM_STRESS
    assert natural.kind != stress.kind
