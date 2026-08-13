import json
import chess
import asyncio
from chessheat.engine import StockfishAdapter, analyze
from chessheat.attribution import aggregate_square_attributions
from chessheat.geometry import extract_geometry, compute_geometry_delta
from chessheat.association import aggregate_geometry_associations

def analyze_fixture(adapter: StockfishAdapter, fen: str, root_side: str) -> dict:
    board = chess.Board(fen)

    # 1. Get engine analysis record
    # We will use nodes=100_000 to match the original M1 measurements
    record = analyze(fen, adapter, "nodes", 100000)
    aggregate_square_attributions(record)

    # 2. Extract base geometry
    g_before = extract_geometry(board)

    # 3. Compute geometry delta for every candidate
    move_deltas = {}
    for move in board.generate_legal_moves():
        b_copy = board.copy()
        b_copy.push(move)
        g_after = extract_geometry(b_copy)
        move_deltas[move.uci()] = compute_geometry_delta(g_before, g_after)

    # 4. Associate
    associations = aggregate_geometry_associations(record, move_deltas)

    return [a.model_dump() for a in associations]

def main():
    with open("tests/fixtures/validation_m5.json", "r") as f:
        fixtures = json.load(f)

    m7_fixtures = [f for f in fixtures if f["fixture_id"].startswith(("F3", "F4", "F6"))]

    report = {}

    adapter = StockfishAdapter(stockfish_path="stockfish", options={"Threads": 1, "Hash": 16})

    try:
        for fx in m7_fixtures:
            fid = fx["fixture_id"]
            fen = fx["fen"]
            side = fx["side_to_move"]

            print(f"Analyzing {fid}...")
            assocs = analyze_fixture(adapter, fen, side)
            report[fid] = assocs
    finally:
        adapter.close()

    with open("tests/fixtures/results_m7_5.json", "w") as f:
        json.dump(report, f, indent=2)

if __name__ == "__main__":
    main()
