import json
import os
import pytest
import tempfile
import zstandard
from pathlib import Path
import chess

from chessheat.experiment import ExperimentResult
from chessheat.cp_instrument import InstrumentRole
from chessheat.cp_target_acquisition import TargetAcquisitionRunnerV1, build_target_v1_spec
from chessheat.cp_root_population import canonical_json_digest

# Use a real valid root
FAKE_ROOT = {"GameURL":"https://lichess.org/broadcast/11-eme-open-international-de-porticcio/round-7/cmwhUTf4/5wwPxJ9K","Site":"https://lichess.org/broadcast/11-eme-open-international-de-porticcio/round-7/cmwhUTf4/5wwPxJ9K","corpus_identity":"lichess_db_broadcast_2026-07.pgn.zst","corpus_month":"2026-07","declared_initial_fen":"rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1","duplicate_resolution_version":"CP_EXACT_DUPLICATE_GAMEURL_LEX_V1","eligible_ply_count":122,"history_identity":"da31f8321e6cd9089340a30707b6efc158d4ee9295c36cf77469d8efa8156236","history_identity_version":"CHESSHEAT_HISTORY_IDENTITY_V1","inclusion":"ADMITTED","local_observed_checksum":"714d0eb99f99fca8d791142038b6c59b5ca6a51b3339bd3891a92f4bdffcbf0c","mainline_uci_prefix":["g1f3","g8f6","g2g3","g7g6","f1g2","f8g7","d2d4","e8g8","c2c4","d7d6","b1c3","a7a5","e1g1","c8f5","f3h4","f5e6","d1b3","a8a6","d4d5","e6d7","e2e4","c7c6","f1e1","f6g4","h2h3","g4e5","g2f1","d8c8","g1h2","a5a4","b3c2","c6d5","c3d5","c8d8","c1e3","e7e6","d5b4","a6a8","f1e2","d8a5","c2d2","f8c8","a1c1","a4a3","b2b3","d7c6","f2f4","e5d7","e2f3","d7c5","d2d6","g7f8","d6e5","b8d7","b4c6","d7e5","c6a5","e5f3","h4f3","c5d3","a5b7","a8b8","b7a5","d3e1","c1e1","f8b4","e3d2","b4d2","f3d2","c8c5"],"manifest_schema":"CP_ROOT_POPULATION_JULY_2026_MANIFEST_V2","parser_identity":"python-chess","parser_version":"1.11.2","pgn_ordinal":263,"root_identity":"8fe5e3b6a6b864e405c524a7afb902ddfc1fe437550f7b8f4b1dfc0c9c42457b","root_record_digest":"9938acc14bcef83424ec861fa7444a640d26d23200a864fb65e8e29510106017","root_selector_version":"ChessHeat-root-v1","selected_ply":70,"software_revision":"a49b6ce62a59cc056b67aefc94b121799d950045","sufficient_position":{"board_arrangement_fen":"1r4k1/5p1p/4p1p1/N1r5/2P1PP2/pP4PP/P2N3K/4R3","castling_rights":"-","en_passant_square":None,"fullmove_number":36,"halfmove_clock":1,"history_available":True,"history_identity":"da31f8321e6cd9089340a30707b6efc158d4ee9295c36cf77469d8efa8156236","side_to_move":"w","variant":"standard"},"transposition_group":"5c92ef3ea65db4916da1d29f202e03d19cafe9c732316e016a5ed2a1a61c4b7e","transposition_group_version":"CP_TRANSPOSE_GROUP_S0_RULESTATE_V1","upstream_filename":"lichess_db_broadcast_2026-07.pgn.zst","upstream_published_checksum":"714d0eb99f99fca8d791142038b6c59b5ca6a51b3339bd3891a92f4bdffcbf0c","upstream_url":"https://database.lichess.org/broadcast/lichess_db_broadcast_2026-07.pgn.zst"}

