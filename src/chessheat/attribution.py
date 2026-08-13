from typing import Dict, List, Optional
from .models import AnalysisRecord, MoveObservation, Regret, Score, SquareEffectRole, SquareAttribution, ImplicatedMove

def calculate_regret(best_score: Score, move_score: Score) -> Regret:
    # Both scores must be from the same perspective
    assert best_score.perspective == move_score.perspective

    if best_score.type == "cp" and move_score.type == "cp":
        # Best score is higher, so regret is best - move
        diff = best_score.value - move_score.value
        return Regret(type="cp", value=diff, perspective=best_score.perspective)
    elif best_score.type == "mate" and move_score.type == "mate":
        # Mate values: positive is mate in X for us, negative is mate in X against us.
        # Actually it's simpler to just not do math on mates for now, or just track difference.
        # But difference between mates isn't a linear "regret". Let's use mixed/null for mate regret for now
        # to avoid bad math, unless they are literally identical.
        if best_score.value == move_score.value:
            return Regret(type="mate_diff", value=0, perspective=best_score.perspective)
        return Regret(type="mate_diff", value=None, perspective=best_score.perspective)
    else:
        # Mixed
        return Regret(type="mixed", value=None, perspective=best_score.perspective)

def extract_direct_effects(move_obs: MoveObservation) -> Dict[str, List[SquareEffectRole]]:
    effects: Dict[str, List[SquareEffectRole]] = {}

    def add_effect(sq: str, role: SquareEffectRole):
        if sq not in effects:
            effects[sq] = []
        effects[sq].append(role)

    # Standard origin/destination
    if not move_obs.is_castling:
        add_effect(move_obs.origin_square, SquareEffectRole.ORIGIN)
        add_effect(move_obs.destination_square, SquareEffectRole.DESTINATION)

    if move_obs.is_capture:
        if move_obs.is_en_passant:
            # For en passant, the captured square is different from destination
            add_effect(move_obs.captured_square, SquareEffectRole.EN_PASSANT_CAPTURE)
        else:
            add_effect(move_obs.destination_square, SquareEffectRole.CAPTURE)

    if move_obs.is_castling:
        # We need to map the castling move to its 4 squares.
        # origin is king origin, dest is king dest.
        add_effect(move_obs.origin_square, SquareEffectRole.KING_ORIGIN)
        add_effect(move_obs.destination_square, SquareEffectRole.KING_DESTINATION)

        # Infer rook squares based on king destination
        # White Kingside: e1g1 (rook h1 -> f1)
        # White Queenside: e1c1 (rook a1 -> d1)
        # Black Kingside: e8g8 (rook h8 -> f8)
        # Black Queenside: e8c8 (rook a8 -> d8)

        if move_obs.uci == "e1g1":
            add_effect("h1", SquareEffectRole.ROOK_ORIGIN)
            add_effect("f1", SquareEffectRole.ROOK_DESTINATION)
        elif move_obs.uci == "e1c1":
            add_effect("a1", SquareEffectRole.ROOK_ORIGIN)
            add_effect("d1", SquareEffectRole.ROOK_DESTINATION)
        elif move_obs.uci == "e8g8":
            add_effect("h8", SquareEffectRole.ROOK_ORIGIN)
            add_effect("f8", SquareEffectRole.ROOK_DESTINATION)
        elif move_obs.uci == "e8c8":
            add_effect("a8", SquareEffectRole.ROOK_ORIGIN)
            add_effect("d8", SquareEffectRole.ROOK_DESTINATION)

    return effects

