import pytest
import chess
from chessheat.temporal import build_temporal_ledger_from_pgn

def test_pure_creation():
    # 1. a4
    pgn = "1. a4"
    ledger = build_temporal_ledger_from_pgn(pgn)
    t = ledger.transitions[0] # White ply 1
    
    assert len(t.born_events) > 0
    # There should be an attack from Ra1 to a3 created
    ra1_a3 = [e for e in t.born_events if getattr(e, 'event_type', None) == 'attack' or (hasattr(e, 'attacker') and getattr(e, 'target_square', None) == 'a3')]
    assert len(ra1_a3) > 0

def test_pure_removal():
    # 1. e4 d5 2. exd5
    pgn = "1. e4 d5 2. exd5"
    ledger = build_temporal_ledger_from_pgn(pgn)
    t = ledger.transitions[2] # White ply 3 (exd5)
    
    assert len(t.removed_events) > 0
    # The Black d5 pawn's attacks should be removed.
    d5_attacks = [e for e in t.removed_events if hasattr(e, 'attacker') and e.attacker.square == 'd5']
    assert len(d5_attacks) > 0

def test_persistence_with_no_turnover():
    # 1. e4 e5 2. Ke2 Ke7
    pgn = "1. e4 e5 2. Ke2 Ke7"
    ledger = build_temporal_ledger_from_pgn(pgn)
    t = ledger.transitions[2] # White ply 3 (Ke2)
    
    # Check that a pawn on h2 still defends g3, and it is in persisting_events.
    h2_g3 = [e for e in t.persisting_events if hasattr(e, 'attacker') and e.attacker.square == 'h2' and getattr(e, 'target_square', None) == 'g3']
    assert len(h2_g3) > 0
    # The event is not in born or removed
    assert not any(e for e in t.born_events if hasattr(e, 'attacker') and e.attacker.square == 'h2' and getattr(e, 'target_square', None) == 'g3')
    assert not any(e for e in t.removed_events if hasattr(e, 'attacker') and e.attacker.square == 'h2' and getattr(e, 'target_square', None) == 'g3')

def test_simultaneous_creation_and_removal():
    pgn = "1. Nf3"
    ledger = build_temporal_ledger_from_pgn(pgn)
    t = ledger.transitions[0]
    
    # Nf3 creates attacks from f3 and removes attacks from g1.
    removed = [e for e in t.removed_events if hasattr(e, 'attacker') and e.attacker.square == 'g1']
    born = [e for e in t.born_events if hasattr(e, 'attacker') and e.attacker.square == 'f3']
    
    assert len(removed) > 0
    assert len(born) > 0

def test_reappearance_vs_first_creation():
    pgn = "1. Nf3 d5 2. Ng1 c5 3. Nf3"
    ledger = build_temporal_ledger_from_pgn(pgn)
    
    # At ply 1 (1. Nf3), Nf3 attacks e5. This is a first creation.
    t1 = ledger.transitions[0]
    first_creation = [e for e in t1.born_events if hasattr(e, 'attacker') and e.attacker.square == 'f3' and getattr(e, 'target_square', None) == 'e5']
    assert len(first_creation) == 1
    # It should not be in reappearing
    assert len([e for e in t1.reappearing_events if e == first_creation[0]]) == 0
    
    # At ply 5 (3. Nf3), Nf3 attacks e5 again. This is a reappearance.
    t5 = ledger.transitions[4]
    reappearance = [e for e in t5.born_events if hasattr(e, 'attacker') and e.attacker.square == 'f3' and getattr(e, 'target_square', None) == 'e5']
    assert len(reappearance) == 1
    # It SHOULD be in reappearing
    assert len([e for e in t5.reappearing_events if e == reappearance[0]]) == 1

def test_one_to_many_and_many_to_one():
    # 1. d4 opens the c1 bishop to many squares (f4, g5, h6, etc)
    pgn = "1. d4"
    ledger = build_temporal_ledger_from_pgn(pgn)
    t = ledger.transitions[0]
    
    # We can check that the number of removed vs born is not 1:1.
    assert len(t.born_events) > len(t.removed_events)

def test_spatially_overlapping_co_transition():
    # 1. e4
    pgn = "1. e4"
    ledger = build_temporal_ledger_from_pgn(pgn)
    t = ledger.transitions[0]
    
    # Find a co-transition that overlaps
    overlapping = [ct for ct in t.co_transitions if ct.overlaps]
    assert len(overlapping) > 0

def test_spatially_disjoint_co_transition():
    pgn = "1. e4"
    ledger = build_temporal_ledger_from_pgn(pgn)
    t = ledger.transitions[0]
    
    # e2 pawn moving removes defense of d1 (queen) and creates attack on d5.
    disjoint = [ct for ct in t.co_transitions if not ct.overlaps]
    assert len(disjoint) > 0

def test_identical_final_geometry_different_topology():
    # History A: 1. d4 d5 2. c4 c6
    # History B: 1. c4 c6 2. d4 d5
    # Both arrive at exactly the same FEN (including clocks)
    pgn_A = "1. d4 d5 2. c4 c6"
    pgn_B = "1. c4 c6 2. d4 d5"
    
    ledger_A = build_temporal_ledger_from_pgn(pgn_A)
    ledger_B = build_temporal_ledger_from_pgn(pgn_B)
    
    assert ledger_A.final_fen == ledger_B.final_fen
    
    t_A = ledger_A.transitions[0]
    t_B = ledger_B.transitions[0]
    
    assert t_A.move_san != t_B.move_san
    assert t_A.born_events != t_B.born_events
