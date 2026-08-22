import hashlib
import json
import math
import struct
import re
from typing import Tuple, List, Set, Dict, Any, Optional, Mapping

class CanonicalTensorF32:
    def __init__(self, shape: Tuple[int, ...], values: List[float]):
        if math.prod(shape) != len(values):
            raise ValueError(f"Shape {shape} requires {math.prod(shape)} elements, got {len(values)}")
        self.shape = shape
        self.dtype = "float32-le"
        self.values = []
        for v in values:
            v_float = float(v)
            if not math.isfinite(v_float):
                raise ValueError("Values must be finite")
            packed = struct.pack("<f", v_float)
            unpacked = struct.unpack("<f", packed)[0]
            self.values.append(unpacked)
            
    def to_bytes(self) -> bytes:
        return b"".join(struct.pack("<f", v) for v in self.values)

def _validate_square(square: str):
    if not isinstance(square, str) or not re.match(r"^[a-h][1-8]$", square):
        raise ValueError(f"Invalid canonical square: {square}")

def _validate_move(move: str):
    if not isinstance(move, str) or not re.match(r"^[a-h][1-8][a-h][1-8][qrbn]?$", move):
        raise ValueError(f"Invalid canonical move: {move}")

def uci_square_index(square: str) -> int:
    _validate_square(square)
    f = ord(square[0]) - ord('a')
    r = int(square[1]) - 1
    return r * 8 + f

def spatial_row_col(square: str) -> Tuple[int, int]:
    _validate_square(square)
    f = ord(square[0]) - ord('a')
    r = int(square[1])
    return 8 - r, f

def spatial_flat_index(square: str) -> int:
    row, col = spatial_row_col(square)
    return row * 8 + col

class SourcePairFeatures:
    def __init__(self, m_a: str, cp_a: int, m_b: str, cp_b: int):
        _validate_move(m_a)
        _validate_move(m_b)
        if m_a == m_b:
            raise ValueError("Moves must be distinct")
        if not math.isfinite(cp_a) or not math.isfinite(cp_b):
            raise ValueError("CP values must be finite")
            
        if m_a < m_b:
            self.m1_uci, self.cp1 = m_a, cp_a
            self.m2_uci, self.cp2 = m_b, cp_b
        else:
            self.m1_uci, self.cp1 = m_b, cp_b
            self.m2_uci, self.cp2 = m_a, cp_a
            
        if self.cp1 > self.cp2:
            self.d_x = "SOURCE_FIRST_BETTER"
        elif self.cp1 == self.cp2:
            self.d_x = "SOURCE_EQUAL"
        else:
            self.d_x = "SOURCE_SECOND_BETTER"
            
        self.a_x = abs(self.cp1 - self.cp2)

def encode_position(sufficient_position: dict) -> CanonicalTensorF32:
    out = [0.0] * (18 * 64)
    def set_val(plane: int, sq_str: str, val: float):
        idx = spatial_flat_index(sq_str)
        out[plane * 64 + idx] = val
        
    fen = sufficient_position['board_arrangement_fen']
    side = sufficient_position['side_to_move']
    castling = sufficient_position['castling_rights']
    ep = sufficient_position.get('en_passant_square')
    
    pieces = 'PNBRQKpnbrqk'
    ranks = fen.split()[0].split('/')
    for r_idx, rank_str in enumerate(ranks):
        rank_num = 8 - r_idx
        f_idx = 0
        for char in rank_str:
            if char.isdigit():
                f_idx += int(char)
            else:
                p_idx = pieces.index(char)
                sq_str = f"{chr(ord('a') + f_idx)}{rank_num}"
                set_val(p_idx, sq_str, 1.0)
                f_idx += 1
                
    side_val = 1.0 if side == 'w' else 0.0
    for r in range(1, 9):
        for f in "abcdefgh":
            set_val(12, f"{f}{r}", side_val)
            
    if castling != '-':
        if 'K' in castling:
            for r in range(1, 9):
                for f in "abcdefgh": set_val(13, f"{f}{r}", 1.0)
        if 'Q' in castling:
            for r in range(1, 9):
                for f in "abcdefgh": set_val(14, f"{f}{r}", 1.0)
        if 'k' in castling:
            for r in range(1, 9):
                for f in "abcdefgh": set_val(15, f"{f}{r}", 1.0)
        if 'q' in castling:
            for r in range(1, 9):
                for f in "abcdefgh": set_val(16, f"{f}{r}", 1.0)
                
    if ep:
        set_val(17, ep, 1.0)
        
    return CanonicalTensorF32((18, 8, 8), out)

