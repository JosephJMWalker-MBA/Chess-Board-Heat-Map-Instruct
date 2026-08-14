import os
import json
import pytest
from unittest.mock import patch
from chessheat.validation.t1_11_preflight import run_preflight

def test_run_preflight(tmp_path):
    # We test that run_preflight doesn't crash on the actual manifest
    # Assuming manifest is already generated
    manifest_path = "docs/research/t1/t1_11_manifest.json"
    if not os.path.exists(manifest_path):
        pytest.skip("Manifest not available to run preflight test")
        
    out_path = tmp_path / "t1_11_structural_preflight.json"
    
    with patch("chessheat.validation.t1_11_preflight.open") as mock_open:
        # We need to mock open to read the real manifest but write to tmp
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
    
    # Assert zero FAIL states
    for f in data["fixtures"]:
        assert f.get("eligibility_status") != "FAIL", f"Fixture {f['fixture_id']} eligibility failed"
        for dim in f.get("dimensions", []):
            assert dim.get("dimension_preflight_status") != "FAIL", f"Fixture {f['fixture_id']} dim {dim['name']} failed"
            
            # Additional assertions based on dimensions
            if dim["name"] == "bundle":
                ev = dim.get("dimension_evidence", {})
                assert len(ev.get("constituent_pairs", [])) >= 2, "Q7 needs at least 2 constituents"
                
            if dim["name"] == "temporal":
                ev = dim.get("dimension_evidence", {})
                assert "intervals" in ev, "Temporal evidence needs intervals"
                
            if dim["name"] == "paired_history":
                ev = dim.get("dimension_evidence", {})
                assert "fen_a" in ev and "fen_b" in ev, "Q13 needs literal fens"
                assert ev["fen_a"] == ev["fen_b"], "Q13 FENs must match"
                assert ev.get("geometry_equality") is True, "Q13 geometry must match"
                assert ev.get("legal_root_equality") is True, "Q13 legal roots must match"
                
            if f["id"] == "Q14" and dim["name"] == "structural_partition":
                ev = dim.get("dimension_evidence", {})
                assert "mapped_partitions_from_primary" in ev, "Q14 needs mapped partitions"
