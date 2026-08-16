import json
import hashlib
import sys
import os
import subprocess
import chess
import chess.engine

PROTOCOL_COMMIT = "3281d05b4ebf9bc65520504dc3e045c47dafcac4"
MANIFEST_COMMIT = "f31b616a44894eacf8f489aedff6628209e2afd1"
INTEGRITY_COMMIT = "65b288ed4c1343b46105a9fcf6afccf860dfbc7b"
MANIFEST_SHA = "27321ceb4bf5c48716d836f9d4433c017be3a127e94b6d1508bd8973e0d23bc0"

def get_git_commit():
    return subprocess.check_output(["git", "rev-parse", "HEAD"]).decode("utf-8").strip()

def run_execution():
    if os.path.exists("tests/fixtures/t3b3/t3b3_raw_execution.json"):
        print("GLOBAL_ACQUISITION_PROVENANCE_FAILURE: Output file already exists")
        sys.exit(1)
        
    execution_code_commit = get_git_commit()
    
    with open("docs/research/t3/t3b2_fixture_manifest.json", "rb") as f:
        manifest_bytes = f.read()
        if hashlib.sha256(manifest_bytes).hexdigest() != MANIFEST_SHA:
            print("GLOBAL_ACQUISITION_PROVENANCE_FAILURE: Manifest SHA mismatch")
            sys.exit(1)
            
    manifest = json.loads(manifest_bytes.decode("utf-8"))
    
    # Verify identities
    assert manifest["schema_version"] == 1
    assert manifest["generator_id"] == "T3B2_V1"
    assert manifest["protocol_commit"] == PROTOCOL_COMMIT
    assert manifest["chess_version"] == "1.11.2"
    assert manifest["python_version"] == "3.13.5"
    assert manifest["fixture_count"] == 12
    assert manifest["history_available"] is False
    assert manifest["history_identity"] is None
    assert manifest["engine_observations_present"] is False
    
    # Compute total search count
    expected_search_count = sum(len(f["legal_reply_ucis"]) for f in manifest["fixtures"])
    if expected_search_count != 362:
        print(f"GLOBAL_ACQUISITION_PROVENANCE_FAILURE: Expected 362 searches, got {expected_search_count}")
        sys.exit(1)
        
    # Resolve engine
    engine_path = "stockfish"
    try:
        resolved_path = subprocess.check_output(["which", engine_path]).decode("utf-8").strip()
    except subprocess.CalledProcessError:
        print("GLOBAL_ACQUISITION_PROVENANCE_FAILURE: Engine not found")
        sys.exit(1)
        
    with open(resolved_path, "rb") as f:
        engine_sha = hashlib.sha256(f.read()).hexdigest()
        
    game_token = object()
    
    engine = chess.engine.SimpleEngine.popen_uci(resolved_path)
    try:
        if engine.id.get("name") != "Stockfish 18":
            print("GLOBAL_ACQUISITION_PROVENANCE_FAILURE: Engine is not Stockfish 18")
            engine.quit()
            sys.exit(1)
            
        engine.configure({"Threads": 1, "Hash": 16})
        
        actual_search_count = 0
        raw_output_fixtures = []
        
        for fixture in sorted(manifest["fixtures"], key=lambda x: x["fixture_index"]):
            intervention_fen = fixture["intervention_fen"]
            pi_board = chess.Board(intervention_fen)
            
            raw_replies = []
            reply_ucis = sorted(fixture["legal_reply_ucis"])
            
            for reply_uci in reply_ucis:
                move = chess.Move.from_uci(reply_uci)
                child_board = pi_board.copy()
                child_board.push(move)
                child_fen = child_board.fen(shredder=False, en_passant="fen")
                
                # Check it matches manifest precisely
                manifest_child_fen = next(r["child_fen"] for r in fixture["replies"] if r["uci"] == reply_uci)
                if child_fen != manifest_child_fen:
                    print(f"GLOBAL_ACQUISITION_PROVENANCE_FAILURE: Child FEN mismatch for {reply_uci}")
                    sys.exit(1)
                    
                limit = chess.engine.Limit(nodes=100000)
                info = engine.analyse(child_board, limit, info=chess.engine.INFO_SCORE, game=game_token, multipv=None, root_moves=None)
                
                score = info["score"].white()
                if score.is_mate():
                    typed_score = {"type": "mate", "value": score.mate(), "perspective": "white"}
                else:
                    typed_score = {"type": "cp", "value": score.score(), "perspective": "white"}
                    
                raw_replies.append({
                    "uci": reply_uci,
                    "child_fen": child_fen,
                    "outcome": typed_score
                })
                
                actual_search_count += 1
                
            raw_output_fixtures.append({
                "fixture_index": fixture["fixture_index"],
                "game_index": fixture["game_index"],
                "half_move_index": fixture["half_move_index"],
                "root_fen": fixture["root_fen"],
                "white_root_uci": fixture["white_root_uci"],
                "intervention_fen": fixture["intervention_fen"],
                "target_event": fixture["target_event"],
                "legal_reply_ucis": fixture["legal_reply_ucis"],
                "C_reply_ucis": fixture["C_reply_ucis"],
                "N_reply_ucis": fixture["N_reply_ucis"],
                "observed_replies": raw_replies
            })
            
        if actual_search_count != 362:
            print("GLOBAL_ACQUISITION_PROVENANCE_FAILURE: Actual search count not 362")
            sys.exit(1)
            
        os.makedirs("tests/fixtures/t3b3", exist_ok=True)
        raw_artifact = {
            "protocol_commit": PROTOCOL_COMMIT,
            "manifest_commit": MANIFEST_COMMIT,
            "manifest_sha": MANIFEST_SHA,
            "integrity_commit": INTEGRITY_COMMIT,
            "execution_code_commit": execution_code_commit,
            "actual_uci_engine_name": engine.id.get("name"),
            "resolved_executable_path": resolved_path,
            "engine_binary_sha256": engine_sha,
            "threads": 1,
            "hash": 16,
            "node_budget": 100000,
            "comparison_perspective": "white",
            "game_state_policy": "one stable game token / one uninterrupted process",
            "acquisition_order": "fixture_index ascending then reply UCI ASCII-lexicographic",
            "expected_search_count": 362,
            "actual_search_count": 362,
            "global_acquisition_sequence_number": 1,
            "fixtures": raw_output_fixtures
        }
        
        output_bytes = json.dumps(raw_artifact, sort_keys=True, indent=2, ensure_ascii=False).encode("utf-8") + b"\n"
        with open("tests/fixtures/t3b3/t3b3_raw_execution.json", "wb") as f:
            f.write(output_bytes)
            
        raw_sha = hashlib.sha256(output_bytes).hexdigest()
        print(f"RAW SHA-256: {raw_sha}")
        
    finally:
        engine.quit()

if __name__ == "__main__":
    run_execution()
