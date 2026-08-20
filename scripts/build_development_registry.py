import json
import chess
import hashlib
import subprocess
from pathlib import Path
from chessheat.semantics import SufficientPosition
from chessheat.cp_root_population import get_conservative_transposition_group, canonical_json_digest

def main():
    registry = []
    seen = set()
    
    # Git ls-files to get tracked files only
    result = subprocess.run(["git", "ls-files"], capture_output=True, text=True, check=True)
    files = result.stdout.strip().split("\n")
    files.sort()
    
    # Exclude list
    exclude_paths = [
        "docs/research/CP_PRIOR_DEVELOPMENT_REGISTRY.json",
        "docs/research/CP_PRIOR_DEVELOPMENT_REGISTRY_V2.json",
    ]
    
    for fpath in files:
        if fpath in exclude_paths or fpath.startswith("docs/research/CP_ROOT_POPULATION_JULY_2026_MANIFEST") or fpath.startswith("docs/research/CP_SOURCE_FEASIBILITY") or fpath.startswith("artifacts/research/cp_source_feasibility_2026_07/") or fpath.startswith("data/"):
            continue
            
        path = Path(fpath)
        if not path.is_file():
            continue
            
        if path.suffix == ".json":
            try:
                with open(path) as f:
                    data = json.load(f)
                
                def extract_all_suff(obj):
                    res = []
                    if isinstance(obj, dict):
                        if "board_arrangement_fen" in obj and "side_to_move" in obj and "history_available" in obj:
                            try:
                                # Ensure it maps completely to SufficientPosition
                                suff = SufficientPosition(**obj)
                                res.append(obj)
                            except Exception:
                                pass
                        for v in obj.values():
                            res.extend(extract_all_suff(v))
                    elif isinstance(obj, list):
                        for item in obj:
                            res.extend(extract_all_suff(item))
                    return res

                suff_list = extract_all_suff(data)
                for i, suff_data in enumerate(suff_list):
                    try:
                        suff = SufficientPosition(**suff_data)
                        board = chess.Board(suff.board_arrangement_fen)
                        board.turn = chess.WHITE if suff.side_to_move == "w" else chess.BLACK
                        board.set_castling_fen(suff.castling_rights)
                        if suff.en_passant_square:
                            board.ep_square = chess.parse_square(suff.en_passant_square)
                        
                        conservative_key = get_conservative_transposition_group(board)
                        exact_s0_digest = canonical_json_digest(suff.model_dump())
                        
                        rec = {
                            "registry_schema": "CP_PRIOR_DEVELOPMENT_REGISTRY_V2",
                            "source_file": str(path),
                            "fixture_id": f"{path.stem}_{i}",
                            "extraction_method": "JSON_S0",
                            "exact_s0": suff.model_dump(),
                            "exact_s0_digest": exact_s0_digest,
                            "conservative_transposition_group": conservative_key,
                            "extraction_status": "SUCCESS"
                        }
                        
                        rec_str = json.dumps(rec, sort_keys=True)
                        if rec_str not in seen:
                            seen.add(rec_str)
                            registry.append(rec)
                    except Exception as e:
                        pass
            except Exception:
                pass
                
        # Simple FEN search across json/md (fen only)
        if path.suffix in [".json", ".jsonl", ".md"]:
            try:
                content = path.read_text(errors='ignore')
                import re
                fens = re.findall(r'([rnbqkpRNBQKP1-8]+/[rnbqkpRNBQKP1-8]+/[rnbqkpRNBQKP1-8]+/[rnbqkpRNBQKP1-8]+/[rnbqkpRNBQKP1-8]+/[rnbqkpRNBQKP1-8]+/[rnbqkpRNBQKP1-8]+/[rnbqkpRNBQKP1-8]+ [wb] (?:K?Q?k?q?|-) (?:[a-h][36]|-) \d+ \d+)', content)
                for i, fen in enumerate(fens):
                    try:
                        board = chess.Board(fen)
                        conservative_key = get_conservative_transposition_group(board)
                        rec = {
                            "registry_schema": "CP_PRIOR_DEVELOPMENT_REGISTRY_V2",
                            "source_file": str(path),
                            "fixture_id": f"{path.stem}_fen_{i}",
                            "extraction_method": "REGEX_FEN",
                            "exact_s0": None,
                            "exact_s0_digest": None,
                            "conservative_transposition_group": conservative_key,
                            "extraction_status": "FEN_ONLY"
                        }
                        rec_str = json.dumps(rec, sort_keys=True)
                        if rec_str not in seen:
                            seen.add(rec_str)
                            registry.append(rec)
                    except Exception:
                        pass
            except Exception:
                pass

    # Sort
    registry.sort(key=lambda x: canonical_json_digest(x))
    
    out_path = Path("docs/research/CP_PRIOR_DEVELOPMENT_REGISTRY_V2.json")
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w") as f:
        json.dump(registry, f, indent=2, sort_keys=True)
        
    print(f"Built registry with {len(registry)} items.")

if __name__ == "__main__":
    main()