def encode_side_information(pair: SourcePairFeatures) -> CanonicalTensorF32:
    out = [0.0] * 270
    def encode_move(m: str, offset: int):
        from_sq = uci_square_index(m[0:2])
        to_sq = uci_square_index(m[2:4])
        out[offset + from_sq] = 1.0
        out[offset + 64 + to_sq] = 1.0
        
        promo = m[4] if len(m) == 5 else None
        p_idx = 0
        if promo == 'q': p_idx = 1
        elif promo == 'r': p_idx = 2
        elif promo == 'b': p_idx = 3
        elif promo == 'n': p_idx = 4
        elif promo is not None:
            raise ValueError(f"Invalid promotion {promo}")
        out[offset + 128 + p_idx] = 1.0

    encode_move(pair.m1_uci, 0)
    encode_move(pair.m2_uci, 133)
    
    if pair.d_x == "SOURCE_FIRST_BETTER": out[266] = 1.0
    elif pair.d_x == "SOURCE_EQUAL": out[267] = 1.0
    elif pair.d_x == "SOURCE_SECOND_BETTER": out[268] = 1.0
    else: raise ValueError(f"Unknown d_x: {pair.d_x}")
        
    out[269] = float(pair.a_x)
    return CanonicalTensorF32((270,), out)

def build_m_d(pair: SourcePairFeatures) -> CanonicalTensorF32:
    D = set([pair.m1_uci[2:4], pair.m2_uci[2:4]])
    val = pair.a_x / len(D) if len(D) > 0 else 0.0
    out = [0.0] * 64
    for sq in D:
        out[spatial_flat_index(sq)] = val
    return CanonicalTensorF32((1, 8, 8), out)

def build_m_t(pair: SourcePairFeatures) -> CanonicalTensorF32:
    T = set([pair.m1_uci[0:2], pair.m1_uci[2:4], pair.m2_uci[0:2], pair.m2_uci[2:4]])
    val = pair.a_x / len(T) if len(T) > 0 else 0.0
    out = [0.0] * 64
    for sq in T:
        out[spatial_flat_index(sq)] = val
    return CanonicalTensorF32((1, 8, 8), out)

def build_m_zero() -> CanonicalTensorF32:
    return CanonicalTensorF32((1, 8, 8), [0.0] * 64)

def get_b_perm_mapping() -> Dict[str, str]:
    canon = []
    for r in range(1, 9):
        for f in "abcdefgh":
            canon.append(f"{f}{r}")
    
    def key_fn(s: str):
        return hashlib.sha256(b"CHESSHEAT_MATCHED_PERM_V3|" + s.encode("ascii")).digest()
        
    sorted_canon = sorted(canon, key=lambda x: (key_fn(x), x))
    return {canon[i]: sorted_canon[i] for i in range(64)}

_B_PERM_MAP = get_b_perm_mapping()

def build_m_perm(pair: SourcePairFeatures) -> CanonicalTensorF32:
    m_t = build_m_t(pair)
    out = [0.0] * 64
    for r in range(1, 9):
        for f in "abcdefgh":
            sq = f"{f}{r}"
            mapped_sq = _B_PERM_MAP[sq]
            out[spatial_flat_index(mapped_sq)] = m_t.values[spatial_flat_index(sq)]
    return CanonicalTensorF32((1, 8, 8), out)

