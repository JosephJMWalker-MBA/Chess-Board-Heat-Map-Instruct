import pytest
import chess
from chessheat.temporal import build_temporal_ledger_from_pgn

def get_cf(pgn: str, ply_idx: int, removed_sig_check, born_sig_check):
    ledger = build_temporal_ledger_from_pgn(pgn)
    t = ledger.transitions[ply_idx]
    for cf in t.counterfactual_evidence:
        if removed_sig_check(cf.predecessor_signature) and born_sig_check(cf.successor_signature):
            return cf
    return None

def test_n01_zero():
    # 1. e4
    # e2 pawn disappears, e4 pawn is born.
    cf = get_cf("1. e4", 0, 
                lambda d: getattr(d, 'attacker', None) and d.attacker.square == 'e2',
                lambda b: getattr(b, 'attacker', None) and b.attacker.square == 'e4')
    assert cf is not None
    assert cf.n_01 == 0
    assert cf.p_b_given_not_d == 0.0

def test_equal_probability():
    # 1. Nf3 
    cf = get_cf("1. Nf3", 0, 
                lambda d: getattr(d, 'attacker', None) and d.attacker.square == 'g1',
                lambda b: getattr(b, 'attacker', None) and b.attacker.square == 'f3')
    assert cf is not None
    assert cf.n_11 > 0
    assert cf.p_b_given_d is not None

def test_rare_successor():
    # 1. d4 opens the Bc1, Qd1, but only a few moves birth a specific attack.
    cf = get_cf("1. d4", 0,
                lambda d: getattr(d, 'attacker', None) and d.attacker.square == 'd2',
                lambda b: getattr(b, 'attacker', None) and b.attacker.square == 'd4')
    assert cf is not None
    assert cf.n_10 > 0
    assert cf.n_11 > 0
    assert cf.n_10 >= cf.n_11

def test_strong_association_no_overlap():
    # 1. Nf3 creates an attack on e5 and removes an attack on h3. No overlap.
    cf = get_cf("1. Nf3", 0,
                lambda d: getattr(d, 'attacker', None) and d.attacker.square == 'g1' and getattr(d, 'target_square', None) == 'h3',
                lambda b: getattr(b, 'attacker', None) and b.attacker.square == 'f3' and getattr(b, 'target_square', None) == 'e5')
    assert cf is not None
    assert not cf.spatial_overlap
    assert cf.n_11 > 0

def test_weak_association_with_overlap():
    # 1. Nf3
    # Removed: g1->f3 attack. Born: f3->e5 attack.
    # Overlap is f3.
    cf = get_cf("1. Nf3", 0,
                lambda d: getattr(d, 'attacker', None) and d.attacker.square == 'g1' and getattr(d, 'target_square', None) == 'f3',
                lambda b: getattr(b, 'attacker', None) and b.attacker.square == 'f3' and getattr(b, 'target_square', None) == 'e5')
    assert cf is not None
    assert cf.spatial_overlap
    # Weak association because Nh3 removes g1->f3 but does not birth f3->e5
    assert cf.n_10 > 0

def test_successor_immediately_disappears():
    pgn = "1. e4 d5 2. e5 f5 3. exf6"
    cf = get_cf(pgn, 2,
                lambda d: getattr(d, 'attacker', None) and d.attacker.square == 'e4',
                lambda b: getattr(b, 'attacker', None) and b.attacker.square == 'e5')
    assert cf is not None
    assert cf.observed_duration_of_born_episode == 2

def test_right_censored_successor():
    cf = get_cf("1. e4", 0,
                lambda d: getattr(d, 'attacker', None) and d.attacker.square == 'e2',
                lambda b: getattr(b, 'attacker', None) and b.attacker.square == 'e4')
    assert cf is not None
    assert cf.is_born_right_censored

def test_reappearing_successor():
    pgn = "1. Nf3 d5 2. Ng1 c5 3. Nf3"
    cf = get_cf(pgn, 4,
                lambda d: getattr(d, 'attacker', None) and d.attacker.square == 'g1',
                lambda b: getattr(b, 'attacker', None) and b.attacker.square == 'f3')
    assert cf is not None
    assert cf.is_born_reappearance

def test_competing_successors():
    pgn = "1. d4"
    ledger = build_temporal_ledger_from_pgn(pgn)
    t = ledger.transitions[0]
    
    d2_removed = [cf for cf in t.counterfactual_evidence if getattr(cf.predecessor_signature, 'attacker', None) and cf.predecessor_signature.attacker.square == 'd2']
    assert len(d2_removed) > 1

def test_different_evidence_exact_fen():
    pgn_A = "1. d4 d5 2. c4 c6"
    pgn_B = "1. c4 c6 2. d4 d5"
    
    ledger_A = build_temporal_ledger_from_pgn(pgn_A)
    ledger_B = build_temporal_ledger_from_pgn(pgn_B)
    
    cf_A = ledger_A.transitions[2].counterfactual_evidence
    cf_B = ledger_B.transitions[2].counterfactual_evidence
    
    # Check that they aren't exactly the same list of evidence
    assert len(cf_A) != len(cf_B) or cf_A[0].m_11 != cf_B[0].m_11