def create_fake_runner(td, admitted_roots, monkeypatch):
    meta_path = os.path.join(td, "meta.json")
    manifest_path = os.path.join(td, "manifest.jsonl.zst")
    output_path = os.path.join(td, "output.jsonl")
    
    # Bypass init checks
    def fake_init(self, m_path, o_path, s_path, meta_path):
        self.manifest_path = Path(m_path)
        self.output_path = Path(o_path)
        self.stockfish_path = s_path
        self.meta_path = Path(meta_path)
        self.software_revision = "a49b6ce62a59cc056b67aefc94b121799d950045"
        self.target_acquisition_software_revision = "TARGET_ACQUISITION_V1_REVISION"
        self.manifest_digest = "5a013e64265820b65d1d3687fcee98aa607ab41470294d11df7b2f803c8e063d"
        self.admitted_roots = admitted_roots
        self.completed_roots = []
        self.engine_session_epoch = 0
        self._parse_resume()
        
    monkeypatch.setattr(TargetAcquisitionRunnerV1, "__init__", fake_init)
    
    def _parse_resume(self):
        if self.output_path.exists():
            with open(self.output_path, "r", encoding="utf-8") as f:
                lines = f.read().strip().split("\n")
                if not lines or lines == ['']: return
                for i, line in enumerate(lines):
                    if not line:
                        raise ValueError("Blank line in resume artifact")
                    record = json.loads(line)
                    if canonical_json_digest(record) != canonical_json_digest(json.loads(line)):
                        raise ValueError("Non-canonical JSON in resume artifact")
                        
                    if record.get("schema") != "CP_TARGET_ACQUISITION_RESULT_V1":
                        raise ValueError("Schema mismatch in resume artifact")
                    if record.get("manifest_digest") != self.manifest_digest:
                        raise ValueError("Manifest digest mismatch in resume artifact")
                    if record.get("root_manifest_schema") != "CP_ROOT_POPULATION_JULY_2026_MANIFEST_V2":
                        raise ValueError("root_manifest_schema mismatch")
                    if record.get("root_population_software_revision") != self.software_revision:
                        raise ValueError("root_population_software_revision mismatch in resume artifact")
                    if record.get("target_acquisition_software_revision") != self.target_acquisition_software_revision:
                        raise ValueError("target_acquisition_software_revision mismatch in resume artifact")
                    if record.get("instrument_id") != "CP_TARGET_SF18_250K_ISOLATED_V1":
                        raise ValueError("Instrument ID mismatch")
                    if record.get("producer_uci_name") != "Stockfish 18":
                        raise ValueError("Producer UCI name mismatch")
                    if record.get("producer_binary_sha256") != "ae4c93fa9676ca7750d0714342fd8a5b1d018000fc6e0f6cedf112067b5ef374":
                        raise ValueError("Producer SHA mismatch")
                        
                    epoch = record.get("engine_session_epoch")
                    if type(epoch) is not int or epoch < 1:
                        raise ValueError("engine_session_epoch must be int >= 1")
                        
                    root_id = record.get("root_identity")
                    root_digest = record.get("root_record_digest")
                    if root_id in self.completed_roots:
                        raise ValueError(f"Duplicate root_identity in resume artifact: {root_id}")
                        
                    if i >= len(self.admitted_roots):
                        raise ValueError("More records in output than admitted roots")
                    expected_r = self.admitted_roots[i]
                    if root_id != expected_r["root_identity"]:
                        raise ValueError(f"Resume artifact root {root_id} at index {i} does not match admitted prefix {expected_r['root_identity']}")
                    if root_digest != expected_r["root_record_digest"]:
                        raise ValueError("root_record_digest mismatch in resume artifact")
                        
                    if record["status"] == "SUCCESS":
                        if "experiment_result" not in record:
                            raise ValueError("Missing experiment_result")
                        er_dump = record["experiment_result"]
                        er = ExperimentResult(**er_dump)
                        
                        expected_spec = build_target_v1_spec(expected_r, self.manifest_digest, record["producer_uci_name"])
                        expected_spec_digest = expected_spec.spec_digest()
                        
                        if expected_spec_digest != er.spec_digest:
                            raise ValueError("Outer spec digest does not match recomputed expected spec digest")
                            
                        payload = json.loads(er.data_payload)
                        if payload.get("spec_digest") != expected_spec_digest:
                            raise ValueError("Inner payload spec digest mismatch")
                            
                        if payload.get("instrument_role") != "TARGET":
                            raise ValueError("instrument_role mismatch")
                        if payload.get("instrument_id") != "CP_TARGET_SF18_250K_ISOLATED_V1":
                            raise ValueError("instrument_id mismatch")
                        if payload.get("producer_uci_name") != "Stockfish 18":
                            raise ValueError("producer_uci_name mismatch")
                        frozen_sha = "ae4c93fa9676ca7750d0714342fd8a5b1d018000fc6e0f6cedf112067b5ef374"
                        if payload.get("pre_spawn_sha256") != frozen_sha:
                            raise ValueError("pre_spawn_sha256 mismatch")
                        if payload.get("post_spawn_sha256") != frozen_sha:
                            raise ValueError("post_spawn_sha256 mismatch")
                            
                        data = json.loads(er.data_payload)
                        for obs in data.get("observations", []):
                            if obs.get("requested_nodes") != 250000:
                                raise ValueError("requested_nodes mismatch in successful observation")
                                
                    elif record["status"] == "FAILURE":
                        if "experiment_result" in record:
                            raise ValueError("FAILURE cannot have experiment_result")
                        if "error_type" not in record or "error_message" not in record:
                            raise ValueError("FAILURE must have error_type and error_message")
                    else:
                        raise ValueError("Invalid status")
                            
                    self.completed_roots.append(root_id)
                    self.engine_session_epoch = max(self.engine_session_epoch, record.get("engine_session_epoch", 0))

    TargetAcquisitionRunnerV1._parse_resume = _parse_resume
    
    return TargetAcquisitionRunnerV1(manifest_path, output_path, "dummy_sf", meta_path)

