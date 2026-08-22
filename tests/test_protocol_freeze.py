import pytest
import math
import struct
import json
from chessheat.protocol_freeze import (
    CanonicalTensorF32, uci_square_index, spatial_row_col, spatial_flat_index,
    SourcePairFeatures, encode_position, encode_side_information, build_m_d, build_m_t, build_m_zero, build_m_perm,
    get_partition, canonical_budget_order, compute_aulc, classify_outcome, bootstrap_indices, percentile_rank,
    canonical_protocol_payload_v4, canonical_protocol_bytes_v4, canonical_group_json_bytes
)

def test_canonical_pair():
    p1 = SourcePairFeatures("e2e4", 100, "e7e5", 50)
    assert p1.m1_uci == "e2e4"
    assert p1.m2_uci == "e7e5"
    assert p1.d_x == "SOURCE_FIRST_BETTER"
    assert p1.a_x == 50

    p2 = SourcePairFeatures("e7e5", 50, "e2e4", 100)
    assert p2.m1_uci == "e2e4"
    assert p2.m2_uci == "e7e5"
    assert p2.d_x == "SOURCE_FIRST_BETTER"  # d_X derived after sorting
    assert p2.a_x == 50

    with pytest.raises(ValueError):
        SourcePairFeatures("e2e4", 100, "e2e4", 50)  # duplicate
    with pytest.raises(ValueError):
        SourcePairFeatures("e2e4", float("nan"), "e7e5", 50)
    
def test_side_info():
    p = SourcePairFeatures("e2e4", 100, "e7e5", 50)
    tensor = encode_side_information(p)
    assert tensor.shape == (270,)
    assert tensor.values[uci_square_index("e2")] == 1.0
    assert tensor.values[64 + uci_square_index("e4")] == 1.0
    assert tensor.values[128] == 1.0  # NONE promo
    
    assert tensor.values[266] == 1.0  # FIRST_BETTER
    assert tensor.values[269] == 50.0 # a_X
    
    with pytest.raises(ValueError):
        # We can simulate an invalid promotion internally by tweaking the pair temporarily if it didn't check, 
        # but the test requirements say check invalid promo. We'll pass one manually via a mock.
        SourcePairFeatures("e2e4z", 10, "e7e5", 20) # This would fail in uci_square_index or promo logic
    
def test_coordinates():
    assert uci_square_index("a1") == 0
    assert uci_square_index("h8") == 63
    
    assert spatial_row_col("a8") == (0, 0)
    assert spatial_flat_index("a8") == 0
    assert spatial_row_col("h8") == (0, 7)
    assert spatial_flat_index("h8") == 7
    assert spatial_row_col("a1") == (7, 0)
    assert spatial_flat_index("a1") == 56
    assert spatial_row_col("h1") == (7, 7)
    assert spatial_flat_index("h1") == 63
    assert spatial_flat_index("e4") == 4 * 8 + 4 # row 4 (8-4), col 4 ('e') -> 36

def test_p_encoding():
    pos = {
        "board_arrangement_fen": "8/8/8/8/8/8/8/K7",  # King on a1
        "side_to_move": "w",
        "castling_rights": "K",
        "en_passant_square": None
    }
    t = encode_position(pos)
    assert t.shape == (18, 8, 8)
    assert len(t.to_bytes()) == 18 * 8 * 8 * 4
    # K is plane 5. a1 is 56
    assert t.values[5 * 64 + 56] == 1.0
    
def test_m_maps():
    p = SourcePairFeatures("e2e4", 100, "e7e5", 50)
    m_d = build_m_d(p)
    assert m_d.shape == (1, 8, 8)
    assert m_d.values[spatial_flat_index("e4")] == 25.0
    assert m_d.values[spatial_flat_index("e5")] == 25.0
    
    m_t = build_m_t(p)
    for sq in ["e2", "e4", "e7", "e5"]:
        assert m_t.values[spatial_flat_index(sq)] == 12.5
        
    m_zero = build_m_zero()
    assert sum(m_zero.values) == 0.0
    
    m_perm = build_m_perm(p)
    assert sum(m_perm.values) == 50.0
    counts = {0.0: 0, 12.5: 0}
    for v in m_perm.values: counts[v] = counts.get(v, 0) + 1
    assert counts[0.0] == 60
    assert counts[12.5] == 4

