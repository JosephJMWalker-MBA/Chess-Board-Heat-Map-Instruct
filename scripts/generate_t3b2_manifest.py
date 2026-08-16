import chess
import hashlib
import json
import sys
from typing import List, Dict, Any, Tuple, Set

PROTOCOL_COMMIT = "3281d05b4ebf9bc65520504dc3e045c47dafcac4"
CHESS_VERSION = "1.11.2"
GENERATOR_ID = "T3B2_V1"

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

def verify_and_extract_exposure_set() -> Tuple[Set[str], int, str, List[Dict[str, Any]]]:
    canonical_fens = set()
    total_raw = 0
    provenance_blocks = []
    
    for path, expected_sha in HISTORICAL_SOURCES.items():
        with open(path, "rb") as f:
            content_bytes = f.read()
            actual_sha = hashlib.sha256(content_bytes).hexdigest()
            if actual_sha != expected_sha:
                print("HISTORICAL_EXPOSURE_SOURCE_DIGEST_MISMATCH")
                sys.exit(1)
        
        data = json.loads(content_bytes.decode("utf-8"))
        
        # Extract fen and resulting_fens based on rules
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
        
        total_raw += len(raw_fens)
        for rfen in raw_fens:
            canonical_fens.add(chess.Board(rfen).fen(shredder=False, en_passant="fen"))
            
        provenance_blocks.append({
            "source_path": path,
            "expected_sha256": expected_sha,
            "actual_sha256": actual_sha,
            "extraction_rule": rule
        })
        
    sorted_unique = sorted(list(canonical_fens))
    digest_input = "\n".join(sorted_unique) + "\n"
    exposure_digest = hashlib.sha256(digest_input.encode("utf-8")).hexdigest()
    
    return canonical_fens, total_raw, exposure_digest, provenance_blocks

