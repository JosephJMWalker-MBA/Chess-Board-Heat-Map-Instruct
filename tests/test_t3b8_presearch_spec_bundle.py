import json
import hashlib
import sys
import os
import ast

sys.path.insert(0, os.path.abspath("src"))
from chessheat.experiment import SufficientPosition, SuiteManifest, SuiteKind, ExperimentSpec
from chessheat.semantics import SemanticSignatureV1

def get_file_sha(path):
    with open(path, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()

def test_t3b8_presearch_spec_bundle():
    manifest_path = "docs/research/t3/t3b7_matched_fixture_manifest.json"
    manifest_sha = get_file_sha(manifest_path)
    assert manifest_sha == "40949ceeaa5ff1cd1c8a083df45f0dbe0f252d3f1637a692dbf96ae98156ad13"
    
    with open(manifest_path, "r", encoding="utf-8") as f:
        manifest = json.load(f)
        
    canonical_sig = SemanticSignatureV1.create_canonical()
    assert canonical_sig.version == "1.0"
    assert canonical_sig.signature_hash() == "5fa4d57cf43c673fa31874ce5d19e777acf0ea695fd032412b193c2123461080"
    
    fixtures_dict = {fix["fixture_identity"]: fix["fixture_content_digest"] for fix in manifest["fixtures"]}
    suite = SuiteManifest(
        suite_id="t3b7_matched_intervention_v1",
        kind=SuiteKind.MECHANISM_STRESS,
        fixtures=fixtures_dict
    )
    suite_digest = suite.suite_digest()
    assert suite_digest == "b483e152cbfd51704f62befabdfd2a9f7880999a199409b63253802a965ed6d7"
    
    bundle_path = "docs/research/t3/t3b8_presearch_spec_bundle.json"
    bundle_sha = get_file_sha(bundle_path)
    EXPECTED_BUNDLE_SHA = "6ce6b91d3839998f2b9f24c3c6368cbb30cf799c1e8ddaeb9a9a3dcfc54e957b"
    assert bundle_sha == EXPECTED_BUNDLE_SHA
    
    with open(bundle_path, "r", encoding="utf-8") as f:
        bundle = json.load(f)
        
    assert bundle["schema_version"] == 1
    assert bundle["phase"] == "PRESEARCH_PRODUCER_IDENTITY_AND_S1_SPEC_FREEZE"
    assert bundle["protocol_commit"] == manifest["protocol_commit"]
    assert bundle["manifest_integrity_commit"] == "4099a8a9def8d177614258d3289210f9da44e7cf"
    assert bundle["manifest_sha256"] == manifest_sha
    assert bundle["s1_suite_digest"] == suite_digest
    assert bundle["semantic_signature_version"] == "1.0"
    assert bundle["semantic_signature_digest"] == "5fa4d57cf43c673fa31874ce5d19e777acf0ea695fd032412b193c2123461080"
    
    assert bundle["observed_uci_engine_name"] == "Stockfish 18"
    assert bundle["Threads"] == 1
    assert bundle["Hash"] == 16
    assert bundle["nodes_per_required_child"] == 100000
    assert bundle["comparison_perspective"] == "white"
    assert bundle["fixture_count"] == 16
    assert bundle["expected_future_search_count"] == 171
    assert bundle["engine_identity_observation_present"] is True
    assert bundle["chess_position_search_count"] == 0
    assert bundle["chess_position_engine_observations_present"] is False
    assert bundle["consequence_observations_present"] is False
    
    observed_uci_name = bundle["observed_uci_engine_name"]
    engine_binary_sha256 = bundle["engine_binary_sha256"]
    
    assert observed_uci_name == "Stockfish 18"
    assert engine_binary_sha256 == "ae4c93fa9676ca7750d0714342fd8a5b1d018000fc6e0f6cedf112067b5ef374"
    assert bundle["resolved_executable_path"] == "/opt/homebrew/Cellar/stockfish/18/bin/stockfish"
    
    assert len(bundle["specs"]) == 16
    spec_digests = set()
    
    for i, fixture in enumerate(manifest["fixtures"]):
        bspec = bundle["specs"][i]
        
        sp_data = fixture["sufficient_position"]
        validated_sufficient_position = SufficientPosition(**sp_data)
        
        candidate_policy = {
            "scope": "t3b7_matched_observation_universe",
            "target_square": fixture["target_event"]["square"],
            "event_reply_ucis": fixture["C_reply_ucis"],
            "c_1": fixture["c_1"],
            "c_2": fixture["c_2"],
            "M_1_ucis": fixture["M_1_ucis"],
            "M_2_ucis": fixture["M_2_ucis"],
            "H_1_ucis": fixture["H_1_ucis"],
            "H_2_ucis": fixture["H_2_ucis"],
            "observation_reply_ucis": fixture["observation_reply_ucis"],
            "required_search_count": fixture["required_search_count"],
        }
        
        instrument_config = {
            "binary_sha256": engine_binary_sha256,
            "Threads": 1,
            "Hash": 16,
            "acquisition_process_policy": "one_uninterrupted_process",
            "hash_reset_between_searches": False,
            "resume_allowed": False,
        }
        
        spec = ExperimentSpec(
            semantic_signature_version="1.0",
            semantic_signature_digest="5fa4d57cf43c673fa31874ce5d19e777acf0ea695fd032412b193c2123461080",
            suite_identity="t3b7_matched_intervention_v1",
            suite_digest="b483e152cbfd51704f62befabdfd2a9f7880999a199409b63253802a965ed6d7",
            fixture_identity=fixture["fixture_identity"],
            fixture_digest=fixture["fixture_content_digest"],
            sufficient_position=validated_sufficient_position,
            candidate_policy=candidate_policy,
            producer_identity=observed_uci_name,
            instrument_config=instrument_config,
            budget_config={"type": "nodes", "value": 100000},
            line_source="none",
            hypothesis_identifier="T3b-7",
            spec_version=2,
            comparison_perspective="white",
        )
        
        sd = spec.spec_digest()
        
        assert bspec["fixture_identity"] == fixture["fixture_identity"]
        assert bspec["fixture_digest"] == fixture["fixture_content_digest"]
        assert bspec["spec_digest"] == sd
        assert bspec["spec"] == spec.model_dump(mode="json")
        
        spec_digests.add(sd)
        
    assert len(spec_digests) == 16
    
    def reject_keys(obj):
        bad_keys = {"outcome", "score", "cp", "mate", "evaluation", "pv", "principal_variation", "regret", "S", "Q", "Delta"}
        if isinstance(obj, dict):
            for k, v in obj.items():
                assert k not in bad_keys, f"Found rejected key {k}"
                reject_keys(v)
        elif isinstance(obj, list):
            for item in obj:
                reject_keys(item)
                
    reject_keys(bundle)
    
    # Zero-search invariant check via AST
    generator_path = "scripts/prepare_t3b8_s1_specs.py"
    with open(generator_path, "r", encoding="utf-8") as f:
        tree = ast.parse(f.read())
        
    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            if isinstance(node.func, ast.Attribute):
                if isinstance(node.func.value, ast.Name) and node.func.value.id == "engine":
                    assert node.func.attr in {"configure", "quit"}, f"Disallowed engine call: {node.func.attr}"
                if node.func.attr in {"analyse", "analysis", "play"}:
                    assert False, f"Disallowed callable: {node.func.attr}"
        elif isinstance(node, ast.Constant) and isinstance(node.value, str):
            val = node.value.strip().lower()
            if val == "go" or val.startswith("go "):
                assert False, f"Disallowed string literal: {node.value}"

if __name__ == "__main__":
    test_t3b8_presearch_spec_bundle()
    print("Test passed.")
