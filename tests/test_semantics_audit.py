import pytest
from chessheat.selectivity import apply_shape_selectivity_v1
from chessheat.recurrence import aggregate_square_recurrence
from chessheat.models import AnalysisRecord, CandidateProvenance

def test_channel_independence_no_suppression():
    """
    Assert mechanically that failure in one channel cannot suppress
    evidence independently selected by another channel.
    """
    
    # 1. Selected by Direct, rejected by Recurrence and Bundle
    prof1 = {
        "direct": {"candidate_fraction": 0.20}, # pass
        "recurrence": {"earliest_ply": 3, "distinct_line_count": 5}, # fail (ply > 2)
        "bundle": {"producing_move_count": 2, "implicated_region_size": 10} # fail (moves < 3)
    }
    is_sel, src, reason = apply_shape_selectivity_v1(prof1)
    assert is_sel is True
    assert src == "direct"
    
    # 2. Selected by Recurrence, rejected by Direct and Bundle
    prof2 = {
        "direct": {"candidate_fraction": 0.10}, # fail
        "recurrence": {"earliest_ply": 1, "distinct_line_count": 4}, # pass
        "bundle": {"producing_move_count": 1, "implicated_region_size": 10} # fail
    }
    is_sel, src, reason = apply_shape_selectivity_v1(prof2)
    assert is_sel is True
    assert src == "recurrence"
    
    # 3. Selected by Bundle, rejected by Direct and Recurrence
    prof3 = {
        "direct": {"candidate_fraction": 0.05}, # fail
        "recurrence": {"earliest_ply": 4, "distinct_line_count": 1}, # fail
        "bundle": {"producing_move_count": 4, "implicated_region_size": 12} # pass
    }
    is_sel, src, reason = apply_shape_selectivity_v1(prof3)
    assert is_sel is True
    assert src == "bundle"

def test_recurrence_distinct_line_count_invariant():
    """
    Verify for every recurrence observation: distinct_line_count <= admitted_candidate_count.
    """
    # Create a mock AnalysisRecord with a specific candidate policy
    from chessheat.models import Score, MoveObservation, PlyObservation
    
    # Policy limits to 2 candidates
    record = AnalysisRecord(
        fen="8/8/8/8/4k3/8/8/4K3 w - - 0 1",
        root_side="white",
        comparison_perspective="white",
        engine_name="mock",
        search_budget_type="nodes",
        search_budget_value=100,
        baseline_observation=Score(type="cp", value=0, perspective="white"),
        candidate_policy={"top_n": 2},
        move_observations=[
            MoveObservation(
                uci="e1d1", san="Kd1", origin_square="e1", destination_square="d1",
                is_capture=False, is_castling=False, is_en_passant=False, resulting_fen="",
                score=Score(type="cp", value=0, perspective="white"),
                parsed_pv=[
                    PlyObservation(ply_number=2, uci="e1d1", origin="e1", destination="d1", roles=[])
                ]
            ),
            MoveObservation(
                uci="e1f1", san="Kf1", origin_square="e1", destination_square="f1",
                is_capture=False, is_castling=False, is_en_passant=False, resulting_fen="",
                score=Score(type="cp", value=0, perspective="white"),
                parsed_pv=[
                    PlyObservation(ply_number=2, uci="e1f1", origin="e1", destination="f1", roles=[])
                ]
            ),
            MoveObservation(
                uci="e1d2", san="Kd2", origin_square="e1", destination_square="d2",
                is_capture=False, is_castling=False, is_en_passant=False, resulting_fen="",
                score=Score(type="cp", value=0, perspective="white"),
                parsed_pv=[
                    PlyObservation(ply_number=2, uci="e1d2", origin="e1", destination="d2", roles=[])
                ]
            )
        ]
    )
    
    # 3 total legal root moves analyzed
    assert len(record.move_observations) == 3
    
    res = aggregate_square_recurrence(record)
    
    # Candidates admitted should be 2 (due to top_n=2)
    assert res.provenance.admitted_count == 2
    
    for sq, rec in res.squares.items():
        # The invariant: distinct_line_count cannot exceed admitted_count
        assert rec.overall.distinct_line_count <= res.provenance.admitted_count
        
        # When admitted candidates exist, line_fraction must match
        if res.provenance.admitted_count > 0:
            assert rec.overall.line_fraction == rec.overall.distinct_line_count / res.provenance.admitted_count
        
        # We explicitly distinguish:
        # - legal root moves analyzed: len(record.move_observations)
        # - candidates admitted to Recurrence: res.provenance.admitted_count
        # - PV length: handled dynamically per observation
        # - distinct candidate lines containing a square: rec.overall.distinct_line_count
        # - total square visits: rec.overall.visit_count