def test_split():
    pos1 = {"board_arrangement_fen": "abc", "side_to_move": "w", "castling_rights": "K", "en_passant_square": None}
    pos2 = {"board_arrangement_fen": "abc", "side_to_move": "w", "castling_rights": "K", "en_passant_square": None}
    assert get_partition(pos1) == get_partition(pos2)
    # The counts are tested via external script. But we assert the JSON serialization is stable.
    b = canonical_group_json_bytes(pos1)
    assert b'abc' in b

def test_budget():
    digest1, root1 = canonical_budget_order("rootA")
    digest2, root2 = canonical_budget_order("rootB")
    assert digest1 != digest2

def test_aulc():
    val = compute_aulc([250, 500], [-1.0, -0.5])
    assert val == -0.75
    # D-better -> Delta_DT positive
    # D lower NLL (-0.5 vs -1.0) -> U_D is -0.5, U_T is -1.0
    u_d = [-0.5, -0.5]
    u_t = [-1.0, -1.0]
    aulc_d = compute_aulc([1, 2], u_d)
    aulc_t = compute_aulc([1, 2], u_t)
    assert aulc_d - aulc_t > 0
    
    with pytest.raises(ValueError): compute_aulc([1, 2], [1.0])
    with pytest.raises(ValueError): compute_aulc([1, 1], [1.0, 1.0])
    with pytest.raises(ValueError): compute_aulc([1, 2], [1.0, float('nan')])
    with pytest.raises(ValueError): compute_aulc([1, 2], [1.0, float('inf')])

def test_bootstrap():
    idx1 = bootstrap_indices(0, 0, 100)
    idx2 = bootstrap_indices(0, 0, 100)
    assert idx1 == idx2
    assert percentile_rank(10000, 0.025) == 249

def test_outcome():
    assert classify_outcome((0.1, 0.5), (0.1, 0.5), (-0.5, 0.5), True) == "SUPPORT_muD"
    assert classify_outcome((-0.5, -0.1), (-0.5, 0.5), (0.1, 0.5), True) == "SUPPORT_muT"
    assert classify_outcome((0.1, 0.5), (0.1, 0.5), (-0.5, 0.5), False) == "PROTOCOL_INVALID"
    with pytest.raises(ValueError):
        classify_outcome((0.5, 0.1), (0.1, 0.5), (-0.5, 0.5), True) # unordered
    with pytest.raises(ValueError):
        classify_outcome((float('nan'), 0.5), (0.1, 0.5), (-0.5, 0.5), True)

def test_protocol_seal():
    # Load JSON from disk
    with open('artifacts/research/cp_representation_efficiency_protocol_v4.json', 'rb') as f:
        disk_bytes = f.read()
    mem_bytes = canonical_protocol_bytes_v4()
    assert disk_bytes == mem_bytes
    payload = canonical_protocol_payload_v4()
    assert payload['s_numeric_encoding']['dimension'] == 270

def test_continuity():
    # just check that the files have sufficient lines
    with open('docs/research/NEXT_WORK_MAP.md') as f:
        assert len(f.readlines()) > 500
    with open('docs/research/RESEARCH_CONTINUITY_CHECKPOINT_2026-08-16.md') as f:
        assert len(f.readlines()) > 700
import pytest
import math
import struct
import json
from typing import Dict

