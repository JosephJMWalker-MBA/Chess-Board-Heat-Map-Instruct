import json
from unittest.mock import MagicMock, patch
from chessheat.cli import analyze
from chessheat.models import AnalysisRecord, Score, MoveObservation

@patch('chessheat.cli.StockfishAdapter')
@patch('chessheat.cli.analyze')
def test_cli_attribution_schema(mock_analyze, mock_adapter, capsys):
    import sys

    # Mock analysis record
    best = MoveObservation(
        uci="e2e4", san="e4", origin_square="e2", destination_square="e4",
        is_capture=False, is_castling=False, is_en_passant=False, resulting_fen="",
        score=Score(type="cp", value=100, perspective="white")
    )
    mock_record = AnalysisRecord(
        fen="start_fen",
        root_side="white",
        engine_name="test_engine",
        search_budget_type="nodes",
        search_budget_value=1000,
        baseline_observation=Score(type="cp", value=0, perspective="white"),
        move_observations=[best]
    )
    mock_analyze.return_value = mock_record

    # We need to simulate running the CLI
    test_args = ["chessheat", "--fen", "start_fen", "--stockfish-path", "dummy", "--layer", "attribution"]

    with patch.object(sys, 'argv', test_args):
        from chessheat.cli import main
        main()

    captured = capsys.readouterr()
    output_json = json.loads(captured.out)

    assert output_json["schema_version"] == "1.0"
    assert output_json["fen"] == "start_fen"
    assert output_json["root_side"] == "white"
    assert output_json["engine_name"] == "test_engine"
    assert output_json["search_budget_value"] == 1000
    assert "e4" in output_json["attributions"]
