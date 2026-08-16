import json
import hashlib
import pytest

MANIFEST_PATH = "docs/research/t3/t3b2_fixture_manifest.json"
EXPECTED_SHA = "27321ceb4bf5c48716d836f9d4433c017be3a127e94b6d1508bd8973e0d23bc0"

FORBIDDEN_KEYS = {
    "score",
    "cp",
    "mate",
    "evaluation",
    "principal_variation",
    "parsed_pv",
    "regret",
    "s_u",
    "q_u",
    "delta_u",
    "classification",
    "expected_direction"
}

def check_no_forbidden_keys(obj):
    if isinstance(obj, dict):
        for k, v in obj.items():
            if k.lower() in FORBIDDEN_KEYS:
                raise ValueError(f"Forbidden key found in manifest: {k}")
            check_no_forbidden_keys(v)
    elif isinstance(obj, list):
        for item in obj:
            check_no_forbidden_keys(item)

def test_manifest_integrity():
    # 1. Bind exact manifest bytes
    with open(MANIFEST_PATH, "rb") as f:
        manifest_bytes = f.read()
    
    actual_sha = hashlib.sha256(manifest_bytes).hexdigest()
    assert actual_sha == EXPECTED_SHA, f"Manifest SHA mismatch. Expected {EXPECTED_SHA}, got {actual_sha}"
    
    manifest = json.loads(manifest_bytes.decode("utf-8"))
    
    # 2. Bind top-level identity
    assert manifest["schema_version"] == 1
    assert manifest["generator_id"] == "T3B2_V1"
    assert manifest["protocol_commit"] == "3281d05b4ebf9bc65520504dc3e045c47dafcac4"
    assert manifest["chess_version"] == "1.11.2"
    assert manifest["python_version"] == "3.13.5"
    assert manifest["fixture_count"] == 12
    assert manifest["history_available"] is False
    assert manifest["history_identity"] is None
    assert manifest["engine_observations_present"] is False
    
    hep = manifest["historical_exposure_provenance"]
    assert hep["total_raw_extracted_states"] == 414
    assert hep["total_unique_canonical_states"] == 414
    assert hep["canonical_exposure_digest"] == "a4342f713a22ccc3c4790fcc220136b2f78f16e5f014d7a195f26d6fd8842476"
    
    # 3. Bind the frozen corpus headline identity
    fixtures = manifest["fixtures"]
    assert len(fixtures) == 12
    
    fixture_indices = [f["fixture_index"] for f in fixtures]
    assert fixture_indices == list(range(12))
    
    game_indices = [f["game_index"] for f in fixtures]
    assert game_indices == list(range(12))
    
    for f in fixtures:
        assert f["half_move_index"] == 12
        
    final_fixture = fixtures[11]
    assert final_fixture["fixture_index"] == 11
    assert final_fixture["game_index"] == 11
    assert final_fixture["half_move_index"] == 12
    assert final_fixture["white_root_uci"] == "a2a3"
    assert final_fixture["target_event"]["square"] == "c4"
    assert final_fixture["C_reply_ucis"] == ["b5c4", "d5c4"]
    
    # 4. Recursively prohibit engine/result fields
    check_no_forbidden_keys(manifest)
