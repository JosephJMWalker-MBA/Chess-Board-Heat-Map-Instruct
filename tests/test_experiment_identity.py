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
    kw_white["spec_version"] = 2
    kw_white["comparison_perspective"] = "white"
    
    kw_black = get_base_kwargs()
    kw_black["spec_version"] = 2
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
    # And spec_version should default to 1 and not be serialized.
    kw1 = get_base_kwargs()
    spec1 = ExperimentSpec(**kw1)
    
    kw2 = get_base_kwargs()
    kw2["comparison_perspective"] = None
    spec2 = ExperimentSpec(**kw2)
    
    # Omitted and explicit None must yield same identity (and match historical behavior)
    assert spec1.spec_digest() == spec2.spec_digest()

def test_experiment_identity_v2_rejects_omitted_or_invalid_perspective():
    kw = get_base_kwargs()
    kw["spec_version"] = 2
    
    # Omitted
    with pytest.raises(ValidationError) as exc1:
        ExperimentSpec(**kw)
    assert "comparison_perspective must be 'white' or 'black'" in str(exc1.value)
    
    # Explicit None
    kw["comparison_perspective"] = None
    with pytest.raises(ValidationError) as exc2:
        ExperimentSpec(**kw)
    assert "comparison_perspective must be 'white' or 'black'" in str(exc2.value)
    
    # Invalid arbitrary string
    kw["comparison_perspective"] = "arbitrary"
    with pytest.raises(ValidationError) as exc3:
        ExperimentSpec(**kw)
    assert "comparison_perspective must be 'white' or 'black'" in str(exc3.value)

def test_t3a2_historical_digest():
    from chessheat.semantics import SufficientPosition
    sp = SufficientPosition(
        board_arrangement_fen="4k3/8/1b6/8/3R4/8/8/4K3",
        side_to_move="w",
        castling_rights="-",
        en_passant_square=None,
        halfmove_clock=0,
        fullmove_number=1,
        history_available=False,
        history_identity=None,
        variant="standard"
    )
    
    spec = ExperimentSpec(
        semantic_signature_version="1.0",
        semantic_signature_digest="5fa4d57cf43c673fa31874ce5d19e777acf0ea695fd032412b193c2123461080",
        suite_identity="t3a2_suite",
        suite_digest="3be6773230028cf53f79c0904bd8685075141f76327fb2f0feb56e786b9bc4f2",
        fixture_identity="t3a2_immediate_capture",
        fixture_digest="ec55f31c873292aaefe2229a8b197458b678e6bb3617d6094b22068b8240a1b1",
        sufficient_position=sp,
        candidate_policy={},
        producer_identity="Stockfish 18",
        instrument_config={"Threads": 1, "Hash": 16},
        budget_config={"type": "nodes", "value": 100000},
        line_source="pv",
        hypothesis_identifier="T3a-2"
    )
    assert spec.spec_digest() == "e2a56fe3da7d965d1bc6080f7028504da9832a0030e5038eff7cdc35d8fa4730"
