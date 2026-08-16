import fractions
from typing import List, Tuple, Set, Dict

def exact_median(values: List[int]) -> fractions.Fraction:
    if not values:
        return fractions.Fraction(0, 1)
    sorted_vals = sorted(values)
    n = len(sorted_vals)
    if n % 2 == 1:
        return fractions.Fraction(sorted_vals[n // 2], 1)
    else:
        return fractions.Fraction(sorted_vals[n // 2 - 1] + sorted_vals[n // 2], 2)

def compute_S(y_c: List[int], y_n: List[int]) -> fractions.Fraction:
    P = len(y_c) * len(y_n)
    G = sum(1 for c in y_c for n in y_n if c > n)
    T = sum(1 for c in y_c for n in y_n if c == n)
    return fractions.Fraction(abs(2 * G + T - P), P)

def compute_Q(y_all: Dict[str, int], c_keys: List[str]) -> fractions.Fraction:
    all_keys = sorted(y_all.keys())
    # Compute S for actual C
    y_c = [y_all[k] for k in c_keys]
    y_n = [y_all[k] for k in all_keys if k not in c_keys]
    s_actual = compute_S(y_c, y_n)
    
    # Enumerate all subsets of size 2
    import itertools
    L = 0
    E = 0
    total_Z = 0
    
    for z_keys in itertools.combinations(all_keys, 2):
        total_Z += 1
        z_c = [y_all[k] for k in z_keys]
        z_n = [y_all[k] for k in all_keys if k not in z_keys]
        s_z = compute_S(z_c, z_n)
        
        if s_z < s_actual:
            L += 1
        elif s_z == s_actual:
            E += 1
            
    return fractions.Fraction(2 * L + E, 2 * total_Z)

def test_exact_ties():
    y_all = {"a": 10, "b": 10, "c": 10, "d": 10, "e": 10, "f": 10}
    # All outcomes tied -> Q = 1/2
    q = compute_Q(y_all, ["a", "b"])
    assert q == fractions.Fraction(1, 2)
    
    s = compute_S([10, 10], [10, 10, 10, 10])
    assert s == fractions.Fraction(0, 1)

def test_complete_separation():
    # C is strictly greater than N
    y_all = {"a": 100, "b": 90, "c": 10, "d": 5, "e": 0, "f": -10}
    c_keys = ["a", "b"]
    s = compute_S([y_all[k] for k in c_keys], [y_all[k] for k in y_all if k not in c_keys])
    assert s == fractions.Fraction(1, 1)
    
    q = compute_Q(y_all, c_keys)
    # Only {a,b} gives S=1, no other subset gives S=1 (e.g. {a,c} has N with b=90, so S < 1)
    # Actually {e,f} also gives S=1.
    # Total subsets = 15
    # L = 13, E = 2 (the subset itself and the complement's extremeness? wait, {e,f} gives S=1)
    # If L=13, E=2, Q = (26+2)/30 = 28/30 = 14/15
    assert q > fractions.Fraction(1, 2)

def test_reversed_separation():
    # C is strictly less than N
    y_all = {"a": -100, "b": -90, "c": 10, "d": 5, "e": 0, "f": -10}
    c_keys = ["a", "b"]
    s = compute_S([y_all[k] for k in c_keys], [y_all[k] for k in y_all if k not in c_keys])
    assert s == fractions.Fraction(1, 1)

def test_odd_even_exact_medians():
    assert exact_median([1, 2, 3]) == fractions.Fraction(2, 1)
    assert exact_median([1, 2, 3, 4]) == fractions.Fraction(5, 2)

def test_suite_classification():
    # SUPPORTED
    q_vals_supported = [fractions.Fraction(3, 4)] * 12
    q_suite = exact_median(q_vals_supported)
    assert q_suite == fractions.Fraction(3, 4)
    h_75 = sum(1 for q in q_vals_supported if q >= fractions.Fraction(3, 4))
    import math
    assert h_75 >= math.ceil(0.75 * 12)
    
    # WEAK_SUPPORT
    q_vals_weak = [fractions.Fraction(6, 10)] * 12
    q_suite_weak = exact_median(q_vals_weak)
    assert q_suite_weak > fractions.Fraction(1, 2)
    h_75_weak = sum(1 for q in q_vals_weak if q >= fractions.Fraction(3, 4))
    assert h_75_weak < math.ceil(0.75 * 12)
    
    # FALSIFIED
    q_vals_falsified = [fractions.Fraction(1, 2)] * 12
    assert exact_median(q_vals_falsified) <= fractions.Fraction(1, 2)
