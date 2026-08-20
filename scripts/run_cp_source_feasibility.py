import os
import sys
from chessheat.cp_source_feasibility import SourceFeasibilityRunnerV2

def main():
    sf_path = os.environ.get("CHESSHEAT_STOCKFISH18")
    if not sf_path:
        print("Missing CHESSHEAT_STOCKFISH18 environment variable.")
        sys.exit(1)
        
    manifest = "artifacts/research/cp_source_feasibility_2026_07/cp_root_population_manifest_v2.jsonl.zst"
    output = "artifacts/research/cp_source_feasibility_2026_07/raw/cp_source_root_results_v2.jsonl"
    meta = "artifacts/research/cp_source_feasibility_2026_07/cp_root_population_manifest_v2.meta.json"
    
    runner = SourceFeasibilityRunnerV2(manifest, output, sf_path, meta)
    runner.run()
    
if __name__ == "__main__":
    main()
