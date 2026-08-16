import chess
import hashlib
import json

def get_pseudo_random_move(board, g, p):
    legal_ucis = sorted(m.uci() for m in board.legal_moves)
    msg = f"T3A4_V1:{g}:{p}".encode("utf-8")
    digest_hex = hashlib.sha256(msg).hexdigest()
    digest_int = int(digest_hex, 16)
    idx = digest_int % len(legal_ucis)
    return chess.Move.from_uci(legal_ucis[idx])

def evaluate_eligibility(fen):
    fixture_board = chess.Board(fen)
    
    if not fixture_board.is_valid():
        return None
    if fixture_board.is_game_over(claim_draw=False):
        return None
    if fixture_board.turn != chess.WHITE:
        return None
    if fixture_board.is_check():
        return None

    legal_roots = list(fixture_board.legal_moves)
    
    # Check if every legal root gives Black at least one legal reply
    for root in legal_roots:
        fixture_board.push(root)
        replies = list(fixture_board.legal_moves)
        fixture_board.pop()
        if len(replies) == 0:
            return None

    qualifying_squares = []
    square_evaluations = {}

    for s in chess.SQUARES:
        piece = fixture_board.piece_at(s)
        if piece and piece.color == chess.WHITE and piece.piece_type != chess.KING:
            # Evaluate L_fi for all roots
            l_mapping = {}
            for root in legal_roots:
                root_uci = root.uci()
                # If the piece at s moved, then it's not preserved.
                if root.from_square == s:
                    l_mapping[root_uci] = 0
                else:
                    fixture_board.push(root)
                    has_capture = False
                    for reply in fixture_board.legal_moves:
                        if fixture_board.is_capture(reply) and reply.to_square == s:
                            has_capture = True
                            break
                    fixture_board.pop()
                    l_mapping[root_uci] = 1 if has_capture else 0

            count_1 = sum(1 for v in l_mapping.values() if v == 1)
            count_0 = sum(1 for v in l_mapping.values() if v == 0)

            if count_1 >= 2 and count_0 >= 2:
                sq_name = chess.square_name(s)
                qualifying_squares.append(sq_name)
                square_evaluations[sq_name] = {
                    "l_mapping": l_mapping,
                    "target_piece": piece,
                    "count_1": count_1,
                    "count_0": count_0
                }

    if not qualifying_squares:
        return None

    target_sq_name = min(qualifying_squares)
    return {
        "target_square": target_sq_name,
        "eval_data": square_evaluations[target_sq_name],
        "sorted_roots": sorted(r.uci() for r in legal_roots)
    }

def generate_corpus():
    exclusions = {
        "4k3/8/1b6/8/3R4/8/8/4K3 w - - 0 1",
        "4k3/8/1n6/8/2B5/8/8/4K3 w - - 0 1"
    }

    accepted_fens = set()
    fixtures = []
    final_g = -1
    final_p = -1

    for g in range(10000):
        board = chess.Board()
        p = 0

        while not board.is_game_over(claim_draw=False) and p <= 80:
            if 12 <= p <= 80:
                fen = board.fen(shredder=False, en_passant="fen")
                if fen not in accepted_fens and fen not in exclusions:
                    eligibility = evaluate_eligibility(fen)
                    if eligibility is not None:
                        accepted_fens.add(fen)
                        
                        target_sq = eligibility["target_square"]
                        eval_data = eligibility["eval_data"]
                        target_piece = eval_data["target_piece"]
                        
                        l_mapping = eval_data["l_mapping"]
                        sorted_roots = eligibility["sorted_roots"]
                        
                        opp_present = sorted([r for r, v in l_mapping.items() if v == 1])
                        opp_absent = sorted([r for r, v in l_mapping.items() if v == 0])

                        b_recon = chess.Board(fen)
                        ep_sq = chess.square_name(b_recon.ep_square) if b_recon.ep_square else "-"
                        castling = b_recon.castling_xfen()
                        if not castling: castling = "-"

                        fixtures.append({
                            "fixture_index": len(fixtures),
                            "game_index": g,
                            "half_move_index": p,
                            "fen": fen,
                            "target_square": target_sq,
                            "original_target_piece_color": "white",
                            "original_target_piece_type": target_piece.piece_type,
                            "original_target_piece_symbol": target_piece.symbol(),
                            "event": {
                                "square": target_sq,
                                "role": "capture",
                                "ply": 2
                            },
                            "exact_sorted_legal_white_root_uci_set": sorted_roots,
                            "exact_root_count": len(sorted_roots),
                            "root_uci_to_L_fi_mapping": l_mapping,
                            "sorted_opportunity_present_roots": opp_present,
                            "sorted_opportunity_absent_roots": opp_absent,
                            "L_equals_1_count": eval_data["count_1"],
                            "L_equals_0_count": eval_data["count_0"],
                            "sufficient_position_fields": {
                                "board_arrangement": fen.split(" ")[0],
                                "side_to_move": fen.split(" ")[1],
                                "castling": castling,
                                "en_passant": ep_sq,
                                "halfmove": b_recon.halfmove_clock,
                                "fullmove": b_recon.fullmove_number,
                                "history_unavailable": True,
                                "history_available": False,
                                "history_identity": None,
                                "variant": "standard"
                            }
                        })
                        
                        if len(fixtures) == 12:
                            final_g = g
                            final_p = p
                            break

            if p == 80:
                break

            move = get_pseudo_random_move(board, g, p)
            board.push(move)
            p += 1

        if len(fixtures) == 12:
            break

    if len(fixtures) < 12:
        return None, final_g, final_p

    manifest = {
        "schema_identifier": "T3a-4_Corpus_Manifest",
        "schema_version": "1.0",
        "protocol_commit_sha": "6c599dc2b2705f3958274aef06d8aab15bd8e616",
        "generator_identifier": "T3A4_V1",
        "executing_chess_version": chess.__version__,
        "fixture_count": len(fixtures),
        "history_contract": {
            "history_available": False,
            "history_identity": None
        },
        "engine_observations_present": False,
        "fixtures": fixtures
    }
    
    return manifest, final_g, final_p

def main():
    manifest, final_g, final_p = generate_corpus()
    if manifest is None:
        print("INSUFFICIENT_QUALIFYING_RULE_ONLY_FIXTURES")
        exit(1)

    with open("docs/research/t3/t3a4_corpus_manifest.json", "w") as f:
        json.dump(manifest, f, indent=2)

    print(f"Accepted 12 fixtures ending at game {final_g}, ply {final_p}.")

if __name__ == "__main__":
    main()
