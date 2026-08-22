import hashlib
import json
import math
import struct
from typing import Tuple, List, Set, Dict, Any, Optional

class CanonicalTensorF32:
    """Canonical IEEE-754 float32 tensor."""
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

def uci_square_index(square: str) -> int:
    """Categorical square index for S*. a1=0, b1=1... h8=63."""
    file_c = square[0]
    rank_c = square[1]
    f = ord(file_c) - ord('a')
    r = int(rank_c) - 1
    return r * 8 + f

def spatial_row_col(square: str) -> Tuple[int, int]:
    """Spatial tensor coordinates. row 0 = rank 8, col 0 = file a."""
    file_c = square[0]
    rank_c = square[1]
    f = ord(file_c) - ord('a')
    r = int(rank_c)
    row = 8 - r
    col = f
    return row, col

def spatial_flat_index(square: str) -> int:
    """Row-major spatial flat index."""
    row, col = spatial_row_col(square)
    return row * 8 + col

class SourcePairFeatures:
    def __init__(self, m_a: str, cp_a: int, m_b: str, cp_b: int):
        for m in [m_a, m_b]:
            if len(m) == 5 and m[4] not in "qrbn":
                raise ValueError("Invalid promo")
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
    
    if pair.d_x == "SOURCE_FIRST_BETTER":
        out[266] = 1.0
    elif pair.d_x == "SOURCE_EQUAL":
        out[267] = 1.0
    elif pair.d_x == "SOURCE_SECOND_BETTER":
        out[268] = 1.0
    else:
        raise ValueError(f"Unknown d_x: {pair.d_x}")
        
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
    for i in range(1, len(budgets)):
        if budgets[i] <= budgets[i-1]:
            raise ValueError("Budgets must be strictly increasing")
        if not math.isfinite(utilities[i]) or not math.isfinite(utilities[i-1]):
            raise ValueError("Utility must be finite")
            
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
        
    if dt_lcb > 0 and d0_lcb > 0:
        return "SUPPORT_muD"
    if dt_ucb < 0 and t0_lcb > 0:
        return "SUPPORT_muT"
    if (d0_lcb > 0 or t0_lcb > 0) and dt_lcb <= 0 <= dt_ucb:
        return "SPATIAL_EFFICIENCY_OPERATOR_UNRESOLVED"
    if d0_ucb <= 0 and t0_ucb <= 0:
        return "NO_SPATIAL_EFFICIENCY_ADVANTAGE"
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

def full_bootstrap_procedure(root_ids: List[str], lbar_D: List[float], lbar_T: List[float], lbar_0: List[float], budgets: List[int]) -> Dict[str, Tuple[float, float]]:
    # This is a simplified mathematical representation for validation in tests
    # In reality, this requires evaluating at multiple budgets. 
    # To strictly freeze it, we'd need a multi-budget matrix.
    pass

def canonical_protocol_payload_v3() -> dict:
    return {
        "protocol_identifier": "CP_REPRESENTATION_EFFICIENCY_PROTOCOL_V3",
        "authoritative_references": {
            "pre_freeze_sha": "8876f8cf2d6e1da47b2b40b818413b4095786c36"
        },
        "source_evidence": {
            "population_count": 33859,
            "source_pair_eligible_count": 33444,
            "source_zero_pair_count": 415,
            "eligibility_rule": ">=2 finite SOURCE CP alternatives, determined before TARGET"
        },
        "target_labels": {
            "semantics": "Inherited CompareTyped. Typed mate observations remain typed and ordered if CompareTyped allows. Not blindly excluded.",
            "attrition_training": "Nominal selected training roots with 0 TARGET-evaluable pairs contribute 0 training examples, are not replaced, consume no minibatch slot.",
            "attrition_val_test": "Roots must have >=1 TARGET-evaluable pair. Exact identical root set across all representations and budgets."
        },
        "canonical_pair_orientation": "lexicographical_uci_m1_lt_m2",
        "split": {
            "domain_string": "CHESSHEAT_SPLIT_V3|",
            "key_definition": "JSON serialization of board_arrangement_fen, castling_rights, en_passant_square, side_to_move",
            "partitions": {"TRAIN": [0, 69], "VALIDATION": [70, 84], "TEST": [85, 99]},
            "expected_all_root_counts": {"TRAIN": 23689, "VALIDATION": 5013, "TEST": 5157}, # Will update with exact counts later
            "expected_eligible_counts": {"TRAIN": 23395, "VALIDATION": 4955, "TEST": 5094}
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
        "m_channel_definitions": {
            "shape": [1, 8, 8],
            "orientation": "spatial_row_col: row 0 = rank 8, col 0 = file a",
            "mu_D": "a_X / |D| if s in deduplicated D else 0",
            "mu_T": "a_X / |T| if s in deduplicated T else 0",
            "B_daS": "M_0 (all zeros)",
            "B_perm": "M_T mapped through global fixed spatial permutation",
            "quantization": "IEEE-754 float32 of analytical values"
        },
        "learner": {
            "architecture": "Conv3(19->64)->Conv3(64->64)->Conv3(64->64)->GAP(64) concat Dense(270->128) -> Dense(192->128)->Dense(128->3)",
            "activation": "ReLU",
            "normalization": "none",
            "dropout": "none",
            "optimizer": {
                "name": "Adam",
                "lr": 0.001,
                "betas": [0.9, 0.999],
                "eps": 1e-08,
                "weight_decay": 1e-05,
                "amsgrad": False
            },
            "initialization": "kaiming_uniform_(a=sqrt(5)) for weights, uniform(-1/sqrt(fan_in), 1/sqrt(fan_in)) for bias"
        },
        "training": {
            "batch_size_effective_roots": 64,
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
        "outcome_logic": {
            "utility": "- mean_root(NLL)",
            "primary_contrast": "Delta_DT = AULC_D - AULC_T",
            "sign": "positive Delta_DT favors D",
            "aulc_rules": "fail-closed on non-finite U, mismatched lengths, non-strict budgets"
        },
        "bootstrap": {
            "replicates": 10000,
            "domain_string": "CHESSHEAT_BOOTSTRAP_V3|b|j",
            "unit": "held-out root",
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

def canonical_protocol_bytes_v3() -> bytes:
    payload = canonical_protocol_payload_v3()
    return json.dumps(payload, sort_keys=True, separators=(',', ':')).encode('utf-8')

def canonical_protocol_sha256_v3() -> str:
    return hashlib.sha256(canonical_protocol_bytes_v3()).hexdigest()
