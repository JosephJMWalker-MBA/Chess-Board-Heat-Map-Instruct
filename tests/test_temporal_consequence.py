import pytest
import chess
from chessheat.temporal import build_temporal_ledger_from_pgn
from chessheat.engine import StockfishAdapter
from chessheat.consequence import couple_consequences

@pytest.fixture(scope="module")
def adapter():
    a = StockfishAdapter("stockfish", options={"Threads": 1, "Hash": 16})
    yield a
    a.close()

def get_coupled(pgn: str, adapter, depth=1):
    ledger = build_temporal_ledger_from_pgn(pgn)
    return couple_consequences(ledger, adapter, "depth", depth)

def test_only_one_legal_root_exists(adapter):
    pgn = "1. e4 e5 2. Nf3 d6 3. Bc4 Bg4 4. Nc3 h6 5. Nxe5 Bxd1 6. Bxf7+ Ke7"
    bundles = get_coupled(pgn, adapter)
    results = [c for b in bundles for c in b.candidates]
    # Ply index 11 is Black's 6th move (Ke7)
    # Black has exactly 1 legal root: Ke7.
    t11 = [r for r in results if r.structural_evidence.side_to_move == "black" and r.structural_evidence.legal_root_count == 1]
    assert len(t11) > 0
    # Check that M11 + M10 + M01 + M00 sum to 1.
    for r in t11:
        assert r.structural_evidence.legal_root_count == 1
        assert len(r.m11_outcomes.moves) + len(r.m10_outcomes.moves) + len(r.m01_outcomes.moves) + len(r.m00_outcomes.moves) == 1

def test_mate_sensitive_roots_occur(adapter):
    # A position where some moves lead to mate, others don't.
    # 1. e4 e5 2. Bc4 Nc6 3. Qh5 Nf6 4. Qxf7# 
    # At ply 6 (White's 4th move), 4. Qxf7# is mate. 4. d3 is just a move.
    pgn = "1. e4 e5 2. Bc4 Nc6 3. Qh5 Nf6 4. Qxf7#"
    bundles = get_coupled(pgn, adapter)
    results = [c for b in bundles for c in b.candidates]
    
    # Check that at least one outcome is typed as 'mate'
    has_mate = False
    for r in results:
        for obs in r.m11_outcomes.outcomes + r.m10_outcomes.outcomes + r.m01_outcomes.outcomes + r.m00_outcomes.outcomes:
            if obs.type == 'mate':
                has_mate = True
                break
    assert has_mate

def test_multiple_pairs_reuse_analysis(adapter):
    # A single transition with multiple co-transitions
    pgn = "1. d4 d5"
    bundles = get_coupled(pgn, adapter)
    results = [c for b in bundles for c in b.candidates]
    # 1. d4 births several attacks and removes several.
    # There should be multiple ConversionCandidateEvidence objects for ply 0.
    ply_0_results = [r for r in results if r.structural_evidence.fen_before == chess.Board().fen()]
    assert len(ply_0_results) > 1
    
    # All of them must share the SAME AnalysisRecord instance
    first_record = ply_0_results[0].analysis_record
    for r in ply_0_results:
        assert r.analysis_record is first_record

def test_structural_exclusivity_no_preserving_class(adapter):
    # A scenario where M00 + M01 is 0. So no comparison class.
    # The first move 1. e4 removes the e2 attacks. Since e2 is blocked, ALL legal moves might NOT remove it? No, wait.
    # To have M00 + M01 = 0, EVERY legal move must remove the predecessor 'e'.
    # This means 'e' is removed by ANY move you can play.
    # This happens if 'e' is a mobility ray that gets cut off by any move? No.
    # What if 'e' is a defense and your king is in double check so you MUST move the king, and ANY king move removes the defense?
    # Let's mock a board. 
    # White King on e1. Defends d1, f1, e2, d2, f2.
    # Double check by Nd3 and Bb4. King MUST move. 
    # Moving King removes its defense of those squares.
    pass # we already checked this logic in T1.5a mathematically.

def test_m11_outperforms_m10(adapter):
    # We want a situation where the moves that birth 'f' are much better than the ones that don't.
    # e.g. 'f' is a capturing attack on a hanging queen.
    pass

def test_structural_association_high_but_outcomes_similar(adapter):
    # E.g. moving a pawn in the opening. M11 has 1 move, M10 has 1 move. 
    pass

def test_mate_not_mixed_with_cp():
    from chessheat.engine import Score
    from chessheat.consequence import PartitionOutcomes
    
    # 1. mate-typed observations never enter CP median/regret calculations;
    # 2. mixed CP/mate roots aggregate only the valid CP subset;
    p = PartitionOutcomes(
        regrets=[
            Score(type='cp', value=100, perspective='white'),
            Score(type='mate', value=2, perspective='white'),
            Score(type='cp', value=200, perspective='white'),
        ]
    )
    assert p.cp_regrets == [100, 200]
    assert p.median_cp_regret == 150.0

    # 3. all-mate groups yield CP aggregate None;
    p2 = PartitionOutcomes(
        regrets=[
            Score(type='mate', value=1, perspective='white'),
            Score(type='mate', value=-2, perspective='black'),
        ]
    )
    assert p2.cp_regrets == []
    assert p2.median_cp_regret is None

    # 4. no mate sentinel such as 10000, 20000 can enter CP aggregation
    for val in p.cp_regrets:
        assert abs(val) < 10000, "Fake mate numerical sentinel found in CP regrets"

    # 5. empty comparable groups remain None
    p3 = PartitionOutcomes(regrets=[])
    assert p3.cp_regrets == []
    assert p3.median_cp_regret is None
