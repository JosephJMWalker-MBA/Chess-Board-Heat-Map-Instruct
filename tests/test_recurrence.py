import pytest
from chessheat.models import AnalysisRecord, MoveObservation, Score, Regret, PlyObservation, SquareEffectRole
from chessheat.recurrence import aggregate_square_recurrence

def test_distinct_line_count():
    # 3 visits to d5 in 1 line = 1 distinct line, but 3 visits
    obs = MoveObservation(
        uci="e2e4",
        san="e4",
        origin_square="e2",
        destination_square="e4",
        is_capture=False,
        resulting_fen="mock",
        score=Score(type="cp", value=10, perspective="white"),
        regret=Regret(type="cp", value=0, perspective="white"),
        parsed_pv=[
            PlyObservation(ply_number=1, uci="e2e4", origin="e2", destination="e4", roles=[SquareEffectRole.ORIGIN, SquareEffectRole.DESTINATION]),
            PlyObservation(ply_number=2, uci="d7d5", origin="d7", destination="d5", roles=[SquareEffectRole.ORIGIN, SquareEffectRole.DESTINATION]),
            PlyObservation(ply_number=3, uci="e4d5", origin="e4", destination="d5", capture="d5", roles=[SquareEffectRole.ORIGIN, SquareEffectRole.DESTINATION, SquareEffectRole.CAPTURE]),
            PlyObservation(ply_number=4, uci="d8d5", origin="d8", destination="d5", capture="d5", roles=[SquareEffectRole.ORIGIN, SquareEffectRole.DESTINATION, SquareEffectRole.CAPTURE])
        ]
    )
    
    record = AnalysisRecord(
        fen="mock",
        root_side="white",
        comparison_perspective="white",
        engine_name="mock",
        search_budget_type="nodes",
        search_budget_value=1,
        baseline_observation=Score(type="cp", value=0, perspective="white"),
        move_observations=[obs],
        candidate_policy={"top_n": 1}
    )
    
    res = aggregate_square_recurrence(record)
    
    assert "d5" in res
    d5 = res["d5"].overall
    assert d5.visit_count == 3  # d7d5, e4d5, d8d5
    assert d5.distinct_line_count == 1 # all in e2e4 line
    assert d5.earliest_ply == 2
    
def test_multiple_lines():
    obs1 = MoveObservation(
        uci="e2e4",
        san="e4",
        origin_square="e2",
        destination_square="e4",
        is_capture=False,
        resulting_fen="mock",
        score=Score(type="cp", value=10, perspective="white"),
        regret=Regret(type="cp", value=0, perspective="white"),
        parsed_pv=[
            PlyObservation(ply_number=1, uci="e2e4", origin="e2", destination="e4", roles=[SquareEffectRole.ORIGIN, SquareEffectRole.DESTINATION]),
            PlyObservation(ply_number=2, uci="d7d5", origin="d7", destination="d5", roles=[SquareEffectRole.ORIGIN, SquareEffectRole.DESTINATION]),
        ]
    )
    
    obs2 = MoveObservation(
        uci="d2d4",
        san="d4",
        origin_square="d2",
        destination_square="d4",
        is_capture=False,
        resulting_fen="mock",
        score=Score(type="cp", value=5, perspective="white"),
        regret=Regret(type="cp", value=5, perspective="white"),
        parsed_pv=[
            PlyObservation(ply_number=1, uci="d2d4", origin="d2", destination="d4", roles=[SquareEffectRole.ORIGIN, SquareEffectRole.DESTINATION]),
            PlyObservation(ply_number=2, uci="d7d5", origin="d7", destination="d5", roles=[SquareEffectRole.ORIGIN, SquareEffectRole.DESTINATION]),
        ]
    )
    
    record = AnalysisRecord(
        fen="mock",
        root_side="white",
        comparison_perspective="white",
        engine_name="mock",
        search_budget_type="nodes",
        search_budget_value=1,
        baseline_observation=Score(type="cp", value=0, perspective="white"),
        move_observations=[obs1, obs2],
        candidate_policy={"top_n": 2}
    )
    
    res = aggregate_square_recurrence(record)
    assert res["d5"].overall.distinct_line_count == 2
    assert res["d5"].overall.line_fraction == 1.0
    
    assert res["e4"].overall.line_fraction == 0.5

def test_root_move_not_duplicated():
    # Verify that in a real (mocked) engine parse, the root move isn't duplicated
    from chessheat.engine import analyze, StockfishAdapter
    import chess
    
    class MockAdapter(StockfishAdapter):
        def analyze_position(self, board: chess.Board, budget_type: str, budget_value: int) -> dict:
            # return a mocked POV score
            import chess.engine
            score = chess.engine.PovScore(chess.engine.Cp(10), board.turn)
            # return the root move as the first move in the PV
            if list(board.move_stack):
                last_move = board.move_stack[-1].uci()
                return {"score": score, "pv": [last_move, "d7d5"]}
            return {"score": score, "pv": []}
            
    adapter = MockAdapter("/opt/homebrew/bin/stockfish")
    record = analyze(fen="rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1", adapter=adapter, budget_type="nodes", budget_value=1)
    
    # Check that for e2e4, the first parsed ply is e2e4 and the second is d7d5, not e2e4 again.
    e2e4_obs = next(o for o in record.move_observations if o.uci == "e2e4")
    assert len(e2e4_obs.parsed_pv) == 2
    assert e2e4_obs.parsed_pv[0].ply_number == 1
    assert e2e4_obs.parsed_pv[0].uci == "e2e4"
    assert e2e4_obs.parsed_pv[1].ply_number == 2
    assert e2e4_obs.parsed_pv[1].uci == "d7d5"

