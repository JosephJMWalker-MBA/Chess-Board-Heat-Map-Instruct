import zstandard
import chess.pgn
import io
import json
import hashlib
from typing import Dict, Any
from pathlib import Path
from chessheat.cp_root_population import process_game
import datetime

def main():
    corpus_path = "data/external/lichess/broadcast/2026-07/lichess_db_broadcast_2026-07.pgn.zst"
    expected_sha256 = "714d0eb99f99fca8d791142038b6c59b5ca6a51b3339bd3891a92f4bdffcbf0c"

    # Compute hash
    h = hashlib.sha256()
    with open(corpus_path, "rb") as f:
        while chunk := f.read(8192):
            h.update(chunk)
    observed_sha256 = h.hexdigest()
    if observed_sha256 != expected_sha256:
        raise ValueError(f"Checksum mismatch! Expected {expected_sha256}, got {observed_sha256}")

    print("Checksum verified.")

    # Load registry
    registry = []
    reg_path = Path("docs/research/CP_PRIOR_DEVELOPMENT_REGISTRY.json")
    if reg_path.exists():
        with open(reg_path) as f:
            registry = json.load(f)
            
    exact_s0_set = {r["exact_s0"]["board_arrangement_fen"] + r["exact_s0"]["side_to_move"] + r["exact_s0"]["castling_rights"] + str(r["exact_s0"]["en_passant_square"]) for r in registry if r.get("exact_s0")}
    cons_key_set = {r["conservative_key"] for r in registry if r.get("conservative_key")}

    # We need to process the stream
    manifest_out = "artifacts/research/cp_source_feasibility_2026_07/cp_root_population_manifest.jsonl.zst"
    Path(manifest_out).parent.mkdir(parents=True, exist_ok=True)

    records = []
    
    with open(corpus_path, "rb") as f:
        dctx = zstandard.ZstdDecompressor()
        with dctx.stream_reader(f) as reader:
            pgn = io.TextIOWrapper(reader, encoding="utf-8")
            count = 0
            while True:
                game = chess.pgn.read_game(pgn)
                if game is None:
                    break
                
                res = process_game(game)
                rec = {
                    "pgn_ordinal": count,
                    "game_url": game.headers.get("Site", ""),
                }
                if "error" in res:
                    rec["inclusion"] = "EXCLUDED"
                    rec["exclusion_reason"] = res["error"]
                else:
                    rec["inclusion"] = "CANDIDATE"
                    rec.update({
                        "declared_initial_fen": res["declared_initial_fen"],
                        "eligible_ply_count": res["eligible_ply_count"],
                        "selected_ply": res["selected_ply"],
                        "sufficient_position": res["sufficient_position"],
                        "root_identity": res["root_identity"],
                        "transposition_group": res["transposition_group"],
                        "history_identity": res["history_identity"],
                    })
                records.append(rec)
                count += 1
                if count % 1000 == 0:
                    print(f"Processed {count} games...")

    # Sort records by exact GameURL
    records.sort(key=lambda x: x["game_url"])

    # Deduplicate exact
    seen_identities = set()
    final_records = []
    for r in records:
        if r["inclusion"] != "CANDIDATE":
            final_records.append(r)
            continue
            
        root_id = r["root_identity"]
        if root_id in seen_identities:
            r["inclusion"] = "EXCLUDED"
            r["exclusion_reason"] = "DUPLICATE_S0_ROOT"
            r["duplicate_of_root_identity"] = root_id
            final_records.append(r)
            continue
            
        seen_identities.add(root_id)
        
        # Check exact overlap
        suff = r["sufficient_position"]
        suff_str = suff["board_arrangement_fen"] + suff["side_to_move"] + suff["castling_rights"] + str(suff["en_passant_square"])
        if suff_str in exact_s0_set:
            r["inclusion"] = "EXCLUDED"
            r["exclusion_reason"] = "PRIOR_DEVELOPMENT_EXACT_OVERLAP"
            final_records.append(r)
            continue
            
        # Check conservative overlap
        if r["transposition_group"] in cons_key_set:
            r["inclusion"] = "EXCLUDED"
            r["exclusion_reason"] = "PRIOR_DEVELOPMENT_TRANSPOSITION_OVERLAP"
            final_records.append(r)
            continue
            
        # If made it here, it's ADMITTED
        r["inclusion"] = "ADMITTED"
        final_records.append(r)

    # Write out to zst
    # Also record digest of manifest
    cctx = zstandard.ZstdCompressor()
    h_out = hashlib.sha256()
    
    with open(manifest_out, "wb") as f_out:
        with cctx.stream_writer(f_out) as writer:
            for r in final_records:
                line = json.dumps(r, sort_keys=True, separators=(",", ":")) + "\n"
                encoded = line.encode("utf-8")
                writer.write(encoded)
                h_out.update(encoded)
                
    manifest_digest = h_out.hexdigest()
    
    summary = {
        "manifest_schema": "CP_ROOT_POPULATION_JULY_2026_MANIFEST_V1",
        "corpus_identity": "lichess_db_broadcast_2026-07.pgn.zst",
        "upstream_published_checksum": expected_sha256,
        "local_observed_checksum": observed_sha256,
        "manifest_digest": manifest_digest,
        "total_pgn_count": count,
        "admitted_root_count": sum(1 for r in final_records if r["inclusion"] == "ADMITTED"),
        "exclusions": {
            "MISSING_CANONICAL_GAME_ID": sum(1 for r in final_records if r.get("exclusion_reason") == "MISSING_CANONICAL_GAME_ID"),
            "VARIANT_EXCLUDED": sum(1 for r in final_records if r.get("exclusion_reason") == "VARIANT_EXCLUDED"),
            "MALFORMED_INITIAL_STATE": sum(1 for r in final_records if r.get("exclusion_reason") == "MALFORMED_INITIAL_STATE"),
            "MALFORMED_REPLAY": sum(1 for r in final_records if r.get("exclusion_reason") == "MALFORMED_REPLAY"),
            "NO_RULE_ELIGIBLE_ROOT": sum(1 for r in final_records if r.get("exclusion_reason") == "NO_RULE_ELIGIBLE_ROOT"),
            "DUPLICATE_S0_ROOT": sum(1 for r in final_records if r.get("exclusion_reason") == "DUPLICATE_S0_ROOT"),
            "PRIOR_DEVELOPMENT_EXACT_OVERLAP": sum(1 for r in final_records if r.get("exclusion_reason") == "PRIOR_DEVELOPMENT_EXACT_OVERLAP"),
            "PRIOR_DEVELOPMENT_TRANSPOSITION_OVERLAP": sum(1 for r in final_records if r.get("exclusion_reason") == "PRIOR_DEVELOPMENT_TRANSPOSITION_OVERLAP"),
        }
    }
    
    out_sum = Path("docs/research/CP_ROOT_POPULATION_JULY_2026_MANIFEST.md")
    out_sum.parent.mkdir(parents=True, exist_ok=True)
    with open(out_sum, "w") as f:
        f.write("# CP Root Population July 2026 Manifest\n\n")
        f.write("```json\n")
        f.write(json.dumps(summary, indent=2))
        f.write("\n```\n")

    print(f"Admitted roots: {summary['admitted_root_count']}")

if __name__ == "__main__":
    main()
