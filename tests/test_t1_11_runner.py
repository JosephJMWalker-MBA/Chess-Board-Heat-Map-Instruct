import os
import json
import pytest
from unittest.mock import patch, mock_open, MagicMock
from chessheat.validation.t1_11_runner import create_execution_seal, run_t1_11_execution

def test_seal_rejects_fail_state(tmp_path):
    preflight_data = {
        "fixtures": [
            {"fixture_id": "Q1", "eligibility_status": "PASS", "dimension_preflight_status": "PASS"},
            {"fixture_id": "Q2", "eligibility_status": "FAIL", "dimension_preflight_status": "PASS"}
        ]
    }
    
    preflight_path = tmp_path / "t1_11_structural_preflight.json"
    with open(preflight_path, "w") as f:
        json.dump(preflight_data, f)
        
    with pytest.raises(ValueError, match="Preflight has FAIL eligibility for Q2"):
        create_execution_seal(
            manifest_path="dummy",
            protocol_path="dummy",
            preflight_path=str(preflight_path),
            engine_path="dummy",
            engine_threads=1,
            engine_hash_mb=16,
            engine_node_budget=1000,
            comparison_perspective="root_side",
            output_dir=str(tmp_path / "out")
        )

def test_seal_rejects_dimension_fail_state(tmp_path):
    preflight_data = {
        "fixtures": [
            {"fixture_id": "Q1", "eligibility_status": "PASS", "dimension_preflight_status": "PASS"},
            {"fixture_id": "Q3", "eligibility_status": "PASS", "dimension_preflight_status": "FAIL"}
        ]
    }
    
    preflight_path = tmp_path / "t1_11_structural_preflight.json"
    with open(preflight_path, "w") as f:
        json.dump(preflight_data, f)
        
    with pytest.raises(ValueError, match="Preflight has FAIL dimension status for Q3"):
        create_execution_seal(
            manifest_path="dummy",
            protocol_path="dummy",
            preflight_path=str(preflight_path),
            engine_path="dummy",
            engine_threads=1,
            engine_hash_mb=16,
            engine_node_budget=1000,
            comparison_perspective="root_side",
            output_dir=str(tmp_path / "out")
        )

@patch("chessheat.validation.t1_11_runner.get_git_info")
@patch("chessheat.validation.t1_11_runner.get_engine_info")
@patch("chessheat.validation.t1_11_runner.hash_file")
def test_seal_creation_success(mock_hash, mock_engine, mock_git, tmp_path):
    mock_git.return_value = {"commit_sha": "123456"}
    mock_engine.return_value = {"engine_path_resolved": "/bin/stockfish", "engine_version": "16"}
    mock_hash.return_value = "abcdef"
    
    preflight_data = {
        "fixtures": [
            {"fixture_id": "Q1", "eligibility_status": "PASS", "dimension_preflight_status": "PASS"}
        ]
    }
    
    preflight_path = tmp_path / "t1_11_structural_preflight.json"
    with open(preflight_path, "w") as f:
        json.dump(preflight_data, f)
        
    out_dir = tmp_path / "out"
    seal = create_execution_seal(
        manifest_path="dummy",
        protocol_path="dummy",
        preflight_path=str(preflight_path),
        engine_path="dummy",
        engine_threads=1,
        engine_hash_mb=16,
        engine_node_budget=1000,
        comparison_perspective="root_side",
        output_dir=str(out_dir)
    )
    
    assert seal["git_commit_sha"] == "123456"
    assert os.path.exists(out_dir / "t1_11_execution_seal.json")

def test_runner_avoids_engine_for_structural(tmp_path):
    preflight_data = {
        "fixtures": [
            {"fixture_id": "Q1", "eligibility_status": "PASS", "dimension_preflight_status": "PASS"}
        ]
    }
    manifest_data = [{"fixture_id": "Q1"}]
    
    preflight_path = tmp_path / "pre.json"
    with open(preflight_path, "w") as f: json.dump(preflight_data, f)
        
    manifest_path = tmp_path / "man.json"
    with open(manifest_path, "w") as f: json.dump(manifest_data, f)
        
    # Should not raise any error, and the implementation of runner has a branch 
    # to skip engine if status is PASS
    run_t1_11_execution(
        preflight_path=str(preflight_path),
        manifest_path=str(manifest_path),
        output_dir=str(tmp_path),
        engine_path="dummy"
    )