def canonical_group_json_bytes(sufficient_position: dict) -> bytes:
    group = {
        "board_arrangement_fen": sufficient_position['board_arrangement_fen'],
        "side_to_move": sufficient_position['side_to_move'],
        "castling_rights": sufficient_position['castling_rights'],
        "en_passant_square": sufficient_position.get('en_passant_square')
    }
    return json.dumps(group, sort_keys=True, separators=(',', ':')).encode('utf-8')

def get_partition(sufficient_position: dict) -> str:
    group_bytes = canonical_group_json_bytes(sufficient_position)
    digest = hashlib.sha256(b"CHESSHEAT_SPLIT_V3|" + group_bytes).digest()
    val = int.from_bytes(digest, byteorder='big') % 100
    if val < 70: return "TRAIN"
    elif val < 85: return "VALIDATION"
    else: return "TEST"

def canonical_budget_order(root_identity: str) -> Tuple[bytes, str]:
    digest = hashlib.sha256(b"CHESSHEAT_BUDGET_ORDER_V3|" + root_identity.encode("ascii")).digest()
    return (digest, root_identity)

def compute_aulc(budgets: List[int], utilities: List[float]) -> float:
    if len(budgets) != len(utilities):
        raise ValueError("Mismatched lengths")
    if len(budgets) < 2:
        raise ValueError("Requires >= 2 points")
    for i in range(len(utilities)):
        if not math.isfinite(utilities[i]):
            raise ValueError("Utility must be finite")
    for i in range(1, len(budgets)):
        if budgets[i] <= budgets[i-1]:
            raise ValueError("Budgets must be strictly increasing")
            
    width = budgets[-1] - budgets[0]
    if width <= 0:
        raise ValueError("Positive width required")
        
    area = 0.0
    for i in range(1, len(budgets)):
        dx = budgets[i] - budgets[i-1]
        y_avg = (utilities[i] + utilities[i-1]) / 2.0
        area += dx * y_avg
    
    return area / width

def classify_outcome(delta_dt_ci: Tuple[float, float], delta_d0_ci: Tuple[float, float], delta_t0_ci: Tuple[float, float], protocol_valid: bool) -> str:
    if not protocol_valid:
        return "PROTOCOL_INVALID"
        
    dt_lcb, dt_ucb = delta_dt_ci
    d0_lcb, d0_ucb = delta_d0_ci
    t0_lcb, t0_ucb = delta_t0_ci
    
    for v in [dt_lcb, dt_ucb, d0_lcb, d0_ucb, t0_lcb, t0_ucb]:
        if not math.isfinite(v):
            raise ValueError("CIs must be finite")
            
    if dt_lcb > dt_ucb or d0_lcb > d0_ucb or t0_lcb > t0_ucb:
        raise ValueError("CIs must be ordered correctly")
        
    if dt_lcb > 0 and d0_lcb > 0: return "SUPPORT_muD"
    if dt_ucb < 0 and t0_lcb > 0: return "SUPPORT_muT"
    if (d0_lcb > 0 or t0_lcb > 0) and dt_lcb <= 0 <= dt_ucb: return "SPATIAL_EFFICIENCY_OPERATOR_UNRESOLVED"
    if d0_ucb <= 0 and t0_ucb <= 0: return "NO_SPATIAL_EFFICIENCY_ADVANTAGE"
    return "INCONCLUSIVE"

def bootstrap_indices(b: int, j: int, n_test: int) -> int:
    if n_test <= 0:
        raise ValueError("n_test must be positive")
    digest = hashlib.sha256(
        b"CHESSHEAT_BOOTSTRAP_V3|" +
        str(b).encode("ascii") + b"|" +
        str(j).encode("ascii")
    ).digest()
    return int.from_bytes(digest, byteorder='big') % n_test