def compare_scores(s1: Score, s2: Score) -> int:
    """Returns 1 if s1 > s2, -1 if s1 < s2, 0 if equal. From the score's perspective."""
    if s1.type == "mate" and s2.type != "mate":
        return 1 if s1.value > 0 else -1
    if s2.type == "mate" and s1.type != "mate":
        return -1 if s2.value > 0 else 1
    if s1.type == "mate" and s2.type == "mate":
        # Both mate. Positive is better. Faster positive mate is better (smaller value).
        # Slower negative mate is better (larger negative value... wait. -1 is mate against us in 1. -5 is mate against us in 5. -5 is better than -1).
        # Actually chess.engine Mate compares: Mate(1) > Mate(2) > Cp(x) > Mate(-2) > Mate(-1).
        if s1.value > 0 and s2.value > 0:
            return -1 if s1.value > s2.value else (1 if s1.value < s2.value else 0)
        elif s1.value < 0 and s2.value < 0:
            return 1 if s1.value < s2.value else (-1 if s1.value > s2.value else 0)
        else:
            return 1 if s1.value > s2.value else -1

    # Both CP
    if s1.value > s2.value:
        return 1
    elif s1.value < s2.value:
        return -1
    return 0

def aggregate_square_attributions(record: AnalysisRecord) -> Dict[str, SquareAttribution]:
    if not record.move_observations:
        return {}

    # 1. Find best move to calculate regret
    best_move_obs = record.move_observations[0]
    for obs in record.move_observations[1:]:
        if compare_scores(obs.score, best_move_obs.score) > 0:
            best_move_obs = obs

    best_score = best_move_obs.score

    # 2. Map moves to squares
    # square -> list of move observations
    square_moves: Dict[str, List[MoveObservation]] = {}

    for obs in record.move_observations:
        # compute regret
        obs.regret = calculate_regret(best_score, obs.score)

        effects = extract_direct_effects(obs)
        for sq in effects.keys():
            if sq not in square_moves:
                square_moves[sq] = []
            square_moves[sq].append(obs)

    # 3. Aggregate
    attributions: Dict[str, SquareAttribution] = {}

    for sq, moves in square_moves.items():
        attr = SquareAttribution(square=sq)

        cp_outcomes = []
        cp_regrets = []

        sq_best_obs: Optional[MoveObservation] = None
        sq_worst_obs: Optional[MoveObservation] = None

        for m in moves:
            attr.move_count += 1
            effects = extract_direct_effects(m)
            roles = effects.get(sq, [])

            im = ImplicatedMove(
                uci=m.uci,
                roles=roles,
                outcome=m.score,
                regret=m.regret,
                promotion=m.promotion
            )
            attr.implicated_moves.append(im)

            if SquareEffectRole.ORIGIN in roles or SquareEffectRole.KING_ORIGIN in roles or SquareEffectRole.ROOK_ORIGIN in roles:
                attr.as_origin += 1
            if SquareEffectRole.DESTINATION in roles or SquareEffectRole.KING_DESTINATION in roles or SquareEffectRole.ROOK_DESTINATION in roles:
                attr.as_destination += 1
            if SquareEffectRole.CAPTURE in roles or SquareEffectRole.EN_PASSANT_CAPTURE in roles:
                attr.as_capture += 1

            if m.score.type == "cp":
                cp_outcomes.append(m.score.value)
            else:
                attr.mate_outcomes += 1

            if m.regret and m.regret.type == "cp" and m.regret.value is not None:
                cp_regrets.append(m.regret.value)

            if sq_best_obs is None or compare_scores(m.score, sq_best_obs.score) > 0:
                sq_best_obs = m

            if sq_worst_obs is None or compare_scores(m.score, sq_worst_obs.score) < 0:
                sq_worst_obs = m

        if sq_best_obs:
            attr.best_move = sq_best_obs.uci
        if sq_worst_obs:
            attr.worst_move = sq_worst_obs.uci

        if cp_outcomes:
            attr.best_outcome_cp = max(cp_outcomes)
            attr.worst_outcome_cp = min(cp_outcomes)
            attr.mean_cp_outcome = sum(cp_outcomes) / len(cp_outcomes)

        if cp_regrets:
            attr.min_cp_regret = min(cp_regrets)
            attr.max_cp_regret = max(cp_regrets)
            attr.mean_cp_regret = sum(cp_regrets) / len(cp_regrets)

        attributions[sq] = attr

    return attributions
