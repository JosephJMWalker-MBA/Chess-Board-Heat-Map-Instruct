import argparse
import hashlib
import json
import os
import sys
import subprocess

import chess
import chess.engine

sys.path.insert(0, os.path.abspath("src"))
from chessheat.experiment import SufficientPosition, SuiteManifest, SuiteKind, ExperimentSpec, ExperimentResult

def exit_error(msg):
    print(msg, file=sys.stderr)
    sys.exit(1)

def get_file_sha(path):
    with open(path, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()

def main():
    parser = argparse.ArgumentParser(description="T3b-8B Matched Acquisition Executor")
    parser.add_argument("--engine", required=True, help="Path to Stockfish")
    parser.add_argument("--authorized-execution-commit", required=True, help="Full SHA")
    args = parser.parse_args()

    # 1. Future invocation must be explicit
    engine_path = os.path.realpath(args.engine)
    if not os.path.exists(engine_path):
        exit_error("Engine path does not exist")
    if not os.path.isfile(engine_path):
        exit_error("Engine path is not a regular file")
    if not os.access(engine_path, os.X_OK):
        exit_error("Engine is not executable")
        
    engine_sha256 = get_file_sha(engine_path)
    if engine_sha256 != "ae4c93fa9676ca7750d0714342fd8a5b1d018000fc6e0f6cedf112067b5ef374":
        exit_error("ENGINE_SHA256_MISMATCH")

    # 2. Require reviewed-code identity
    try:
        head_commit = subprocess.check_output(["git", "rev-parse", "HEAD"]).decode("utf-8").strip()
        status_out = subprocess.check_output(["git", "status", "--porcelain"]).decode("utf-8").strip()
    except subprocess.CalledProcessError:
        exit_error("EXECUTION_CODE_IDENTITY_FAILURE")

    if head_commit != args.authorized_execution_commit:
        exit_error("EXECUTION_CODE_IDENTITY_FAILURE")
    if status_out != "":
        exit_error("EXECUTION_CODE_IDENTITY_FAILURE")

    # 3. Freeze input bytes before engine startup
    manifest_path = "docs/research/t3/t3b7_matched_fixture_manifest.json"
    bundle_path = "docs/research/t3/t3b8_presearch_spec_bundle.json"
    
    manifest_sha = get_file_sha(manifest_path)
    if manifest_sha != "40949ceeaa5ff1cd1c8a083df45f0dbe0f252d3f1637a692dbf96ae98156ad13":
        exit_error("MANIFEST_SHA_MISMATCH")
        
    bundle_sha = get_file_sha(bundle_path)
    if bundle_sha != "6ce6b91d3839998f2b9f24c3c6368cbb30cf799c1e8ddaeb9a9a3dcfc54e957b":
        exit_error("BUNDLE_SHA_MISMATCH")

    with open(manifest_path, "r", encoding="utf-8") as f:
        manifest = json.load(f)
    with open(bundle_path, "r", encoding="utf-8") as f:
        bundle = json.load(f)

    fixtures_dict = {fix["fixture_identity"]: fix["fixture_content_digest"] for fix in manifest["fixtures"]}
    suite = SuiteManifest(
        suite_id="t3b7_matched_intervention_v1",
        kind=SuiteKind.MECHANISM_STRESS,
        fixtures=fixtures_dict
    )
    if suite.suite_digest() != "b483e152cbfd51704f62befabdfd2a9f7880999a199409b63253802a965ed6d7":
        exit_error("SUITE_DIGEST_MISMATCH")

    if bundle["fixture_count"] != 16: exit_error("BUNDLE_STATE_MISMATCH")
    if bundle["expected_future_search_count"] != 171: exit_error("BUNDLE_STATE_MISMATCH")
    if bundle["observed_uci_engine_name"] != "Stockfish 18": exit_error("BUNDLE_STATE_MISMATCH")
    if bundle["engine_binary_sha256"] != "ae4c93fa9676ca7750d0714342fd8a5b1d018000fc6e0f6cedf112067b5ef374": exit_error("BUNDLE_STATE_MISMATCH")
    if bundle["Threads"] != 1: exit_error("BUNDLE_STATE_MISMATCH")
    if bundle["Hash"] != 16: exit_error("BUNDLE_STATE_MISMATCH")
    if bundle["nodes_per_required_child"] != 100000: exit_error("BUNDLE_STATE_MISMATCH")
    if bundle["comparison_perspective"] != "white": exit_error("BUNDLE_STATE_MISMATCH")
    if bundle["chess_position_search_count"] != 0: exit_error("BUNDLE_STATE_MISMATCH")
    if bundle["consequence_observations_present"] is not False: exit_error("BUNDLE_STATE_MISMATCH")

    spec_digests_frozen = []
    for f_idx, fixture in enumerate(manifest["fixtures"]):
        bspec = bundle["specs"][f_idx]
        sp_data = fixture["sufficient_position"]
        validated_sufficient_position = SufficientPosition(**sp_data)
        
        spec = ExperimentSpec(**bspec["spec"])
        sd = spec.spec_digest()
        if sd != bspec["spec_digest"]:
            exit_error("SPEC_DIGEST_RECONSTRUCTION_FAILURE")
        spec_digests_frozen.append(sd)

    # 4. Preconstruct the complete search plan
    search_plan = []
    global_search_index = 0
    
    for f_idx, fixture in enumerate(manifest["fixtures"]):
        b_fixture = bundle["specs"][f_idx]
        policy = b_fixture["spec"]["candidate_policy"]
        obs_ucis = policy["observation_reply_ucis"]
        man_obs_ucis = fixture["observation_reply_ucis"]
        
        if obs_ucis != man_obs_ucis:
            exit_error("OBSERVATION_REPLY_MISMATCH")
        if obs_ucis != sorted(obs_ucis):
            exit_error("OBSERVATION_REPLY_NOT_SORTED")
        if policy["required_search_count"] != len(obs_ucis):
            exit_error("REQUIRED_SEARCH_COUNT_MISMATCH")
            
        req_children = {child["uci"]: child["child_fen"] for child in fixture["required_children"]}
            
        for reply_uci in obs_ucis:
            intervention_fen = fixture["intervention_fen"]
            board = chess.Board(intervention_fen)
            move = chess.Move.from_uci(reply_uci)
            
            if not board.is_legal(move):
                exit_error("ILLEGAL_REPLY_IN_PLAN")
                
            board.push(move)
            child_fen = board.fen(shredder=False, en_passant="fen")
            
            if child_fen != req_children[reply_uci]:
                exit_error("CHILD_FEN_RECONSTRUCTION_MISMATCH")
                
            search_plan.append({
                "global_search_index": global_search_index,
                "fixture_identity": fixture["fixture_identity"],
                "fixture_index": fixture["fixture_index"],
                "spec_digest": spec_digests_frozen[f_idx],
                "reply_uci": reply_uci,
                "intervention_fen": intervention_fen,
                "expected_child_fen": child_fen
            })
            global_search_index += 1
            
    if len(search_plan) != 171:
        exit_error("SEARCH_PLAN_LENGTH_MISMATCH")

    # 5. No prior acquisition attempt
    started_path = "tests/fixtures/t3b8/t3b8_acquisition_started.json"
    raw_path = "tests/fixtures/t3b8/t3b8_raw_acquisition.json"
    
    if os.path.exists(started_path) or os.path.exists(raw_path):
        exit_error("ACQUISITION_ALREADY_ATTEMPTED")

    # 6. Future engine process
    engine = chess.engine.SimpleEngine.popen_uci(engine_path)
    engine_started = True
    marker_created = False
    
    try:
        observed_uci_name = engine.id.get("name", "")
        if observed_uci_name != "Stockfish 18":
            exit_error("PRODUCER_IDENTITY_MISMATCH")
            
        engine.configure({
            "Threads": 1,
            "Hash": 16,
        })
        
        # 7. Freeze the no-resume attempt boundary
        os.makedirs(os.path.dirname(started_path), exist_ok=True)
        
        attempt_marker = {
            "schema_version": 1,
            "phase": "T3B8_MATCHED_ACQUISITION_STARTED",
            "execution_code_commit": head_commit,
            "manifest_sha256": manifest_sha,
            "presearch_bundle_sha256": bundle_sha,
            "s1_suite_digest": "b483e152cbfd51704f62befabdfd2a9f7880999a199409b63253802a965ed6d7",
            "observed_uci_engine_name": observed_uci_name,
            "resolved_executable_path": engine_path,
            "engine_binary_sha256": engine_sha256,
            "Threads": 1,
            "Hash": 16,
            "nodes_per_required_child": 100000,
            "comparison_perspective": "white",
            "expected_search_count": 171,
            "acquisition_order": "fixture_index ascending then reply UCI ASCII-lexicographic",
            "chess_position_search_count_at_marker": 0,
            "resume_allowed": False
        }
        
        try:
            with open(started_path, "x", encoding="utf-8") as f:
                f.write(json.dumps(attempt_marker, sort_keys=True, indent=2, ensure_ascii=False) + "\n")
        except FileExistsError:
            exit_error("ACQUISITION_ALREADY_ATTEMPTED")
            
        marker_created = True
        attempt_marker_sha256 = get_file_sha(started_path)

        # 8. Exactly one uninterrupted acquisition process
        game_token = object()
        results_by_fixture = {i: [] for i in range(16)}
        
        for plan in search_plan:
            child_board = chess.Board(plan["expected_child_fen"])
            
            info = engine.analyse(
                child_board,
                chess.engine.Limit(nodes=100000),
                info=chess.engine.INFO_SCORE,
                game=game_token,
                multipv=None,
                root_moves=None,
            )
            
            # 9. Preserve typed White-perspective outcomes exactly
            if "score" not in info:
                raise ValueError("MISSING_SCORE")
                
            score = info["score"].white()
            if score.is_mate():
                outcome = {
                    "type": "mate",
                    "value": score.mate(),
                    "perspective": "white"
                }
            else:
                s_val = score.score()
                if not isinstance(s_val, int):
                    raise ValueError("SCORE_NOT_INTEGER")
                outcome = {
                    "type": "cp",
                    "value": s_val,
                    "perspective": "white"
                }
                
            obs = {
                "uci": plan["reply_uci"],
                "child_fen": plan["expected_child_fen"],
                "outcome": outcome
            }
            results_by_fixture[plan["fixture_index"]].append(obs)
            
        # 11. Build canonical S1 ExperimentResults
        actual_search_count = sum(len(obs) for obs in results_by_fixture.values())
        if actual_search_count != 171:
            raise ValueError("ACTUAL_SEARCH_COUNT_MISMATCH")
            
        experiment_results = []
        result_digests = set()
        
        for f_idx in range(16):
            fixture = manifest["fixtures"][f_idx]
            spec_digest = spec_digests_frozen[f_idx]
            
            result = ExperimentResult.create(
                spec_digest=spec_digest,
                data={
                    "fixture_identity": fixture["fixture_identity"],
                    "fixture_index": fixture["fixture_index"],
                    "comparison_perspective": "white",
                    "search_count": fixture["required_search_count"],
                    "observed_replies": results_by_fixture[f_idx]
                }
            )
            
            rd = result.artifact_digest
            if rd in result_digests:
                raise ValueError("NON_UNIQUE_RESULT_DIGEST")
            result_digests.add(rd)
            
            experiment_results.append({
                "fixture_identity": fixture["fixture_identity"],
                "fixture_index": fixture["fixture_index"],
                "spec_digest": spec_digest,
                "experiment_result": result.model_dump(mode="json")
            })

        # 12. Future raw acquisition artifact
        raw_artifact = {
            "schema_version": 1,
            "phase": "T3B8_MATCHED_RAW_ACQUISITION",
            "protocol_commit": manifest["protocol_commit"],
            "manifest_integrity_commit": "4099a8a9def8d177614258d3289210f9da44e7cf",
            "presearch_spec_commit": "fe87cd0f3b6a86c37125b4e08905624183f363c8",
            "presearch_integrity_commit": "6cb9c467bde75bfa6ff56f2430ba43ea375be1d9",
            "execution_code_commit": head_commit,
            "manifest_sha256": manifest_sha,
            "presearch_bundle_sha256": bundle_sha,
            "s1_suite_digest": "b483e152cbfd51704f62befabdfd2a9f7880999a199409b63253802a965ed6d7",
            "observed_uci_engine_name": observed_uci_name,
            "resolved_executable_path": engine_path,
            "engine_binary_sha256": engine_sha256,
            "Threads": 1,
            "Hash": 16,
            "nodes_per_required_child": 100000,
            "comparison_perspective": "white",
            "acquisition_process_policy": "one_uninterrupted_process",
            "hash_reset_between_searches": False,
            "resume_allowed": False,
            "acquisition_order": "fixture_index ascending then reply UCI ASCII-lexicographic",
            "expected_search_count": 171,
            "actual_search_count": 171,
            "attempt_marker_sha256": attempt_marker_sha256,
            "fixture_count": 16,
            "fixtures": experiment_results
        }
        
        try:
            with open(raw_path, "x", encoding="utf-8") as f:
                f.write(json.dumps(raw_artifact, sort_keys=True, indent=2, ensure_ascii=False) + "\n")
        except FileExistsError:
            raise ValueError("RAW_ACQUISITION_ALREADY_EXISTS")
            
        print(f"Raw acquisition SHA-256: {get_file_sha(raw_path)}")
        
    except Exception as e:
        if marker_created:
            exit_error(f"GLOBAL_ACQUISITION_FAILURE_AFTER_START: {e}")
        else:
            exit_error(f"PREFLIGHT_FAILURE: {e}")
            
    finally:
        if engine_started:
            engine.quit()

if __name__ == "__main__":
    main()
