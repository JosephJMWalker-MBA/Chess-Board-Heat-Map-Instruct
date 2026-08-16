import chess
import hashlib
import json
import sys
import os
import pytest

sys.path.insert(0, os.path.abspath("src"))
from chessheat.semantics import SemanticSignatureV1
from chessheat.experiment import SufficientPosition, SuiteManifest, SuiteKind

EXPECTED_MANIFEST_SHA = "cdb51243f5561a1c18bd8d0667691663360dcf4316364ca0665ea5344de1e8c9"

def get_file_sha(path):
    with open(path, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()

def canonicalize_fen(fen):
    return chess.Board(fen).fen(shredder=False, en_passant="fen")

def digest_fens(fens):
    sorted_unique = sorted(list(set(fens)))
    digest_input = "\n".join(sorted_unique) + "\n"
    return hashlib.sha256(digest_input.encode("utf-8")).hexdigest()

def serialize_piece_type(pt):
    if pt is None:
        return None
    return {
        chess.PAWN: "pawn",
        chess.KNIGHT: "knight",
        chess.BISHOP: "bishop",
        chess.ROOK: "rook",
        chess.QUEEN: "queen",
        chess.KING: "king"
    }[pt]

def get_B_strict_tuple(board, move):
    origin = chess.square_name(move.from_square)
    moving_piece = board.piece_at(move.from_square)
    assert moving_piece is not None
    moving_piece_type = serialize_piece_type(moving_piece.piece_type)
    
    if board.is_en_passant(move):
        capture_mode = "en_passant"
        captured_piece_type = "pawn"
    elif board.is_capture(move):
        capture_mode = "ordinary"
        captured_piece = board.piece_at(move.to_square)
        assert captured_piece is not None
        captured_piece_type = serialize_piece_type(captured_piece.piece_type)
    else:
        capture_mode = "none"
        captured_piece_type = None
        
    promotion_piece_type = serialize_piece_type(move.promotion)
    is_castling = board.is_castling(move)
    
    return (
        origin,
        moving_piece_type,
        capture_mode,
        captured_piece_type,
        promotion_piece_type,
        is_castling
    )

def test_t3b7_manifest_integrity():
    assert chess.__version__ == "1.11.2"
    
    manifest_path = "docs/research/t3/t3b7_matched_fixture_manifest.json"
    actual_sha = get_file_sha(manifest_path)
    assert actual_sha == EXPECTED_MANIFEST_SHA
    
    with open(manifest_path, "r", encoding="utf-8") as f:
        manifest = json.load(f)
        
    # Historical exposure
    HISTORICAL_SOURCES = {
        "tests/fixtures/t3a1_fixture.json": "151a5ad4414ef6caadf4251441b72dfbe934fa0d05bb57aa4dd03c6107f61bf5",
        "tests/fixtures/t3a2_fixture.json": "ec55f31c873292aaefe2229a8b197458b678e6bb3617d6094b22068b8240a1b1",
        "tests/fixtures/t3a3_fixture.json": "8a0f700123697df9892914a7f38f56efbfe09945f2d7752479895a57a70cdf5a",
        "tests/fixtures/t3a4/raw/t3a4_f00.json": "dd102d9b7826dededa21ff54c72e9d92a7350f94a4bce82fff517b5b52cd685d",
        "tests/fixtures/t3a4/raw/t3a4_f01.json": "9601744071efd9b6d39ff94110f8f22b369ad35afc6e8db7f1278a70ed64e4eb",
        "tests/fixtures/t3a4/raw/t3a4_f02.json": "cfa55403c8053e2f2b84bcccec745e150cc261ff1566c6ae87b49dd6ee66d855",
        "tests/fixtures/t3a4/raw/t3a4_f03.json": "71a5927f427f072a65c767a7a75dbedff9b874b3b2a79a324976bf554d6a5e98",
        "tests/fixtures/t3a4/raw/t3a4_f04.json": "f7478bde4c1cd624c4a01c9b2ed1b0601defef0f0888fff91eff1359077cc748",
        "tests/fixtures/t3a4/raw/t3a4_f05.json": "2d0b40d8ca65de1447619c7beee8ba33d0ffb9165eb4012ae8f30df79c2dfd82",
        "tests/fixtures/t3a4/raw/t3a4_f06.json": "2f70e07e98d1a72611f932d815e8339f0bbd1a821ff89cd181f9335f3fe633a0",
        "tests/fixtures/t3a4/raw/t3a4_f07.json": "9d63d91803f9b769ecc3caf8ced4868c7951f461ad326010e85ece0944e7b976",
        "tests/fixtures/t3a4/raw/t3a4_f08.json": "c71be07ec2299159bf86bc2a1454af16513a12261d2b7b46e17f650a40b63031",
        "tests/fixtures/t3a4/raw/t3a4_f09.json": "f3c284a6dfc3f6260aa2fa84a0b26c4046b9a465c52218ce3c14174d24691070",
        "tests/fixtures/t3a4/raw/t3a4_f10.json": "ffa4fa05fc6e251f2e8d3d7a0f536e548717d503d27801b7b08646420fd9bfd7",
        "tests/fixtures/t3a4/raw/t3a4_f11.json": "37cfc3b58962aeeeecc4723d58ef63b5c9ec00e6f588d9c37c53ba9e41368641"
    }

    pre_t3b3_canonical_fens = set()
    for path, expected_sha in HISTORICAL_SOURCES.items():
        assert get_file_sha(path) == expected_sha
        with open(path, "r") as f:
            data = json.load(f)
            
        if "t3a1" in path or "t3a2" in path:
            raw_fens = [data["fen"]]
            if "observations" in data:
                raw_fens.extend([obs["resulting_fen"] for obs in data["observations"]])
        elif "t3a3" in path or "t3a4" in path:
            raw_fens = [data["fen"]]
            if "move_observations" in data:
                raw_fens.extend([obs["resulting_fen"] for obs in data["move_observations"]])
        else:
            assert False
            
        for rfen in raw_fens:
            pre_t3b3_canonical_fens.add(canonicalize_fen(rfen))
            
    assert len(pre_t3b3_canonical_fens) == 414
    assert digest_fens(pre_t3b3_canonical_fens) == "a4342f713a22ccc3c4790fcc220136b2f78f16e5f014d7a195f26d6fd8842476"

    # T3b-3
    t3b3_raw_path = "tests/fixtures/t3b3/t3b3_raw_execution.json"
    assert get_file_sha(t3b3_raw_path) == "9333f9d26480f43f4d64846be498f720892d93d73da5127296e067653b476d6b"
    
    with open(t3b3_raw_path, "r") as f:
        t3b3_data = json.load(f)
        
    assert t3b3_data["actual_search_count"] == 362
    
    t3b3_fens = []
    for fixture in t3b3_data["fixtures"]:
        legal_reply_ucis = fixture["legal_reply_ucis"]
        observed_replies = fixture.get("observed_replies", [])
        
        observed_ucis = [obs["uci"] for obs in observed_replies]
        assert sorted(observed_ucis) == sorted(legal_reply_ucis)
            
        for obs in observed_replies:
            t3b3_fens.append(canonicalize_fen(obs["child_fen"]))

    assert len(t3b3_fens) == 362
    t3b3_fens_set = set(t3b3_fens)
    combined_engine_exposure = pre_t3b3_canonical_fens.union(t3b3_fens_set)

    # T3b-2 / T3b-5 design states
    t3b2_manifest_path = "docs/research/t3/t3b2_fixture_manifest.json"
    assert get_file_sha(t3b2_manifest_path) == "27321ceb4bf5c48716d836f9d4433c017be3a127e94b6d1508bd8973e0d23bc0"
    with open(t3b2_manifest_path, "r") as f:
        t3b2_data = json.load(f)
    t3b2_raw_fens = [fix["intervention_fen"] for fix in t3b2_data["fixtures"]]
    assert len(t3b2_raw_fens) == 12
    t3b2_canonical = {canonicalize_fen(fen) for fen in t3b2_raw_fens}

    t3b5_artifact_path = "docs/research/t3/t3b5_coverage_artifact.json"
    assert get_file_sha(t3b5_artifact_path) == "642006581ce870f0ab0eb4fea6ddeadb07b9796b653bdc7afefa3e09492ecceb"
    with open(t3b5_artifact_path, "r") as f:
        t3b5_data = json.load(f)
        
    assert t3b5_data["trajectory_count"] == 256
    t3b5_terminated_before_sample = sum(1 for rec in t3b5_data["trajectory_records"] if rec.get("status") == "TERMINATED_BEFORE_SAMPLE")
    assert t3b5_terminated_before_sample == 3
    
    t3b5_raw_fens = [rec["sampled_fen"] for rec in t3b5_data["trajectory_records"] if "sampled_fen" in rec and rec["sampled_fen"] is not None]
    assert len(t3b5_raw_fens) == 253
    t3b5_canonical = {canonicalize_fen(fen) for fen in t3b5_raw_fens}
    
    combined_design_state = t3b2_canonical.union(t3b5_canonical)

    # Generate
    accepted_fixtures = []
    accepted_p_i_fens = set()
    accepted_child_fens = set()
    
    for g in range(10000):
        if len(accepted_fixtures) == 16:
            break
            
        board = chess.Board()
        p = 0
        fixture_found_for_game = False
        
        while not fixture_found_for_game:
            if board.is_game_over(claim_draw=False):
                break
                
            if p in (13, 15, 17, 19, 21, 23, 25, 27, 29, 31, 33, 35, 37, 39, 41, 43, 45, 47, 49, 51, 53, 55, 57, 59, 61, 63, 65, 67, 69, 71, 73, 75, 77, 79):
                intervention_fen = board.fen(shredder=False, en_passant="fen")
                P_i = chess.Board(intervention_fen)
                
                if P_i.is_valid() and P_i.turn == chess.BLACK and not P_i.is_game_over(claim_draw=False) and not P_i.is_check():
                    legal_reply_ucis = sorted(move.uci() for move in P_i.legal_moves)
                    dest_map = {}
                    for move_uci in legal_reply_ucis:
                        move = chess.Move.from_uci(move_uci)
                        dest = chess.square_name(move.to_square)
                        if dest not in dest_map:
                            dest_map[dest] = []
                        dest_map[dest].append(move_uci)
                        
                    qualifying_target_squares = []
                    
                    for dest, move_ucis in dest_map.items():
                        if len(move_ucis) == 2:
                            m1 = chess.Move.from_uci(move_ucis[0])
                            m2 = chess.Move.from_uci(move_ucis[1])
                            
                            if m1.from_square != m2.from_square and m1.promotion is None and m2.promotion is None:
                                c1_sig = get_B_strict_tuple(P_i, m1)
                                c2_sig = get_B_strict_tuple(P_i, m2)
                                
                                m1_count = sum(1 for uci in legal_reply_ucis if uci not in move_ucis and get_B_strict_tuple(P_i, chess.Move.from_uci(uci)) == c1_sig)
                                m2_count = sum(1 for uci in legal_reply_ucis if uci not in move_ucis and get_B_strict_tuple(P_i, chess.Move.from_uci(uci)) == c2_sig)
                                
                                if m1_count >= 2 and m2_count >= 2:
                                    qualifying_target_squares.append(dest)
                                    
                    qualifying_target_squares.sort()
                    
                    if qualifying_target_squares:
                        target_square = qualifying_target_squares[0]
                        C_reply_ucis = sorted([uci for uci in legal_reply_ucis if chess.square_name(chess.Move.from_uci(uci).to_square) == target_square])
                        
                        assert len(C_reply_ucis) == 2
                            
                        c_1 = C_reply_ucis[0]
                        c_2 = C_reply_ucis[1]
                        
                        m1_sig = get_B_strict_tuple(P_i, chess.Move.from_uci(c_1))
                        m2_sig = get_B_strict_tuple(P_i, chess.Move.from_uci(c_2))
                        
                        M_1_ucis = sorted([uci for uci in legal_reply_ucis if uci not in C_reply_ucis and get_B_strict_tuple(P_i, chess.Move.from_uci(uci)) == m1_sig])
                        M_2_ucis = sorted([uci for uci in legal_reply_ucis if uci not in C_reply_ucis and get_B_strict_tuple(P_i, chess.Move.from_uci(uci)) == m2_sig])
                        
                        H_1_ucis = sorted(list({c_1}.union(set(M_1_ucis))))
                        H_2_ucis = sorted(list({c_2}.union(set(M_2_ucis))))
                        O_i = sorted(list(set(H_1_ucis).union(set(H_2_ucis))))
                        
                        assert set(H_1_ucis).isdisjoint(set(H_2_ucis))
                            
                        child_fens = []
                        children_data = []
                        B_strict_map = {}
                        
                        for r_uci in O_i:
                            r_move = chess.Move.from_uci(r_uci)
                            child_board = chess.Board(intervention_fen)
                            child_board.push(r_move)
                            child_fen = canonicalize_fen(child_board.fen(shredder=False, en_passant="fen"))
                            child_fens.append(child_fen)
                            
                            children_data.append({
                                "uci": r_uci,
                                "child_fen": child_fen,
                                "is_terminal_claim_draw_false": child_board.is_game_over(claim_draw=False)
                            })
                            
                            B_strict_map[r_uci] = list(get_B_strict_tuple(P_i, r_move))
                            
                        # Identity gates
                        can_p_i = canonicalize_fen(intervention_fen)
                        if can_p_i in combined_engine_exposure or can_p_i in combined_design_state or can_p_i in accepted_p_i_fens:
                            pass # Rejected
                        else:
                            child_fail = False
                            for cf in child_fens:
                                if cf in combined_engine_exposure or cf in combined_design_state or cf in accepted_child_fens:
                                    child_fail = True
                                    break
                                    
                            if not child_fail:
                                # Accept
                                fixture_index = len(accepted_fixtures)
                                fixture_identity = f"t3b7_f{fixture_index:02d}"
                                
                                fen_parts = intervention_fen.split()
                                sp = SufficientPosition(
                                    board_arrangement_fen=fen_parts[0],
                                    side_to_move="black",
                                    castling_rights=fen_parts[2],
                                    en_passant_square=fen_parts[3],
                                    halfmove_clock=int(fen_parts[4]),
                                    fullmove_number=int(fen_parts[5]),
                                    history_available=False,
                                    history_identity=None,
                                    variant="standard"
                                )
                                
                                payload_without_digest = {
                                    "fixture_identity": fixture_identity,
                                    "fixture_index": fixture_index,
                                    "game_index": g,
                                    "half_move_index": p,
                                    "intervention_fen": intervention_fen,
                                    "sufficient_position": sp.model_dump(mode="json"),
                                    "qualifying_target_squares": qualifying_target_squares,
                                    "target_event": {
                                        "square": target_square,
                                        "role": "destination",
                                        "ply": 1
                                    },
                                    "legal_reply_ucis": legal_reply_ucis,
                                    "C_reply_ucis": C_reply_ucis,
                                    "c_1": c_1,
                                    "c_2": c_2,
                                    "m_1": len(M_1_ucis),
                                    "m_2": len(M_2_ucis),
                                    "M_1_ucis": M_1_ucis,
                                    "M_2_ucis": M_2_ucis,
                                    "H_1_ucis": H_1_ucis,
                                    "H_2_ucis": H_2_ucis,
                                    "observation_reply_ucis": O_i,
                                    "B_strict": B_strict_map,
                                    "required_children": children_data,
                                    "required_search_count": len(O_i)
                                }
                                
                                digest_bytes = json.dumps(payload_without_digest, sort_keys=True).encode("utf-8")
                                fixture_content_digest = hashlib.sha256(digest_bytes).hexdigest()
                                
                                fixture_payload = payload_without_digest.copy()
                                fixture_payload["fixture_content_digest"] = fixture_content_digest
                                
                                accepted_fixtures.append(fixture_payload)
                                accepted_p_i_fens.add(can_p_i)
                                for cf in child_fens:
                                    accepted_child_fens.add(cf)
                                
                                fixture_found_for_game = True
                                
            if not fixture_found_for_game:
                legal = sorted(move.uci() for move in board.legal_moves)
                payload = f"T3B7_MATCHED_V1:{g}:{p}".encode("utf-8")
                idx = int(hashlib.sha256(payload).hexdigest(), 16) % len(legal)
                board.push(chess.Move.from_uci(legal[idx]))
                p += 1

    assert len(accepted_fixtures) == 16

    # Compare with manifest
    assert len(manifest["fixtures"]) == 16
    for i in range(16):
        mf = manifest["fixtures"][i]
        rf = accepted_fixtures[i]
        
        # Test exact conditions
        assert mf["fixture_identity"] == f"t3b7_f{i:02d}"
        assert mf["fixture_index"] == i
        
        if i > 0:
            assert mf["game_index"] > manifest["fixtures"][i-1]["game_index"]
            
        assert mf["target_event"]["square"] == mf["qualifying_target_squares"][0]
        assert mf["m_1"] >= 2
        assert mf["m_2"] >= 2
        
        assert set(mf["H_1_ucis"]).isdisjoint(set(mf["H_2_ucis"]))
        assert mf["observation_reply_ucis"] == sorted(list(set(mf["H_1_ucis"]).union(set(mf["H_2_ucis"]))))
        
        for c in mf["C_reply_ucis"]:
            assert c not in mf["M_1_ucis"]
            assert c not in mf["M_2_ucis"]
            
        for key in rf.keys():
            assert rf[key] == mf[key], f"Mismatch for {key} in fixture {i}"
            
    assert len(accepted_p_i_fens) == 16
    assert len(accepted_child_fens) == sum(len(f["observation_reply_ucis"]) for f in accepted_fixtures)
    
    assert not manifest["engine_observations_present"]
    assert not manifest["consequence_observations_present"]
    
    semantic_signature = SemanticSignatureV1.create_canonical()
    assert semantic_signature.version == "1.0"
    assert semantic_signature.signature_hash() == "5fa4d57cf43c673fa31874ce5d19e777acf0ea695fd032412b193c2123461080"
    
    fixtures_dict = {fix["fixture_identity"]: fix["fixture_content_digest"] for fix in accepted_fixtures}
    suite = SuiteManifest(
        suite_id="t3b7_matched_intervention_v1",
        kind=SuiteKind.MECHANISM_STRESS,
        fixtures=fixtures_dict
    )
    assert suite.model_dump(mode="json") == manifest["s1_suite_manifest"]
    assert suite.suite_digest() == manifest["s1_suite_digest"]
    
    expected_future_search_count = sum(f["required_search_count"] for f in accepted_fixtures)
    assert expected_future_search_count == manifest["expected_future_search_count"]

    def reject_keys(obj):
        bad_keys = {"outcome", "score", "cp", "mate", "evaluation", "pv", "principal_variation", "regret", "S", "Q", "Delta", "engine_binary_sha256", "actual_uci_engine_name"}
        if isinstance(obj, dict):
            for k, v in obj.items():
                assert k not in bad_keys, f"Found rejected key {k}"
                reject_keys(v)
        elif isinstance(obj, list):
            for item in obj:
                reject_keys(item)
                
    reject_keys(manifest["fixtures"])
    
if __name__ == "__main__":
    test_t3b7_manifest_integrity()
    print("Test passed.")