def main():
    if chess.__version__ != CHESS_VERSION:
        print(f"Error: python-chess version must be {CHESS_VERSION}")
        sys.exit(1)
        
    exposure_set, total_raw, exposure_digest, exposure_provenance = verify_and_extract_exposure_set()
    
    accepted_fixtures = []
    accepted_roots = set()
    accepted_interventions = set()
    
    for g in range(10000):
        if len(accepted_fixtures) == 12:
            break
            
        board = chess.Board()
        p = 0
        fixture_found_for_game = False
        
        while p <= 80 and not fixture_found_for_game:
            if 12 <= p <= 80:
                root_fen = board.fen(shredder=False, en_passant="fen")
                root = chess.Board(root_fen)
                
                # Check root eligibility
                if root.is_valid() and root.turn == chess.WHITE and not root.is_game_over(claim_draw=False) and not root.is_check():
                    white_roots = sorted(move.uci() for move in root.legal_moves)
                    eligible_tuples = []
                    
                    # Store data to reconstruct if selected
                    tuple_data = {}
                    
                    for w_root_uci in white_roots:
                        pi_board = chess.Board(root_fen)
                        pi_board.push(chess.Move.from_uci(w_root_uci))
                        intervention_fen = pi_board.fen(shredder=False, en_passant="fen")
                        
                        # Check P_i eligibility
                        if pi_board.is_valid() and pi_board.turn == chess.BLACK and not pi_board.is_game_over(claim_draw=False) and not pi_board.is_check():
                            legal_black_replies = list(pi_board.legal_moves)
                            if len(legal_black_replies) >= 6:
                                # Group by destination
                                dest_map = {}
                                for move in legal_black_replies:
                                    dest = chess.square_name(move.to_square)
                                    if dest not in dest_map:
                                        dest_map[dest] = []
                                    dest_map[dest].append(move)
                                    
                                for dest, moves in dest_map.items():
                                    if len(moves) == 2:
                                        # Distinct origin squares
                                        if moves[0].from_square != moves[1].from_square:
                                            # Neither is a promotion
                                            if moves[0].promotion is None and moves[1].promotion is None:
                                                eligible_tuples.append((w_root_uci, dest))
                                                tuple_data[(w_root_uci, dest)] = (intervention_fen, pi_board)
                                                
                    if eligible_tuples:
                        selected_tuple = min(eligible_tuples)
                        w_root_uci, target_square = selected_tuple
                        intervention_fen, pi_board = tuple_data[selected_tuple]
                        
                        c_moves = []
                        n_moves = []
                        reply_ucis = sorted(move.uci() for move in pi_board.legal_moves)
                        
                        for move_uci in reply_ucis:
                            move = chess.Move.from_uci(move_uci)
                            if chess.square_name(move.to_square) == target_square:
                                c_moves.append(move_uci)
                            else:
                                n_moves.append(move_uci)
                                
                        if len(c_moves) == 2 and len(n_moves) >= 4 and len(reply_ucis) >= 6:
                            # Materialize children
                            children_data = []
                            child_fens_to_check = []
                            
                            for move_uci in reply_ucis:
                                move = chess.Move.from_uci(move_uci)
                                child_board = chess.Board(intervention_fen)
                                child_board.push(move)
                                child_fen = child_board.fen(shredder=False, en_passant="fen")
                                child_fens_to_check.append(child_fen)
                                
                                children_data.append({
                                    "uci": move_uci,
                                    "origin_square": chess.square_name(move.from_square),
                                    "destination_square": chess.square_name(move.to_square),
                                    "promotion_piece": chess.piece_name(move.promotion) if move.promotion else None,
                                    "is_capture": pi_board.is_capture(move),
                                    "is_en_passant": pi_board.is_en_passant(move),
                                    "is_castling": pi_board.is_castling(move),
                                    "child_fen": child_fen,
                                    "is_terminal": child_board.is_game_over(claim_draw=False),
                                    "event_member": move_uci in c_moves
                                })
                            
                            # Exposure and uniqueness gates
                            candidate_fens = [root_fen, intervention_fen] + child_fens_to_check
                            exposure_fail = any(f in exposure_set for f in candidate_fens)
                            uniqueness_fail = root_fen in accepted_roots or intervention_fen in accepted_interventions
                            
                            if not exposure_fail and not uniqueness_fail:
                                accepted_roots.add(root_fen)
                                accepted_interventions.add(intervention_fen)
                                
                                fixture = {
                                    "fixture_index": len(accepted_fixtures),
                                    "game_index": g,
                                    "half_move_index": p,
                                    "root_fen": root_fen,
                                    "white_root_uci": w_root_uci,
                                    "intervention_fen": intervention_fen,
                                    "target_event": {
                                        "square": target_square,
                                        "role": "destination",
                                        "ply": 1
                                    },
                                    "t3a_equivalent_ply": 2,
                                    "reply_count": len(reply_ucis),
                                    "legal_reply_ucis": reply_ucis,
                                    "C_reply_ucis": c_moves,
                                    "N_reply_ucis": n_moves,
                                    "replies": children_data,
                                    "intervention_sufficient_position": {
                                        "board_arrangement": intervention_fen.split()[0],
                                        "side_to_move": "black",
                                        "castling": intervention_fen.split()[2],
                                        "en_passant": intervention_fen.split()[3],
                                        "halfmove": intervention_fen.split()[4],
                                        "fullmove": intervention_fen.split()[5],
                                        "history_available": False,
                                        "history_identity": None,
                                        "variant": "standard"
                                    }
                                }
                                accepted_fixtures.append(fixture)
                                fixture_found_for_game = True

            if fixture_found_for_game or p == 80:
                break
                
            if board.is_game_over(claim_draw=False):
                break
                
            legal = sorted(move.uci() for move in board.legal_moves)
            payload = f"T3B2_V1:{g}:{p}".encode("utf-8")
            idx = int(hashlib.sha256(payload).hexdigest(), 16) % len(legal)
            board.push(chess.Move.from_uci(legal[idx]))
            p += 1

    if len(accepted_fixtures) < 12:
        print("INSUFFICIENT_QUALIFYING_RULE_ONLY_FIXTURES")
        sys.exit(1)
        
    manifest = {
        "schema_version": 1,
        "generator_id": GENERATOR_ID,
        "protocol_commit": PROTOCOL_COMMIT,
        "chess_version": CHESS_VERSION,
        "python_version": sys.version.split()[0],
        "fixture_count": len(accepted_fixtures),
        "history_available": False,
        "history_identity": None,
        "engine_observations_present": False,
        "historical_exposure_provenance": {
            "sources": exposure_provenance,
            "total_raw_extracted_states": total_raw,
            "total_unique_canonical_states": len(exposure_set),
            "canonical_exposure_digest": exposure_digest
        },
        "fixtures": accepted_fixtures
    }
    
    with open("docs/research/t3/t3b2_fixture_manifest.json", "w", encoding="utf-8") as f:
        f.write(json.dumps(manifest, sort_keys=True, indent=2, ensure_ascii=False) + "\n")

if __name__ == "__main__":
    main()
