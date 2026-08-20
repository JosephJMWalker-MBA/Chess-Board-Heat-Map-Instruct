import pytest
import json
import zstandard
import hashlib
from pathlib import Path
import chess
from chessheat.cp_source_feasibility import SourceFeasibilityRunnerV2, build_source_v2_spec
from chessheat.cp_root_population import canonical_json_digest, get_history_identity
from chessheat.semantics import SufficientPosition
from chessheat.experiment import ExperimentResult

def write_mock_manifest(path, records):
    h_out = hashlib.sha256()
    with open(path, "wb") as f_out:
        cctx = zstandard.ZstdCompressor()
        with cctx.stream_writer(f_out) as writer:
            for r in records:
                line = json.dumps(r, sort_keys=True, separators=(",", ":")) + "\n"
                encoded = line.encode("utf-8")
                writer.write(encoded)
                h_out.update(encoded)
    return h_out.hexdigest()

def make_valid_root(identity="r1", software_revision="REV", digest="d1", fen="rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"):
    hist_id = get_history_identity(fen, [])
    
    board = chess.Board(fen)
    suff = SufficientPosition(
        board_arrangement_fen=board.board_fen(),
        side_to_move="w" if board.turn == chess.WHITE else "b",
        castling_rights=board.castling_xfen(),
        en_passant_square=chess.square_name(board.ep_square) if board.ep_square is not None else None,
        halfmove_clock=board.halfmove_clock,
        fullmove_number=board.fullmove_number,
        history_available=True,
        history_identity=hist_id,
        variant="standard"
    )
    actual_identity = canonical_json_digest(suff.model_dump())
    
    rec = {
        "manifest_schema": "CP_ROOT_POPULATION_JULY_2026_MANIFEST_V2",
        "software_revision": software_revision,
        "inclusion": "ADMITTED",
        "root_identity": actual_identity,
        "sufficient_position": suff.model_dump(),
        "selected_ply": 0,
        "declared_initial_fen": fen,
        "mainline_uci_prefix": [],
        "history_identity": hist_id,
        "transposition_group": "tg1"
    }
    canonical = {k: v for k, v in rec.items() if k != "root_record_digest"}
    rec["root_record_digest"] = canonical_json_digest(canonical)
    return rec

def make_valid_meta(digest, count=1, software_revision="REV"):
    return {
        "manifest_schema": "CP_ROOT_POPULATION_JULY_2026_MANIFEST_V2",
        "manifest_digest": digest,
        "software_revision": software_revision,
        "record_count": count,
        "admitted_root_count": count
    }

def test_resume_corrupt(tmp_path):
    manifest = tmp_path / "manifest.jsonl.zst"
    digest = write_mock_manifest(manifest, [])
    
    out_path = tmp_path / "out.jsonl"
    out_path.write_text("{bad json\n")
    
    meta_path = tmp_path / "meta.json"
    meta_path.write_text(json.dumps(make_valid_meta(digest, count=0)))
    
    with pytest.raises(ValueError, match="Malformed JSON"):
        SourceFeasibilityRunnerV2(str(manifest), str(out_path), "stockfish", str(meta_path))

def test_resume_schema_mismatch(tmp_path):
    manifest = tmp_path / "manifest.jsonl.zst"
    digest = write_mock_manifest(manifest, [])
    
    out_path = tmp_path / "out.jsonl"
    out_path.write_text(json.dumps({"schema": "WRONG"}) + "\n")
    
    meta_path = tmp_path / "meta.json"
    meta_path.write_text(json.dumps(make_valid_meta(digest, count=0)))
    
    with pytest.raises(ValueError, match="Non-canonical JSON"):
        SourceFeasibilityRunnerV2(str(manifest), str(out_path), "stockfish", str(meta_path))