def percentile_rank(n_elements: int, p: float) -> int:
    return math.ceil(p * n_elements) - 1

def mean_five_seed_root_nll(losses_by_seed: Mapping[int, float]) -> float:
    expected_seeds = {1729, 2718, 31415, 65537, 104729}
    if set(losses_by_seed.keys()) != expected_seeds:
        raise ValueError("Must have exactly the five frozen seeds")
    total = 0.0
    for v in losses_by_seed.values():
        if not math.isfinite(v):
            raise ValueError("Loss must be finite")
        total += v
    return total / 5.0

def canonical_bootstrap_root_order(root_ids: List[str]) -> Tuple[str, ...]:
    if not root_ids:
        raise ValueError("root_ids must be nonempty")
    for r in root_ids:
        if not isinstance(r, str) or not r:
            raise ValueError("root_ids must be nonempty strings")
    if len(root_ids) != len(set(root_ids)):
        raise ValueError("root_ids must be unique")
    return tuple(sorted(root_ids))

def full_bootstrap_procedure(root_ids: List[str], root_losses: Dict[str, Dict[int, Dict[str, float]]]) -> Dict[str, Dict[str, float]]:
    ordered_root_ids = canonical_bootstrap_root_order(root_ids)
    
    expected_conditions = {"mu_D", "mu_T", "B_daS"}
    expected_budgets = [250, 500, 1000, 2000, 4000, 8000, 16000, 20000]
    
    if set(root_losses.keys()) != expected_conditions:
        raise ValueError("Missing or extra conditions")
        
    for cond in expected_conditions:
        if sorted(list(root_losses[cond].keys())) != expected_budgets:
            raise ValueError("Budgets do not match frozen budgets exactly")
        for b in expected_budgets:
            if set(root_losses[cond][b].keys()) != set(ordered_root_ids):
                raise ValueError("Root set mismatch")
            for v in root_losses[cond][b].values():
                if not math.isfinite(v): raise ValueError("Loss must be finite")
                
    N = len(ordered_root_ids)
    delta_dt_all = []
    delta_d0_all = []
    delta_t0_all = []
    
    for b in range(10000):
        sample_indices = [bootstrap_indices(b, j, N) for j in range(N)]
        sampled_roots = [ordered_root_ids[i] for i in sample_indices]
        
        aulc = {}
        for cond in expected_conditions:
            u_vals = []
            for budget in expected_budgets:
                u_budget = -sum(root_losses[cond][budget][r] for r in sampled_roots) / N
                u_vals.append(u_budget)
            aulc[cond] = compute_aulc(expected_budgets, u_vals)
            
        delta_dt_all.append(aulc["mu_D"] - aulc["mu_T"])
        delta_d0_all.append(aulc["mu_D"] - aulc["B_daS"])
        delta_t0_all.append(aulc["mu_T"] - aulc["B_daS"])
        
    delta_dt_all.sort()
    delta_d0_all.sort()
    delta_t0_all.sort()
    
    l_idx = percentile_rank(10000, 0.025)
    u_idx = percentile_rank(10000, 0.975)
    
    return {
        "Delta_DT": {"lcb": delta_dt_all[l_idx], "ucb": delta_dt_all[u_idx]},
        "Delta_D0": {"lcb": delta_d0_all[l_idx], "ucb": delta_d0_all[u_idx]},
        "Delta_T0": {"lcb": delta_t0_all[l_idx], "ucb": delta_t0_all[u_idx]}
    }

def canonical_json_bytes(obj: Any) -> bytes:
    return json.dumps(
        obj,
        sort_keys=True,
        separators=(',', ':'),
        allow_nan=False
    ).encode('utf-8')

