import pytest
from chessheat.protocol_freeze import (
    canonical_pair, transposition_group_key, get_partition, canonical_budget_order,
    get_square_index, encode_position, encode_side_information, build_m_d, build_m_t, build_m_zero, build_m_perm,
    mean_root_nll, mean_seed_root_nll, utility_from_root_losses, compute_aulc, bootstrap_indices, classify_outcome
)

def test_canonical_pair():
    assert canonical_pair("e2e4", "e7e5") == ("e2e4", "e7e5")
    assert canonical_pair("e7e5", "e2e4") == ("e2e4", "e7e5")

def test_transposition_group():
    pos = {
        "board_arrangement_fen": "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR",
        "side_to_move": "w",
        "castling_rights": "KQkq",
        "en_passant_square": None
    }
    assert transposition_group_key(pos) == "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR|w|KQkq|None"

def test_partition():
    pos = {
        "board_arrangement_fen": "abc",
        "side_to_move": "w",
        "castling_rights": "-",
        "en_passant_square": None
    }
    assert get_partition(pos) in ["TRAIN", "VALIDATION", "TEST"]

def test_encode_position():
    pos = {
        "board_arrangement_fen": "8/8/8/8/8/8/8/K7",
        "side_to_move": "w",
        "castling_rights": "K",
        "en_passant_square": "e3"
    }
    p = encode_position(pos)
    assert len(p) == 18 * 64
    
    # White king at a1
    assert p[5 * 64 + get_square_index("a1")] == 1.0
    # side to move W = 1.0
    assert p[12 * 64] == 1.0
    # Castling K
    assert p[13 * 64] == 1.0
    assert p[14 * 64] == 0.0
    # En passant e3
    assert p[17 * 64 + get_square_index("e3")] == 1.0

def test_encode_side_information():
    s = encode_side_information("e2e4", "e7e5", "SOURCE_FIRST_BETTER", 12.5)
    assert len(s) == 270
    # m1 = e2e4
    assert s[get_square_index("e2")] == 1.0
    assert s[64 + get_square_index("e4")] == 1.0
    assert s[128] == 1.0 # NONE promo
    
    # m2 = e7e5
    assert s[133 + get_square_index("e7")] == 1.0
    assert s[133 + 64 + get_square_index("e5")] == 1.0
    assert s[133 + 128] == 1.0 # NONE promo
    
    # dx = FIRST_BETTER
    assert s[266] == 1.0
    # ax = 12.5
    assert s[269] == 12.5

def test_m_maps():
    m_d = build_m_d("e2e4", "e7e5", 10.0)
    assert sum(m_d) == 10.0
    assert m_d[get_square_index("e4")] == 5.0
    assert m_d[get_square_index("e5")] == 5.0

    m_t = build_m_t("e2e4", "e7e5", 10.0)
    assert sum(m_t) == 10.0
    assert sum(build_m_zero()) == 0.0

    m_perm = build_m_perm("e2e4", "e7e5", 10.0)
    assert sum(m_perm) == 10.0
    counts = {0.0: 0, 2.5: 0}
    for v in m_perm: counts[v] = counts.get(v, 0) + 1
    assert counts[0.0] == 60
    assert counts[2.5] == 4

def test_loss_functions():
    with pytest.raises(ValueError): mean_root_nll([])
    assert mean_root_nll([1.0, 2.0]) == 1.5

    with pytest.raises(ValueError): mean_seed_root_nll([1.0])
    assert mean_seed_root_nll([1.0, 1.0, 2.0, 2.0, 1.5]) == 1.5

    with pytest.raises(ValueError): utility_from_root_losses([])
    assert utility_from_root_losses([1.0, 2.0]) == -1.5

def test_compute_aulc():
    with pytest.raises(ValueError): compute_aulc([1, 2], [1.0])
    val = compute_aulc([250, 500], [-1.0, -0.5])
    assert val == -0.75

def test_bootstrap():
    with pytest.raises(ValueError): bootstrap_indices(0, 0, 0)
    idx = bootstrap_indices(0, 0, 100)
    assert 0 <= idx < 100

def test_outcome():
    assert classify_outcome((0.1, 0.5), (0.1, 0.5), (-0.5, 0.5)) == "SUPPORT_muD"
    assert classify_outcome((-0.5, -0.1), (-0.5, 0.5), (0.1, 0.5)) == "SUPPORT_muT"
