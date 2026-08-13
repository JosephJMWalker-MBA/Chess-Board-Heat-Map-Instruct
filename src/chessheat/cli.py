import argparse
import sys
import json
from .engine import StockfishAdapter, analyze
from .attribution import aggregate_square_attributions
from .recurrence import aggregate_square_recurrence

def main():
    parser = argparse.ArgumentParser(description="ChessHeat Analysis CLI - Milestone 1")
    parser.add_argument("--fen", type=str, required=True, help="FEN string to analyze")
    parser.add_argument("--stockfish-path", type=str, required=True, help="Path to Stockfish executable")
    parser.add_argument("--nodes", type=int, default=100000, help="Search budget in nodes (default: 100000)")
    parser.add_argument("--layer", type=str, choices=["attribution", "delta", "recurrence"], default="attribution",
                        help="Which metric layer to output.")
    parser.add_argument("--multipv", type=int, default=5,
                        help="Number of candidate lines to consider for recurrence.")
    parser.add_argument("--transition-move", type=str, help="Legal move to transition to the next position (e.g. e2e4) for paired analysis.")
    parser.add_argument("--output", type=str, help="Path to save JSON output (defaults to stdout)")

    args = parser.parse_args()

    adapter = StockfishAdapter(args.stockfish_path)
    try:
        if args.transition_move:
            from .delta import analyze_transition
            paired_record = analyze_transition(fen=args.fen, move_uci=args.transition_move, adapter=adapter, budget_type="nodes", budget_value=args.nodes)
            json_out = paired_record.model_dump_json(indent=2)
        else:
            candidate_policy = {"top_n": args.multipv}
            record = analyze(fen=args.fen, adapter=adapter, budget_type="nodes", budget_value=args.nodes, candidate_policy=candidate_policy)

            if args.layer == "attribution":
                attributions = aggregate_square_attributions(record)
                output_data = {
                    "schema_version": "1.0",
                    "fen": record.fen,
                    "root_side": record.root_side,
                    "engine_name": record.engine_name,
                    "engine_options": record.engine_options,
                    "search_budget_type": record.search_budget_type,
                    "search_budget_value": record.search_budget_value,
                    "baseline_observation": record.baseline_observation.model_dump(),
                    "attributions": {sq: attr.model_dump() for sq, attr in attributions.items()}
                }
                json_out = json.dumps(output_data, indent=2)
            elif args.layer == "recurrence":
                attributions = aggregate_square_attributions(record)
                recurrence_result = aggregate_square_recurrence(record)
                output_data = {
                    "fen": record.fen,
                    "layer": "recurrence",
                    "candidate_policy": record.candidate_policy,
                    "recurrence_provenance": recurrence_result.provenance.model_dump(),
                    "recurrence": {sq: r.model_dump() for sq, r in recurrence_result.squares.items()},
                    "attributions": {sq: a.model_dump() for sq, a in attributions.items()},
                    "engine_name": record.engine_name,
                    "engine_options": record.engine_options
                }
                json_out = json.dumps(output_data, indent=2)
            else:
                json_out = record.model_dump_json(indent=2)

        if args.output:
            with open(args.output, "w") as f:
                f.write(json_out)
        else:
            print(json_out)
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    finally:
        adapter.close()

if __name__ == "__main__":
    main()