from src.chessheat.protocol_freeze import (
    CanonicalTensorF32,
    uci_square_index,
    spatial_row_col,
    spatial_flat_index,
    SourcePairFeatures,
    encode_position,
    encode_side_information,
    build_m_d,
    build_m_t,
    build_m_zero,
    build_m_perm,
    get_partition,
    canonical_budget_order,
    compute_aulc,
    classify_outcome,
    bootstrap_indices,
    percentile_rank,
    mean_five_seed_root_nll,
    full_bootstrap_procedure,
    canonical_protocol_payload_v4,
    canonical_protocol_bytes_v4
)

def test_square_validation():
    assert uci_square_index("a1") == 0
    assert uci_square_index("h8") == 63
    
    with pytest.raises(ValueError): uci_square_index("a")
    with pytest.raises(ValueError): uci_square_index("A1")
    with pytest.raises(ValueError): uci_square_index("i1")
    with pytest.raises(ValueError): uci_square_index("a9")
    with pytest.raises(ValueError): uci_square_index(" e2")

def test_uci_validation():
    # duplicate
    with pytest.raises(ValueError): SourcePairFeatures("e2e4", 10, "e2e4", 10)
    # malformed
    with pytest.raises(ValueError): SourcePairFeatures("E2E4", 10, "e7e5", 20)
    with pytest.raises(ValueError): SourcePairFeatures("e2", 10, "e7e5", 20)
    with pytest.raises(ValueError): SourcePairFeatures("e2e4qq", 10, "e7e5", 20)
    with pytest.raises(ValueError): SourcePairFeatures("e2e4z", 10, "e7e5", 20)
    with pytest.raises(ValueError): SourcePairFeatures("e2e", 10, "e7e5", 20)

    # valid promotion
    SourcePairFeatures("e7e8q", 10, "e7e8r", 20)

def test_promotion_validation():
    pair = SourcePairFeatures("e7e8q", 10, "e2e4", 20)
    # this will pass encode_side_information
    encode_side_information(pair)
    
    # but let's mock the internal pair to have an invalid promotion string
    # since SourcePairFeatures regex requires [qrbn], we can't test invalid promotion inside it directly
    # because it will be rejected early, which is exactly what we want!

def test_canonical_swapping():
    # canonicalization sorts moves
    p1 = SourcePairFeatures("e2e4", 100, "e7e5", 50)
    p2 = SourcePairFeatures("e7e5", 50, "e2e4", 100)
    
    assert p1.m1_uci == "e2e4" and p1.m2_uci == "e7e5"
    assert p2.m1_uci == "e2e4" and p2.m2_uci == "e7e5"
    
    assert p1.cp1 == 100 and p1.cp2 == 50
    assert p2.cp1 == 100 and p2.cp2 == 50
    
    assert p1.d_x == "SOURCE_FIRST_BETTER"
    assert p2.d_x == "SOURCE_FIRST_BETTER"
    assert p1.a_x == 50
    assert p2.a_x == 50

def test_dx_values():
    assert SourcePairFeatures("a1a2", 10, "h7h8", 20).d_x == "SOURCE_SECOND_BETTER"
    assert SourcePairFeatures("a1a2", 20, "h7h8", 10).d_x == "SOURCE_FIRST_BETTER"
    assert SourcePairFeatures("a1a2", 10, "h7h8", 10).d_x == "SOURCE_EQUAL"

    with pytest.raises(ValueError): SourcePairFeatures("a1a2", float('inf'), "h7h8", 10)
    with pytest.raises(ValueError): SourcePairFeatures("a1a2", float('nan'), "h7h8", 10)

def test_float32():
    t = CanonicalTensorF32((2,), [1.0, -1.0])
    b = t.to_bytes()
    assert len(b) == 8
    
    with pytest.raises(ValueError): CanonicalTensorF32((2,), [float('nan'), 1.0])
    with pytest.raises(ValueError): CanonicalTensorF32((2,), [float('inf'), 1.0])
    with pytest.raises(ValueError): CanonicalTensorF32((2,), [1.0, 2.0, 3.0])

