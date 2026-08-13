import chess
from typing import Dict, List, Optional
from pydantic import BaseModel
from .models import AnalysisRecord, EventBundle
from .geometry import BoardGeometry, extract_geometry, compute_geometry_delta
from .attribution import aggregate_square_attributions
from .recurrence import aggregate_square_recurrence
from .association import aggregate_bundle_leverage

class SquareFusion(BaseModel):
    square: str

    # Raw values
    raw_attack_density: Optional[int] = None
    raw_dest_regret: Optional[float] = None
    raw_direct_regret: Optional[float] = None
    raw_recurrence: Optional[float] = None
    raw_bundle_leverage: Optional[float] = None

    # Normalized [0, 1] ranks
    norm_attack_density: Optional[float] = None
    norm_dest_regret: Optional[float] = None
    norm_direct_regret: Optional[float] = None
    norm_recurrence: Optional[float] = None
    norm_bundle_leverage: Optional[float] = None

    # Fusions
    model_A: Optional[float] = None # Direct
    model_B: Optional[float] = None # Recurrence
    model_C: Optional[float] = None # Bundle
    model_D: Optional[float] = None # Direct + Recurrence
    model_E: Optional[float] = None # Direct + Bundle
    model_F: Optional[float] = None # Recurrence + Bundle
    model_G: Optional[float] = None # All 3
    baseline_H: Optional[float] = None # Attack Density
    baseline_I: Optional[float] = None # Dest Regret

def _normalize_values(val_dict: Dict[str, float], higher_is_hotter: bool) -> Dict[str, float]:
    if not val_dict: return {}

    # Sort values to create a percentile map
    sorted_vals = sorted(list(val_dict.items()), key=lambda x: x[1], reverse=higher_is_hotter)

    norm = {}
    n = len(sorted_vals)
    for i, (sq, val) in enumerate(sorted_vals):
        if n == 1:
            norm[sq] = 1.0
        else:
            norm[sq] = (n - 1 - i) / (n - 1)

    return norm

def fuse_signals(fen: str, record: AnalysisRecord) -> Dict[str, SquareFusion]:
    board = chess.Board(fen)
    g_before = extract_geometry(board)

    # 1. Baseline H: Attack Density
    attack_counts = {}
    for sq in chess.SQUARES:
        attack_counts[chess.square_name(sq)] = len(board.attackers(chess.WHITE, sq)) + len(board.attackers(chess.BLACK, sq))

    norm_attack = _normalize_values(attack_counts, higher_is_hotter=True)

    # 2. Baseline I: Destination Regret
    attrs = aggregate_square_attributions(record)
    dest_regrets = {}
    for sq, attr in attrs.items():
        if attr.as_destination > 0 and attr.min_cp_regret is not None:
            dest_regrets[sq] = attr.min_cp_regret

    norm_dest = _normalize_values(dest_regrets, higher_is_hotter=True)

    # 3. Model A: Direct Attribution
    direct_regrets = {}
    for sq, attr in attrs.items():
        if attr.mean_cp_regret is not None:
            direct_regrets[sq] = attr.mean_cp_regret

    norm_direct = _normalize_values(direct_regrets, higher_is_hotter=True)

    # 4. Model B: PV Recurrence
    rec_res = aggregate_square_recurrence(record)
    recurrence_vals = {}
    for sq, sr in rec_res.squares.items():
        if sr.overall.line_fraction > 0:
            recurrence_vals[sq] = sr.overall.line_fraction

    norm_rec = _normalize_values(recurrence_vals, higher_is_hotter=True)

    # 5. Model C: Bundle Leverage
    deltas = {}
    legal_moves = list(board.generate_legal_moves())
    for m in legal_moves:
        b_copy = board.copy()
        b_copy.push(m)
        g_after = extract_geometry(b_copy)
        deltas[m.uci()] = compute_geometry_delta(g_before, g_after)

    bundles = aggregate_bundle_leverage(record, deltas)

    bundle_leverage = {}
    for b in bundles:
        diff = b.median_regret_diff
        for sq in b.implicated_squares:
            if sq not in bundle_leverage:
                bundle_leverage[sq] = diff
            else:
                bundle_leverage[sq] = max(bundle_leverage[sq], diff)

    norm_bundle = _normalize_values(bundle_leverage, higher_is_hotter=True)

    # 6. Build the final fusion models
    fusions = {}
    for sq in chess.SQUARES:
        s = chess.square_name(sq)
        f = SquareFusion(square=s)

        f.raw_attack_density = attack_counts.get(s)
        f.raw_dest_regret = dest_regrets.get(s)
        f.raw_direct_regret = direct_regrets.get(s)
        f.raw_recurrence = recurrence_vals.get(s)
        f.raw_bundle_leverage = bundle_leverage.get(s)

        f.norm_attack_density = norm_attack.get(s)
        f.norm_dest_regret = norm_dest.get(s)
        f.norm_direct_regret = norm_direct.get(s)
        f.norm_recurrence = norm_rec.get(s)
        f.norm_bundle_leverage = norm_bundle.get(s)

        # Models
        f.baseline_H = f.norm_attack_density
        f.baseline_I = f.norm_dest_regret

        f.model_A = f.norm_direct_regret
        f.model_B = f.norm_recurrence
        f.model_C = f.norm_bundle_leverage

        def _avg(vals: List[Optional[float]]) -> Optional[float]:
            valid = [v for v in vals if v is not None]
            if not valid: return None
            return sum(valid) / len(valid)

        f.model_D = _avg([f.model_A, f.model_B])
        f.model_E = _avg([f.model_A, f.model_C])
        f.model_F = _avg([f.model_B, f.model_C])
        f.model_G = _avg([f.model_A, f.model_B, f.model_C])

        fusions[s] = f

    return fusions