def canonical_protocol_payload_v6() -> dict:
    return {
        "protocol_identifier": "CP_REPRESENTATION_EFFICIENCY_PROTOCOL_V6",
        "authoritative_references": {
            "pre_freeze_sha": "8876f8cf2d6e1da47b2b40b818413b4095786c36",
            "repair_v1_fail": "ba11bde7af3623b3272900b7da66bc5ec53627de",
            "repair_v2_fail": "c0914d88530810d9e07bc4e951c8721aca1a611d",
            "repair_v3_fail": "af620cd1f5b5beaa850baf08baca0f8bd6b90894",
            "repair_v4_fail": "7bbbef81fa83ff9babab6049aa7c891a53cdf948"
        },
        "source_evidence": {
            "commit": "8876f8cf2d6e1da47b2b40b818413b4095786c36",
            "raw_path": "artifacts/research/cp_source_feasibility_2026_07/raw/cp_source_root_results_v2.jsonl",
            "raw_sha256": "7eb640c572dad4c6607cfb1b5ccf99597672042e5c516f131feab02223ccfa6b",
            "population_count": 33859,
            "source_pair_eligible_count": 33444,
            "source_zero_pair_count": 415,
            "eligibility_rule": ">=2 finite SOURCE CP alternatives, determined before TARGET"
        },
        "target_labels": {
            "semantics": "Concrete CompareTyped binding to src/chessheat/attribution.py:compare_scores. Typed mate observations remain ordered. Not blanket excluded.",
            "attrition_training": "Nominal selected training roots with 0 TARGET-evaluable pairs contribute 0 training examples, are not replaced, consume no minibatch slot.",
            "attrition_val_test": "Roots must have >=1 TARGET-evaluable pair. Exact identical root set across all representations and budgets."
        },
        "canonical_pair_orientation": "lexicographical_uci_m1_lt_m2",
        "split": {
            "domain_string": "CHESSHEAT_SPLIT_V3|",
            "key_definition": "JSON serialization of board_arrangement_fen, castling_rights, en_passant_square, side_to_move",
            "partitions": {"TRAIN": [0, 69], "VALIDATION": [70, 84], "TEST": [85, 99]},
            "expected_all_root_counts": {"TRAIN": 23639, "VALIDATION": 5148, "TEST": 5072},
            "expected_eligible_counts": {"TRAIN": 23350, "VALIDATION": 5094, "TEST": 5000},
            "expected_zero_counts": {"TRAIN": 289, "VALIDATION": 54, "TEST": 72}
        },
        "budget": {
            "domain_string": "CHESSHEAT_BUDGET_ORDER_V3|",
            "sizes": [250, 500, 1000, 2000, 4000, 8000, 16000, 20000],
            "tie_break": "(digest_bytes, root_identity)"
        },
        "p_numeric_encoding": {
            "shape": [18, 8, 8],
            "dtype": "float32-le",
            "orientation": "spatial_row_col: row 0 = rank 8, col 0 = file a",
            "channels": [
                "white pawn", "white knight", "white bishop", "white rook", "white queen", "white king",
                "black pawn", "black knight", "black bishop", "black rook", "black queen", "black king",
                "side to move", "white kingside", "white queenside", "black kingside", "black queenside",
                "en-passant target"
            ],
            "omitted_s0_features": ["halfmove_clock", "fullmove_number", "history_available", "history_identity", "variant"]
        },
        "s_numeric_encoding": {
            "dimension": 270,
            "dtype": "float32-le",
            "orientation": "uci_square_index: a1=0, h8=63",
            "structure": "133 (m1), 133 (m2), 3 (d_X), 1 (a_X)",
            "promotion_order": ["NONE", "QUEEN", "ROOK", "BISHOP", "KNIGHT"],
            "d_X_order": ["SOURCE_FIRST_BETTER", "SOURCE_EQUAL", "SOURCE_SECOND_BETTER"]
        },
        "spatial_operators": {
            "a_X": {
                "definition": "abs(CP_X(m1) - CP_X(m2))",
                "source_type": "finite SOURCE CP"
            },
            "D": {
                "collection_type": "set",
                "deduplicate": True,
                "members": ["to(m1)", "to(m2)"]
            },
            "T": {
                "collection_type": "set",
                "deduplicate": True,
                "members": ["from(m1)", "to(m1)", "from(m2)", "to(m2)"]
            },
            "M_D": {
                "nonzero_rule": "a_X / |D|",
                "support": "D",
                "else": 0
            },
            "M_T": {
                "nonzero_rule": "a_X / |T|",
                "support": "T",
                "else": 0
            },
            "M_0": {
                "rule": "0 on all 64 squares"
            },
            "B_daS": "M_0",
            "B_perm": "M_T mapped through global fixed spatial permutation (domain CHESSHEAT_MATCHED_PERM_V3|)",
            "B_raw": {
                "role": "diagnostic only",
                "primary_contrast": False
            },
            "quantization": "IEEE-754 float32 of analytical values",
            "shape": [1, 8, 8],
            "orientation": "spatial_row_col: row 0 = rank 8, col 0 = file a"
        },
        "learner": {
            "layers": [
                {"type": "Conv2d", "in": 19, "out": 64, "kernel": [3,3], "stride": [1,1], "padding": [1,1], "dilation": [1,1], "groups": 1, "bias": True, "activation": "ReLU"},
                {"type": "Conv2d", "in": 64, "out": 64, "kernel": [3,3], "stride": [1,1], "padding": [1,1], "dilation": [1,1], "groups": 1, "bias": True, "activation": "ReLU"},
                {"type": "Conv2d", "in": 64, "out": 64, "kernel": [3,3], "stride": [1,1], "padding": [1,1], "dilation": [1,1], "groups": 1, "bias": True, "activation": "ReLU"},
                {"type": "GAP", "operation": "mean across both 8x8 axes"},
                {"type": "Linear", "in": 270, "out": 128, "bias": True, "activation": "ReLU"},
                {"type": "Concat", "sources": ["GAP", "Linear_270_128"]},
                {"type": "Linear", "in": 192, "out": 128, "bias": True, "activation": "ReLU"},
                {"type": "Linear", "in": 128, "out": 3, "bias": True, "activation": "none"}
            ],
            "output_logits": {
                "class_order": [
                    "FIRST_BETTER",
                    "EQUAL",
                    "SECOND_BETTER"
                ]
            },
            "normalization": "none",
            "dropout": "none",
            "class_weighting": "none",
            "gradient_clipping": "none",
            "optimizer": {
                "name": "Adam",
                "lr": 0.001,
                "betas": [0.9, 0.999],
                "eps": 1e-08,
                "weight_decay": 1e-05,
                "amsgrad": False
            },
            "initialization": {
                "weights": "torch.nn.init.kaiming_uniform_(a=sqrt(5), mode=fan_in, nonlinearity=leaky_relu)",
                "bias": "uniform(-1/sqrt(fan_in), 1/sqrt(fan_in))",
                "fan_in_conv1": 171,
                "fan_in_conv2": 576,
                "fan_in_conv3": 576,
                "fan_in_side": 270,
                "fan_in_fusion": 192,
                "fan_in_output": 128
            }
        },
        "training": {
            "batch_unit": "EFFECTIVE_ROOT",
            "batch_size": 64,
            "final_short_batch_allowed": True,
            "pair_policy": "all TARGET-evaluable pairs within each effective root",
            "root_loss": "arithmetic mean pair NLL within root",
            "batch_loss": "arithmetic mean root losses within minibatch",
            "target_zero_root": "excluded before minibatch construction; nominal budget retained; no replacement",
            "validation_frequency": "after every completed epoch",
            "test_evaluation": "exactly once after best checkpoint restoration",
            "epoch_ordering": "SHA256(CHESSHEAT_MINIBATCH_V3|s|e|root_identity)",
            "max_epochs": 200,
            "validation_metric": "root-weighted NLL",
            "early_stopping": {
                "patience": 20,
                "min_delta": 0.0,
                "improvement": "strict inequality",
                "tie_break": "earliest epoch"
            },
            "best_checkpoint_restored": True
        },
        "seed": {
            "set": [1729, 2718, 31415, 65537, 104729],
            "aggregation": "mean seed root NLL across 5 seeds BEFORE computing root inference or AULC"
        },
        "outcome_classifier": {
            "utility": "U_mu(n) = - mean_root(NLL) with five-seed averaging already performed within root",
            "x_axis": "linear nominal SOURCE-selected training-root budget",
            "budgets": [250, 500, 1000, 2000, 4000, 8000, 16000, 20000],
            "integration": "normalized trapezoidal integral over linear n. AULC = [ sum_j (n_j - n_{j-1}) (U_j + U_{j-1}) / 2 ] / (n_max - n_min). larger AULC = better",
            "primary_contrast": "Delta_DT = AULC_D - AULC_T",
            "primary_contrast_status": "sole PRIMARY operator contrast",
            "gating_contrasts": {
                "Delta_D0": "AULC_D - AULC_BdaS (prespecified gating/control contrast)",
                "Delta_T0": "AULC_T - AULC_BdaS (prespecified gating/control contrast)"
            },
            "ci_boundary_semantics": {
                "resolved_positive": "LCB > 0",
                "resolved_negative": "UCB < 0",
                "non_positive": "UCB <= 0",
                "contains_zero": "LCB <= 0 <= UCB"
            },
            "evaluation_order": [
                "PROTOCOL_INVALID",
                "SUPPORT_muD",
                "SUPPORT_muT",
                "SPATIAL_EFFICIENCY_OPERATOR_UNRESOLVED",
                "NO_SPATIAL_EFFICIENCY_ADVANTAGE",
                "INCONCLUSIVE"
            ],
            "logic": {
                "PROTOCOL_INVALID": "protocol_valid == false",
                "SUPPORT_muD": "LCB(Delta_DT) > 0 AND LCB(Delta_D0) > 0",
                "SUPPORT_muT": "UCB(Delta_DT) < 0 AND LCB(Delta_T0) > 0",
                "SPATIAL_EFFICIENCY_OPERATOR_UNRESOLVED": "(LCB(Delta_D0) > 0 OR LCB(Delta_T0) > 0) AND LCB(Delta_DT) <= 0 AND UCB(Delta_DT) >= 0",
                "NO_SPATIAL_EFFICIENCY_ADVANTAGE": "UCB(Delta_D0) <= 0 AND UCB(Delta_T0) <= 0",
                "INCONCLUSIVE": "otherwise"
            }
        },
        "bootstrap": {
            "replicates": 10000,
            "domain_string": "CHESSHEAT_BOOTSTRAP_V3|b|j",
            "unit": "held-out root",
            "procedure": "Resample roots -> recompute U at every budget -> recompute AULC -> recompute contrasts",
            "root_order": "lexicographically ascending canonical root_identity",
            "index_binding": "SHA-derived integer modulo N indexes canonical_root_order",
            "ci_type": "percentile",
            "bounds": [2.5, 97.5],
            "indices": [249, 9749]
        },
        "runtime": {
            "framework": "PyTorch",
            "version": None,
            "status": "ML_RUNTIME_DEPENDENCY_NOT_YET_SATISFIED"
        },
        "execution_status": {
            "target": "STRICTLY UNAUTHORIZED",
            "model_training": "STRICTLY UNAUTHORIZED"
        },
        "claim_ceiling": "representation efficiency comparison only"
    }

def canonical_protocol_bytes_v6() -> bytes:
    payload = canonical_protocol_payload_v6()
    return canonical_json_bytes(payload)

def canonical_protocol_sha256_v6() -> str:
    return hashlib.sha256(canonical_protocol_bytes_v6()).hexdigest()
