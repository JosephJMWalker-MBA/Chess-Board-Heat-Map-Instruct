import chess
import hashlib
import json
import sys
import os

def exit_error(code):
    print(code)
    sys.exit(1)

if chess.__version__ != "1.11.2":
    exit_error("CHESS_VERSION_MISMATCH")

PROTOCOL_COMMIT = "fd54ad04c54e4756ad904f17454b9e70e881afea"
MATCHER_COMMIT = "23281ca6d75a239de6f63a6ff542597c1cfc0fc2"
MATHEMATICS_COMMIT = "100e4f20b41b260875fb14901b61bbe51c4fe74e"

def get_file_sha(path):
    with open(path, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()

PROTOCOL_FILE_PATH = "docs/research/t3/T3B7_RULE_ONLY_MATCHED_FIXTURE_PROTOCOL.md"
MATCHER_FILE_PATH = "docs/research/t3/T3B4_MATCHED_CONTROL_IDENTIFIABILITY_AUDIT.md"
MATHEMATICS_FILE_PATH = "docs/research/t3/T3B6_MATCHED_ESTIMAND_CALIBRATION.md"

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
    if moving_piece is None:
        exit_error("B_STRICT_INVARIANT_FAILURE")
    moving_piece_type = serialize_piece_type(moving_piece.piece_type)
    
    if board.is_en_passant(move):
        capture_mode = "en_passant"
        captured_piece_type = "pawn"
        ep_captured_square = chess.square(chess.square_file(move.to_square), chess.square_rank(move.from_square))
        ep_captured_piece = board.piece_at(ep_captured_square)
        if ep_captured_piece is None or ep_captured_piece.piece_type != chess.PAWN or ep_captured_piece.color == moving_piece.color:
            exit_error("B_STRICT_INVARIANT_FAILURE")
    elif board.is_capture(move):
        capture_mode = "ordinary"
        captured_piece = board.piece_at(move.to_square)
        if captured_piece is None:
            exit_error("B_STRICT_INVARIANT_FAILURE")
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

def canonicalize_fen(fen):
    return chess.Board(fen).fen(shredder=False, en_passant="fen")

def digest_fens(fens):
    sorted_unique = sorted(list(set(fens)))
    digest_input = "\n".join(sorted_unique) + "\n"
    return hashlib.sha256(digest_input.encode("utf-8")).hexdigest()

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

def generate():
    protocol_file_sha256 = get_file_sha(PROTOCOL_FILE_PATH)
    if protocol_file_sha256 != "2b9377a46b5ff54453ec1796b9a5ce8ca3f1e7bf36a112820d9390b69ed819b9":
        exit_error("PROTOCOL_DIGEST_MISMATCH")
    
    matcher_file_sha256 = get_file_sha(MATCHER_FILE_PATH)
    if matcher_file_sha256 != "568fe380107859ed2e8d7aee0ac6f81d95131ac5a25f1f67fb85073653d1a907":
        exit_error("MATCHER_DIGEST_MISMATCH")
        
    mathematics_file_sha256 = get_file_sha(MATHEMATICS_FILE_PATH)
    if mathematics_file_sha256 != "7f395355e2505db8cc24468e541db5f9618d81c206a8f489c30a09607b0ac8a8":
        exit_error("MATHEMATICS_DIGEST_MISMATCH")

    # Historical exposure
    pre_t3b3_canonical_fens = set()
    pre_t3b3_raw_count = 0
    exposure_provenance = []

    for path, expected_sha in HISTORICAL_SOURCES.items():
        if get_file_sha(path) != expected_sha:
            exit_error("HISTORICAL_SOURCE_DIGEST_MISMATCH")
        
        with open(path, "r") as f:
            data = json.load(f)
            
        if "t3a1" in path or "t3a2" in path:
            rule = "top-level fen, observations[*].resulting_fen"
            raw_fens = [data["fen"]]
            if "observations" in data:
                raw_fens.extend([obs["resulting_fen"] for obs in data["observations"]])
        elif "t3a3" in path or "t3a4" in path:
            rule = "top-level fen, move_observations[*].resulting_fen"
            raw_fens = [data["fen"]]
            if "move_observations" in data:
                raw_fens.extend([obs["resulting_fen"] for obs in data["move_observations"]])
        else:
            exit_error("HISTORICAL_EXPOSURE_IDENTITY_MISMATCH")
            
        pre_t3b3_raw_count += len(raw_fens)
        for rfen in raw_fens:
            pre_t3b3_canonical_fens.add(canonicalize_fen(rfen))
            
        exposure_provenance.append({
            "source_path": path,
            "expected_sha256": expected_sha,
            "actual_sha256": expected_sha,
            "extraction_rule": rule
        })

    if len(pre_t3b3_canonical_fens) != 414:
        exit_error("HISTORICAL_EXPOSURE_IDENTITY_MISMATCH")
        
    pre_t3b3_engine_exposure_digest = digest_fens(pre_t3b3_canonical_fens)
    if pre_t3b3_engine_exposure_digest != "a4342f713a22ccc3c4790fcc220136b2f78f16e5f014d7a195f26d6fd8842476":
        exit_error("HISTORICAL_EXPOSURE_IDENTITY_MISMATCH")

    # T3b-3 raw execution
    t3b3_raw_path = "tests/fixtures/t3b3/t3b3_raw_execution.json"
    t3b3_raw_sha = get_file_sha(t3b3_raw_path)
    if t3b3_raw_sha != "9333f9d26480f43f4d64846be498f720892d93d73da5127296e067653b476d6b":
        exit_error("T3B3_RAW_DIGEST_MISMATCH")
        
    with open(t3b3_raw_path, "r") as f:
        t3b3_data = json.load(f)
        
    if t3b3_data.get("actual_search_count") != 362:
        exit_error("T3B3_SEARCH_COUNT_MISMATCH")
        
    t3b3_fens = []
    t3b3_raw_count = 0
    for fixture in t3b3_data.get("fixtures", []):
        legal_reply_ucis = fixture["legal_reply_ucis"]
        observed_replies = fixture.get("observed_replies", [])
        
        observed_ucis = [obs["uci"] for obs in observed_replies]
        if sorted(observed_ucis) != sorted(legal_reply_ucis):
            exit_error("T3B3_REPLY_UNIVERSE_MISMATCH")
            
        for obs in observed_replies:
            t3b3_raw_count += 1
            t3b3_fens.append(canonicalize_fen(obs["child_fen"]))

    if t3b3_raw_count != 362:
        exit_error("T3B3_SEARCH_COUNT_MISMATCH")
        
    t3b3_fens_set = set(t3b3_fens)
    t3b3_observed_child_digest = digest_fens(t3b3_fens_set)
    
    combined_engine_exposure = pre_t3b3_canonical_fens.union(t3b3_fens_set)
    combined_engine_exposure_digest = digest_fens(combined_engine_exposure)

    prior_engine_exposure_provenance = {
        "pre_t3b3_engine_exposure_count": len(pre_t3b3_canonical_fens),
        "pre_t3b3_engine_exposure_digest": pre_t3b3_engine_exposure_digest,
        "t3b3_observed_child_raw_count": t3b3_raw_count,
        "t3b3_observed_child_unique_count": len(t3b3_fens_set),
        "t3b3_observed_child_digest": t3b3_observed_child_digest,
        "combined_prior_engine_exposure_unique_count": len(combined_engine_exposure),
        "combined_prior_engine_exposure_digest": combined_engine_exposure_digest,
        "sources": exposure_provenance,
        "t3b3_raw_execution_sha256": t3b3_raw_sha
    }

    # Prior design states
    t3b2_manifest_path = "docs/research/t3/t3b2_fixture_manifest.json"
    if get_file_sha(t3b2_manifest_path) != "27321ceb4bf5c48716d836f9d4433c017be3a127e94b6d1508bd8973e0d23bc0":
        exit_error("T3B2_MANIFEST_DIGEST_MISMATCH")
        
    with open(t3b2_manifest_path, "r") as f:
        t3b2_data = json.load(f)
        
    t3b2_raw_fens = [fix["intervention_fen"] for fix in t3b2_data.get("fixtures", [])]
    if len(t3b2_raw_fens) != 12:
        exit_error("T3B5_EXTRACTION_COUNT_MISMATCH")
        
    t3b2_canonical = {canonicalize_fen(fen) for fen in t3b2_raw_fens}

    t3b5_artifact_path = "docs/research/t3/t3b5_coverage_artifact.json"
    if get_file_sha(t3b5_artifact_path) != "642006581ce870f0ab0eb4fea6ddeadb07b9796b653bdc7afefa3e09492ecceb":
        exit_error("T3B5_ARTIFACT_DIGEST_MISMATCH")
        
    with open(t3b5_artifact_path, "r") as f:
        t3b5_data = json.load(f)
        
    if t3b5_data.get("trajectory_count") != 256:
        exit_error("T3B5_EXTRACTION_COUNT_MISMATCH")
        
    t3b5_terminated_before_sample = sum(1 for rec in t3b5_data.get("trajectory_records", []) if rec.get("status") == "TERMINATED_BEFORE_SAMPLE")
    if t3b5_terminated_before_sample != 3:
        exit_error("T3B5_EXTRACTION_COUNT_MISMATCH")
        
    t3b5_raw_fens = [rec["sampled_fen"] for rec in t3b5_data.get("trajectory_records", []) if "sampled_fen" in rec and rec["sampled_fen"] is not None]
    if len(t3b5_raw_fens) != 253:
        exit_error("T3B5_EXTRACTION_COUNT_MISMATCH")
        
    t3b5_canonical = {canonicalize_fen(fen) for fen in t3b5_raw_fens}
    
    combined_design_state = t3b2_canonical.union(t3b5_canonical)
    
    prior_design_state_provenance = {
        "t3b2_design_state_raw_count": len(t3b2_raw_fens),
        "t3b2_design_state_unique_count": len(t3b2_canonical),
        "t3b2_design_state_digest": digest_fens(t3b2_canonical),
        "t3b5_design_state_raw_count": len(t3b5_raw_fens),
        "t3b5_design_state_unique_count": len(t3b5_canonical),
        "t3b5_design_state_digest": digest_fens(t3b5_canonical),
        "combined_prior_design_state_unique_count": len(combined_design_state),
        "combined_prior_design_state_digest": digest_fens(combined_design_state)
    }

    # Generate trajectories
    accepted_fixtures = []
    accepted_p_i_fens = set()
    accepted_child_fens = set()
    
    sys.path.insert(0, os.path.abspath("src"))
    from chessheat.semantics import SemanticSignatureV1
    from chessheat.experiment import SufficientPosition, SuiteManifest, SuiteKind

    for g in range(10000):
        if len(accepted_fixtures) == 16:
            break
            
        board = chess.Board()
        p = 0
        fixture_found_for_game = False
        
        while not fixture_found_for_game:
            if board.is_game_over(claim_draw=False):
                break
                
            if p > 79:
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
                                c1_uci = move_ucis[0]
                                c2_uci = move_ucis[1]
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
                        
                        if len(C_reply_ucis) != 2:
                            exit_error("CHILD_RECONSTRUCTION_FAILURE")
                            
                        c_1 = C_reply_ucis[0]
                        c_2 = C_reply_ucis[1]
                        
                        m1_sig = get_B_strict_tuple(P_i, chess.Move.from_uci(c_1))
                        m2_sig = get_B_strict_tuple(P_i, chess.Move.from_uci(c_2))
                        
                        M_1_ucis = sorted([uci for uci in legal_reply_ucis if uci not in C_reply_ucis and get_B_strict_tuple(P_i, chess.Move.from_uci(uci)) == m1_sig])
                        M_2_ucis = sorted([uci for uci in legal_reply_ucis if uci not in C_reply_ucis and get_B_strict_tuple(P_i, chess.Move.from_uci(uci)) == m2_sig])
                        
                        H_1_ucis = sorted(list({c_1}.union(set(M_1_ucis))))
                        H_2_ucis = sorted(list({c_2}.union(set(M_2_ucis))))
                        O_i = sorted(list(set(H_1_ucis).union(set(H_2_ucis))))
                        
                        if not set(H_1_ucis).isdisjoint(set(H_2_ucis)):
                            exit_error("MATCHER_DISJOINTNESS_INVARIANT_FAILURE")
                            
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
                                ep_field = fen_parts[3]
                                en_passant_square = None if ep_field == "-" else ep_field
                                sp = SufficientPosition(
                                    board_arrangement_fen=fen_parts[0],
                                    side_to_move="black",
                                    castling_rights=fen_parts[2],
                                    en_passant_square=en_passant_square,
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

    if len(accepted_fixtures) < 16:
        exit_error("INSUFFICIENT_CALIBRATION_ADMISSIBLE_MATCHED_FIXTURES")
        
    fixtures_dict = {}
    for fix in accepted_fixtures:
        fixtures_dict[fix["fixture_identity"]] = fix["fixture_content_digest"]
        
    suite = SuiteManifest(
        suite_id="t3b7_matched_intervention_v1",
        kind=SuiteKind.MECHANISM_STRESS,
        fixtures=fixtures_dict
    )
    
    semantic_signature = SemanticSignatureV1.create_canonical()
    if semantic_signature.version != "1.0":
        exit_error("CHILD_RECONSTRUCTION_FAILURE") # proxy for generic error
    if semantic_signature.signature_hash() != "5fa4d57cf43c673fa31874ce5d19e777acf0ea695fd032412b193c2123461080":
        exit_error("CHILD_RECONSTRUCTION_FAILURE")
        
    expected_future_search_count = sum(f["required_search_count"] for f in accepted_fixtures)
    
    manifest = {
        "schema_version": 1,
        "protocol_commit": PROTOCOL_COMMIT,
        "matcher_commit": MATCHER_COMMIT,
        "mathematics_commit": MATHEMATICS_COMMIT,
        "generator_id": "T3B7_MATCHED_V1",
        "chess_version": "1.11.2",
        "python_version": sys.version.split()[0],
        "fixture_count": 16,
        "suite_size": 16,
        "K_min": 12,
        "comparison_perspective": "white",
        "evidence_ceiling": "intervention_sensitivity",
        "history_available": False,
        "history_identity": None,
        "engine_observations_present": False,
        "consequence_observations_present": False,
        "expected_future_search_count": expected_future_search_count,
        "semantic_signature_version": "1.0",
        "semantic_signature_digest": "5fa4d57cf43c673fa31874ce5d19e777acf0ea695fd032412b193c2123461080",
        "s1_suite_manifest": suite.model_dump(mode="json"),
        "s1_suite_digest": suite.suite_digest(),
        "protocol_file_sha256": protocol_file_sha256,
        "matcher_file_sha256": matcher_file_sha256,
        "mathematics_file_sha256": mathematics_file_sha256,
        "prior_engine_exposure_provenance": prior_engine_exposure_provenance,
        "prior_design_state_provenance": prior_design_state_provenance,
        "future_instrument_preregistration": {
            "expected_producer_uci_name": "Stockfish 18",
            "Threads": 1,
            "Hash_MB": 16,
            "nodes_per_required_child": 100000
        },
        "fixtures": accepted_fixtures
    }
    
    manifest_bytes = json.dumps(manifest, sort_keys=True, indent=2, ensure_ascii=False) + "\n"
    return manifest_bytes.encode("utf-8")

if __name__ == "__main__":
    bytes1 = generate()
    bytes2 = generate()
    if bytes1 != bytes2:
        exit_error("CHILD_RECONSTRUCTION_FAILURE") # proxy
        
    manifest1 = json.loads(bytes1)
    
    with open("docs/research/t3/t3b7_matched_fixture_manifest_historical.json", "r") as f:
        hist_manifest = json.load(f)
        
    for i in range(16):
        mf = hist_manifest["fixtures"][i]
        rf = manifest1["fixtures"][i]
        
        check_keys = [
            "fixture_identity", "fixture_index", "game_index", "half_move_index",
            "intervention_fen", "qualifying_target_squares", "target_event",
            "legal_reply_ucis", "C_reply_ucis", "c_1", "c_2", "m_1", "m_2",
            "M_1_ucis", "M_2_ucis", "H_1_ucis", "H_2_ucis", "observation_reply_ucis",
            "B_strict", "required_children", "required_search_count"
        ]
        
        for k in check_keys:
            if mf[k] != rf[k]:
                exit_error(f"IDENTITY_REPAIR_FAILURE: {k} changed for fixture {i}")
                
    if hist_manifest["expected_future_search_count"] != manifest1["expected_future_search_count"]:
        exit_error("IDENTITY_REPAIR_FAILURE: expected_future_search_count changed")
        
    with open("docs/research/t3/t3b7_matched_fixture_manifest.json", "wb") as f:
        f.write(bytes1)
    
    sha = hashlib.sha256(bytes1).hexdigest()
    print(f"Manifest SHA-256: {sha}")
    print(f"S1 Suite Digest: {manifest1['s1_suite_digest']}")
    print(f"Protocol SHA: {manifest1['protocol_file_sha256']}")
    print(f"Matcher SHA: {manifest1['matcher_file_sha256']}")
    print(f"Mathematics SHA: {manifest1['mathematics_file_sha256']}")
