from typing import Optional

def compute_typed_amplitude(legal_moves_count: int, cp_range: float, has_mate: bool, mixed_types: bool) -> dict:
    """
    Computes the separated typed amplitude: A(P) = {A_cp, A_mate}.
    Implements Zero-Optionality semantics.
    """
    if legal_moves_count <= 1:
        return {"a_cp": 0.0, "a_mate": False, "zero_optionality": True}
        
    a_cp = cp_range if not mixed_types else 0.0
    
    return {
        "a_cp": a_cp,
        "a_mate": has_mate,
        "zero_optionality": False
    }
