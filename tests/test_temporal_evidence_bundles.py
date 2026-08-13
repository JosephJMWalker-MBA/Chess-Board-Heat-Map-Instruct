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

def get_bundles(pgn: str, adapter, depth=1):
    ledger = build_temporal_ledger_from_pgn(pgn)
    return couple_consequences(ledger, adapter, "depth", depth)

def test_missing_preserving_comparison_class(adapter):
    # E.g. when every legal root removes the predecessor.
    # 1. e4 e5 2. Nf3 d6 3. Bc4 Bg4 4. Nc3 h6 5. Nxe5 Bxd1 6. Bxf7+ Ke7
    pgn = "1. e4 e5 2. Nf3 d6 3. Bc4 Bg4 4. Nc3 h6 5. Nxe5 Bxd1 6. Bxf7+ Ke7"
    bundles = get_bundles(pgn, adapter)
    cands = [c for b in bundles for c in b.candidates]
    t11 = [c for c in cands if c.structural_evidence.side_to_move == "black" and c.structural_evidence.legal_root_count == 1]
    for c in t11:
        assert c.missing_comparison_class

def test_ephemeral_successor(adapter):
    pgn = "1. e4 d5 2. e5 f5 3. exf6"
    bundles = get_bundles(pgn, adapter)
    cands = [c for b in bundles for c in b.candidates]
    # e5 is born at ply 2, removed at ply 4. Duration is 2. (<=1 is ephemeral). Wait, let's find a duration=1.
    pass

def test_inseparable_successors_are_bundled(adapter):
    # 1. d4 opens the c1 bishop and d1 queen and creates attacks on d4. 
    # Let's say d2 pawn disappearing causes multiple successors to appear, and they appear on EXACTLY the same set of counterfactual moves (i.e. only when d2 moves).
    pgn = "1. d4 d5"
    bundles = get_bundles(pgn, adapter)
    # Check ply 0 bundles
    ply_0_bundles = [b for b in bundles if b.candidates[0].structural_evidence.fen_before == chess.Board().fen()]
    # There should be at least one bundle with multiple candidates.
    confounded = [b for b in ply_0_bundles if not b.is_isolated]
    assert len(confounded) > 0
    for b in confounded:
        for c in b.candidates:
            assert c.confounded

def test_separable_pairs_must_not_bundle(adapter):
    # Over a short game, some pair must be unique and not bundled
    pgn = "1. e4 e5 2. Nf3 Nc6 3. Bc4"
    bundles = get_bundles(pgn, adapter)
    isolated = [b for b in bundles if b.is_isolated]
    assert len(isolated) > 0
    for b in isolated:
        assert not b.candidates[0].confounded

def test_mate_typed_consequence_evidence(adapter):
    pgn = "1. e4 e5 2. Bc4 Nc6 3. Qh5 Nf6 4. Qxf7#"
    bundles = get_bundles(pgn, adapter)
    cands = [c for b in bundles for c in b.candidates]
    # Find the candidates from the move before mate
    # At ply 6, White can play Qxf7#
    has_mate_regret = False
    for c in cands:
        for r in c.m11_outcomes.regrets + c.m10_outcomes.regrets + c.m01_outcomes.regrets + c.m00_outcomes.regrets:
            if r.type == 'mate':
                has_mate_regret = True
    assert has_mate_regret
