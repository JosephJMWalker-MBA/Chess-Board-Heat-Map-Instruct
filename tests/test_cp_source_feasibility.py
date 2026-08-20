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
import subprocess

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

def make_valid_root(identity="r1", software_revision="REV", fen="rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"):
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

def create_fake_experiment_result(r1, manifest_digest="mock_manifest_digest", obs_mutator=None):
    spec = build_source_v2_spec(r1, manifest_digest, "Stockfish 18")
    board = chess.Board(r1["declared_initial_fen"])
    legal_ucis = [m.uci() for m in board.legal_moves]
    legal_ucis.sort()
    
    observations = []
    for uci in legal_ucis:
        observations.append({
            "root_move_uci": uci,
            "score_type": "cp",
            "score_value": 10,
            "depth": 24,
            "nodes": 50000,
            "time_ms": 100,
            "pv_ucis": [uci],
            "is_engine_mate": False,
            "bound": "exact"
        })
        
    if obs_mutator:
        observations = obs_mutator(observations)
        
    payload = {
        "spec_digest": spec.spec_digest(),
        "instrument_role": "SOURCE",
        "instrument_id": "CP_SOURCE_SF18_50K_ISOLATED_V1",
        "producer_uci_name": "Stockfish 18",
        "pre_spawn_sha256": "ae4c93fa9676ca7750d0714342fd8a5b1d018000fc6e0f6cedf112067b5ef374",
        "post_spawn_sha256": "ae4c93fa9676ca7750d0714342fd8a5b1d018000fc6e0f6cedf112067b5ef374",
        "observations": observations,
        "canonical_acquisition_order": [o["root_move_uci"] for o in observations] if observations else [],
        "options_surface": [{"name": "Hash", "value": "16"}]
    }
    return ExperimentResult.create(spec.spec_digest(), payload).model_dump()

def test_coverage_validation(tmp_path):
    r1 = make_valid_root("r1")
    manifest = tmp_path / "manifest.jsonl.zst"
    digest = write_mock_manifest(manifest, [r1])
    meta_path = tmp_path / "meta.json"
    meta_path.write_text(json.dumps(make_valid_meta(digest, count=1)))
    out_path = tmp_path / "out.jsonl"
    
    # Base success
    er = create_fake_experiment_result(r1, digest)
    rec = {
        "engine_session_epoch": 1,
        "instrument_id": "CP_SOURCE_SF18_50K_ISOLATED_V1",
        "manifest_digest": digest,
        "producer_binary_sha256": "ae4c93fa9676ca7750d0714342fd8a5b1d018000fc6e0f6cedf112067b5ef374",
        "producer_uci_name": "Stockfish 18",
        "root_identity": r1["root_identity"],
        "root_manifest_schema": "CP_ROOT_POPULATION_JULY_2026_MANIFEST_V2",
        "root_record_digest": r1["root_record_digest"],
        "schema": "CP_SOURCE_FEASIBILITY_RESULT_V2",
        "software_revision": "REV",
        "status": "SUCCESS",
        "experiment_result": er
    }
    out_path.write_text(json.dumps(rec, sort_keys=True, separators=(",", ":")) + "\n")
    
    from scripts.compute_coverage import main as cc_main
    import sys
    sys.argv = ["compute_coverage.py", "--manifest", str(manifest), "--output", str(out_path), "--meta", str(meta_path)]
    cc_main() # Should succeed
    
    # Negative test: invalid score type
    def mut1(obs):
        obs[0]["score_type"] = "invalid"
        return obs
    rec["experiment_result"] = create_fake_experiment_result(r1, digest, mut1)
    out_path.write_text(json.dumps(rec, sort_keys=True, separators=(",", ":")) + "\n")
    with pytest.raises(ValueError, match="Invalid score_type"):
        cc_main()
        
    # Negative test: length mismatch
    def mut2(obs):
        return obs[:-1]
    rec["experiment_result"] = create_fake_experiment_result(r1, digest, mut2)
    out_path.write_text(json.dumps(rec, sort_keys=True, separators=(",", ":")) + "\n")
    with pytest.raises(ValueError, match="Observations length != expected required_search_count"):
        cc_main()

