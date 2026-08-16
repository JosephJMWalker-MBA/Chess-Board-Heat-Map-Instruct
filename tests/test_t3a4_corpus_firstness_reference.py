import hashlib
import json
import pytest
import chess

EXPECTED_SHA256 = "4337dd0c8ef2579a1b15eb58f5cb00f4bb566c6fdde6ef612f09b2bab2e1ecc7"
EXCLUSIONS = {
    "4k3/8/1b6/8/3R4/8/8/4K3 w - - 0 1",
    "4k3/8/1n6/8/2B5/8/8/4K3 w - - 0 1"
}

def get_hash(filepath):
    sha256 = hashlib.sha256()
    with open(filepath, "rb") as f:
        sha256.update(f.read())
    return sha256.hexdigest()

def test_t3a4_corpus_firstness_and_manifest_bytes():
    manifest_path = "docs/research/t3/t3a4_corpus_manifest.json"
    
    # 1. Bind the manifest bytes
    actual_sha = get_hash(manifest_path)
    assert actual_sha == EXPECTED_SHA256, f"Manifest SHA-256 changed: {actual_sha}"
    
    with open(manifest_path, "r", encoding="utf-8") as f:
        manifest = json.load(f)
        
    committed_fixtures = manifest["fixtures"]
    assert len(committed_fixtures) == 12
    
    # 2. Independent reproduction
    accepted_fens = set()
    generated_fixtures = []
    
    for g in range(10000):
        board = chess.Board()
        p = 0
        
        while not board.is_game_over(claim_draw=False) and p <= 80:
            if 12 <= p <= 80:
                fen = board.fen(shredder=False, en_passant="fen")
                if fen not in accepted_fens and fen not in EXCLUSIONS:
                    b = chess.Board(fen)
                    if b.is_valid() and not b.is_game_over(claim_draw=False) and b.turn == chess.WHITE and not b.is_check():
                        legal_roots = list(b.legal_moves)
                        
                        all_roots_give_reply = True
                        for root in legal_roots:
                            b.push(root)
                            if len(list(b.legal_moves)) == 0:
                                all_roots_give_reply = False
                            b.pop()
                            
                        if all_roots_give_reply:
                            qualifying_squares = []
                            square_data = {}
                            
                            for s in chess.SQUARES:
                                piece = b.piece_at(s)
                                if piece and piece.color == chess.WHITE and piece.piece_type != chess.KING:
                                    l_map = {}
                                    for root in legal_roots:
                                        if root.from_square == s:
                                            l_map[root.uci()] = 0
                                        else:
                                            b.push(root)
                                            has_cap = False
                                            for reply in b.legal_moves:
                                                if b.is_capture(reply) and reply.to_square == s:
                                                    has_cap = True
                                                    break
                                            b.pop()
                                            l_map[root.uci()] = 1 if has_cap else 0
                                            
                                    c1 = sum(1 for v in l_map.values() if v == 1)
                                    c0 = sum(1 for v in l_map.values() if v == 0)
                                    
                                    if c1 >= 2 and c0 >= 2:
                                        sq_name = chess.square_name(s)
                                        qualifying_squares.append(sq_name)
                                        square_data[sq_name] = {
                                            "l_map": l_map,
                                            "c1": c1,
                                            "c0": c0
                                        }
                                        
                            if qualifying_squares:
                                target_sq = min(qualifying_squares)
                                data = square_data[target_sq]
                                accepted_fens.add(fen)
                                
                                opp_pres = sorted(r for r, v in data["l_map"].items() if v == 1)
                                opp_abs = sorted(r for r, v in data["l_map"].items() if v == 0)
                                
                                generated_fixtures.append({
                                    "fixture_index": len(generated_fixtures),
                                    "game_index": g,
                                    "half_move_index": p,
                                    "fen": fen,
                                    "target_square": target_sq,
                                    "exact_sorted_legal_white_root_uci_set": sorted(r.uci() for r in legal_roots),
                                    "root_uci_to_L_fi_mapping": data["l_map"],
                                    "sorted_opportunity_present_roots": opp_pres,
                                    "sorted_opportunity_absent_roots": opp_abs,
                                    "L_equals_1_count": data["c1"],
                                    "L_equals_0_count": data["c0"]
                                })
                                
                                if len(generated_fixtures) == 12:
                                    break
                                    
            if len(generated_fixtures) == 12:
                break
                
            if p == 80:
                break
                
            # Selection of next move
            legal_ucis = sorted(m.uci() for m in board.legal_moves)
            msg = f"T3A4_V1:{g}:{p}".encode("utf-8")
            digest_hex = hashlib.sha256(msg).hexdigest()
            idx = int(digest_hex, 16) % len(legal_ucis)
            move = chess.Move.from_uci(legal_ucis[idx])
            
            board.push(move)
            p += 1
            
        if len(generated_fixtures) == 12:
            # We must break here and the last game index and p should be checked
            assert g == 0
            assert p == 34
            break

    assert len(generated_fixtures) == 12
    
    # 3. Compare with committed manifest exactly
    for i in range(12):
        c_fix = committed_fixtures[i]
        r_fix = generated_fixtures[i]
        
        assert c_fix["fixture_index"] == r_fix["fixture_index"]
        assert c_fix["game_index"] == r_fix["game_index"]
        assert c_fix["half_move_index"] == r_fix["half_move_index"]
        assert c_fix["fen"] == r_fix["fen"]
        assert c_fix["target_square"] == r_fix["target_square"]
        assert c_fix["exact_sorted_legal_white_root_uci_set"] == r_fix["exact_sorted_legal_white_root_uci_set"]
        assert c_fix["root_uci_to_L_fi_mapping"] == r_fix["root_uci_to_L_fi_mapping"]
        assert c_fix["sorted_opportunity_present_roots"] == r_fix["sorted_opportunity_present_roots"]
        assert c_fix["sorted_opportunity_absent_roots"] == r_fix["sorted_opportunity_absent_roots"]
        assert c_fix["L_equals_1_count"] == r_fix["L_equals_1_count"]
        assert c_fix["L_equals_0_count"] == r_fix["L_equals_0_count"]

if __name__ == "__main__":
    pytest.main([__file__])
