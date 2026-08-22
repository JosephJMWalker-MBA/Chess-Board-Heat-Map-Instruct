#!/usr/bin/env python3
import os
import sys
import hashlib
from pathlib import Path

# Bound fixed paths
MANIFEST_PATH = "artifacts/research/cp_source_feasibility_2026_07/cp_root_population_manifest_v2.jsonl.zst"
META_PATH = "artifacts/research/cp_source_feasibility_2026_07/cp_root_population_manifest_v2.meta.json"
TARGET_OUTPUT_PATH = "artifacts/research/cp_target_acquisition_2026_07/raw/cp_target_root_results_v2.jsonl"

def verify_executable(path: str) -> bool:
    with open(path, "rb") as f:
        digest = hashlib.sha256(f.read()).hexdigest()
    return digest == "ae4c93fa9676ca7750d0714342fd8a5b1d018000fc6e0f6cedf112067b5ef374"

def main():
    if not os.environ.get("CHESSHEAT_TARGET_ACQUISITION_APPROVED_SHA"):
        print("ERROR: CHESSHEAT_TARGET_ACQUISITION_APPROVED_SHA environment variable must be set.")
        sys.exit(1)
        
    stockfish_path = os.environ.get("CHESSHEAT_STOCKFISH18")
    if not stockfish_path:
        print("ERROR: CHESSHEAT_STOCKFISH18 environment variable must be set.")
        sys.exit(1)
        
    if not Path(stockfish_path).is_file():
        print(f"ERROR: Stockfish executable not found at {stockfish_path}")
        sys.exit(1)
        
    if not verify_executable(stockfish_path):
        print(f"ERROR: Stockfish executable at {stockfish_path} does not match exact SHA256 ae4c93fa9676ca7750d0714342fd8a5b1d018000fc6e0f6cedf112067b5ef374")
        sys.exit(1)
        
    from chessheat.cp_target_acquisition import TargetAcquisitionRunnerV2
    
    runner = TargetAcquisitionRunnerV2(
        manifest_path=MANIFEST_PATH,
        output_path=TARGET_OUTPUT_PATH,
        stockfish_path=stockfish_path,
        meta_path=META_PATH
    )
    
    print("Starting CP TARGET Acquisition V2...")
    runner.run()
    print("Completed CP TARGET Acquisition.")

if __name__ == "__main__":
    main()
