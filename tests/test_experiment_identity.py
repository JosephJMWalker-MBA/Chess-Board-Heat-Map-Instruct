import pytest
from pydantic import ValidationError
from chessheat.experiment import ExperimentSpec
from chessheat.semantics import SufficientPosition

def get_base_kwargs():
    return {
        "semantic_signature_version": "1.0",
        "semantic_signature_digest": "s0_mock_digest",
        "suite_identity": "mock_suite",
        "suite_digest": "suite_mock_digest",
        "fixture_identity": "mock_fixture",
        "fixture_digest": "fixture_mock_digest",
        "sufficient_position": SufficientPosition(
            board_arrangement_fen="rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR",
            side_to_move="w",
            castling_rights="KQkq",
            en_passant_square=None,
            halfmove_clock=0,
            fullmove_number=1,
            history_available=False,
            history_identity=None,
            variant="standard"
        ),
        "candidate_policy": {},
        "producer_identity": "MockEngine 1",
        "instrument_config": {},
        "budget_config": {"type": "nodes", "value": 100},
        "line_source": "pv",
        "hypothesis_identifier": "Mock-Hypothesis"
    }

def test_experiment_identity_binds_comparison_perspective():
    kw_white = get_base_kwargs()
    kw_white["comparison_perspective"] = "white"
    
    kw_black = get_base_kwargs()
    kw_black["comparison_perspective"] = "black"
    
    spec_white = ExperimentSpec(**kw_white)
    spec_black = ExperimentSpec(**kw_black)
    
    # Must have different identities
    assert spec_white.spec_digest() != spec_black.spec_digest()
    
    # Must have comparison_perspective explicitly present
    assert spec_white.comparison_perspective == "white"
    assert spec_black.comparison_perspective == "black"

def test_experiment_identity_forbids_unknown_fields():
    kw = get_base_kwargs()
    kw["unknown_identity_field"] = "some_value"
    kw["comparison_persepctive"] = "white" # Misspelled
    
    with pytest.raises(ValidationError) as exc:
        ExperimentSpec(**kw)
        
    err_msg = str(exc.value)
    assert "unknown_identity_field" in err_msg
    assert "comparison_persepctive" in err_msg
    assert "Extra inputs are not permitted" in err_msg

def test_experiment_identity_backward_compatibility():
    # If comparison_perspective is omitted, the digest should not contain a null/None key.
    kw1 = get_base_kwargs()
    spec1 = ExperimentSpec(**kw1)
    
    kw2 = get_base_kwargs()
    kw2["comparison_perspective"] = None
    spec2 = ExperimentSpec(**kw2)
    
    # Omitted and explicit None must yield same identity (and match historical behavior)
    assert spec1.spec_digest() == spec2.spec_digest()
