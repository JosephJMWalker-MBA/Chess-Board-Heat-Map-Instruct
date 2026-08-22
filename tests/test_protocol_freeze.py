from chessheat.protocol_freeze import get_partition, sort_budget_roots, compute_root_weighted_loss, compute_aulc

def test_partition_deterministic():
    r1 = "8fe5e3b6a6b864e405c524a7afb902ddfc1fe437550f7b8f4b1dfc0c9c42457b"
    assert get_partition(r1) == get_partition(r1)
    
    parts = {"TRAIN": 0, "VALIDATION": 0, "TEST": 0}
    for i in range(1000):
        parts[get_partition(f"root_{i}")] += 1
    
    assert parts["TRAIN"] > 600
    assert parts["VALIDATION"] > 100
    assert parts["TEST"] > 100

def test_budget_sort_nested():
    roots = [f"r_{i}" for i in range(10)]
    s1 = sort_budget_roots(roots, 1729)
    s2 = sort_budget_roots(roots, 1729)
    assert s1 == s2
    
    # Subset nesting: top 3 of s1 is a subset of top 5 of s1
    assert set(s1[:3]).issubset(set(s1[:5]))

def test_root_weighted_loss():
    # Root 1 has 5 pairs with loss 1.0
    # Root 2 has 1 pair with loss 0.0
    # Root-weighted average should be 0.5, not 5/6.
    losses = [
        [1.0, 1.0, 1.0, 1.0, 1.0],
        [0.0]
    ]
    avg = compute_root_weighted_loss(losses)
    assert avg == 0.5

def test_aulc():
    budgets = [250, 500, 1000]
    losses = [1.0, 0.8, 0.4]
    # width = 750
    # trapz 1: dx=250, y=0.9 => area=225
    # trapz 2: dx=500, y=0.6 => area=300
    # total area = 525, normalized = 525 / 750 = 0.7
    val = compute_aulc(budgets, losses)
    assert abs(val - 0.7) < 1e-6

