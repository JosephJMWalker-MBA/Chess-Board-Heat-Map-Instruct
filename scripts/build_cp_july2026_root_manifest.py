import zstandard
import chess.pgn
import io
import json
import hashlib
from typing import Dict, Any
from pathlib import Path
from chessheat.cp_root_population import (
    process_game, canonical_json_digest,
    ROOT_SELECTOR_VERSION, HISTORY_IDENTITY_VERSION, TRANSPOSITION_GROUP_VERSION,
    ROOT_MANIFEST_SCHEMA_V2, DUPLICATE_RESOLUTION_VERSION
)

def main():
    corpus_path = "data/external/lichess/broadcast/2026-07/lichess_db_broadcast_2026-07.pgn.zst"
    expected_sha256 = "714d0eb99f99fca8d791142038b6c59b5ca6a51b3339bd3891a92f4bdffcbf0c"

    h = hashlib.sha256()
    with open(corpus_path, "rb") as f:
        while chunk := f.read(8192):
            h.update(chunk)
    observed_sha256 = h.hexdigest()
    if observed_sha256 != expected_sha256:
        raise ValueError(f"Checksum mismatch! Expected {expected_sha256}, got {observed_sha256}")

    registry = []
    reg_path = Path("docs/research/CP_PRIOR_DEVELOPMENT_REGISTRY_V2.json")
    if reg_path.exists():
        with open(reg_path) as f:
            registry = json.load(f)
            
    exact_s0_set = {r["exact_s0_digest"] for r in registry if r.get("exact_s0_digest")}
    cons_key_set = {r["conservative_transposition_group"] for r in registry if r.get("conservative_transposition_group")}

    manifest_out = "artifacts/research/cp_source_feasibility_2026_07/cp_root_population_manifest_v2.jsonl.zst"
    Path(manifest_out).parent.mkdir(parents=True, exist_ok=True)

    records = []
    game_errors_count = 0
    game_url_present_count = 0
    
    with open(corpus_path, "rb") as f:
        dctx = zstandard.ZstdDecompressor()
        with dctx.stream_reader(f) as reader:
            pgn = io.TextIOWrapper(reader, encoding="utf-8")
            count = 0
            while True:
                game = chess.pgn.read_game(pgn)
                if game is None:
                    break
                    
                if game.errors:
                    game_errors_count += 1
                
                game_url = game.headers.get("GameURL", "").strip()
                if game_url and game_url != "?":
                    game_url_present_count += 1
                    
                res = process_game(game)
                
                rec = {
                    "manifest_schema": ROOT_MANIFEST_SCHEMA_V2,
                    "corpus_identity": "lichess_db_broadcast_2026-07.pgn.zst",
                    "corpus_month": "2026-07",
                    "upstream_filename": "lichess_db_broadcast_2026-07.pgn.zst",
                    "upstream_url": "https://database.lichess.org/broadcast/lichess_db_broadcast_2026-07.pgn.zst",
                    "upstream_published_checksum": expected_sha256,
                    "local_observed_checksum": observed_sha256,
                    "parser_identity": "python-chess",
                    "parser_version": chess.__version__,
                    "root_selector_version": ROOT_SELECTOR_VERSION,
                    "history_identity_version": HISTORY_IDENTITY_VERSION,
                    "duplicate_resolution_version": DUPLICATE_RESOLUTION_VERSION,
                    "transposition_group_version": TRANSPOSITION_GROUP_VERSION,
                    "software_revision": "V2_REPAIR",
                    "GameURL": game_url,
                    "Site": game.headers.get("Site", ""),
                    "pgn_ordinal": count,
                }
                
                if "error" in res:
                    rec["inclusion"] = "EXCLUDED"
                    rec["exclusion_reason"] = res["error"]
                else:
                    rec["inclusion"] = "CANDIDATE"
                    rec.update({
                        "declared_initial_fen": res["declared_initial_fen"],
                        "mainline_uci_prefix": res["mainline_uci_prefix"],
                        "eligible_ply_count": res["eligible_ply_count"],
                        "selected_ply": res["selected_ply"],
                        "sufficient_position": res["sufficient_position"],
                        "root_identity": res["root_identity"],
                        "transposition_group": res["transposition_group"],
                        "history_identity": res["history_identity"],
                    })
                records.append(rec)
                count += 1

    records.sort(key=lambda x: (x.get("GameURL", ""), x["pgn_ordinal"]))

    seen_identities = {}
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
            r["duplicate_of_game_url"] = seen_identities[root_id]
            final_records.append(r)
            continue
            
        seen_identities[root_id] = r["GameURL"]
        
        if root_id in exact_s0_set:
            r["inclusion"] = "EXCLUDED"
            r["exclusion_reason"] = "PRIOR_DEVELOPMENT_EXACT_OVERLAP"
            final_records.append(r)
            continue
            
        if r["transposition_group"] in cons_key_set:
            r["inclusion"] = "EXCLUDED"
            r["exclusion_reason"] = "PRIOR_DEVELOPMENT_TRANSPOSITION_OVERLAP"
            final_records.append(r)
            continue
            
        r["inclusion"] = "ADMITTED"
        
        # Calculate root_record_digest
        canonical = {k: v for k, v in r.items() if k != "root_record_digest"}
        r["root_record_digest"] = canonical_json_digest(canonical)
        
        final_records.append(r)

    # Re-sort to original PGN ordinal
    final_records.sort(key=lambda x: x["pgn_ordinal"])

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
    
    registry_digest = canonical_json_digest(registry) if registry else None
    
    summary = {
        "manifest_schema": ROOT_MANIFEST_SCHEMA_V2,
        "manifest_digest": manifest_digest,
        "registry_digest": registry_digest,
        "record_count": len(final_records),
        "admitted_root_count": sum(1 for r in final_records if r["inclusion"] == "ADMITTED"),
        "total_pgn_count": count,
        "game_errors_count": game_errors_count,
        "game_url_present_count": game_url_present_count,
        "software_revision": "V2_REPAIR",
        "corpus_checksum": observed_sha256,
        "parser_identity": "python-chess",
        "parser_version": chess.__version__,
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
    
    out_meta = Path("artifacts/research/cp_source_feasibility_2026_07/cp_root_population_manifest_v2.meta.json")
    with open(out_meta, "w") as f:
        json.dump(summary, f, indent=2)

    out_sum = Path("docs/research/CP_ROOT_POPULATION_JULY_2026_MANIFEST_V2.md")
    out_sum.parent.mkdir(parents=True, exist_ok=True)
    with open(out_sum, "w") as f:
        f.write("# CP Root Population July 2026 Manifest V2\n\n")
        f.write("```json\n")
        f.write(json.dumps(summary, indent=2))
        f.write("\n```\n")

if __name__ == "__main__":
    main()
