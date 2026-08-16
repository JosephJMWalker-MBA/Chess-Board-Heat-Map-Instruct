import json
import hashlib
import chess
import pytest
from typing import Dict, Any, List, Set, Tuple

def load_manifest():
    with open("docs/research/t3/t3b2_fixture_manifest.json", "r", encoding="utf-8") as f:
        return json.load(f)

def test_manifest_firstness_and_invariants():
    manifest = load_manifest()
    
    # 12 distinct game indices and 12 fixtures
    assert manifest["fixture_count"] == 12
    assert len(manifest["fixtures"]) == 12
    game_indices = [f["game_index"] for f in manifest["fixtures"]]
    assert len(set(game_indices)) == 12
    assert sorted(f["fixture_index"] for f in manifest["fixtures"]) == list(range(12))
    
    assert manifest["engine_observations_present"] is False
    
    forbidden_fields = ["score", "CP", "mate score", "evaluation", "PV", "regret", "S_u", "Q_u", "Delta_u", "classification", "expected direction"]
    for f in manifest["fixtures"]:
        for field in forbidden_fields:
            assert field not in f
            for reply in f["replies"]:
                assert field not in reply
                
    # Verify historical exposure sources
    provenance = manifest["historical_exposure_provenance"]
    expected_sources = {
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
    
    canonical_fens = set()
    for path, expected_sha in expected_sources.items():
        with open(path, "rb") as f:
            content_bytes = f.read()
            assert hashlib.sha256(content_bytes).hexdigest() == expected_sha
            data = json.loads(content_bytes.decode("utf-8"))
            
            raw_fens = [data["fen"]]
            if "t3a1" in path or "t3a2" in path:
                if "observations" in data:
                    raw_fens.extend([obs["resulting_fen"] for obs in data["observations"]])
            elif "t3a3" in path or "t3a4" in path:
                if "move_observations" in data:
                    raw_fens.extend([obs["resulting_fen"] for obs in data["move_observations"]])
            for rfen in raw_fens:
                canonical_fens.add(chess.Board(rfen).fen(shredder=False, en_passant="fen"))
                
    digest_input = "\n".join(sorted(list(canonical_fens))) + "\n"
    assert hashlib.sha256(digest_input.encode("utf-8")).hexdigest() == provenance["canonical_exposure_digest"]
    
    # Firstness reconstruction
    accepted_roots = set()
    accepted_interventions = set()
    generated_fixtures = []
    
    for g in range(10000):
        if len(generated_fixtures) == 12:
            break
            
        board = chess.Board()
        p = 0
        fixture_found = False
        
        while p <= 80 and not fixture_found:
            if 12 <= p <= 80:
                root_fen = board.fen(shredder=False, en_passant="fen")
                root = chess.Board(root_fen)
                
                if root.is_valid() and root.turn == chess.WHITE and not root.is_game_over(claim_draw=False) and not root.is_check():
                    white_roots = sorted(move.uci() for move in root.legal_moves)
                    eligible_tuples = []
                    tuple_data = {}
                    
                    for w_root_uci in white_roots:
                        pi_board = chess.Board(root_fen)
                        pi_board.push(chess.Move.from_uci(w_root_uci))
                        intervention_fen = pi_board.fen(shredder=False, en_passant="fen")
                        
                        if pi_board.is_valid() and pi_board.turn == chess.BLACK and not pi_board.is_game_over(claim_draw=False) and not pi_board.is_check():
                            legal_black_replies = list(pi_board.legal_moves)
                            if len(legal_black_replies) >= 6:
                                dest_map = {}
                                for move in legal_black_replies:
                                    dest = chess.square_name(move.to_square)
                                    if dest not in dest_map:
                                        dest_map[dest] = []
                                    dest_map[dest].append(move)
                                    
                                for dest, moves in dest_map.items():
                                    if len(moves) == 2:
                                        if moves[0].from_square != moves[1].from_square:
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
                            child_fens_to_check = []
                            for move_uci in reply_ucis:
                                move = chess.Move.from_uci(move_uci)
                                child_board = chess.Board(intervention_fen)
                                child_board.push(move)
                                child_fens_to_check.append(child_board.fen(shredder=False, en_passant="fen"))
                            
                            candidate_fens = [root_fen, intervention_fen] + child_fens_to_check
                            exposure_fail = any(f in canonical_fens for f in candidate_fens)
                            uniqueness_fail = root_fen in accepted_roots or intervention_fen in accepted_interventions
                            
                            if not exposure_fail and not uniqueness_fail:
                                accepted_roots.add(root_fen)
                                accepted_interventions.add(intervention_fen)
                                
                                generated_fixtures.append({
                                    "g": g,
                                    "p": p,
                                    "root_fen": root_fen,
                                    "w_root_uci": w_root_uci,
                                    "intervention_fen": intervention_fen,
                                    "target_square": target_square,
                                    "reply_ucis": reply_ucis,
                                    "c_moves": c_moves,
                                    "n_moves": n_moves,
                                    "child_fens": child_fens_to_check
                                })
                                fixture_found = True
            
            if fixture_found or p == 80:
                break
                
            if board.is_game_over(claim_draw=False):
                break
                
            legal = sorted(move.uci() for move in board.legal_moves)
            payload = f"T3B2_V1:{g}:{p}".encode("utf-8")
            idx = int(hashlib.sha256(payload).hexdigest(), 16) % len(legal)
            board.push(chess.Move.from_uci(legal[idx]))
            p += 1

    assert len(generated_fixtures) == 12
    
    # Check uniqueness globally
    manifest_root_fens = [f["root_fen"] for f in manifest["fixtures"]]
    manifest_intervention_fens = [f["intervention_fen"] for f in manifest["fixtures"]]
    assert len(set(manifest_root_fens)) == 12
    assert len(set(manifest_intervention_fens)) == 12
    
    for i, gen in enumerate(generated_fixtures):
        man = manifest["fixtures"][i]
        assert man["game_index"] == gen["g"]
        assert man["half_move_index"] == gen["p"]
        assert man["root_fen"] == gen["root_fen"]
        assert man["white_root_uci"] == gen["w_root_uci"]
        assert man["intervention_fen"] == gen["intervention_fen"]
        assert man["target_event"]["square"] == gen["target_square"]
        assert man["legal_reply_ucis"] == gen["reply_ucis"]
        assert man["C_reply_ucis"] == gen["c_moves"]
        assert man["N_reply_ucis"] == gen["n_moves"]
        
        pi_board = chess.Board(man["intervention_fen"])
        assert pi_board.turn == chess.BLACK
        assert not pi_board.is_game_over(claim_draw=False)
        assert not pi_board.is_check()
        
        assert sorted([move.uci() for move in pi_board.legal_moves]) == man["legal_reply_ucis"]
        assert len(man["C_reply_ucis"]) == 2
        assert len(man["N_reply_ucis"]) >= 4
        
        c_moves = [chess.Move.from_uci(u) for u in man["C_reply_ucis"]]
        assert c_moves[0].from_square != c_moves[1].from_square
        assert c_moves[0].promotion is None
        assert c_moves[1].promotion is None
        
        for c_move in c_moves:
            assert chess.square_name(c_move.to_square) == man["target_event"]["square"]
            
        for n_move_uci in man["N_reply_ucis"]:
            n_move = chess.Move.from_uci(n_move_uci)
            assert chess.square_name(n_move.to_square) != man["target_event"]["square"]
            
        for idx, reply in enumerate(man["replies"]):
            assert reply["child_fen"] == gen["child_fens"][idx]
            child_board = chess.Board(man["intervention_fen"])
            child_board.push(chess.Move.from_uci(reply["uci"]))
            assert reply["is_terminal"] == child_board.is_game_over(claim_draw=False)
            
            assert reply["child_fen"] not in canonical_fens
        
        assert man["root_fen"] not in canonical_fens
        assert man["intervention_fen"] not in canonical_fens