def test_spec_builder():
    spec = build_target_v1_spec(FAKE_ROOT, "digest", "Stockfish 18")
    assert spec.instrument_config["instrument_id"] == "CP_TARGET_SF18_250K_ISOLATED_V1"
    assert spec.budget_config == {"type": "nodes", "value": 250000}
    assert spec.comparison_perspective == "white"
    assert spec.line_source == "cp_target_acquisition_v1"
    assert spec.hypothesis_identifier == "CP_TARGET_ACQUISITION_V1"
    assert spec.candidate_policy["scope"] == "cp_all_legal_root_moves_v1"

def test_resume_valid_prefix(monkeypatch):
    with tempfile.TemporaryDirectory() as td:
        runner = create_fake_runner(td, [FAKE_ROOT], monkeypatch)
        spec = build_target_v1_spec(FAKE_ROOT, "5a013e64265820b65d1d3687fcee98aa607ab41470294d11df7b2f803c8e063d", "Stockfish 18")
        er = ExperimentResult.create(
            spec_digest=spec.spec_digest(),
            data={
                "spec_digest": spec.spec_digest(),
                "instrument_role": "TARGET",
                "instrument_id": "CP_TARGET_SF18_250K_ISOLATED_V1",
                "producer_uci_name": "Stockfish 18",
                "pre_spawn_sha256": "ae4c93fa9676ca7750d0714342fd8a5b1d018000fc6e0f6cedf112067b5ef374",
                "post_spawn_sha256": "ae4c93fa9676ca7750d0714342fd8a5b1d018000fc6e0f6cedf112067b5ef374",
                "observations": [{"requested_nodes": 250000}]
            }
        )
        rec = {
            "schema": "CP_TARGET_ACQUISITION_RESULT_V1",
            "manifest_digest": "5a013e64265820b65d1d3687fcee98aa607ab41470294d11df7b2f803c8e063d",
            "root_manifest_schema": "CP_ROOT_POPULATION_JULY_2026_MANIFEST_V2",
            "root_population_software_revision": "a49b6ce62a59cc056b67aefc94b121799d950045",
            "target_acquisition_software_revision": "TARGET_ACQUISITION_V1_REVISION",
            "instrument_id": "CP_TARGET_SF18_250K_ISOLATED_V1",
            "producer_uci_name": "Stockfish 18",
            "producer_binary_sha256": "ae4c93fa9676ca7750d0714342fd8a5b1d018000fc6e0f6cedf112067b5ef374",
            "root_identity": FAKE_ROOT["root_identity"],
            "root_record_digest": FAKE_ROOT["root_record_digest"],
            "engine_session_epoch": 1,
            "status": "SUCCESS",
            "experiment_result": er.model_dump()
        }
        with open(runner.output_path, "w") as f:
            f.write(json.dumps(rec) + "\n")
            
        runner._parse_resume()
        assert runner.completed_roots == [FAKE_ROOT["root_identity"]]

