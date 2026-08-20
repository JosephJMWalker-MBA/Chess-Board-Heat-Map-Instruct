import pytest
from chessheat.cp_source_feasibility import SourceFeasibilityRunner
import os
import json
import zstandard
from pathlib import Path

def test_source_feasibility_init(tmp_path):
    manifest_path = tmp_path / "manifest.jsonl.zst"
    output_path = tmp_path / "out.jsonl.zst"
    
    # write dummy manifest
    cctx = zstandard.ZstdCompressor()
    with open(manifest_path, "wb") as f:
        with cctx.stream_writer(f) as w:
            w.write(b"")
            
    runner = SourceFeasibilityRunner(str(manifest_path), str(output_path), "stockfish")
    assert len(runner.completed_roots) == 0

def test_source_feasibility_resumes(tmp_path):
    manifest_path = tmp_path / "manifest.jsonl.zst"
    output_path = tmp_path / "out.jsonl.zst"
    
    cctx = zstandard.ZstdCompressor()
    with open(output_path, "wb") as f:
        with cctx.stream_writer(f) as w:
            rec = {"status": "SUCCESS", "root_identity": "abc"}
            w.write((json.dumps(rec) + "\n").encode("utf-8"))
            
    runner = SourceFeasibilityRunner(str(manifest_path), str(output_path), "stockfish")
    assert "abc" in runner.completed_roots
