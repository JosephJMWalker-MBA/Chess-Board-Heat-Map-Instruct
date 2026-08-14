import os
import json
import pytest
from unittest.mock import patch, mock_open, MagicMock, call
import chess
from chessheat.validation.t1_11_runner import create_execution_seal, run_t1_11_execution, T1_11_CONFIG

def test_seal_rejects_id_mismatch(tmp_path):
    preflight_data = {"fixtures": [{"fixture_id": "Q1", "eligibility_status": "PASS", "dimension_preflight_status": "PASS"}]}
    manifest_data = [{"fixture_id": "Q2"}]
    
    preflight_path = tmp_path / "pre.json"
    with open(preflight_path, "w") as f: json.dump(preflight_data, f)
    manifest_path = tmp_path / "man.json"
    with open(manifest_path, "w") as f: json.dump(manifest_data, f)
        
    with pytest.raises(ValueError, match="Manifest and preflight fixture IDs do not match exactly"):
        run_t1_11_execution(str(preflight_path), str(manifest_path), str(tmp_path / "out"), "dummy")

def test_seal_rejects_fail_state(tmp_path):
    preflight_data = {"fixtures": [
        {"fixture_id": "Q1", "eligibility_status": "PASS", "dimension_preflight_status": "PASS"},
        {"fixture_id": "Q2", "eligibility_status": "FAIL", "dimension_preflight_status": "PASS"}
    ]}
    manifest_data = [{"fixture_id": "Q1"}, {"fixture_id": "Q2"}]
    
    preflight_path = tmp_path / "pre.json"
    with open(preflight_path, "w") as f: json.dump(preflight_data, f)
    manifest_path = tmp_path / "man.json"
    with open(manifest_path, "w") as f: json.dump(manifest_data, f)
        
    with pytest.raises(ValueError, match="Preflight has FAIL eligibility for Q2"):
        run_t1_11_execution(str(preflight_path), str(manifest_path), str(tmp_path / "out"), "dummy")

def test_seal_rejects_unexpected_pending(tmp_path):
    preflight_data = {"fixtures": [
        {"fixture_id": "Q1", "eligibility_status": "PASS", "dimension_preflight_status": "PRECONDITIONS_PASS_PENDING_ENGINE"},
        {"fixture_id": "Q4", "eligibility_status": "PASS", "dimension_preflight_status": "PRECONDITIONS_PASS_PENDING_ENGINE"},
        {"fixture_id": "Q11", "eligibility_status": "PASS", "dimension_preflight_status": "PRECONDITIONS_PASS_PENDING_ENGINE"},
        {"fixture_id": "Q14", "eligibility_status": "PASS", "dimension_preflight_status": "PRECONDITIONS_PASS_PENDING_ENGINE"}
    ]}
    manifest_data = [{"fixture_id": "Q1"}, {"fixture_id": "Q4"}, {"fixture_id": "Q11"}, {"fixture_id": "Q14"}]
    
    preflight_path = tmp_path / "pre.json"
    with open(preflight_path, "w") as f: json.dump(preflight_data, f)
    manifest_path = tmp_path / "man.json"
    with open(manifest_path, "w") as f: json.dump(manifest_data, f)
        
    with pytest.raises(ValueError, match="Expected exactly Q4, Q11, Q14 to be pending engine"):
        # We test seal creation which calls validate_preflight_and_manifest
        with patch("chessheat.validation.t1_11_runner.verify_preflight_reproducibility"):
            create_execution_seal(str(manifest_path), "dummy", str(preflight_path), "dummy", str(tmp_path / "out"))

