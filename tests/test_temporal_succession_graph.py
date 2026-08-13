import pytest
import chess
from chessheat.temporal import build_temporal_ledger_from_pgn, build_temporal_succession_graph
from chessheat.geometry import AttackRelationship

def test_simple_succession_a_to_b():
    # 1. e4 e5 2. Nf3
    # Nf3 removes an attack from g1 and borns an attack from f3.
    pgn = "1. e4 e5 2. Nf3"
    ledger = build_temporal_ledger_from_pgn(pgn)
    graph = build_temporal_succession_graph(ledger)
    
    # Let's find the Ng1 defense/attack that was removed and Nf3 born.
    ng1_f3_removed = [e for e in ledger.events if getattr(e.event_identity, 'attacker', None) and e.event_identity.attacker.square == 'g1'][0]
    nf3_e5_born = [e for e in ledger.events if getattr(e.event_identity, 'attacker', None) and e.event_identity.attacker.square == 'f3'][0]
    
    assert graph.transition_count(ng1_f3_removed.event_identity, nf3_e5_born.event_identity) == 1

def test_one_to_many_a_to_bc():
    # 1. d4 opens Bc1 to many squares
    pgn = "1. d4"
    ledger = build_temporal_ledger_from_pgn(pgn)
    graph = build_temporal_succession_graph(ledger)
    
    d2_d4_removed = [e for e in ledger.events if getattr(e.event_identity, 'attacker', None) and e.event_identity.attacker.square == 'd2'][0]
    degree = graph.branching_degree(d2_d4_removed.event_identity)
    assert degree > 1

def test_many_to_one_ab_to_c():
    # 1. d4
    # Bc1 gets mobility, Qd1 gets mobility. Many things are born when d2 pawn moves.
    # What about multiple removals leading to one birth?
    # e.g., capturing a piece that was defending/attacking many things, and replacing it with one piece.
    # 1. e4 d5 2. exd5
    pgn = "1. e4 d5 2. exd5"
    ledger = build_temporal_ledger_from_pgn(pgn)
    graph = build_temporal_succession_graph(ledger)
    
    # Born on d5: e4 pawn becomes d5 pawn.
    # Removed: e4 pawn, d5 pawn.
    d5_born = [e for e in ledger.events if getattr(e.event_identity, 'attacker', None) and e.event_identity.attacker.square == 'd5']
    if d5_born:
        convergence = graph.convergence_degree(d5_born[0].event_identity)
        assert convergence > 1

def test_repeated_a_to_b_transitions():
    # 1. Nf3 d5 2. Ng1 c5 3. Nf3
    pgn = "1. Nf3 d5 2. Ng1 c5 3. Nf3"
    ledger = build_temporal_ledger_from_pgn(pgn)
    graph = build_temporal_succession_graph(ledger)
    
    # Ng1 -> Nf3 happens twice
    ng1_events = [e.event_identity for e in ledger.events if getattr(e.event_identity, 'attacker', None) and e.event_identity.attacker.square == 'g1']
    nf3_events = [e.event_identity for e in ledger.events if getattr(e.event_identity, 'attacker', None) and e.event_identity.attacker.square == 'f3']
    
    count = 0
    for ng1 in ng1_events:
        for nf3 in nf3_events:
            count += graph.transition_count(ng1, nf3)
            
    assert count >= 2

def test_succession_chain():
    # 1. e4 e5 2. Nf3 Nc6 3. Nxe5
    pgn = "1. e4 e5 2. Nf3 Nc6 3. Nxe5"
    ledger = build_temporal_ledger_from_pgn(pgn)
    graph = build_temporal_succession_graph(ledger)
    
    # Chain: Ng1 -> Nf3 -> Ne5
    g1_id = [e.event_identity for e in ledger.events if getattr(e.event_identity, 'attacker', None) and e.event_identity.attacker.square == 'g1'][0]
    f3_id = [e.event_identity for e in ledger.events if getattr(e.event_identity, 'attacker', None) and e.event_identity.attacker.square == 'f3'][0]
    e5_id = [e.event_identity for e in ledger.events if getattr(e.event_identity, 'attacker', None) and e.event_identity.attacker.square == 'e5' and getattr(e.event_identity.attacker, 'symbol', None) == 'N'][0]
    
    assert graph.get_succession_chain([g1_id, f3_id, e5_id])

def test_cycle_caused_by_reappearance():
    # 1. Nf3 d5 2. Ng1
    pgn = "1. Nf3 d5 2. Ng1"
    ledger = build_temporal_ledger_from_pgn(pgn)
    graph = build_temporal_succession_graph(ledger)
    
    g1_id = [e.event_identity for e in ledger.events if getattr(e.event_identity, 'attacker', None) and e.event_identity.attacker.square == 'g1'][0]
    f3_id = [e.event_identity for e in ledger.events if getattr(e.event_identity, 'attacker', None) and e.event_identity.attacker.square == 'f3'][0]
    
    assert graph.get_succession_chain([g1_id, f3_id, g1_id])

def test_spatially_overlapping_succession():
    pgn = "1. e4"
    ledger = build_temporal_ledger_from_pgn(pgn)
    graph = build_temporal_succession_graph(ledger)
    
    # The e2->e4 move should have some overlapping successions
    has_overlap = any(e.overlaps for e in graph.edges)
    assert has_overlap

def test_spatially_disjoint_succession():
    pgn = "1. e4"
    ledger = build_temporal_ledger_from_pgn(pgn)
    graph = build_temporal_succession_graph(ledger)
    
    has_disjoint = any(not e.overlaps for e in graph.edges)
    assert has_disjoint

def test_short_lived_predecessor_long_observed_successor():
    # 1. Nf3 d5 2. Ng1 c5 3. Nf3 e6 4. a3
    # First Nf3 is short-lived (1 ply), second Nf3 is long-observed (until end).
    pgn = "1. Nf3 d5 2. Ng1 c5 3. Nf3 e6 4. a3"
    ledger = build_temporal_ledger_from_pgn(pgn)
    graph = build_temporal_succession_graph(ledger)
    
    # We can check that the edges have observed durations appropriately
    edge = [e for e in graph.edges if getattr(e.born_event_signature, 'attacker', None) and e.born_event_signature.attacker.square == 'f3']
    assert len(edge) > 0
    assert any(e.observed_duration_of_born_episode is not None for e in edge)

def test_right_censored_successor():
    pgn = "1. e4"
    ledger = build_temporal_ledger_from_pgn(pgn)
    graph = build_temporal_succession_graph(ledger)
    
    edge = [e for e in graph.edges if e.is_born_right_censored]
    assert len(edge) > 0

def test_identical_fen_different_graphs():
    pgn_A = "1. d4 d5 2. c4 c6"
    pgn_B = "1. c4 c6 2. d4 d5"
    
    ledger_A = build_temporal_ledger_from_pgn(pgn_A)
    ledger_B = build_temporal_ledger_from_pgn(pgn_B)
    
    graph_A = build_temporal_succession_graph(ledger_A)
    graph_B = build_temporal_succession_graph(ledger_B)
    
    assert ledger_A.final_fen == ledger_B.final_fen
    
    # Their edge sequences are different due to different move order
    edges_A = [(e.removed_event_signature, e.born_event_signature) for e in graph_A.edges]
    edges_B = [(e.removed_event_signature, e.born_event_signature) for e in graph_B.edges]
    
    assert set(edges_A) != set(edges_B)
