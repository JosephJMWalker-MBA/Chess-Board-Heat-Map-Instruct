import os
from chessheat.cp_source_feasibility import SourceFeasibilityRunner
import sys

def main():
    sf_path = os.environ.get("CHESSHEAT_STOCKFISH18")
    if not sf_path:
        print("Missing CHESSHEAT_STOCKFISH18 environment variable.")
        sys.exit(1)
        
    manifest = "artifacts/research/cp_source_feasibility_2026_07/cp_root_population_manifest.jsonl.zst"
    output = "artifacts/research/cp_source_feasibility_2026_07/raw/cp_source_root_results.jsonl.zst"
    
    runner = SourceFeasibilityRunner(manifest, output, sf_path)
    runner.run()
    
if __name__ == "__main__":
    main()
