import json
import chess
from chessheat.engine import StockfishAdapter, analyze
from chessheat.fusion import fuse_signals
from chessheat.evaluation import evaluate_model

# Extracted from M5 validation definitions
M8_FIXTURES = {
    "F1_Tactical_Fork": ["d6", "f6", "e8", "d7"],
    "F2_Poisoned_Destination": ["d5"],
    "F3_Soft_Pin": ["e1", "e2", "e3", "e4", "e7"],
    "F4_Overloaded_Defender": ["f6", "d5", "h7"],
    "F5_Central_Pawn_Break": ["c4", "c5", "d4", "d5", "e4", "e5"],
    "F6_Discovered_Attack": ["d1", "d4", "d5"],
    "F7_Quiet_Positional_Move": ["d4", "e5", "f4", "c5"],
    "F8_Negative_Control": []
}

def main():
    with open("tests/fixtures/validation_m5.json", "r") as f:
        fixtures = json.load(f)

    adapter = StockfishAdapter(stockfish_path="stockfish", options={"Threads": 1, "Hash": 16})

    import sys
    nodes = int(sys.argv[1]) if len(sys.argv) > 1 else 100000
    report = {}

    try:
        for fx in fixtures:
            fid = fx["fixture_id"]
            if fid not in M8_FIXTURES:
                continue

            print(f"Analyzing {fid}...")
            fen = fx["fen"]
            expected_region = M8_FIXTURES[fid]

            # 1. Gather all evidence
            record = analyze(fen, adapter, "nodes", nodes)

            # 2. Fuse signals
            fusions = fuse_signals(fen, record)

            # 3. Evaluate models
            models = ["baseline_H", "baseline_I", "model_A", "model_B", "model_C", "model_D", "model_E", "model_F", "model_G"]
            evals = {}
            for m in models:
                evals[m] = evaluate_model(m, fusions, expected_region).model_dump()

            report[fid] = evals

    finally:
        adapter.close()

    with open(f"tests/fixtures/results_m8_{nodes//1000}k.json", "w") as f:
        json.dump(report, f, indent=2)

if __name__ == "__main__":
    main()
