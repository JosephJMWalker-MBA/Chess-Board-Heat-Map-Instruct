import json
import io
import os
import zstandard
from pathlib import Path
from typing import Dict, Any
import chess
from chessheat.cp_instrument import InstrumentSession, InstrumentRole, ProtocolError, get_canonical_instrument_config
from chessheat.experiment import ExperimentSpec, ExperimentResult
from chessheat.semantics import SemanticSignatureV1
from chessheat.cp_root_population import reconstruct_root_board, canonical_json_digest

class SourceFeasibilityRunnerV2:
    def __init__(self, manifest_path: str, output_path: str, stockfish_path: str, meta_path: str):
        self.manifest_path = Path(manifest_path)
        self.output_path = Path(output_path)
        self.stockfish_path = stockfish_path
        self.meta_path = Path(meta_path)
        
        self.completed_roots = set()
        self.engine_session_epoch = 0
        
        with open(self.meta_path) as f:
            self.meta = json.load(f)
            
        self.manifest_digest = self.meta["manifest_digest"]
        self.software_revision = self.meta["software_revision"]
        
        if self.output_path.exists():
            with open(self.output_path, "r", encoding="utf-8") as f:
                for line in f:
                    if not line.strip(): continue
                    try:
                        record = json.loads(line)
                    except json.JSONDecodeError:
                        raise ValueError("Malformed JSON in resume artifact")
                        
                    if record.get("schema") != "CP_SOURCE_FEASIBILITY_RESULT_V2":
                        raise ValueError("Schema mismatch in resume artifact")
                    if record.get("manifest_digest") != self.manifest_digest:
                        raise ValueError("Manifest digest mismatch in resume artifact")
                    if record.get("software_revision") != self.software_revision:
                        raise ValueError("Software revision mismatch in resume artifact")
                    if record.get("instrument_id") != "CP_SOURCE_SF18_50K_ISOLATED_V1":
                        raise ValueError("Instrument ID mismatch")
                    if record.get("producer_binary_sha256") != "ae4c93fa9676ca7750d0714342fd8a5b1d018000fc6e0f6cedf112067b5ef374":
                        raise ValueError("Producer SHA mismatch")
                        
                    root_id = record["root_identity"]
                    if root_id in self.completed_roots:
                        raise ValueError(f"Duplicate root_identity in resume artifact: {root_id}")
                        
                    if record["status"] == "SUCCESS":
                        er_dump = record["experiment_result"]
                        er = ExperimentResult(**er_dump)
                        er.verify_artifact_digest()
                        
                        expected_outer_spec = record["experiment_result"]["spec_digest"]
                        if expected_outer_spec != er.spec_digest:
                            raise ValueError("Spec digest mismatch")
                            
                        payload = json.loads(er.data_payload)
                        if payload["instrument_role"] != "SOURCE" or payload["instrument_id"] != "CP_SOURCE_SF18_50K_ISOLATED_V1" or payload["pre_spawn_sha256"] != "ae4c93fa9676ca7750d0714342fd8a5b1d018000fc6e0f6cedf112067b5ef374":
                            raise ValueError("Payload mismatches in resume artifact")
                            
                    self.completed_roots.add(root_id)

    def run(self):
        manifest_records = []
        with open(self.manifest_path, "rb") as f:
            dctx = zstandard.ZstdDecompressor()
            with dctx.stream_reader(f) as reader:
                for line in io.TextIOWrapper(reader, encoding="utf-8"):
                    if not line.strip(): continue
                    manifest_records.append(json.loads(line))
        
        admitted = [r for r in manifest_records if r.get("inclusion") == "ADMITTED"]
        
        # Check prefix match for completed
        for i, r in enumerate(admitted):
            if i < len(self.completed_roots):
                if r["root_identity"] not in self.completed_roots:
                    raise ValueError("Resume artifact roots do not form the exact canonical PREFIX of admitted manifest roots")
                    
        self.output_path.parent.mkdir(parents=True, exist_ok=True)
        f_out = open(self.output_path, "a", encoding="utf-8")
        
        session = None
        
        def start_session():
            nonlocal session
            if session:
                session.close()
            session = InstrumentSession(self.stockfish_path, InstrumentRole.SOURCE)
            session.start()
            self.engine_session_epoch += 1

        start_session()
        
        try:
            for r in admitted:
                root_id = r["root_identity"]
                if root_id in self.completed_roots:
                    continue
                    
                # Reconstruct and verify
                try:
                    board = reconstruct_root_board(r)
                except Exception as e:
                    raise ValueError(f"Root reconstruction failed: {e}")
                    
                if len(board.move_stack) != r["selected_ply"]:
                    raise ValueError("move_stack length doesn't match selected_ply")
                
                sorted_moves = sorted(list(board.legal_moves), key=lambda m: m.uci())
                sorted_ucis = [m.uci() for m in sorted_moves]
                expected_policy = {
                    "scope": "cp_all_legal_root_moves_v1",
                    "ordered_legal_root_ucis": sorted_ucis,
                    "required_search_count": len(sorted_ucis)
                }
                
                canonical_sig = SemanticSignatureV1.create_canonical()
                spec = ExperimentSpec(
                    semantic_signature_version=canonical_sig.version,
                    semantic_signature_digest=canonical_sig.digest(),
                    suite_identity="CP_ROOT_POPULATION_LICHESS_BROADCAST_2026_07_V2",
                    suite_digest=self.manifest_digest,
                    fixture_identity=r["root_identity"],
                    fixture_digest=r["root_record_digest"],
                    sufficient_position=r["sufficient_position"],
                    candidate_policy=expected_policy,
                    producer_identity=session._provenance["producer"],
                    instrument_config=get_canonical_instrument_config(InstrumentRole.SOURCE),
                    budget_config={"type": "nodes", "value": 50000},
                    line_source="cp_source_feasibility_v2",
                    hypothesis_identifier="CP_SOURCE_FEASIBILITY_COVERAGE_V2",
                    spec_version=2,
                    comparison_perspective="white" if r["sufficient_position"]["side_to_move"] == "w" else "black"
                )
                
                try:
                    result = session.acquire(spec, board)
                    rec = {
                        "schema": "CP_SOURCE_FEASIBILITY_RESULT_V2",
                        "manifest_digest": self.manifest_digest,
                        "root_manifest_schema": r["manifest_schema"],
                        "software_revision": self.software_revision,
                        "instrument_id": "CP_SOURCE_SF18_50K_ISOLATED_V1",
                        "producer_uci_name": session._provenance["producer"],
                        "producer_binary_sha256": session._provenance["pre_spawn_sha256"],
                        "root_identity": root_id,
                        "root_record_digest": r["root_record_digest"],
                        "engine_session_epoch": self.engine_session_epoch,
                        "status": "SUCCESS",
                        "experiment_result": result.model_dump()
                    }
                except Exception as e:
                    rec = {
                        "schema": "CP_SOURCE_FEASIBILITY_RESULT_V2",
                        "manifest_digest": self.manifest_digest,
                        "root_manifest_schema": r["manifest_schema"],
                        "software_revision": self.software_revision,
                        "instrument_id": "CP_SOURCE_SF18_50K_ISOLATED_V1",
                        "producer_uci_name": session._provenance["producer"] if session else "UNKNOWN",
                        "producer_binary_sha256": session._provenance["pre_spawn_sha256"] if session else "UNKNOWN",
                        "root_identity": root_id,
                        "root_record_digest": r["root_record_digest"],
                        "engine_session_epoch": self.engine_session_epoch,
                        "status": "FAILURE",
                        "error_type": type(e).__name__,
                        "error_message": str(e)
                    }
                    start_session()
                    
                line = json.dumps(rec, separators=(",", ":")) + "\n"
                f_out.write(line)
                f_out.flush()
                os.fsync(f_out.fileno())
                self.completed_roots.add(root_id)
                
        finally:
            if session:
                session.close()
            f_out.close()
