import chess
from typing import Dict, List, Optional, Union
from .models import (
    AnalysisRecord, PairedAnalysisRecord, SquareAttribution, ImplicatedMove,
    SquareDeltaSummary, SquareRoleDeltas, MetricDelta, SquareEffectRole
)
from .engine import EngineAdapter, analyze
from .attribution import aggregate_square_attributions

def filter_moves(moves: List[ImplicatedMove], role_filter: str) -> List[ImplicatedMove]:
    if role_filter == "all":
        return moves
    return [m for m in moves if role_filter in [r.value for r in m.roles]]

def calculate_metric(moves: List[ImplicatedMove], metric_filter: str) -> Optional[Union[float, int]]:
    if not moves:
        return None

    if metric_filter == "move_count":
        return len(moves)

    if metric_filter == "mate_count":
        return sum(1 for m in moves if m.outcome.type == "mate")

    cp_outcomes = [m.outcome.value for m in moves if m.outcome.type == "cp"]
    cp_regrets = [m.regret.value for m in moves if m.regret and m.regret.type == "cp" and m.regret.value is not None]

    if "outcome" in metric_filter:
        if not cp_outcomes:
            return None
        if metric_filter == "best_cp":
            return max(cp_outcomes)
        if metric_filter == "worst_cp":
            return min(cp_outcomes)
        if metric_filter == "mean_cp":
            return sum(cp_outcomes) / len(cp_outcomes)

    if "regret" in metric_filter:
        if not cp_regrets:
            return None
        if metric_filter == "min_cp_regret":
            return min(cp_regrets)
        if metric_filter == "max_cp_regret":
            return max(cp_regrets)
        if metric_filter == "mean_cp_regret":
            return sum(cp_regrets) / len(cp_regrets)

    return None

def compute_square_deltas(before_attr: Optional[SquareAttribution], after_attr: Optional[SquareAttribution]) -> SquareDeltaSummary:
    roles = ["all", "origin", "destination", "capture", "en_passant_capture"]
    metrics = ["move_count", "best_cp", "worst_cp", "mean_cp", "min_cp_regret", "max_cp_regret", "mean_cp_regret", "mate_count"]

    before_moves = before_attr.implicated_moves if before_attr else []
    after_moves = after_attr.implicated_moves if after_attr else []

    summary = SquareDeltaSummary(roles={})

    for r in roles:
        b_filtered = filter_moves(before_moves, r)
        a_filtered = filter_moves(after_moves, r)

        role_deltas = SquareRoleDeltas(metrics={})
        for m in metrics:
            b_val = calculate_metric(b_filtered, m)
            a_val = calculate_metric(a_filtered, m)

            if b_val is None and a_val is None:
                state = "absent_both"
                delta_val = None
            elif b_val is not None and a_val is None:
                state = "disappeared"
                delta_val = None
            elif b_val is None and a_val is not None:
                state = "appeared"
                delta_val = None
            else:
                state = "persisted"
                delta_val = a_val - b_val

            role_deltas.metrics[m] = MetricDelta(
                state=state,
                before=b_val,
                after=a_val,
                delta=delta_val
            )
        summary.roles[r] = role_deltas

    return summary

def analyze_transition(fen: str, move_uci: str, adapter: EngineAdapter, budget_type: str, budget_value: int) -> PairedAnalysisRecord:
    board = chess.Board(fen)
    if not board.is_valid():
        raise ValueError("Invalid FEN position")

    try:
        move = chess.Move.from_uci(move_uci)
    except chess.InvalidMoveError:
        raise ValueError("Invalid transition move format")

    if move not in board.legal_moves:
        raise ValueError("Transition move is illegal in given position")

    before_side_to_move = "white" if board.turn == chess.WHITE else "black"
    comparison_perspective = before_side_to_move

    # 1. Analyze before
    before_record = analyze(fen, adapter, budget_type, budget_value, comparison_perspective=comparison_perspective)
    before_attributions = aggregate_square_attributions(before_record)

    # 2. Push move
    board.push(move)
    resulting_fen = board.fen()
    after_side_to_move = "white" if board.turn == chess.WHITE else "black"

    # 3. Analyze after
    after_record = analyze(resulting_fen, adapter, budget_type, budget_value, comparison_perspective=comparison_perspective)
    after_attributions = aggregate_square_attributions(after_record)

    # 4. Compute deltas
    all_squares = set(before_attributions.keys()) | set(after_attributions.keys())
    deltas = {}
    for sq in all_squares:
        b_attr = before_attributions.get(sq)
        a_attr = after_attributions.get(sq)
        deltas[sq] = compute_square_deltas(b_attr, a_attr)

    return PairedAnalysisRecord(
        source_fen=fen,
        transition_move=move_uci,
        resulting_fen=resulting_fen,
        before_side_to_move=before_side_to_move,
        after_side_to_move=after_side_to_move,
        comparison_perspective=comparison_perspective,
        before_record=before_record,
        after_record=after_record,
        before_attributions=before_attributions,
        after_attributions=after_attributions,
        deltas=deltas
    )
