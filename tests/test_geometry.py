import pytest
import chess
from chessheat.geometry import extract_geometry, compute_geometry_delta

def test_deterministic_extraction():
    fen = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"
    b1 = chess.Board(fen)
    b2 = chess.Board(fen)

    g1 = extract_geometry(b1)
    g2 = extract_geometry(b2)

    # Check sets are identical
    assert g1.attacks == g2.attacks
    assert g1.defenses == g2.defenses
    assert g1.rays == g2.rays
    assert g1.mobility == g2.mobility

def test_moving_blocker_opens_ray():
    # Rook on a1, Pawn on a2. Move pawn a2->a4
    b_before = chess.Board("8/8/8/8/8/8/P7/R7 w - - 0 1")
    g_before = extract_geometry(b_before)

    b_after = chess.Board("8/8/8/8/P7/8/8/R7 w - - 0 1")
    g_after = extract_geometry(b_after)

    delta = compute_geometry_delta(g_before, g_after)

    # Ray North from a1 to a2 should disappear
    dis_ray_N = [r for r in delta.disappeared_rays if r.source.square == "a1" and r.direction_name == "N"]
    assert len(dis_ray_N) == 1
    assert dis_ray_N[0].target_square == "a2"

    # Ray North from a1 to a4 should appear
    app_ray_N = [r for r in delta.appeared_rays if r.source.square == "a1" and r.direction_name == "N"]
    assert len(app_ray_N) == 1
    assert app_ray_N[0].target_square == "a4"
    assert "a2" in app_ray_N[0].path
    assert "a3" in app_ray_N[0].path

def test_introducing_blocker_closes_ray():
    # Rook on h1, targeting h8
    b_before = chess.Board("7k/8/8/8/8/8/8/7R b - - 0 1")
    g_before = extract_geometry(b_before)

    # Black king moves to h7, blocking the h8 square
    b_after = chess.Board("8/7k/8/8/8/8/8/7R b - - 0 1")
    g_after = extract_geometry(b_after)

    delta = compute_geometry_delta(g_before, g_after)

    # Ray North from h1 to h8 should disappear
    dis_ray = [r for r in delta.disappeared_rays if r.source.square == "h1" and r.direction_name == "N"]
    assert len(dis_ray) == 1
    assert dis_ray[0].target_square == "h8"

    # Ray North from h1 to h7 should appear
    app_ray = [r for r in delta.appeared_rays if r.source.square == "h1" and r.direction_name == "N"]
    assert len(app_ray) == 1
    assert app_ray[0].target_square == "h7"

def test_captures_remove_relationships():
    # White queen on d4, black knight on e5
    b_before = chess.Board("8/8/8/4n3/3Q4/8/8/8 w - - 0 1")
    g_before = extract_geometry(b_before)

    # Queen captures knight d4xe5
    b_after = chess.Board("8/8/8/4Q3/8/8/8/8 b - - 0 1")
    g_after = extract_geometry(b_after)

    delta = compute_geometry_delta(g_before, g_after)

    # Attack d4->e5 should disappear
    dis_attacks = [a for a in delta.disappeared_attacks if a.attacker.square == "d4" and a.target_square == "e5"]
    assert len(dis_attacks) == 1

    # New attacks from e5 should appear
    app_attacks = [a for a in delta.appeared_attacks if a.attacker.square == "e5"]
    assert len(app_attacks) > 0

def test_defender_relationships():
    # White rook on a1, white knight on b1. Rook defends knight.
    b_before = chess.Board("8/8/8/8/8/8/8/RN6 w - - 0 1")
    g_before = extract_geometry(b_before)

    # Defenses: a1->b1
    defenses = [d for d in g_before.defenses if d.attacker.square == "a1" and d.target_square == "b1"]
    assert len(defenses) == 1

    # Knight moves to c3
    b_after = chess.Board("8/8/8/8/8/2N5/8/R7 w - - 0 1")
    g_after = extract_geometry(b_after)

    delta = compute_geometry_delta(g_before, g_after)

    # Defense a1->b1 disappeared
    dis_defenses = [d for d in delta.disappeared_defenses if d.attacker.square == "a1" and d.target_square == "b1"]
    assert len(dis_defenses) == 1

    # Defense a1->c3 does NOT exist because it's not a knight move
    app_defenses = [d for d in delta.appeared_defenses if d.attacker.square == "a1" and d.target_square == "c3"]
    assert len(app_defenses) == 0

def test_legal_mobility_absolute_pin():
    # Black king on e8, black knight on e7, white rook on e1
    # Knight on e7 is pinned.
    b = chess.Board("4k3/4n3/8/8/8/8/8/4R3 b - - 0 1")
    g = extract_geometry(b)

    mob = next(m for m in g.mobility if m.piece.square == "e7")

    # Pseudo-legal includes standard knight moves e.g., d5, f5, c6, g6, c8, g8, d5... wait e7 can go to c8, d5, f5, g8, c6, g6
    assert "d5" in mob.pseudo_legal_destinations

    # But legal destinations should be empty due to absolute pin
    assert len(mob.legal_destinations) == 0
