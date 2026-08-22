import hashlib
from typing import Tuple, List, Set, Dict, Any

def canonical_pair(m1_uci: str, m2_uci: str) -> Tuple[str, str]:
    return tuple(sorted([m1_uci, m2_uci]))

def transposition_group_key(sufficient_position: dict) -> str:
    ep = sufficient_position.get('en_passant_square')
    ep_str = ep if ep is not None else "None"
    return (
        f"{sufficient_position['board_arrangement_fen']}|"
        f"{sufficient_position['side_to_move']}|"
        f"{sufficient_position['castling_rights']}|"
        f"{ep_str}"
    )

def get_partition(sufficient_position: dict) -> str:
    group_key = transposition_group_key(sufficient_position)
    digest = hashlib.sha256(f"CHESSHEAT_SPLIT_V2|{group_key}".encode('ascii')).digest()
    val = int.from_bytes(digest, byteorder='big') % 100
    if val < 70:
        return "TRAIN"
    elif val < 85:
        return "VALIDATION"
    else:
        return "TEST"

def canonical_budget_order(root_identity: str) -> bytes:
    return hashlib.sha256(f"CHESSHEAT_BUDGET_ORDER_V2|{root_identity}".encode('ascii')).digest()

def get_square_index(sq: str) -> int:
    """Canonical square index: a1=0, b1=1... h8=63"""
    file_c = sq[0]
    rank_c = sq[1]
    f = ord(file_c) - ord('a')
    r = int(rank_c) - 1
    return r * 8 + f

def encode_position(sufficient_position: dict) -> List[float]:
    """
    Returns 18x8x8 flat float32 encoded P array.
    Shape conceptual: [18, 8, 8]
    """
    out = [0.0] * (18 * 64)
    def set_val(plane: int, sq_idx: int, val: float):
        out[plane * 64 + sq_idx] = val
        
    fen = sufficient_position['board_arrangement_fen']
    side = sufficient_position['side_to_move']
    castling = sufficient_position['castling_rights']
    ep = sufficient_position.get('en_passant_square')
    
    # 0-5: white P N B R Q K
    # 6-11: black p n b r q k
    pieces = 'PNBRQKpnbrqk'
    
    ranks = fen.split()[0].split('/')
    for r_idx, rank_str in enumerate(ranks):
        rank_num = 7 - r_idx
        f_idx = 0
        for char in rank_str:
            if char.isdigit():
                f_idx += int(char)
            else:
                p_idx = pieces.index(char)
                sq = rank_num * 8 + f_idx
                set_val(p_idx, sq, 1.0)
                f_idx += 1
                
    side_val = 1.0 if side == 'w' else 0.0
    for sq in range(64):
        set_val(12, sq, side_val)
        
    # Castling
    if castling != '-':
        if 'K' in castling:
            for sq in range(64): set_val(13, sq, 1.0)
        if 'Q' in castling:
            for sq in range(64): set_val(14, sq, 1.0)
        if 'k' in castling:
            for sq in range(64): set_val(15, sq, 1.0)
        if 'q' in castling:
            for sq in range(64): set_val(16, sq, 1.0)
            
    # EP
    if ep:
        set_val(17, get_square_index(ep), 1.0)
        
    return out

def encode_side_information(m1_uci: str, m2_uci: str, dx_label: str, ax_val: float) -> List[float]:
    """
    Returns 270 side vector.
    m1 is smaller UCI, m2 is larger.
    """
    m1, m2 = canonical_pair(m1_uci, m2_uci)
    out = [0.0] * 270
    
    def encode_move(m: str, offset: int):
        from_sq = get_square_index(m[0:2])
        to_sq = get_square_index(m[2:4])
        out[offset + from_sq] = 1.0
        out[offset + 64 + to_sq] = 1.0
        
        promo = m[4] if len(m) == 5 else None
        p_idx = 0
        if promo == 'q': p_idx = 1
        elif promo == 'r': p_idx = 2
        elif promo == 'b': p_idx = 3
        elif promo == 'n': p_idx = 4
        out[offset + 128 + p_idx] = 1.0

    encode_move(m1, 0)
    encode_move(m2, 133)
    
    if dx_label == "SOURCE_FIRST_BETTER":
        out[266] = 1.0
    elif dx_label == "SOURCE_EQUAL":
        out[267] = 1.0
    elif dx_label == "SOURCE_SECOND_BETTER":
        out[268] = 1.0
        
    out[269] = float(ax_val)
    return out

def build_m_d(m1_uci: str, m2_uci: str, a_x: float) -> List[float]:
    m1, m2 = canonical_pair(m1_uci, m2_uci)
    D = set([m1[2:4], m2[2:4]])
    val = a_x / len(D) if len(D) > 0 else 0.0
    out = [0.0] * 64
    for sq in D:
        out[get_square_index(sq)] = val
    return out

