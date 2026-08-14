import chess
import pytest
from unittest.mock import patch, MagicMock
from chessheat.validation.harness import ValidationHarness
from chessheat.models import Score

def test_comparison_perspective_black_cp():
    # A position where it's black's turn to move.
    fen = "rnbqkbnr/pppp1ppp/8/4p3/4P3/8/PPPP1PPP/RNBQKBNR b KQkq - 0 2"
    
    # We create a harness with root_side perspective.
    harness = ValidationHarness(comparison_perspective="root_side")
    
    # We will mock preflight_fixture and evaluate_move
    with patch.object(ValidationHarness, "preflight_fixture") as mock_preflight, \
         patch.object(ValidationHarness, "evaluate_move") as mock_evaluate:
         
        mock_preflight.return_value = ([], [], [], [])
        
        # When evaluating moves, Black's "best" move in terms of CP (from Black's perspective)
        # would be the one with the highest CP score.
        # Let's say Nf6 gets +100 CP (very good for black), Nc6 gets +50 CP, and Bc5 gets -20 CP.
        # The harness should evaluate these and assign regrets based on E^* = max(E(m)).
        # E^* = +100. Regret for Nf6 = 0, Nc6 = 50, Bc5 = 120.
        
        def fake_evaluate(board, move, resolved_perspective):
            assert resolved_perspective == "black"
            san = board.san(move)
            if san == "Nf6":
                return Score(type="cp", value=100, perspective="black")
            elif san == "Nc6":
                return Score(type="cp", value=50, perspective="black")
            elif san == "Bc5":
                return Score(type="cp", value=-20, perspective="black")
            else:
                return Score(type="cp", value=-100, perspective="black")
                
        mock_evaluate.side_effect = fake_evaluate
        
        # Process the position
        result = harness.process_position(fen, "Nf6", "dummy_e", "dummy_f")
        
        # Check regrets
        regrets = result["regrets"]
        
        assert regrets["Nf6"]["value"] == 0
        assert regrets["Nc6"]["value"] == 50
        assert regrets["Bc5"]["value"] == 120
        assert regrets["Qh4"]["value"] == 200 # -100 vs +100 -> regret 200
