from typing import Dict, Any, Tuple

def apply_shape_selectivity_v1(profile: Dict[str, Any]) -> Tuple[bool, str, str]:
    """
    Applies the frozen ShapeSelectivity-v1 rules to a spatial square profile.
    Returns (is_selected, channel_source, rejection_reason).
    """
    
    # Direct
    p_dir = profile.get("direct")
    if p_dir:
        if p_dir.get("candidate_fraction", 0.0) >= 0.15:
            return True, "direct", ""
            
    # Recurrence
    p_rec = profile.get("recurrence")
    if p_rec:
        earliest = p_rec.get("earliest_ply")
        lines = p_rec.get("distinct_line_count", 0)
        if earliest is not None and earliest <= 2 and lines >= 3:
            return True, "recurrence", ""
            
    # Bundle
    p_bun = profile.get("bundle")
    if p_bun:
        moves = p_bun.get("producing_move_count", 0)
        size = p_bun.get("implicated_region_size", 999)
        if moves >= 3 and size <= 15:
            return True, "bundle", ""
            
    # Determine the rejection reason based on which profiles exist
    reason = "No spatial evidence"
    if p_bun:
        if p_bun.get("producing_move_count", 0) < 3: reason = "bundle_producing_moves < 3"
        elif p_bun.get("implicated_region_size", 999) > 15: reason = "bundle_region_size > 15"
    elif p_rec:
        earliest = p_rec.get("earliest_ply")
        if earliest is None or earliest > 2: reason = "recurrence_earliest_ply > 2"
        elif p_rec.get("distinct_line_count", 0) < 3: reason = "recurrence_lines < 3"
    elif p_dir:
        if p_dir.get("candidate_fraction", 0.0) < 0.15: reason = "direct_candidate_fraction < 0.15"
        
    return False, "none", reason
