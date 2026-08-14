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

import shutil
import platform
def test_comparison_perspective_black_cp_native():
    sf_path = shutil.which("stockfish")
    if not sf_path:
        pytest.skip("Stockfish not found")
        
    # A simple black-to-move position where one move is obviously best
    # "rnbqkbnr/pppp1ppp/8/4p3/4P3/8/PPPP1PPP/RNBQKBNR b KQkq - 0 2" (after 1.e4 e5)
    # We'll just run process_position to ensure it returns cleanly without crashing.
    fen = "rnbqkbnr/pppp1ppp/8/4p3/4P3/8/PPPP1PPP/RNBQKBNR b KQkq - 0 2"
    harness = ValidationHarness(engine_path=sf_path, budget_nodes=10000, comparison_perspective="root_side")
    
    with patch.object(ValidationHarness, "preflight_fixture") as mock_preflight:
        mock_preflight.return_value = ([], [], [], [])
        
        with harness:
            result = harness.process_position(fen, "Nf6", "dummy_e", "dummy_f")
            
        assert result["comparison_perspective_policy"] == "root_side"
        assert result["resolved_comparison_perspective"] == "black"
        
        # We don't care exactly about the regret value here, just that it ran natively and evaluated for black
        regrets = result["regrets"]
        assert len(regrets) > 0
        
        # Best move should have regret 0
        min_regret = min(r["value"] for r in regrets.values() if r["type"] == "cp")
        assert min_regret == 0
