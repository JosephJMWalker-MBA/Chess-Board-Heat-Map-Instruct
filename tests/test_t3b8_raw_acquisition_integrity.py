import hashlib
import json
import os
import sys

import chess

sys.path.insert(0, os.path.abspath("src"))
from chessheat.experiment import ExperimentSpec, ExperimentResult, SufficientPosition

def get_file_sha(path):
    with open(path, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()

def assert_canonical_serialization(path, parsed):
    with open(path, "rb") as f:
        actual_bytes = f.read()
    expected_bytes = json.dumps(parsed, sort_keys=True, indent=2, ensure_ascii=False).encode("utf-8") + b"\n"
    assert actual_bytes == expected_bytes, f"File {path} does not match canonical JSON serialization"

def test_t3b8_raw_acquisition_integrity():
    marker_path = "tests/fixtures/t3b8/t3b8_acquisition_started.json"
    raw_path = "tests/fixtures/t3b8/t3b8_raw_acquisition.json"
    manifest_path = "docs/research/t3/t3b7_matched_fixture_manifest.json"
    bundle_path = "docs/research/t3/t3b8_presearch_spec_bundle.json"
    
    # 1. Bind exact artifact bytes
    marker_sha = get_file_sha(marker_path)
    raw_sha = get_file_sha(raw_path)
    manifest_sha = get_file_sha(manifest_path)
    bundle_sha = get_file_sha(bundle_path)
    
    assert marker_sha == "253951b3e2353c07868c301680ce215cab0d17ca6c984394f867ae6dfb8500ca"
    assert raw_sha == "5d89d9efde0b140bd134a4e9e3e57092120619acf335c05fcbd2bb9bf1d09b2e"
    assert manifest_sha == "40949ceeaa5ff1cd1c8a083df45f0dbe0f252d3f1637a692dbf96ae98156ad13"
    assert bundle_sha == "6ce6b91d3839998f2b9f24c3c6368cbb30cf799c1e8ddaeb9a9a3dcfc54e957b"
    
    with open(marker_path, "r", encoding="utf-8") as f: marker = json.load(f)
    with open(raw_path, "r", encoding="utf-8") as f: raw = json.load(f)
    with open(manifest_path, "r", encoding="utf-8") as f: manifest = json.load(f)
    with open(bundle_path, "r", encoding="utf-8") as f: bundle = json.load(f)
        
    assert_canonical_serialization(marker_path, marker)
    assert_canonical_serialization(raw_path, raw)
    
    # 2. Validate the permanent attempt marker
    assert marker["schema_version"] == 1
    assert marker["phase"] == "T3B8_MATCHED_ACQUISITION_STARTED"
    assert marker["execution_code_commit"] == "e72cbeb5702e0c5424198ef08a4a3ca3dd6fdc21"
    assert marker["expected_search_count"] == 171
    assert marker["chess_position_search_count_at_marker"] == 0
    assert marker["observed_uci_engine_name"] == "Stockfish 18"
    assert marker["engine_binary_sha256"] == "ae4c93fa9676ca7750d0714342fd8a5b1d018000fc6e0f6cedf112067b5ef374"
    assert marker["Threads"] == 1
    assert marker["Hash"] == 16
    assert marker["nodes_per_required_child"] == 100000
    assert marker["comparison_perspective"] == "white"
    assert marker["resume_allowed"] is False
    
    assert raw["attempt_marker_sha256"] == marker_sha
    
    # 3. Validate raw top-level provenance exactly
    assert raw["schema_version"] == 1
    assert raw["phase"] == "T3B8_MATCHED_RAW_ACQUISITION"
    assert raw["protocol_commit"] == manifest["protocol_commit"]
    assert raw["manifest_integrity_commit"] == "4099a8a9def8d177614258d3289210f9da44e7cf"
    assert raw["presearch_spec_commit"] == "fe87cd0f3b6a86c37125b4e08905624183f363c8"
    assert raw["presearch_integrity_commit"] == "6cb9c467bde75bfa6ff56f2430ba43ea375be1d9"
    assert raw["execution_code_commit"] == marker["execution_code_commit"]
    assert raw["manifest_sha256"] == manifest_sha
    assert raw["presearch_bundle_sha256"] == bundle_sha
    assert raw["s1_suite_digest"] == bundle["s1_suite_digest"]
    assert raw["s1_suite_digest"] == "b483e152cbfd51704f62befabdfd2a9f7880999a199409b63253802a965ed6d7"
    
    assert raw["observed_uci_engine_name"] == marker["observed_uci_engine_name"]
    assert raw["engine_binary_sha256"] == marker["engine_binary_sha256"]
    assert raw["Threads"] == marker["Threads"]
    assert raw["Hash"] == marker["Hash"]
    assert raw["nodes_per_required_child"] == marker["nodes_per_required_child"]
    assert raw["comparison_perspective"] == marker["comparison_perspective"]
    
    assert raw["acquisition_process_policy"] == "one_uninterrupted_process"
    assert raw["hash_reset_between_searches"] is False
    assert raw["resume_allowed"] is False
    assert raw["acquisition_order"] == "fixture_index ascending then reply UCI ASCII-lexicographic"
    
    assert raw["expected_search_count"] == 171
    assert raw["actual_search_count"] == 171
    assert raw["fixture_count"] == 16
    
    # 4. Independently validate all 16 frozen S1 specs
    spec_digests_frozen = set()
    for entry in bundle["specs"]:
        spec = ExperimentSpec(**entry["spec"])
        sd = spec.spec_digest()
        assert sd == entry["spec_digest"]
        spec_digests_frozen.add(sd)
        
    assert len(spec_digests_frozen) == 16
    
    # 5 & 6. Independently validate every ExperimentResult and observation identities
    artifact_digests = set()
    global_child_fens = set()
    total_observations = 0
    cp_count = 0
    mate_count = 0
    
    assert len(raw["fixtures"]) == 16
    for f_idx, raw_fix in enumerate(raw["fixtures"]):
        assert raw_fix["fixture_index"] == f_idx, "Raw fixtures not ordered by fixture_index"
        
        result_model = ExperimentResult(**raw_fix["experiment_result"])
        reconstructed_result = ExperimentResult.create(
            spec_digest=result_model.spec_digest,
            data=json.loads(result_model.data_payload)
        )
        assert result_model.model_dump() == reconstructed_result.model_dump(), "ExperimentResult reconstruction mismatch"
        
        payload_data = json.loads(result_model.data_payload)
        assert raw_fix["fixture_identity"] == payload_data["fixture_identity"]
        assert raw_fix["fixture_index"] == payload_data["fixture_index"]
        assert raw_fix["spec_digest"] == result_model.spec_digest
        assert result_model.spec_digest in spec_digests_frozen
        
        ad = result_model.artifact_digest
        assert ad not in artifact_digests, "Duplicate ExperimentResult artifact digest"
        artifact_digests.add(ad)
        
        man_fix = manifest["fixtures"][f_idx]
        bun_fix = bundle["specs"][f_idx]
        
        raw_observed_ucis = [obs["uci"] for obs in payload_data["observed_replies"]]
        assert raw_observed_ucis == man_fix["observation_reply_ucis"], "Observation replies out of order or mismatched"
        assert raw_observed_ucis == sorted(raw_observed_ucis), "Observation replies not ASCII sorted"
        
        assert payload_data["search_count"] == len(payload_data["observed_replies"])
        assert man_fix["required_search_count"] == len(payload_data["observed_replies"])
        
        bun_policy = bun_fix["spec"]["candidate_policy"]
        assert bun_policy["required_search_count"] == len(payload_data["observed_replies"])
        assert bun_policy["observation_reply_ucis"] == raw_observed_ucis
        
        req_children_map = {child["uci"]: child["child_fen"] for child in man_fix["required_children"]}
        
        for obs in payload_data["observed_replies"]:
            board = chess.Board(man_fix["intervention_fen"])
            move = chess.Move.from_uci(obs["uci"])
            assert board.is_legal(move)
            board.push(move)
            computed_fen = board.fen(shredder=False, en_passant="fen")
            
            assert computed_fen == obs["child_fen"]
            assert computed_fen == req_children_map[obs["uci"]]
            
            assert computed_fen not in global_child_fens, "Duplicate global child fen"
            global_child_fens.add(computed_fen)
            total_observations += 1
            
            # 7. Audit typed outcomes only
            outcome = obs["outcome"]
            assert outcome["perspective"] == "white"
            assert outcome["type"] in {"cp", "mate"}
            assert isinstance(outcome["value"], int) and not isinstance(outcome["value"], bool)
            
            if outcome["type"] == "cp":
                cp_count += 1
            elif outcome["type"] == "mate":
                mate_count += 1
                
    assert total_observations == 171
    assert len(global_child_fens) == 171
    assert cp_count == 165
    assert mate_count == 6
    assert cp_count + mate_count == 171
    assert len(artifact_digests) == 16
    
    # 8. Prove acquisition contains no downstream analysis
    def reject_keys(obj):
        bad_keys = {
            "G_j", "T_j", "D_j", "S_j", "S_match", "L", "E", "Q", "Q_suite", "H_.75",
            "evaluable", "classification", "supported", "weak_support", "falsified",
            "p_value", "confidence", "significance", "pv", "principal_variation", "multipv"
        }
        if isinstance(obj, dict):
            for k, v in obj.items():
                assert k not in bad_keys, f"Found rejected key {k}"
                reject_keys(v)
        elif isinstance(obj, list):
            for item in obj:
                reject_keys(item)
                
    reject_keys(raw)
    
if __name__ == "__main__":
    test_t3b8_raw_acquisition_integrity()
    print("Test passed.")
