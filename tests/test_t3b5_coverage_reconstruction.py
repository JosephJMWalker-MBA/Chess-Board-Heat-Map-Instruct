import chess
import hashlib
import json
import os

def test_t3b5_coverage_reconstruction():
    # 1. Byte-identity of the artifact
    expected_sha256 = "642006581ce870f0ab0eb4fea6ddeadb07b9796b653bdc7afefa3e09492ecceb"
    artifact_path = "docs/research/t3/t3b5_coverage_artifact.json"
    
    with open(artifact_path, "rb") as f:
        raw_bytes = f.read()
        
    actual_sha256 = hashlib.sha256(raw_bytes).hexdigest()
    assert actual_sha256 == expected_sha256, f"Artifact SHA mismatch: {actual_sha256} != {expected_sha256}"
    
    artifact = json.loads(raw_bytes.decode("utf-8"))
    
    # 2. Recursively reject engine/consequence keys
    def check_keys(obj):
        bad_keys = {
            "score", "cp", "mate", "evaluation", "pv", "principal_variation",
            "regret", "s_u", "q_u", "delta_u", "engine_name", "engine_binary_sha256"
        }
        if isinstance(obj, dict):
            for k, v in obj.items():
                assert k not in bad_keys, f"Found forbidden key: {k}"
                check_keys(v)
        elif isinstance(obj, list):
            for item in obj:
                check_keys(item)
                
    check_keys(artifact)
    
    assert artifact["engine_observations_present"] is False
    assert artifact["consequence_observations_present"] is False
    
    # 3. Independent Reconstruction
    assert chess.__version__ == "1.11.2"
    
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
        moving_piece_type = serialize_piece_type(moving_piece.piece_type)
        
        if board.is_en_passant(move):
            capture_mode = "en_passant"
            captured_piece_type = "pawn"
        elif board.is_capture(move):
            capture_mode = "ordinary"
            captured_piece = board.piece_at(move.to_square)
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
        
    trajectory_records = artifact["trajectory_records"]
    assert len(trajectory_records) == 256
    
    M_ge_1_recon = 0
    M_2_recon = 0
    N_eligible_recon = 0
    
    for record in trajectory_records:
        g = record["g"]
        h = int(hashlib.sha256(f"T3B5_COVERAGE_PLY_V1:{g}".encode("utf-8")).hexdigest(), 16)
        expected_sample_p = 13 + 2 * (h % 34)
        
        assert record["sample_p"] == expected_sample_p
        
        board = chess.Board()
        p = 0
        terminated_before = False
        while p < expected_sample_p:
            if board.is_game_over(claim_draw=False):
                terminated_before = True
                break
            
            legal = sorted(move.uci() for move in board.legal_moves)
            payload = f"T3B5_COVERAGE_MOVE_V1:{g}:{p}".encode("utf-8")
            idx = int(hashlib.sha256(payload).hexdigest(), 16) % len(legal)
            board.push(chess.Move.from_uci(legal[idx]))
            p += 1
            
        if terminated_before:
            assert record["status"] == "TERMINATED_BEFORE_SAMPLE"
            assert record["eligible"] is False
            continue
            
        sampled_fen = board.fen(shredder=False, en_passant="fen")
        assert record["sampled_fen"] == sampled_fen
        
        P_i = chess.Board(sampled_fen)
        valid = P_i.is_valid()
        black_to_move = (P_i.turn == chess.BLACK)
        terminal = P_i.is_game_over(claim_draw=False)
        in_check = P_i.is_check()
        
        assert record["valid"] == valid
        assert record["black_to_move"] == black_to_move
        assert record["terminal"] == terminal
        assert record["in_check"] == in_check
        
        eligible = valid and black_to_move and not terminal and not in_check
        assert record["eligible"] == eligible
        
        if not eligible:
            continue
            
        N_eligible_recon += 1
        
        legal_replies = sorted(move.uci() for move in P_i.legal_moves)
        assert record["legal_reply_ucis"] == legal_replies
        
        # Strata
        strata_dict = {}
        for uci in legal_replies:
            move = chess.Move.from_uci(uci)
            b_strict = get_B_strict_tuple(P_i, move)
            if b_strict not in strata_dict:
                strata_dict[b_strict] = set()
            strata_dict[b_strict].add(uci)
            
        recon_strata = []
        for b_strict, ucis in strata_dict.items():
            recon_strata.append({
                "B_strict": list(b_strict),
                "member_ucis": sorted(ucis),
                "cardinality": len(ucis)
            })
        recon_strata.sort(key=lambda s: (s["B_strict"], s["member_ucis"]))
        assert record["signature_strata"] == recon_strata
        
        # Events
        dest_dict = {}
        for uci in legal_replies:
            move = chess.Move.from_uci(uci)
            dest = chess.square_name(move.to_square)
            if dest not in dest_dict:
                dest_dict[dest] = []
            dest_dict[dest].append(uci)
            
        recon_dest_events = []
        for s in sorted(dest_dict.keys()):
            C = sorted(dest_dict[s])
            N = sorted(set(legal_replies) - set(C))
            
            event_reply_records = []
            strictly_matchable_all_c = True
            
            for c in C:
                move_c = chess.Move.from_uci(c)
                c_sig = get_B_strict_tuple(P_i, move_c)
                
                controls = []
                for n in N:
                    move_n = chess.Move.from_uci(n)
                    n_sig = get_B_strict_tuple(P_i, move_n)
                    if n_sig == c_sig:
                        controls.append(n)
                        
                        # Verify properties independently
                        assert n not in C, "Matched control must not be in C"
                        assert n_sig == c_sig, "Matched control must have exact B_strict"
                        
                controls = sorted(controls)
                
                if len(controls) == 0:
                    strictly_matchable_all_c = False
                    
                event_reply_records.append({
                    "uci": c,
                    "B_strict": list(c_sig),
                    "matched_control_ucis": controls,
                    "matched_control_count": len(controls)
                })
                
            strictly_matchable = strictly_matchable_all_c
            strictly_matchable_two_reply = strictly_matchable and (len(C) == 2)
            
            if strictly_matchable:
                # verify properties independently again
                for err in event_reply_records:
                    assert err["matched_control_count"] >= 1
            if strictly_matchable_two_reply:
                assert len(C) == 2
                
            recon_dest_events.append({
                "square": s,
                "event": {"square": s, "role": "destination", "ply": 1},
                "C_reply_ucis": C,
                "C_cardinality": len(C),
                "event_reply_records": event_reply_records,
                "strictly_matchable": strictly_matchable,
                "strictly_matchable_two_reply": strictly_matchable_two_reply
            })
            
        assert record["destination_events"] == recon_dest_events
        
        has_ge_1 = any(de["strictly_matchable"] for de in recon_dest_events)
        has_2 = any(de["strictly_matchable_two_reply"] for de in recon_dest_events)
        
        assert record["has_any_strictly_matchable_destination"] == has_ge_1
        assert record["has_any_strictly_matchable_two_reply_destination"] == has_2
        
        if has_ge_1:
            M_ge_1_recon += 1
        if has_2:
            M_2_recon += 1
            
    assert artifact["N_eligible"] == N_eligible_recon
    assert artifact["M_ge_1"] == M_ge_1_recon
    assert artifact["M_2"] == M_2_recon
    assert artifact["primary_M"] == M_2_recon
    
    if M_2_recon >= 12:
        expected_class = "FEASIBLE_FOR_MATCHED_PROTOCOL_DESIGN"
    else:
        expected_class = "NOT_FEASIBLE_UNDER_FROZEN_COVERAGE_BUDGET"
        
    assert artifact["classification"] == expected_class