def test_failure_durability_and_success_path(tmp_path, monkeypatch):
    r1 = make_valid_root("r1")
    r2 = make_valid_root("r2", fen="rnbqkbnr/pppppppp/8/8/4P3/8/PPPP1PPP/RNBQKBNR b KQkq e3 0 1")
    manifest = tmp_path / "manifest.jsonl.zst"
    digest = write_mock_manifest(manifest, [r1, r2])
    meta_path = tmp_path / "meta.json"
    meta_path.write_text(json.dumps(make_valid_meta(digest, count=2)))
    out_path = tmp_path / "out.jsonl"
    
    events = []
    
    class FakeSession:
        def __init__(self, stockfish_path, role):
            self.role = role
            self.started = False
            self.closed = False
            self._provenance = {
                "producer": "Stockfish 18",
                "pre_spawn_sha256": "ae4c93fa9676ca7750d0714342fd8a5b1d018000fc6e0f6cedf112067b5ef374",
                "post_spawn_sha256": "ae4c93fa9676ca7750d0714342fd8a5b1d018000fc6e0f6cedf112067b5ef374"
            }
            
        def start(self):
            events.append("start")
            self.started = True
            
        def close(self):
            events.append("close")
            self.closed = True
            
        def acquire(self, spec, board):
            FakeSession.acquire_count = getattr(FakeSession, "acquire_count", 0) + 1
            if FakeSession.acquire_count == 1:  # r1 fails
                events.append("acquire_fail")
                raise RuntimeError("Failed")
            events.append("acquire_success")
            
            payload = {
                "spec_digest": spec.spec_digest(),
                "instrument_role": "SOURCE",
                "instrument_id": "CP_SOURCE_SF18_50K_ISOLATED_V1",
                "producer_uci_name": "Stockfish 18",
                "pre_spawn_sha256": self._provenance["pre_spawn_sha256"],
                "post_spawn_sha256": self._provenance["post_spawn_sha256"],
                "observations": [],
                "canonical_acquisition_order": [],
                "options_surface": []
            }
            for uci in spec.candidate_policy["ordered_legal_root_ucis"]:
                payload["observations"].append({
                    "root_move_uci": uci,
                    "score_type": "cp",
                    "score_value": 0,
                    "depth": 24,
                    "nodes": 50000,
                    "time_ms": 100,
                    "pv_ucis": [uci],
                    "is_engine_mate": False,
                    "bound": "exact"
                })
                payload["canonical_acquisition_order"].append(uci)
            return ExperimentResult.create(spec.spec_digest(), payload)
            
    import chessheat.cp_source_feasibility
    monkeypatch.setattr(chessheat.cp_source_feasibility, "InstrumentSession", FakeSession)
    
    # Overwrite fsync to spy
    import os
    orig_fsync = os.fsync
    def fake_fsync(fd):
        events.append("fsync")
        orig_fsync(fd)
    monkeypatch.setattr(os, "fsync", fake_fsync)
    
    runner = SourceFeasibilityRunnerV2(str(manifest), str(out_path), "stockfish", str(meta_path))
    runner.run()
    
    assert events == [
        "start",
        "acquire_fail",
        "fsync",
        "close",
        "start",
        "acquire_success",
        "fsync",
        "close"
    ]
    
    # Verify exact resume prefix accepts the created output
    runner2 = SourceFeasibilityRunnerV2(str(manifest), str(out_path), "stockfish", str(meta_path))
    assert len(runner2.completed_roots) == 2

def test_manifest_mismatch(tmp_path):
    manifest = tmp_path / "manifest.jsonl.zst"
    digest = write_mock_manifest(manifest, [])
    meta_path = tmp_path / "meta.json"
    meta_path.write_text(json.dumps(make_valid_meta("WRONG", count=0)))
    with pytest.raises(ValueError, match="Manifest digest mismatch"):
        SourceFeasibilityRunnerV2(str(manifest), str(tmp_path / "out.jsonl"), "stockfish", str(meta_path))

def test_manifest_noncanonical(tmp_path):
    r1 = make_valid_root("r1")
    # write manually with spaces
    cctx = zstandard.ZstdCompressor()
    manifest = tmp_path / "manifest.jsonl.zst"
    with open(manifest, "wb") as f_out:
        with cctx.stream_writer(f_out) as writer:
            line = json.dumps(r1, sort_keys=True) + "\n" # Has spaces!
            writer.write(line.encode("utf-8"))
    
    # we don't care about the digest here as it will fail on parsing
    meta_path = tmp_path / "meta.json"
    meta_path.write_text(json.dumps(make_valid_meta("irrelevant", count=1)))
    with pytest.raises(ValueError, match="Non-canonical JSON line in manifest"):
        SourceFeasibilityRunnerV2(str(manifest), str(tmp_path / "out.jsonl"), "stockfish", str(meta_path))