def build_m_t(m1_uci: str, m2_uci: str, a_x: float) -> List[float]:
    m1, m2 = canonical_pair(m1_uci, m2_uci)
    T = set([m1[0:2], m1[2:4], m2[0:2], m2[2:4]])
    val = a_x / len(T) if len(T) > 0 else 0.0
    out = [0.0] * 64
    for sq in T:
        out[get_square_index(sq)] = val
    return out

def build_m_zero() -> List[float]:
    return [0.0] * 64

def _get_permuted_squares() -> List[str]:
    canonical_squares = []
    for r in range(1, 9):
        for f in "abcdefgh":
            canonical_squares.append(f"{f}{r}")
    
    def key_fn(s: str):
        return hashlib.sha256(b"CHESSHEAT_MATCHED_PERM_V2|" + s.encode("ascii")).digest()
        
    return sorted(canonical_squares, key=lambda s: (key_fn(s), s))

_PERMUTATION = None
def build_m_perm(m1_uci: str, m2_uci: str, a_x: float) -> List[float]:
    global _PERMUTATION
    if _PERMUTATION is None:
        canon = []
        for r in range(1, 9):
            for f in "abcdefgh":
                canon.append(f"{f}{r}")
        permuted = _get_permuted_squares()
        _PERMUTATION = {canon[i]: permuted[i] for i in range(64)}
        
    m_t = build_m_t(m1_uci, m2_uci, a_x)
    out = [0.0] * 64
    canon = []
    for r in range(1, 9):
        for f in "abcdefgh":
            canon.append(f"{f}{r}")
    for s in canon:
        out[get_square_index(_PERMUTATION[s])] = m_t[get_square_index(s)]
    return out

def mean_root_nll(pair_nlls: List[float]) -> float:
    if not pair_nlls:
        raise ValueError("Cannot compute root loss for empty pair sequence")
    return sum(pair_nlls) / len(pair_nlls)

def mean_seed_root_nll(seed_nlls: List[float]) -> float:
    if not seed_nlls or len(seed_nlls) != 5:
        raise ValueError("Must provide exactly 5 seed NLLs")
    return sum(seed_nlls) / len(seed_nlls)

def utility_from_root_losses(root_losses: List[float]) -> float:
    if not root_losses:
        raise ValueError("Cannot compute partition utility for empty root sequence")
    return - (sum(root_losses) / len(root_losses))

def compute_aulc(budgets: List[int], utilities: List[float]) -> float:
    if len(budgets) != len(utilities):
        raise ValueError("Mismatched budgets and utilities length")
    if len(budgets) < 2:
        raise ValueError("AULC requires at least 2 points")
    for i in range(1, len(budgets)):
        if budgets[i] <= budgets[i-1]:
            raise ValueError("Budgets must be strictly increasing")
            
    width = budgets[-1] - budgets[0]
    if width <= 0:
        raise ValueError("Budget width must be positive")
        
    area = 0.0
    for i in range(1, len(budgets)):
        dx = budgets[i] - budgets[i-1]
        y_avg = (utilities[i] + utilities[i-1]) / 2.0
        area += dx * y_avg
        
    return area / width

def bootstrap_indices(b: int, j: int, n_test_evaluable: int) -> int:
    """Returns the sampled index for bootstrap replicate b, draw j"""
    if n_test_evaluable <= 0:
        raise ValueError("n_test_evaluable must be positive")
    digest = hashlib.sha256(
        b"CHESSHEAT_BOOTSTRAP_V2|" +
        str(b).encode("ascii") + b"|" +
        str(j).encode("ascii")
    ).digest()
    return int.from_bytes(digest, byteorder='big') % n_test_evaluable

def classify_outcome(delta_dt_ci: Tuple[float, float], delta_d0_ci: Tuple[float, float], delta_t0_ci: Tuple[float, float]) -> str:
    dt_lcb, dt_ucb = delta_dt_ci
    d0_lcb, d0_ucb = delta_d0_ci
    t0_lcb, t0_ucb = delta_t0_ci
    
    if dt_lcb > 0 and d0_lcb > 0:
        return "SUPPORT_muD"
    if dt_ucb < 0 and t0_lcb > 0:
        return "SUPPORT_muT"
        
    if (d0_lcb > 0 or t0_lcb > 0) and dt_lcb <= 0 <= dt_ucb:
        return "SPATIAL_EFFICIENCY_OPERATOR_UNRESOLVED"
        
    if d0_ucb <= 0 and t0_ucb <= 0:
        return "NO_SPATIAL_EFFICIENCY_ADVANTAGE"
        
    return "INCONCLUSIVE"
