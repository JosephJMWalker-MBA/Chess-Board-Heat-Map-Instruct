from typing import Dict, List, Set, Tuple
from collections import defaultdict
import statistics

from chessheat.models import AnalysisRecord, EventSignature, MetricDistribution, EventBundle
from chessheat.geometry import GeometryDelta

def _compute_distribution(move_values: List[Tuple[str, float]], reverse_best: bool = False) -> MetricDistribution:
    if not move_values:
        return MetricDistribution()

    vals = [v for _, v in move_values]
    min_val = min(vals)
    max_val = max(vals)

    best_val = min_val if not reverse_best else max_val
    worst_val = max_val if not reverse_best else min_val

    best_move = next((m for m, v in move_values if v == best_val), None)
    worst_move = next((m for m, v in move_values if v == worst_val), None)

    median_val = statistics.median(vals)
    q1 = None
    q3 = None
    if len(vals) >= 2:
        try:
            quantiles = statistics.quantiles(vals, n=4)
            q1 = quantiles[0]
            q3 = quantiles[2]
        except statistics.StatisticsError:
            pass

    return MetricDistribution(
        min_val=min_val,
        max_val=max_val,
        mean_val=statistics.mean(vals),
        median_val=median_val,
        q1_val=q1,
        q3_val=q3,
        best_move=best_move,
        worst_move=worst_move
    )

def extract_signatures(delta: GeometryDelta) -> Set[EventSignature]:
    sigs = set()

    # Attacks
    for a in delta.appeared_attacks:
        sigs.add(EventSignature(event_type="appeared_attack", source_square=a.attacker.square, target_square=a.target_square, piece_symbol=a.attacker.symbol, target_symbol=a.target_piece.symbol if a.target_piece else None))
    for a in delta.disappeared_attacks:
        sigs.add(EventSignature(event_type="disappeared_attack", source_square=a.attacker.square, target_square=a.target_square, piece_symbol=a.attacker.symbol, target_symbol=a.target_piece.symbol if a.target_piece else None))

    # Defenses
    for d in delta.appeared_defenses:
        sigs.add(EventSignature(event_type="appeared_defense", source_square=d.attacker.square, target_square=d.target_square, piece_symbol=d.attacker.symbol, target_symbol=d.target_piece.symbol if d.target_piece else None))
    for d in delta.disappeared_defenses:
        sigs.add(EventSignature(event_type="disappeared_defense", source_square=d.attacker.square, target_square=d.target_square, piece_symbol=d.attacker.symbol, target_symbol=d.target_piece.symbol if d.target_piece else None))

    # Rays
    for r in delta.appeared_rays:
        sigs.add(EventSignature(event_type="appeared_ray", source_square=r.source.square, target_square=r.target_square, path=list(r.path), piece_symbol=r.source.symbol, target_symbol=r.target_piece.symbol if r.target_piece else None))
    for r in delta.disappeared_rays:
        sigs.add(EventSignature(event_type="disappeared_ray", source_square=r.source.square, target_square=r.target_square, path=list(r.path), piece_symbol=r.source.symbol, target_symbol=r.target_piece.symbol if r.target_piece else None))

    # Mobility
    for p, dest in delta.mobility_gained:
        sigs.add(EventSignature(event_type="mobility_gained", source_square=p.square, target_square=dest, piece_symbol=p.symbol))
    for p, dest in delta.mobility_lost:
        sigs.add(EventSignature(event_type="mobility_lost", source_square=p.square, target_square=dest, piece_symbol=p.symbol))

    return sigs

def aggregate_bundle_leverage(record: AnalysisRecord, move_deltas: Dict[str, GeometryDelta]) -> List[EventBundle]:
    # Extract unique events and mapping to producing moves
    event_to_moves = defaultdict(list)
    total_moves = len(move_deltas)
    all_ucis = set(move_deltas.keys())

    for uci, delta in move_deltas.items():
        sigs = extract_signatures(delta)
        for sig in sigs:
            event_to_moves[sig].append(uci)

    # Group events by perfectly identical producing move sets (confounding bundles)
    moves_to_events = defaultdict(list)
    for sig, producing_moves in event_to_moves.items():
        k = frozenset(producing_moves)
        moves_to_events[k].append(sig)

    # Lookup for engine metrics
    outcomes_cp = {}
    regrets_cp = {}

    for obs in record.move_observations:
        uci = obs.uci
        if obs.score.type == "cp":
            outcomes_cp[uci] = float(obs.score.value)
        if obs.regret and obs.regret.type == "cp" and obs.regret.value is not None:
            regrets_cp[uci] = float(obs.regret.value)

    bundles = []

    for prod_set_fs, events in moves_to_events.items():
        prod_set = set(prod_set_fs)
        non_prod_set = all_ucis - prod_set

        o_with = [(m, outcomes_cp[m]) for m in prod_set if m in outcomes_cp]
        o_without = [(m, outcomes_cp[m]) for m in non_prod_set if m in outcomes_cp]
        r_with = [(m, regrets_cp[m]) for m in prod_set if m in regrets_cp]
        r_without = [(m, regrets_cp[m]) for m in non_prod_set if m in regrets_cp]

        outcome_with = _compute_distribution(o_with, reverse_best=True)
        outcome_without = _compute_distribution(o_without, reverse_best=True)
        regret_with = _compute_distribution(r_with, reverse_best=False)
        regret_without = _compute_distribution(r_without, reverse_best=False)

        mean_regret_diff = 0.0
        if regret_with.mean_val is not None and regret_without.mean_val is not None:
            mean_regret_diff = regret_with.mean_val - regret_without.mean_val

        median_regret_diff = 0.0
        if regret_with.median_val is not None and regret_without.median_val is not None:
            median_regret_diff = regret_with.median_val - regret_without.median_val

        # Collect implicated squares
        implicated = set()
        for e in events:
            if e.source_square: implicated.add(e.source_square)
            if e.target_square: implicated.add(e.target_square)
            for sq in e.path:
                implicated.add(sq)

        b = EventBundle(
            constituent_events=sorted(events, key=lambda e: (e.event_type, e.source_square, e.target_square)),
            producing_moves=sorted(prod_set),
            non_producing_moves=sorted(non_prod_set),
            candidate_fraction=len(prod_set) / total_moves if total_moves > 0 else 0.0,
            regret_with_bundle=regret_with,
            regret_without_bundle=regret_without,
            outcome_with_bundle=outcome_with,
            outcome_without_bundle=outcome_without,
            mean_regret_diff=mean_regret_diff,
            median_regret_diff=median_regret_diff,
            implicated_squares=sorted(implicated),
            is_perfectly_confounded=len(events) > 1
        )
        bundles.append(b)

    # Sort by fraction (desc), then by mean_regret_diff (desc)
    bundles.sort(key=lambda b: (-b.candidate_fraction, -b.mean_regret_diff))

    return bundles
