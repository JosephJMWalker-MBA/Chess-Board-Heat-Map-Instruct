import json
import os
import chess
import pytest
from scripts.generate_t3a4_corpus import generate_corpus, evaluate_eligibility

def test_t3a4_corpus_manifest():
    manifest_path = "docs/research/t3/t3a4_corpus_manifest.json"
    assert os.path.exists(manifest_path), "Manifest file not found."
    
    with open(manifest_path, "r") as f:
        committed_manifest = json.load(f)
        
    assert committed_manifest["fixture_count"] == 12
    assert len(committed_manifest["fixtures"]) == 12
    assert committed_manifest["history_contract"]["history_available"] is False
    assert committed_manifest["history_contract"]["history_identity"] is None
    assert "engine_observations_present" in committed_manifest
    assert committed_manifest["engine_observations_present"] is False
    
    # Regenerate to prove it wasn't curated
    regenerated_manifest, _, _ = generate_corpus()
    assert regenerated_manifest is not None, "Failed to generate 12 fixtures."
    
    # Compare regenerated fixtures to committed fixtures exactly in order
    committed_fixtures = committed_manifest["fixtures"]
    regen_fixtures = regenerated_manifest["fixtures"]
    
    assert len(committed_fixtures) == len(regen_fixtures) == 12
    
    seen_fens = set()
    exclusions = {
        "4k3/8/1b6/8/3R4/8/8/4K3 w - - 0 1",
        "4k3/8/1n6/8/2B5/8/8/4K3 w - - 0 1"
    }

    for i in range(12):
        c_fix = committed_fixtures[i]
        r_fix = regen_fixtures[i]
        
        # Exact equality
        assert c_fix == r_fix
        
        fen = c_fix["fen"]
        assert fen not in seen_fens, f"FEN {fen} is not unique."
        seen_fens.add(fen)
        
        assert fen not in exclusions, f"FEN {fen} matches an exclusion."
        
        # Round trip
        board = chess.Board(fen)
        round_trip_fen = board.fen(shredder=False, en_passant="fen")
        assert round_trip_fen == fen, f"FEN {fen} did not round-trip exactly."
        
        # Root set matches python-chess
        legal_roots = sorted(m.uci() for m in board.legal_moves)
        assert c_fix["exact_sorted_legal_white_root_uci_set"] == legal_roots
        
        # Every root gives Black at least one legal reply
        for root_uci in legal_roots:
            board.push_uci(root_uci)
            replies = list(board.legal_moves)
            board.pop()
            assert len(replies) > 0, f"Root {root_uci} leaves Black with no replies."
            
        # L_fi mapping
        eligibility = evaluate_eligibility(fen)
        assert eligibility is not None
        assert c_fix["root_uci_to_L_fi_mapping"] == eligibility["eval_data"]["l_mapping"]
        
        # |L=1| >= 2 and |L=0| >= 2
        count_1 = c_fix["L_equals_1_count"]
        count_0 = c_fix["L_equals_0_count"]
        assert count_1 >= 2
        assert count_0 >= 2
        
        # Selected target is exactly the min qualifying target
        # Evaluate eligibility again manually to get all qualifying targets
        qualifying_squares = []
        for s in chess.SQUARES:
            piece = board.piece_at(s)
            if piece and piece.color == chess.WHITE and piece.piece_type != chess.KING:
                l_mapping = {}
                for root in board.legal_moves:
                    root_uci = root.uci()
                    if root.from_square == s:
                        l_mapping[root_uci] = 0
                    else:
                        board.push(root)
                        has_capture = False
                        for reply in board.legal_moves:
                            if board.is_capture(reply) and reply.to_square == s:
                                has_capture = True
                                break
                        board.pop()
                        l_mapping[root_uci] = 1 if has_capture else 0

                c1 = sum(1 for v in l_mapping.values() if v == 1)
                c0 = sum(1 for v in l_mapping.values() if v == 0)

                if c1 >= 2 and c0 >= 2:
                    qualifying_squares.append(chess.square_name(s))
                    
        assert qualifying_squares
        assert c_fix["target_square"] == min(qualifying_squares)
        
        # History
        sp = c_fix["sufficient_position_fields"]
        assert sp["history_available"] is False
        assert sp["history_identity"] is None
        
        # No engine-derived fields
        assert "scores" not in c_fix
        assert "regrets" not in c_fix
        assert "D_f" not in c_fix
        assert "M_f" not in c_fix
        assert "P_f" not in c_fix

if __name__ == "__main__":
    pytest.main([__file__])