@patch("chessheat.validation.t1_11_runner.ValidationHarness")
def test_runner_execution_logic(mock_harness_class, tmp_path):
    mock_harness = MagicMock()
    mock_harness_class.return_value = mock_harness
    
    # Q4: median 10 < median 11 => SUPPORTED
    # Q11: mate present => SUPPORTED
    # Q14: primary median != twin median => SUPPORTED
    
    def mock_eval(fen):
        if "w" in fen:
            # white to move, primary
            if "rnbqkbnr/pppp1ppp/8/4p3/4P3/8/PPPP1PPP/RNBQKBNR w KQkq - 0 2" in fen: # Q4 fake
                outcomes = {
                    "e4e5": {"score": {"type": "cp", "value": 10}, "regret": 0},
                    "d4c3": {"score": {"type": "cp", "value": -10}, "regret": 20},
                    "d4e5": {"score": {"type": "cp", "value": 5}, "regret": 5}
                }
                return outcomes, None
            elif "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR" in fen: # Q11 or Q14 primary
                outcomes = {
                    "e2e4": {"score": {"type": "cp", "value": 10}, "regret": 0},
                    "e2e3": {"score": {"type": "mate", "value": 1}, "regret": 0}
                }
                return outcomes, None
        elif "b" in fen:
            outcomes = {
                "a2a4": {"score": {"type": "cp", "value": -5}, "regret": 5}
            }
            return outcomes, None
        return {}, None
        
    mock_harness.evaluate_position.side_effect = mock_eval
    
    preflight_data = {"fixtures": [
        {"fixture_id": "Q1", "eligibility_status": "PASS", "dimension_preflight_status": "PASS", "n11": 1, "n10": 1, "n01": 0, "n00": 0},
        {"fixture_id": "Q4", "eligibility_status": "PASS", "dimension_preflight_status": "PRECONDITIONS_PASS_PENDING_ENGINE", "n11": 1, "n10": 1, "n01": 1, "n00": 1, "m11": ["e4e5"], "m10": ["d4e5"]},
        {"fixture_id": "Q11", "eligibility_status": "PASS", "dimension_preflight_status": "PRECONDITIONS_PASS_PENDING_ENGINE", "n11": 1, "n10": 1, "n01": 1, "n00": 1},
        {"fixture_id": "Q14", "eligibility_status": "PASS", "dimension_preflight_status": "PRECONDITIONS_PASS_PENDING_ENGINE", "n11": 1, "n10": 1, "n01": 1, "n00": 1, "m11": ["e2e4"], "dimension_evidence": {"twin_partitions": {"m11": ["a2a4"]}}}
    ]}
    
    manifest_data = [
        {"fixture_id": "Q1", "human_hypothesis": "", "mechanical_support_condition": "", "pre_move_fen": ""},
        {"fixture_id": "Q4", "human_hypothesis": "", "mechanical_support_condition": "", "pre_move_fen": "rnbqkbnr/pppp1ppp/8/4p3/4P3/8/PPPP1PPP/RNBQKBNR w KQkq - 0 2"},
        {"fixture_id": "Q11", "human_hypothesis": "", "mechanical_support_condition": "", "pre_move_fen": "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"},
        {"fixture_id": "Q14", "human_hypothesis": "", "mechanical_support_condition": "", "pre_move_fen": "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1", "twin_fixture": {"fen": "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR b KQkq - 0 1"}}
    ]
    
    preflight_path = tmp_path / "pre.json"
    with open(preflight_path, "w") as f: json.dump(preflight_data, f)
    manifest_path = tmp_path / "man.json"
    with open(manifest_path, "w") as f: json.dump(manifest_data, f)
    
    run_t1_11_execution(str(preflight_path), str(manifest_path), str(tmp_path / "out"), "dummy")
    
    assert mock_harness.evaluate_position.call_count == 4 # Q4 primary, Q11 primary, Q14 primary, Q14 twin
    
    # Verify results
    with open(tmp_path / "out" / "Q1.json") as f:
        q1 = json.load(f)
        assert q1["engine_invoked"] == False
        assert q1["classification"] == "SUPPORTED"
        
    with open(tmp_path / "out" / "Q4.json") as f:
        q4 = json.load(f)
        assert q4["engine_invoked"] == True
        assert q4["classification"] == "FALSIFIED"
        assert q4["comparison_perspective"] == "root_side"
        
    with open(tmp_path / "out" / "Q11.json") as f:
        q11 = json.load(f)
        assert q11["engine_invoked"] == True
        assert q11["classification"] == "SUPPORTED" # Mate is present
        assert q11["raw_typed_scores"]["e2e3"]["type"] == "mate"
        
    with open(tmp_path / "out" / "Q14.json") as f:
        q14 = json.load(f)
        assert q14["engine_invoked"] == True
        assert q14["classification"] == "SUPPORTED" # Primary median (0) != Twin median (None)
        
    with open(tmp_path / "out" / "aggregate_summary.json") as f:
        agg = json.load(f)
        assert agg["total_fixtures"] == 4
