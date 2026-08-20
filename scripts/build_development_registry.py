import json
import chess
import hashlib
from pathlib import Path
from chessheat.semantics import SufficientPosition
from chessheat.cp_root_population import get_conservative_transposition_group

def main():
    registry = []
    
    # We will search tests/fixtures/ and maybe some docs for FENs or SufficientPositions
    fixture_dir = Path("tests/fixtures")
    if fixture_dir.exists():
        for path in fixture_dir.rglob("*.json"):
            try:
                with open(path) as f:
                    data = json.load(f)
                
                # Check if it has a SufficientPosition inside
                def extract_suff(obj):
                    if isinstance(obj, dict):
                        if "board_arrangement_fen" in obj and "side_to_move" in obj:
                            return obj
                        for v in obj.values():
                            res = extract_suff(v)
                            if res: return res
                    elif isinstance(obj, list):
                        for item in obj:
                            res = extract_suff(item)
                            if res: return res
                    return None

                suff_data = extract_suff(data)
                if suff_data:
                    try:
                        suff = SufficientPosition(**suff_data)
                        board = chess.Board(suff.board_arrangement_fen)
                        board.turn = chess.WHITE if suff.side_to_move == "w" else chess.BLACK
                        board.set_castling_xfen(suff.castling_rights)
                        if suff.en_passant_square:
                            board.ep_square = chess.parse_square(suff.en_passant_square)
                        
                        conservative_key = get_conservative_transposition_group(board)
                        
                        registry.append({
                            "source_file": str(path),
                            "fixture_id": path.stem,
                            "exact_s0": suff_data,
                            "conservative_key": conservative_key,
                            "extraction_status": "SUCCESS"
                        })
                    except Exception as e:
                        registry.append({
                            "source_file": str(path),
                            "fixture_id": path.stem,
                            "exact_s0": None,
                            "conservative_key": None,
                            "extraction_status": f"FAILED: {e}"
                        })
            except Exception:
                pass
                
    # Additional naive FEN search across json/md
    for ext in ["*.json", "*.jsonl", "*.md"]:
        for path in Path(".").rglob(ext):
            if "artifacts" in path.parts or "data" in path.parts: continue
            if not path.is_file(): continue
            try:
                content = path.read_text(errors='ignore')
                import re
                # Simple FEN regex
                fens = re.findall(r'([rnbqkpRNBQKP1-8]+/[rnbqkpRNBQKP1-8]+/[rnbqkpRNBQKP1-8]+/[rnbqkpRNBQKP1-8]+/[rnbqkpRNBQKP1-8]+/[rnbqkpRNBQKP1-8]+/[rnbqkpRNBQKP1-8]+/[rnbqkpRNBQKP1-8]+ [wb] (?:K?Q?k?q?|-) (?:[a-h][36]|-) \d+ \d+)', content)
                for i, fen in enumerate(fens):
                    try:
                        board = chess.Board(fen)
                        conservative_key = get_conservative_transposition_group(board)
                        registry.append({
                            "source_file": str(path),
                            "fixture_id": f"{path.stem}_fen_{i}",
                            "exact_s0": None, # Missing history/etc
                            "conservative_key": conservative_key,
                            "extraction_status": "SUCCESS_FEN_ONLY"
                        })
                    except Exception:
                        pass
            except Exception:
                pass

    out_path = Path("docs/research/CP_PRIOR_DEVELOPMENT_REGISTRY.json")
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w") as f:
        json.dump(registry, f, indent=2, sort_keys=True)
        
    print(f"Built registry with {len(registry)} items.")

if __name__ == "__main__":
    main()
