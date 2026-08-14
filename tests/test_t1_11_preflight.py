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
