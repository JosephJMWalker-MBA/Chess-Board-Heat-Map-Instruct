import argparse
import hashlib
import json
import os
import sys

import chess.engine

sys.path.insert(0, os.path.abspath("src"))
from chessheat.experiment import SufficientPosition, SuiteManifest, SuiteKind, ExperimentSpec
from chessheat.semantics import SemanticSignatureV1

def exit_error(msg):
    print(msg, file=sys.stderr)
    sys.exit(1)

def get_file_sha(path):
    with open(path, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()

def main():
    parser = argparse.ArgumentParser(description="T3b-8A Pre-search Producer Identity & Canonical S1 Spec Freeze")
    parser.add_argument("--engine", required=True, help="Absolute path to the engine executable")
    args = parser.parse_args()

    engine_path = os.path.realpath(args.engine)
    
    if not os.path.exists(engine_path):
        exit_error("Engine path does not exist")
    if not os.path.isfile(engine_path):
        exit_error("Engine path is not a regular file")
    if not os.access(engine_path, os.X_OK):
        exit_error("Engine is not executable")
        
    engine_binary_sha256 = get_file_sha(engine_path)

    manifest_path = "docs/research/t3/t3b7_matched_fixture_manifest.json"
    actual_manifest_sha = get_file_sha(manifest_path)
    if actual_manifest_sha != "40949ceeaa5ff1cd1c8a083df45f0dbe0f252d3f1637a692dbf96ae98156ad13":
        exit_error("MANIFEST_SHA_MISMATCH")

    with open(manifest_path, "r", encoding="utf-8") as f:
        manifest = json.load(f)

    if manifest["fixture_count"] != 16: exit_error("manifest error")
    if manifest["expected_future_search_count"] != 171: exit_error("manifest error")
    if manifest["comparison_perspective"] != "white": exit_error("manifest error")
    if manifest["engine_observations_present"] is not False: exit_error("manifest error")
    if manifest["consequence_observations_present"] is not False: exit_error("manifest error")
    if manifest["semantic_signature_version"] != "1.0": exit_error("manifest error")
    if manifest["semantic_signature_digest"] != "5fa4d57cf43c673fa31874ce5d19e777acf0ea695fd032412b193c2123461080": exit_error("manifest error")
    if manifest["s1_suite_digest"] != "b483e152cbfd51704f62befabdfd2a9f7880999a199409b63253802a965ed6d7": exit_error("manifest error")

    fixtures_dict = {fix["fixture_identity"]: fix["fixture_content_digest"] for fix in manifest["fixtures"]}
    suite = SuiteManifest(
        suite_id="t3b7_matched_intervention_v1",
        kind=SuiteKind.MECHANISM_STRESS,
        fixtures=fixtures_dict
    )
    if suite.suite_digest() != "b483e152cbfd51704f62befabdfd2a9f7880999a199409b63253802a965ed6d7":
        exit_error("SUITE_DIGEST_RECONSTRUCTION_MISMATCH")
        
    canonical_sig = SemanticSignatureV1.create_canonical()
    if canonical_sig.version != "1.0":
        exit_error("SEMANTIC_SIGNATURE_VERSION_MISMATCH")
    if canonical_sig.signature_hash() != "5fa4d57cf43c673fa31874ce5d19e777acf0ea695fd032412b193c2123461080":
        exit_error("SEMANTIC_SIGNATURE_DIGEST_MISMATCH")

    engine = chess.engine.SimpleEngine.popen_uci(engine_path)
    try:
        observed_uci_name = engine.id.get("name", "")
        if observed_uci_name != "Stockfish 18":
            exit_error("PRODUCER_IDENTITY_MISMATCH")
            
        options = engine.options
        if "Threads" not in options or "Hash" not in options:
            exit_error("REQUIRED_OPTIONS_NOT_FOUND")
            
        engine.configure({"Threads": 1, "Hash": 16})
        
        specs = []
        spec_digests = set()
        
        for fixture in manifest["fixtures"]:
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
            if sd in spec_digests:
                exit_error("NON_UNIQUE_SPEC_DIGEST")
            spec_digests.add(sd)
            
            specs.append({
                "fixture_identity": fixture["fixture_identity"],
                "fixture_digest": fixture["fixture_content_digest"],
                "spec": spec.model_dump(mode="json"),
                "spec_digest": sd
            })
            
        sum_required_searches = sum(fixture["required_search_count"] for fixture in manifest["fixtures"])
        if sum_required_searches != 171:
            exit_error("REQUIRED_SEARCHES_NOT_171")

        artifact = {
            "schema_version": 1,
            "phase": "PRESEARCH_PRODUCER_IDENTITY_AND_S1_SPEC_FREEZE",
            "protocol_commit": manifest["protocol_commit"],
            "manifest_integrity_commit": "4099a8a9def8d177614258d3289210f9da44e7cf",
            "manifest_sha256": "40949ceeaa5ff1cd1c8a083df45f0dbe0f252d3f1637a692dbf96ae98156ad13",
            "s1_suite_digest": "b483e152cbfd51704f62befabdfd2a9f7880999a199409b63253802a965ed6d7",
            "semantic_signature_version": "1.0",
            "semantic_signature_digest": "5fa4d57cf43c673fa31874ce5d19e777acf0ea695fd032412b193c2123461080",
            "observed_uci_engine_name": observed_uci_name,
            "resolved_executable_path": engine_path,
            "engine_binary_sha256": engine_binary_sha256,
            "Threads": 1,
            "Hash": 16,
            "nodes_per_required_child": 100000,
            "comparison_perspective": "white",
            "fixture_count": 16,
            "expected_future_search_count": 171,
            "engine_identity_observation_present": True,
            "chess_position_search_count": 0,
            "chess_position_engine_observations_present": False,
            "consequence_observations_present": False,
            "specs": specs
        }
        
        out_path = "docs/research/t3/t3b8_presearch_spec_bundle.json"
        with open(out_path, "wb") as f:
            f.write(json.dumps(artifact, sort_keys=True, indent=2, ensure_ascii=False).encode("utf-8") + b"\n")
            
        print(f"Bundle written to {out_path}")
        print(f"Bundle SHA-256: {get_file_sha(out_path)}")
        
    finally:
        engine.quit()

if __name__ == "__main__":
    main()
