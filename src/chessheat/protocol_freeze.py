import hashlib

def get_partition(root_identity: str) -> str:
    """
    Deterministic root split based on SHA256.
    TRAIN: 70%, VALIDATION: 15%, TEST: 15%
    """
    h = hashlib.sha256(f"CHESSHEAT_SPLIT_V1_{root_identity}".encode('utf-8')).hexdigest()
    val = int(h, 16) % 100
    if val < 70:
        return "TRAIN"
    elif val < 85:
        return "VALIDATION"
    else:
        return "TEST"

def sort_budget_roots(root_identities: list[str], seed: int) -> list[str]:
    """
    Deterministic nested budget root selector.
    Sorts roots based on a seed-specific hash.
    """
    def key_func(rid):
        return hashlib.sha256(f"BUDGET_SORT_{seed}_{rid}".encode('utf-8')).hexdigest()
    return sorted(root_identities, key=key_func)

def compute_root_weighted_loss(root_losses: list[list[float]]) -> float:
    """
    1. Average loss within each root.
    2. Average across roots.
    """
    if not root_losses:
        return 0.0
    root_avgs = [sum(pairs) / len(pairs) for pairs in root_losses if pairs]
    if not root_avgs:
        return 0.0
    return sum(root_avgs) / len(root_avgs)

def compute_aulc(budgets: list[int], losses: list[float]) -> float:
    """
    Trapezoidal integration of AULC.
    x = budget, y = loss. Lower loss is better, so lower AULC is better.
    """
    if len(budgets) != len(losses) or len(budgets) < 2:
        return 0.0
    area = 0.0
    for i in range(1, len(budgets)):
        dx = budgets[i] - budgets[i-1]
        y_avg = (losses[i] + losses[i-1]) / 2.0
        area += dx * y_avg
    
    # Normalize by total width
    width = budgets[-1] - budgets[0]
    return area / width if width > 0 else 0.0

