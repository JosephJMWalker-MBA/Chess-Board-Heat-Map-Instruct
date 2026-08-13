import json
import os
from pathlib import Path
import subprocess

FIXTURES_FILE = "tests/fixtures/validation_m5.json"
OUTPUT_DIR = "tests/fixtures/results"
STOCKFISH_PATH = "/opt/homebrew/bin/stockfish"

def run_cli_for_fixture(fixture, budget):
    fen = fixture["fen"]
    f_id = fixture["fixture_id"]
    transition = fixture.get("transition_move")

    out_file = os.path.join(OUTPUT_DIR, f"{f_id}_{budget}.json")

    cmd = [
        "python", "-m", "chessheat.cli",
        "--fen", fen,
        "--stockfish-path", STOCKFISH_PATH,
        "--nodes", str(budget),
        "--output", out_file
    ]

    if transition:
        cmd.extend(["--transition-move", transition])
    else:
        cmd.extend(["--layer", "attribution"])

    print(f"Running {f_id} at {budget} nodes...")
    try:
        subprocess.run(cmd, check=True, env={**os.environ, "PYTHONPATH": "src"})
    except subprocess.CalledProcessError as e:
        print(f"Error running {f_id}: {e}")

def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    with open(FIXTURES_FILE, 'r') as f:
        fixtures = json.load(f)

    budgets = [50000, 100000, 250000]

    for fixture in fixtures:
        for b in budgets:
            run_cli_for_fixture(fixture, b)

if __name__ == "__main__":
    main()
