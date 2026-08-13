import chess
from chessheat.temporal import build_temporal_ledger_from_pgn
from chessheat.geometry import extract_geometry

def test_temporal_lifecycle():
    # A short game to test appearances, disappearances, and reappearances.
    # We'll move a knight out and then back.
    pgn = "1. Nf3 d5 2. Ng1"
    
    ledger = build_temporal_ledger_from_pgn(pgn)
    
    assert len(ledger.transitions) == 3
    
    # Let's find the attack by Ng1 on f3 at ply 0.
    # At ply 1 (Nf3), that attack disappears.
    # At ply 2 (d5), nothing about white knight changes.
    # At ply 3 (Ng1), the attack on f3 reappears.
    
    # 1. Event present initially, removed, reappeared (Ng1 attack on f3)
    ng1_f3_events = [e for e in ledger.events if e.event_type == 'attack' and e.event_identity.attacker.symbol == 'N' and e.event_identity.target_square == 'f3']
    assert len(ng1_f3_events) == 1
    event = ng1_f3_events[0]
    # It started at ply 0. Disappeared at ply 1 (exclusive endpoint). Reappeared at ply 3, active until end.
    assert event.active_intervals == [(0, 1), (3, None)]
    # observed_total_active_plies at ply 3 should be (1 - 0) + (3 - 3) = 1
    assert event.observed_total_active_plies(3) == 1

    # 2. Event present initially, persists to the end (Rh1 defense of h2)
    rh1_h2_events = [e for e in ledger.events if e.event_type == 'defense' and e.event_identity.attacker.symbol == 'R' and e.event_identity.target_square == 'h2']
    assert len(rh1_h2_events) == 1
    assert rh1_h2_events[0].active_intervals == [(0, None)]

    # 3. Event created and then permanently removed (Nf3 attack on d4)
    nf3_d4_events = [e for e in ledger.events if e.event_type == 'attack' and e.event_identity.attacker.square == 'f3' and e.event_identity.target_square == 'd4']
    assert len(nf3_d4_events) == 1
    assert nf3_d4_events[0].active_intervals == [(1, 3)]

def test_transposition_invariance():
    # History A: 1. e4 e5 2. Nf3 Nc6
    pgn_a = "1. e4 e5 2. Nf3 Nc6"
    
    # History B: 1. Nf3 Nc6 2. e4 e5
    pgn_b = "1. Nf3 Nc6 2. e4 e5"
    
    ledger_a = build_temporal_ledger_from_pgn(pgn_a)
    ledger_b = build_temporal_ledger_from_pgn(pgn_b)
    
    board_a = chess.Board(ledger_a.final_fen)
    board_b = chess.Board(ledger_b.final_fen)
    
    # They should reach the exact same state (ignoring half-move clock which differs due to pawn move timing)
    assert board_a.board_fen() == board_b.board_fen()
    
    geo_a = extract_geometry(board_a)
    geo_b = extract_geometry(board_b)
    
    # Current-state geometry should be strictly identical (ignoring FEN string differences due to clocks)
    assert geo_a.attacks == geo_b.attacks
    assert geo_a.defenses == geo_b.defenses
    assert geo_a.rays == geo_b.rays
    assert geo_a.mobility == geo_b.mobility
    
    # However, the historical ledger should differ because the sequence of events is different.
    # Let's find the Nf3 attack on e5 where the target_piece is the Black Pawn (which is the state at the end).
    nf3_e5_a = [e for e in ledger_a.events if e.event_type == 'attack' and e.event_identity.attacker.square == 'f3' and e.event_identity.target_square == 'e5' and e.event_identity.target_piece is not None][0]
    nf3_e5_b = [e for e in ledger_b.events if e.event_type == 'attack' and e.event_identity.attacker.square == 'f3' and e.event_identity.target_square == 'e5' and e.event_identity.target_piece is not None][0]
    
    # In history A, Nf3 is played at ply 3 (White's 2nd move).
    # In history B, Nf3 is played at ply 1 (White's 1st move). e5 is played at ply 4 (Black's 2nd move).
    # In A: e5 is ply 2. Nf3 is ply 3. Attack appears at ply 3.
    # In B: Nf3 is ply 1. e5 is ply 4. Attack appears at ply 4.
    
    assert nf3_e5_a.active_intervals == [(3, None)]
    assert nf3_e5_b.active_intervals == [(4, None)]
    
    # This proves T(H_A) != T(H_B) while G(P_A) == G(P_B). Note that exact FENs differ due to the half-move clock.

def test_exact_fen_transposition_invariance():
    # History A: 1. Nf3 Nf6 2. Nc3 Nc6 3. e4 e5
    pgn_a = "1. Nf3 Nf6 2. Nc3 Nc6 3. e4 e5"
    
    # History B: 1. Nc3 Nc6 2. Nf3 Nf6 3. e4 e5
    pgn_b = "1. Nc3 Nc6 2. Nf3 Nf6 3. e4 e5"
    
    ledger_a = build_temporal_ledger_from_pgn(pgn_a)
    ledger_b = build_temporal_ledger_from_pgn(pgn_b)
    
    # They should reach strictly identical FENs, including half-move clocks
    assert ledger_a.final_fen == ledger_b.final_fen
    
    board_a = chess.Board(ledger_a.final_fen)
    board_b = chess.Board(ledger_b.final_fen)
    
    geo_a = extract_geometry(board_a)
    geo_b = extract_geometry(board_b)
    
    # Current-state geometry should be strictly identical
    assert geo_a.attacks == geo_b.attacks
    assert geo_a.defenses == geo_b.defenses
    assert geo_a.rays == geo_b.rays
    assert geo_a.mobility == geo_b.mobility
    
    # Legal-root set equality
    legal_a = set(board_a.legal_moves)
    legal_b = set(board_b.legal_moves)
    assert legal_a == legal_b
    
    # Temporal Ledger inequality is permitted and expected.
    # E.g., Nf3 attack on e5.
    nf3_e5_a = [e for e in ledger_a.events if e.event_type == 'attack' and e.event_identity.attacker.square == 'f3' and e.event_identity.target_square == 'e5' and e.event_identity.target_piece is not None][0]
    nf3_e5_b = [e for e in ledger_b.events if e.event_type == 'attack' and e.event_identity.attacker.square == 'f3' and e.event_identity.target_square == 'e5' and e.event_identity.target_piece is not None][0]
    
    # History A: e4 e5 is ply 5,6. Nf3 is ply 1. Attack appears at ply 6.
    # History B: e4 e5 is ply 5,6. Nf3 is ply 3. Attack appears at ply 6.
    # Wait, the attack Nf3->e5 appears when e5 is played, which is ply 6 in BOTH histories.
    # Let's find an event that differs.
    # Nf3 attack on d4:
    # History A: Nf3 is ply 1. Attack on d4 appears at ply 1.
    # History B: Nf3 is ply 3. Attack on d4 appears at ply 3.
    nf3_d4_a = [e for e in ledger_a.events if e.event_type == 'attack' and e.event_identity.attacker.square == 'f3' and e.event_identity.target_square == 'd4'][0]
    nf3_d4_b = [e for e in ledger_b.events if e.event_type == 'attack' and e.event_identity.attacker.square == 'f3' and e.event_identity.target_square == 'd4'][0]
    
    assert nf3_d4_a.active_intervals[0][0] == 1
    assert nf3_d4_b.active_intervals[0][0] == 3
    
    # Temporal ledger separates histories even when exact FENs match completely.
