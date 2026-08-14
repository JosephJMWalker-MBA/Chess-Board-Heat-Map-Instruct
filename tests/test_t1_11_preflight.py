import os
import json
import pytest
from unittest.mock import patch
from chessheat.validation.t1_11_preflight import run_preflight

def test_run_preflight(tmp_path):
    manifest_path = "docs/research/t1/t1_11_manifest.json"
    if not os.path.exists(manifest_path):
        pytest.skip("Manifest not available to run preflight test")
        
    out_path = tmp_path / "t1_11_structural_preflight.json"
    
    with patch("chessheat.validation.t1_11_preflight.open") as mock_open:
        original_open = open
        def fake_open(file, mode="r", *args, **kwargs):
            if mode == "w" and "t1_11_structural_preflight.json" in str(file):
                return original_open(out_path, "w", *args, **kwargs)
            return original_open(file, mode, *args, **kwargs)
            
        mock_open.side_effect = fake_open
        run_preflight()
        
    assert os.path.exists(out_path)
    with original_open(out_path, "r") as f:
        data = json.load(f)
        
    assert "fixtures" in data
    assert len(data["fixtures"]) > 0
    
    q_dict = {f["fixture_id"]: f for f in data["fixtures"]}
    
    for f in data["fixtures"]:
        assert f.get("eligibility_status") != "FAIL", f"Fixture {f['fixture_id']} eligibility failed: {f.get('error_msg')}"
        assert f.get("dimension_preflight_status") != "FAIL", f"Fixture {f['fixture_id']} dimension preflight failed"
        
        if f["fixture_id"] in ["Q4", "Q11", "Q14"]:
            assert f["dimension_preflight_status"] == "PRECONDITIONS_PASS_PENDING_ENGINE", f"Fixture {f['fixture_id']} should be PENDING_ENGINE"
        else:
            assert f["dimension_preflight_status"] == "PASS", f"Fixture {f['fixture_id']} should be PASS"

    q5 = q_dict["Q5"]
    assert "computed_duration" in q5["dimension_evidence"]
    assert q5["dimension_evidence"]["computed_duration"] == 1
    assert q5["dimension_evidence"]["right_censored"] is False
    
    q7 = q_dict["Q7"]
    assert len(q7["dimension_evidence"]["bundle_equality_1"]["m11"]) == len(q7["dimension_evidence"]["bundle_equality_2"]["m11"])
    assert set(q7["dimension_evidence"]["bundle_equality_1"]["m11"]) == set(q7["dimension_evidence"]["bundle_equality_2"]["m11"])
    assert set(q7["dimension_evidence"]["bundle_equality_1"]["m10"]) == set(q7["dimension_evidence"]["bundle_equality_2"]["m10"])
    
    q10 = q_dict["Q10"]
    assert len(q10["dimension_evidence"]["intervals"]) >= 2
    assert q10["dimension_evidence"]["reappearance_boolean"] is True
    
    q13 = q_dict["Q13"]
    assert q13["dimension_evidence"]["fen_a"] == q13["dimension_evidence"]["fen_b"]
    assert q13["dimension_evidence"]["geometry_equality"] is True
    assert q13["dimension_evidence"]["legal_root_equality"] is True
    assert q13["dimension_evidence"]["intervals_a"] != q13["dimension_evidence"]["intervals_b"]
    
    q14 = q_dict["Q14"]
    assert q14["dimension_evidence"]["mapped_partitions_from_primary"] == q14["dimension_evidence"]["twin_partitions"]
    
    q15 = q_dict["Q15"]
    assert q15["dimension_evidence"]["tuple_present_when_white_to_move"] is False
    assert q15["dimension_evidence"]["tuple_present_when_black_to_move"] is True