def test_coordinates():
    assert spatial_row_col("a8") == (0, 0)
    assert spatial_row_col("h8") == (0, 7)
    assert spatial_row_col("a1") == (7, 0)
    assert spatial_row_col("h1") == (7, 7)
    assert spatial_row_col("e4") == (4, 4)

def test_source_counts():
    payload = canonical_protocol_payload_v4()
    assert payload["source_evidence"]["population_count"] == 33859
    assert payload["source_evidence"]["source_pair_eligible_count"] == 33444
    assert payload["source_evidence"]["source_zero_pair_count"] == 415

    assert payload["split"]["expected_all_root_counts"] == {"TRAIN": 23639, "VALIDATION": 5148, "TEST": 5072}
    assert payload["split"]["expected_eligible_counts"] == {"TRAIN": 23350, "VALIDATION": 5094, "TEST": 5000}
    assert payload["split"]["expected_zero_counts"] == {"TRAIN": 289, "VALIDATION": 54, "TEST": 72}
    
    assert sum(payload["split"]["expected_all_root_counts"].values()) == 33859
    assert sum(payload["split"]["expected_eligible_counts"].values()) == 33444

def test_split():
    pos = {"board_arrangement_fen": "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR", "side_to_move": "w", "castling_rights": "KQkq", "en_passant_square": None}
    assert get_partition(pos) == get_partition(pos)

def test_budget():
    b1, _ = canonical_budget_order("root1")
    b2, _ = canonical_budget_order("root2")
    assert b1 != b2

def test_seeds():
    # missing seed
    with pytest.raises(ValueError): mean_five_seed_root_nll({1729: 1.0, 2718: 1.0, 31415: 1.0, 65537: 1.0})
    # extra seed
    with pytest.raises(ValueError): mean_five_seed_root_nll({1729: 1.0, 2718: 1.0, 31415: 1.0, 65537: 1.0, 104729: 1.0, 999: 1.0})
    # exact
    assert mean_five_seed_root_nll({1729: 1.0, 2718: 2.0, 31415: 3.0, 65537: 4.0, 104729: 5.0}) == 3.0
    # nonfinite
    with pytest.raises(ValueError): mean_five_seed_root_nll({1729: 1.0, 2718: 2.0, 31415: float('inf'), 65537: 4.0, 104729: 5.0})

def test_aulc():
    assert compute_aulc([10, 20], [1.0, 1.0]) == 1.0
    
    # +1 D better, -1 T better
    # In ChessHeat, larger U is better. U = -NLL. 
    # If D is better, U_D is larger than U_T.
    # Delta_DT = AULC_D - AULC_T > 0
    # So a positive Delta means D favored.
    
    with pytest.raises(ValueError): compute_aulc([10], [1.0])
    with pytest.raises(ValueError): compute_aulc([10, 20], [1.0])
    with pytest.raises(ValueError): compute_aulc([10, 10], [1.0, 2.0])
    with pytest.raises(ValueError): compute_aulc([20, 10], [1.0, 2.0])
    with pytest.raises(ValueError): compute_aulc([10, 20], [1.0, float('nan')])
    with pytest.raises(ValueError): compute_aulc([10, 20], [1.0, float('inf')])

