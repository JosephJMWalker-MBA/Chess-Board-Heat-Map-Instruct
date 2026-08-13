import pytest
from chessheat.models import AnalysisRecord, MoveObservation, Score, PlyObservation, SquareEffectRole
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
        regret=Score(type="cp", value=0, perspective="white"),
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

    assert "d5" in res.squares
    d5 = res.squares["d5"].overall
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
        regret=Score(type="cp", value=0, perspective="white"),
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
        regret=Score(type="cp", value=5, perspective="white"),
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
    assert res.squares["d5"].overall.distinct_line_count == 2
    assert res.squares["d5"].overall.line_fraction == 1.0

    assert res.squares["e4"].overall.line_fraction == 0.5

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
    try:
        record = analyze(fen="rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1", adapter=adapter, budget_type="nodes", budget_value=1)

        # Check that for e2e4, the first parsed ply is e2e4 and the second is d7d5, not e2e4 again.
        e2e4_obs = next(o for o in record.move_observations if o.uci == "e2e4")
        assert len(e2e4_obs.parsed_pv) == 2
        assert e2e4_obs.parsed_pv[0].ply_number == 1
        assert e2e4_obs.parsed_pv[0].uci == "e2e4"
        assert e2e4_obs.parsed_pv[1].ply_number == 2
        assert e2e4_obs.parsed_pv[1].uci == "d7d5"
    finally:
        adapter.close()

def test_candidate_policy_max_regret():
    obs_list = []
    for i in range(5):
        # Create 5 moves, regrets 0, 10, 20, 30, 40
        parsed_pv = [
            PlyObservation(ply_number=1, uci=f"m{i}", origin=f"a{i+1}", destination=f"b{i+1}", roles=[SquareEffectRole.ORIGIN, SquareEffectRole.DESTINATION])
        ]
        # Make a special square for the excluded ones
        if i >= 2:
            parsed_pv.append(PlyObservation(ply_number=2, uci=f"r{i}", origin="h8", destination="h7", roles=[SquareEffectRole.ORIGIN, SquareEffectRole.DESTINATION]))

        obs = MoveObservation(
            uci=f"m{i}", san=f"M{i}", origin_square=f"a{i+1}", destination_square=f"b{i+1}",
            is_capture=False, is_castling=False, is_en_passant=False, resulting_fen="",
            score=Score(type="cp", value=100-i*10, perspective="white"),
            regret=Score(type="cp", value=i*10, perspective="white"),
            parsed_pv=parsed_pv
        )
        obs_list.append(obs)

    record = AnalysisRecord(
        fen="test", root_side="white", comparison_perspective="white", engine_name="mock", search_budget_type="nodes", search_budget_value=1,
        baseline_observation=Score(type="cp", value=100, perspective="white"),
        move_observations=obs_list,
        candidate_policy={"max_regret_cp": 15}
    )

    res = aggregate_square_recurrence(record)
    prov = res.provenance
    sqs = res.squares

    assert prov.total_legal_moves == 5
    assert prov.admitted_count == 2
    assert prov.admitted_root_moves == ["m0", "m1"]

    # h8 should have 0 recurrence because it only appears in excluded lines
    assert "h8" not in sqs

def test_candidate_policy_changes_denominator():
    obs_list = []
    for i in range(5):
        obs = MoveObservation(
            uci=f"m{i}", san=f"M{i}", origin_square=f"a{i+1}", destination_square=f"b{i+1}",
            is_capture=False, is_castling=False, is_en_passant=False, resulting_fen="",
            score=Score(type="cp", value=100-i*10, perspective="white"),
            regret=Score(type="cp", value=i*10, perspective="white"),
            parsed_pv=[PlyObservation(ply_number=1, uci=f"m{i}", origin=f"a{i+1}", destination=f"b{i+1}", roles=[SquareEffectRole.ORIGIN, SquareEffectRole.DESTINATION])]
        )
        obs_list.append(obs)

    record_top3 = AnalysisRecord(
        fen="test", root_side="white", comparison_perspective="white", engine_name="mock", search_budget_type="nodes", search_budget_value=1,
        baseline_observation=Score(type="cp", value=100, perspective="white"),
        move_observations=obs_list,
        candidate_policy={"top_n": 3}
    )

    record_top5 = AnalysisRecord(
        fen="test", root_side="white", comparison_perspective="white", engine_name="mock", search_budget_type="nodes", search_budget_value=1,
        baseline_observation=Score(type="cp", value=100, perspective="white"),
        move_observations=obs_list,
        candidate_policy={"top_n": 5}
    )

    res3 = aggregate_square_recurrence(record_top3)
    res5 = aggregate_square_recurrence(record_top5)

    assert res3.provenance.admitted_count == 3
    assert res5.provenance.admitted_count == 5

    # Denominator in line_fraction should be different
    # a1 appears in 1 line
    assert res3.squares["a1"].overall.line_fraction == 1.0 / 3.0
    assert res5.squares["a1"].overall.line_fraction == 1.0 / 5.0