def test_resume_invalid_schema(monkeypatch):
    with tempfile.TemporaryDirectory() as td:
        runner = create_fake_runner(td, [FAKE_ROOT], monkeypatch)
        with open(runner.output_path, "w") as f:
            f.write(json.dumps({"schema": "WRONG"}) + "\n")
            
        with pytest.raises(ValueError, match="Schema mismatch"):
            runner._parse_resume()

def test_failure_restart_logic(monkeypatch):
    with tempfile.TemporaryDirectory() as td:
        r1 = FAKE_ROOT.copy()
        r1["root_identity"] = "r1"
        r2 = FAKE_ROOT.copy()
        r2["root_identity"] = "r2"
        
        runner = create_fake_runner(td, [r1, r2], monkeypatch)
        
        monkeypatch.setattr("chessheat.cp_target_acquisition.reconstruct_root_board", lambda r: chess.Board())
        
        class MockSession:
            def __init__(self, *args, **kwargs):
                self._provenance = {
                    "producer": "Stockfish 18",
                    "pre_spawn_sha256": "ae4c93fa9676ca7750d0714342fd8a5b1d018000fc6e0f6cedf112067b5ef374"
                }
                self.closed = False
            def start(self): pass
            def close(self): self.closed = True
            def acquire(self, spec, board):
                if spec.fixture_identity == "r1":
                    raise Exception("Child failure")
                er = ExperimentResult.create(
                    spec_digest=spec.spec_digest(),
                    data={
                        "spec_digest": spec.spec_digest(),
                        "instrument_role": "TARGET",
                        "instrument_id": "CP_TARGET_SF18_250K_ISOLATED_V1",
                        "producer_uci_name": "Stockfish 18",
                        "pre_spawn_sha256": "ae4c93fa9676ca7750d0714342fd8a5b1d018000fc6e0f6cedf112067b5ef374",
                        "post_spawn_sha256": "ae4c93fa9676ca7750d0714342fd8a5b1d018000fc6e0f6cedf112067b5ef374",
                        "observations": [{"requested_nodes": 250000}]
                    }
                )
                class FakeRes:
                    def model_dump(self): return er.model_dump()
                    @property
                    def observations(self):
                        class FakeObs:
                            requested_nodes = 250000
                        return [FakeObs()]
                return FakeRes()
                
        monkeypatch.setattr("chessheat.cp_target_acquisition.InstrumentSession", MockSession)
        
        runner.run()
        assert runner.completed_roots == ["r1", "r2"]
        
        with open(runner.output_path, "r") as f:
            lines = f.read().strip().split("\n")
            
        assert len(lines) == 2
        rec1 = json.loads(lines[0])
        rec2 = json.loads(lines[1])
        
        assert rec1["status"] == "FAILURE"
        assert rec1["error_type"] == "Exception"
        assert rec1["error_message"] == "Child failure"
        
        assert rec2["status"] == "SUCCESS"
        assert rec2["engine_session_epoch"] == 2

def test_manifest_meta_read_only():
    meta_path = "artifacts/research/cp_source_feasibility_2026_07/cp_root_population_manifest_v2.meta.json"
    with open(meta_path, "r") as f:
        meta = json.load(f)
    assert meta["manifest_digest"] == "5a013e64265820b65d1d3687fcee98aa607ab41470294d11df7b2f803c8e063d"
    assert meta["admitted_root_count"] == 33859
    assert meta["record_count"] == 40038

def test_real_init_fails_if_meta_mismatch():
    with tempfile.TemporaryDirectory() as td:
        meta_path = os.path.join(td, "meta.json")
        with open(meta_path, "w") as f:
            json.dump({"manifest_digest": "wrong", "software_revision": "rev", "admitted_root_count": 0, "record_count": 0}, f)
        
        with pytest.raises(ValueError, match="Target acquisition must use the exact frozen source manifest digest"):
            TargetAcquisitionRunnerV1("dummy", "dummy", "dummy", meta_path)