def test_resume_duplicate_root(tmp_path):
    r1 = make_valid_root(identity="r1")
    
    manifest = tmp_path / "manifest.jsonl.zst"
    digest = write_mock_manifest(manifest, [r1])
    
    rec = {
        "engine_session_epoch": 1,
        "error_message": "foo",
        "error_type": "ValueError",
        "instrument_id": "CP_SOURCE_SF18_50K_ISOLATED_V1",
        "manifest_digest": digest,
        "producer_binary_sha256": "ae4c93fa9676ca7750d0714342fd8a5b1d018000fc6e0f6cedf112067b5ef374",
        "producer_uci_name": "Stockfish 18",
        "root_identity": r1["root_identity"],
        "root_manifest_schema": "CP_ROOT_POPULATION_JULY_2026_MANIFEST_V2",
        "root_record_digest": r1["root_record_digest"],
        "schema": "CP_SOURCE_FEASIBILITY_RESULT_V2",
        "software_revision": "REV",
        "status": "FAILURE"
    }
    
    out_path = tmp_path / "out.jsonl"
    line = json.dumps(rec, sort_keys=True, separators=(",", ":"))
    out_path.write_text(line + "\n" + line + "\n")
    
    meta_path = tmp_path / "meta.json"
    meta_path.write_text(json.dumps(make_valid_meta(digest)))
    
    with pytest.raises(ValueError, match="Duplicate root_identity"):
        SourceFeasibilityRunnerV2(str(manifest), str(out_path), "stockfish", str(meta_path))

def test_resume_non_prefix(tmp_path):
    r1 = make_valid_root("r1")
    r2 = make_valid_root("r2", fen="rnbqkbnr/pppppppp/8/8/4P3/8/PPPP1PPP/RNBQKBNR b KQkq e3 0 1")
    
    manifest = tmp_path / "manifest.jsonl.zst"
    digest = write_mock_manifest(manifest, [r1, r2])
    
    rec = {
        "engine_session_epoch": 1,
        "error_message": "foo",
        "error_type": "ValueError",
        "instrument_id": "CP_SOURCE_SF18_50K_ISOLATED_V1",
        "manifest_digest": digest,
        "producer_binary_sha256": "ae4c93fa9676ca7750d0714342fd8a5b1d018000fc6e0f6cedf112067b5ef374",
        "producer_uci_name": "Stockfish 18",
        "root_identity": r2["root_identity"],  # Should be r1 first!
        "root_manifest_schema": "CP_ROOT_POPULATION_JULY_2026_MANIFEST_V2",
        "root_record_digest": r2["root_record_digest"],
        "schema": "CP_SOURCE_FEASIBILITY_RESULT_V2",
        "software_revision": "REV",
        "status": "FAILURE"
    }
    
    out_path = tmp_path / "out.jsonl"
    out_path.write_text(json.dumps(rec, sort_keys=True, separators=(",", ":")) + "\n")
    
    meta_path = tmp_path / "meta.json"
    meta_path.write_text(json.dumps(make_valid_meta(digest, count=2)))
    
    with pytest.raises(ValueError, match="does not match admitted prefix"):
        SourceFeasibilityRunnerV2(str(manifest), str(out_path), "stockfish", str(meta_path))

def test_build_source_v2_spec():
    r1 = make_valid_root("r1")
    spec = build_source_v2_spec(r1, "mock_manifest_digest", "mock_producer")
    assert spec.spec_version == 2
    assert spec.hypothesis_identifier == "CP_SOURCE_FEASIBILITY_COVERAGE_V2"
    assert spec.suite_digest == "mock_manifest_digest"
    assert spec.producer_identity == "mock_producer"

def test_coverage_validation():
    from scripts.compute_coverage import validate_and_extract_coverage
    
    # Missing required counts
    with pytest.raises(Exception):
         validate_and_extract_coverage({"status": "SUCCESS", "experiment_result": {"data_payload": json.dumps({"observations": [], "candidate_policy": {"required_search_count": 1}})}})
         
    # Non-cp/mate type
    with pytest.raises(Exception):
         validate_and_extract_coverage({"status": "SUCCESS", "experiment_result": {"data_payload": json.dumps({"observations": [{"score_type": "eval"}], "candidate_policy": {"required_search_count": 1}})}})
