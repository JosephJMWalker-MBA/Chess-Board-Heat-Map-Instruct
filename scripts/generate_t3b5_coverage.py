import chess
import hashlib
import json
import sys
import os

assert chess.__version__ == "1.11.2", f"chess version {chess.__version__} != 1.11.2"

PROTOCOL_COMMIT = "0fdf4a1dc7a017bc8cb14d782f5e00a8e438c979"
MATCHER_COMMIT = "23281ca6d75a239de6f63a6ff542597c1cfc0fc2"

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

def main():
    # Read protocol and matcher file hashes
    protocol_path = "docs/research/t3/T3B5_STRICT_MATCHABILITY_COVERAGE_PROTOCOL.md"
    matcher_path = "docs/research/t3/T3B4_MATCHED_CONTROL_IDENTIFIABILITY_AUDIT.md"
    
    with open(protocol_path, "rb") as f:
        protocol_file_sha256 = hashlib.sha256(f.read()).hexdigest()
    with open(matcher_path, "rb") as f:
        matcher_file_sha256 = hashlib.sha256(f.read()).hexdigest()

    trajectory_records = []
    
    for g in range(256):
        h = int(hashlib.sha256(f"T3B5_COVERAGE_PLY_V1:{g}".encode("utf-8")).hexdigest(), 16)
        sample_p = 13 + 2 * (h % 34)
        
        board = chess.Board()
        p = 0
        
        terminated_before = False
        while p < sample_p:
            if board.is_game_over(claim_draw=False):
                terminated_before = True
                break
            
            legal = sorted(move.uci() for move in board.legal_moves)
            payload = f"T3B5_COVERAGE_MOVE_V1:{g}:{p}".encode("utf-8")
            idx = int(hashlib.sha256(payload).hexdigest(), 16) % len(legal)
            board.push(chess.Move.from_uci(legal[idx]))
            p += 1
            
        record = {
            "g": g,
            "sample_p": sample_p
        }
            
        if terminated_before:
            record["status"] = "TERMINATED_BEFORE_SAMPLE"
            record["eligible"] = False
            trajectory_records.append(record)
            continue
            
        sampled_fen = board.fen(shredder=False, en_passant="fen")
        record["sampled_fen"] = sampled_fen
        record["status"] = "REACHED_SAMPLE"
        
        P_i = chess.Board(sampled_fen)
        
        valid = P_i.is_valid()
        black_to_move = (P_i.turn == chess.BLACK)
        terminal = P_i.is_game_over(claim_draw=False)
        in_check = P_i.is_check()
        
        record["valid"] = valid
        record["black_to_move"] = black_to_move
        record["terminal"] = terminal
        record["in_check"] = in_check
        
        reasons = []
        if not valid:
            reasons.append("INVALID")
        if not black_to_move:
            reasons.append("WRONG_SIDE_TO_MOVE")
        if terminal:
            reasons.append("TERMINATED")
        if in_check:
            reasons.append("IN_CHECK")
            
        record["ineligibility_reasons"] = reasons
        
        eligible = valid and black_to_move and not terminal and not in_check
        record["eligible"] = eligible
        
        if eligible:
            legal_reply_ucis = sorted(move.uci() for move in P_i.legal_moves)
            record["legal_reply_ucis"] = legal_reply_ucis
            record["legal_reply_count"] = len(legal_reply_ucis)
            
            # 6. Enumerate the full legal reply universe
            reply_records = []
            strata_dict = {} # signature tuple -> set of UCIs
            
            for uci in legal_reply_ucis:
                move = chess.Move.from_uci(uci)
                b_strict = get_B_strict_tuple(P_i, move)
                
                reply_records.append({
                    "uci": uci,
                    "origin": chess.square_name(move.from_square),
                    "destination": chess.square_name(move.to_square),
                    "B_strict": list(b_strict)
                })
                
                if b_strict not in strata_dict:
                    strata_dict[b_strict] = set()
                strata_dict[b_strict].add(uci)
                
            record["replies"] = reply_records
            
            # 7. Preserve whole-position exact signature strata
            strata = []
            for b_strict, ucis in strata_dict.items():
                strata.append({
                    "B_strict": list(b_strict),
                    "member_ucis": sorted(ucis),
                    "cardinality": len(ucis)
                })
            
            # Sort by serialized signature and then member UCIs... well, list(b_strict) is comparable
            strata.sort(key=lambda s: (s["B_strict"], s["member_ucis"]))
            record["signature_strata"] = strata
            record["signature_stratum_count"] = len(strata)
            record["sibling_strata_cardinality_ge_2_count"] = sum(1 for s in strata if s["cardinality"] >= 2)
            
            # 8. Enumerate every destination event
            dest_dict = {}
            for uci in legal_reply_ucis:
                move = chess.Move.from_uci(uci)
                dest = chess.square_name(move.to_square)
                if dest not in dest_dict:
                    dest_dict[dest] = []
                dest_dict[dest].append(uci)
                
            destination_squares = sorted(dest_dict.keys())
            
            dest_events = []
            for s in destination_squares:
                C = sorted(dest_dict[s])
                N = sorted(set(legal_reply_ucis) - set(C))
                
                c_tuples = {}
                for c in C:
                    c_tuples[c] = get_B_strict_tuple(P_i, chess.Move.from_uci(c))
                
                n_tuples = {}
                for n in N:
                    n_tuples[n] = get_B_strict_tuple(P_i, chess.Move.from_uci(n))
                    
                event_reply_records = []
                for c in C:
                    c_sig = c_tuples[c]
                    controls = sorted([n for n in N if n_tuples[n] == c_sig])
                    event_reply_records.append({
                        "uci": c,
                        "B_strict": list(c_sig),
                        "matched_control_ucis": controls,
                        "matched_control_count": len(controls)
                    })
                    
                strictly_matchable = (len(C) > 0) and all(err["matched_control_count"] >= 1 for err in event_reply_records)
                strictly_matchable_two_reply = strictly_matchable and (len(C) == 2)
                
                dest_events.append({
                    "square": s,
                    "event": {"square": s, "role": "destination", "ply": 1},
                    "C_reply_ucis": C,
                    "C_cardinality": len(C),
                    "event_reply_records": event_reply_records,
                    "strictly_matchable": strictly_matchable,
                    "strictly_matchable_two_reply": strictly_matchable_two_reply
                })
                
            record["destination_events"] = dest_events
            
            # 9. Record per-state coverage facts
            sm_dest_count = sum(1 for de in dest_events if de["strictly_matchable"])
            sm_2_dest_count = sum(1 for de in dest_events if de["strictly_matchable_two_reply"])
            
            record["represented_destination_count"] = len(dest_events)
            record["strictly_matchable_destination_count"] = sm_dest_count
            record["strictly_matchable_two_reply_destination_count"] = sm_2_dest_count
            record["has_any_strictly_matchable_destination"] = (sm_dest_count > 0)
            record["has_any_strictly_matchable_two_reply_destination"] = (sm_2_dest_count > 0)
            
        trajectory_records.append(record)
        
    # 10. Compute frozen corpus quantities
    eligible_records = [r for r in trajectory_records if r.get("eligible")]
    N_eligible = len(eligible_records)
    M_ge_1 = sum(1 for r in eligible_records if r["has_any_strictly_matchable_destination"])
    M_2 = sum(1 for r in eligible_records if r["has_any_strictly_matchable_two_reply_destination"])
    
    primary_M = M_2
    classification = "FEASIBLE_FOR_MATCHED_PROTOCOL_DESIGN" if primary_M >= 12 else "NOT_FEASIBLE_UNDER_FROZEN_COVERAGE_BUDGET"
    
    # 11. Descriptive distributions
    freq_sm_dest = {}
    freq_sm_2_dest = {}
    freq_sibling_strata = {}
    freq_strata_cards = {}
    
    for r in eligible_records:
        sdc = r["strictly_matchable_destination_count"]
        freq_sm_dest[sdc] = freq_sm_dest.get(sdc, 0) + 1
        
        s2dc = r["strictly_matchable_two_reply_destination_count"]
        freq_sm_2_dest[s2dc] = freq_sm_2_dest.get(s2dc, 0) + 1
        
        ssc = r["sibling_strata_cardinality_ge_2_count"]
        freq_sibling_strata[ssc] = freq_sibling_strata.get(ssc, 0) + 1
        
        for s in r["signature_strata"]:
            card = s["cardinality"]
            freq_strata_cards[card] = freq_strata_cards.get(card, 0) + 1
            
    descriptive_distributions = {
        "strictly_matchable_destination_count": freq_sm_dest,
        "strictly_matchable_two_reply_destination_count": freq_sm_2_dest,
        "sibling_strata_cardinality_ge_2_count": freq_sibling_strata,
        "strict_stratum_cardinalities": freq_strata_cards
    }
    
    ineligibility_counts = {}
    for r in trajectory_records:
        if "ineligibility_reasons" in r:
            for reason in r["ineligibility_reasons"]:
                ineligibility_counts[reason] = ineligibility_counts.get(reason, 0) + 1
                
    terminated_before_sample = sum(1 for r in trajectory_records if r.get("status") == "TERMINATED_BEFORE_SAMPLE")

    # 12. Bind provenance
    artifact = {
        "schema_version": 1,
        "protocol_commit": PROTOCOL_COMMIT,
        "matcher_commit": MATCHER_COMMIT,
        "protocol_file_sha256": protocol_file_sha256,
        "matcher_file_sha256": matcher_file_sha256,
        "generator_id": "T3B5_COVERAGE_V1",
        "move_domain": "T3B5_COVERAGE_MOVE_V1",
        "ply_domain": "T3B5_COVERAGE_PLY_V1",
        "trajectory_count": 256,
        "chess_version": chess.__version__,
        "python_version": sys.version,
        "engine_observations_present": False,
        "consequence_observations_present": False,
        
        "N_eligible": N_eligible,
        "M_ge_1": M_ge_1,
        "M_2": M_2,
        "primary_M": primary_M,
        "classification": classification,
        
        "M_ge_1_over_256": {"numerator": M_ge_1, "denominator": 256, "decimal": M_ge_1/256.0},
        "M_2_over_256": {"numerator": M_2, "denominator": 256, "decimal": M_2/256.0},
        
        "terminated_before_sample": terminated_before_sample,
        "ineligibility_counts": ineligibility_counts,
        "descriptive_distributions": descriptive_distributions,
        
        "trajectory_records": trajectory_records
    }
    
    # 13. Canonical artifact bytes
    canonical_json = json.dumps(
        artifact,
        sort_keys=True,
        indent=2,
        ensure_ascii=False
    ) + "\n"
    
    encoded_bytes = canonical_json.encode("utf-8")
    sha256 = hashlib.sha256(encoded_bytes).hexdigest()
    
    print(f"Artifact SHA-256: {sha256}")
    
    # Output to file
    with open("docs/research/t3/t3b5_coverage_artifact.json", "wb") as f:
        f.write(encoded_bytes)
        
if __name__ == "__main__":
    main()