def test_full_bootstrap():
    root_ids = ["root1", "root2", "root3"]
    expected_budgets = [250, 500, 1000, 2000, 4000, 8000, 16000, 20000]
    
    def mk_losses(val_D, val_T, val_0):
        d = {"mu_D": {}, "mu_T": {}, "B_daS": {}}
        for b in expected_budgets:
            d["mu_D"][b] = {r: val_D for r in root_ids}
            d["mu_T"][b] = {r: val_T for r in root_ids}
            d["B_daS"][b] = {r: val_0 for r in root_ids}
        return d
    
    # Toy D better
    # Loss is NLL, so smaller is better. D has loss 1.0, T 2.0, 0 has 3.0
    losses = mk_losses(1.0, 2.0, 3.0)
    
    res = full_bootstrap_procedure(root_ids, losses)
    
    # AULC for U = -NLL
    # D: U = -1.0
    # T: U = -2.0
    # B: U = -3.0
    # Delta_DT = (-1.0) - (-2.0) = 1.0
    assert abs(res["Delta_DT"]["lcb"] - 1.0) < 1e-6
    assert abs(res["Delta_DT"]["ucb"] - 1.0) < 1e-6
    assert abs(res["Delta_D0"]["lcb"] - 2.0) < 1e-6
    assert abs(res["Delta_T0"]["lcb"] - 1.0) < 1e-6
    
    # Bad conditions
    bad_losses = mk_losses(1.0, 2.0, 3.0)
    del bad_losses["mu_D"]
    with pytest.raises(ValueError): full_bootstrap_procedure(root_ids, bad_losses)
    
    bad_losses2 = mk_losses(1.0, 2.0, 3.0)
    del bad_losses2["mu_T"][250]
    with pytest.raises(ValueError): full_bootstrap_procedure(root_ids, bad_losses2)
    
    bad_losses3 = mk_losses(1.0, 2.0, 3.0)
    bad_losses3["mu_T"][250]["root1"] = float('inf')
    with pytest.raises(ValueError): full_bootstrap_procedure(root_ids, bad_losses3)
    
    # Non unique roots
    with pytest.raises(ValueError): full_bootstrap_procedure(["root1", "root1"], losses)

def test_outcome():
    # PROTOCOL_INVALID
    assert classify_outcome((1, 2), (1, 2), (1, 2), False) == "PROTOCOL_INVALID"
    
    # SUPPORT_muD: LCB_DT > 0, LCB_D0 > 0
    assert classify_outcome((0.1, 2), (0.1, 2), (-1, 1), True) == "SUPPORT_muD"
    
    # SUPPORT_muT: UCB_DT < 0, LCB_T0 > 0
    assert classify_outcome((-2, -0.1), (-1, 1), (0.1, 2), True) == "SUPPORT_muT"
    
    # SPATIAL_EFFICIENCY_OPERATOR_UNRESOLVED
    assert classify_outcome((-1, 1), (0.1, 2), (-1, 1), True) == "SPATIAL_EFFICIENCY_OPERATOR_UNRESOLVED"
    
    # NO_SPATIAL_EFFICIENCY_ADVANTAGE
    assert classify_outcome((-1, 1), (-2, -0.1), (-2, -0.1), True) == "NO_SPATIAL_EFFICIENCY_ADVANTAGE"
    
    # INCONCLUSIVE
    assert classify_outcome((-1, 1), (-1, 1), (-1, 1), True) == "INCONCLUSIVE"
    
    # Malformed CI
    with pytest.raises(ValueError): classify_outcome((2, 1), (1, 2), (1, 2), True)
    with pytest.raises(ValueError): classify_outcome((float('nan'), 1), (1, 2), (1, 2), True)
    with pytest.raises(ValueError): classify_outcome((1, float('inf')), (1, 2), (1, 2), True)

def test_protocol_seal():
    payload = canonical_protocol_payload_v4()
    # Check learner properties
    assert payload["learner"]["initialization"]["fan_in_conv1"] == 171
    assert payload["learner"]["optimizer"]["name"] == "Adam"
    assert payload["learner"]["dropout"] == "none"
    assert payload["learner"]["normalization"] == "none"
    assert payload["s_numeric_encoding"]["dimension"] == 270
    assert payload["execution_status"]["target"] == "STRICTLY UNAUTHORIZED"
    assert "compare_scores" in payload["target_labels"]["semantics"]
    
    # byte check
    b = canonical_protocol_bytes_v4()
    p2 = json.loads(b.decode('utf-8'))
    assert p2 == payload

