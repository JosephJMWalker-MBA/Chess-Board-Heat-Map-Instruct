#!/usr/bin/env python3
import os
import sys
from pathlib import Path

# Bound fixed paths
MANIFEST_PATH = "artifacts/research/cp_source_feasibility_2026_07/cp_root_population_manifest_v2.jsonl.zst"
META_PATH = "artifacts/research/cp_source_feasibility_2026_07/cp_root_population_manifest_v2.meta.json"
TARGET_OUTPUT_PATH = "artifacts/research/cp_target_acquisition_2026_07/raw/cp_target_root_results_v1.jsonl"

def main():
    stockfish_path = os.environ.get("CHESSHEAT_STOCKFISH18")
    if not stockfish_path:
        print("ERROR: CHESSHEAT_STOCKFISH18 environment variable must be set.")
        sys.exit(1)
        
    if not Path(stockfish_path).is_file():
        print(f"ERROR: Stockfish executable not found at {stockfish_path}")
        sys.exit(1)
        
    from chessheat.cp_target_acquisition import TargetAcquisitionRunnerV1
    
    runner = TargetAcquisitionRunnerV1(
        manifest_path=MANIFEST_PATH,
        output_path=TARGET_OUTPUT_PATH,
        stockfish_path=stockfish_path,
        meta_path=META_PATH
    )
    
    print("Starting CP TARGET Acquisition V1...")
    runner.run()
    print("Completed CP TARGET Acquisition.")

if __name__ == "__main__":
    main()
