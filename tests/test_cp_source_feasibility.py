import pytest
import json
import zstandard
from pathlib import Path
from chessheat.cp_source_feasibility import SourceFeasibilityRunnerV2

def write_mock_manifest(path, records):
    import hashlib
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

def test_resume_corrupt(tmp_path):
    manifest = tmp_path / "manifest.jsonl.zst"
    digest = write_mock_manifest(manifest, [])
    
    out_path = tmp_path / "out.jsonl"
    out_path.write_text("{bad json\n")
    
    meta_path = tmp_path / "meta.json"
    meta_path.write_text(json.dumps({
        "software_revision": "V2_REPAIR"
    }))
    
    with pytest.raises(ValueError, match="Malformed JSON"):
        SourceFeasibilityRunnerV2(str(manifest), str(out_path), "stockfish", str(meta_path))

def test_resume_schema_mismatch(tmp_path):
    manifest = tmp_path / "manifest.jsonl.zst"
    digest = write_mock_manifest(manifest, [])
    
    out_path = tmp_path / "out.jsonl"
    out_path.write_text(json.dumps({"schema": "WRONG"}) + "\n")
    
    meta_path = tmp_path / "meta.json"
    meta_path.write_text(json.dumps({
        "software_revision": "V2_REPAIR"
    }))
    
    with pytest.raises(ValueError, match="Schema mismatch"):
        SourceFeasibilityRunnerV2(str(manifest), str(out_path), "stockfish", str(meta_path))

def test_resume_duplicate_root(tmp_path):
    manifest = tmp_path / "manifest.jsonl.zst"
    digest = write_mock_manifest(manifest, [{"inclusion": "ADMITTED", "root_identity": "r1"}])
    
    rec = {
        "schema": "CP_SOURCE_FEASIBILITY_RESULT_V2",
        "manifest_digest": digest,
        "software_revision": "V2_REPAIR",
        "instrument_id": "CP_SOURCE_SF18_50K_ISOLATED_V1",
        "producer_binary_sha256": "ae4c93fa9676ca7750d0714342fd8a5b1d018000fc6e0f6cedf112067b5ef374",
        "root_identity": "r1",
        "status": "FAILURE"
    }
    out_path = tmp_path / "out.jsonl"
    out_path.write_text(json.dumps(rec) + "\n" + json.dumps(rec) + "\n")
    
    meta_path = tmp_path / "meta.json"
    meta_path.write_text(json.dumps({
        "software_revision": "V2_REPAIR"
    }))
    
    with pytest.raises(ValueError, match="Duplicate root_identity"):
        SourceFeasibilityRunnerV2(str(manifest), str(out_path), "stockfish", str(meta_path))

def test_resume_non_prefix(tmp_path):
    manifest = tmp_path / "manifest.jsonl.zst"
    digest = write_mock_manifest(manifest, [
        {"inclusion": "ADMITTED", "root_identity": "r1"},
        {"inclusion": "ADMITTED", "root_identity": "r2"}
    ])
    
    rec = {
        "schema": "CP_SOURCE_FEASIBILITY_RESULT_V2",
        "manifest_digest": digest,
        "software_revision": "V2_REPAIR",
        "instrument_id": "CP_SOURCE_SF18_50K_ISOLATED_V1",
        "producer_binary_sha256": "ae4c93fa9676ca7750d0714342fd8a5b1d018000fc6e0f6cedf112067b5ef374",
        "root_identity": "r2",  # Should be r1 first!
        "status": "FAILURE"
    }
    out_path = tmp_path / "out.jsonl"
    out_path.write_text(json.dumps(rec) + "\n")
    
    meta_path = tmp_path / "meta.json"
    meta_path.write_text(json.dumps({
        "software_revision": "V2_REPAIR"
    }))
    
    with pytest.raises(ValueError, match="does not match admitted prefix"):
        SourceFeasibilityRunnerV2(str(manifest), str(out_path), "stockfish", str(meta_path))
