import json
import io
import os
import zstandard
import hashlib
from pathlib import Path
from typing import Dict, Any, List
import chess
from chessheat.cp_instrument import InstrumentSession, InstrumentRole, ProtocolError, get_canonical_instrument_config
from chessheat.experiment import ExperimentSpec, ExperimentResult
from chessheat.semantics import SemanticSignatureV1
from chessheat.cp_root_population import reconstruct_root_board, canonical_json_digest

def build_source_v2_spec(root_record: Dict[str, Any], manifest_digest: str, producer: str) -> ExperimentSpec:
    board = reconstruct_root_board(root_record)
    sorted_moves = sorted(list(board.legal_moves), key=lambda m: m.uci())
    sorted_ucis = [m.uci() for m in sorted_moves]
    expected_policy = {
        "scope": "cp_all_legal_root_moves_v1",
        "ordered_legal_root_ucis": sorted_ucis,
        "required_search_count": len(sorted_ucis)
    }
    canonical_sig = SemanticSignatureV1.create_canonical()
    
    return ExperimentSpec(
        semantic_signature_version=canonical_sig.version,
        semantic_signature_digest=canonical_sig.signature_hash(),
        suite_identity="CP_ROOT_POPULATION_LICHESS_BROADCAST_2026_07_V2",
        suite_digest=manifest_digest,
        fixture_identity=root_record["root_identity"],
        fixture_digest=root_record["root_record_digest"],
        sufficient_position=root_record["sufficient_position"],
        candidate_policy=expected_policy,
        producer_identity=producer,
        instrument_config=get_canonical_instrument_config(InstrumentRole.SOURCE),
        budget_config={"type": "nodes", "value": 50000},
        line_source="cp_source_feasibility_v2",
        hypothesis_identifier="CP_SOURCE_FEASIBILITY_COVERAGE_V2",
        spec_version=2,
        comparison_perspective="white" if root_record["sufficient_position"]["side_to_move"] == "w" else "black"
    )

class SourceFeasibilityRunnerV2:
    def __init__(self, manifest_path: str, output_path: str, stockfish_path: str, meta_path: str):
        self.manifest_path = Path(manifest_path)
        self.output_path = Path(output_path)
        self.stockfish_path = stockfish_path
        self.meta_path = Path(meta_path)
        
        with open(self.meta_path) as f:
            self.meta = json.load(f)
            
        self.software_revision = self.meta["software_revision"]
        
        manifest_records = []
        h_manifest = hashlib.sha256()
        with open(self.manifest_path, "rb") as f:
            dctx = zstandard.ZstdDecompressor()
            with dctx.stream_reader(f) as reader:
                for line in io.TextIOWrapper(reader, encoding="utf-8"):
                    if not line.strip(): continue
                    encoded = line.encode("utf-8")
                    h_manifest.update(encoded)
                    rec = json.loads(line)
                    if json.dumps(rec, sort_keys=True, separators=(",", ":")) != json.loads(line, object_pairs_hook=lambda x: json.dumps(dict(x), sort_keys=True, separators=(",", ":"))):
                         pass
                    
                    if rec["software_revision"] != self.software_revision:
                         raise ValueError("Record software revision mismatch")
                    manifest_records.append(rec)
        
        self.manifest_digest = h_manifest.hexdigest()
        
        if self.manifest_digest != self.meta["manifest_digest"]:
             raise ValueError("Manifest digest mismatch")
        if self.meta["manifest_schema"] != "CP_ROOT_POPULATION_JULY_2026_MANIFEST_V2":
             raise ValueError("Meta schema mismatch")
        if self.meta["record_count"] != len(manifest_records):
             raise ValueError("Record count mismatch")
             
        self.manifest_records = manifest_records
        
        admitted = []
        seen_roots = set()
        for r in manifest_records:
             if r["manifest_schema"] != "CP_ROOT_POPULATION_JULY_2026_MANIFEST_V2":
                 raise ValueError("Record schema mismatch")
             if r.get("inclusion") == "ADMITTED":
                 if r["root_identity"] in seen_roots:
                     raise ValueError("Duplicate admitted roots")
                 seen_roots.add(r["root_identity"])
                 
                 canonical = {k: v for k, v in r.items() if k != "root_record_digest"}
                 if r["root_record_digest"] != canonical_json_digest(canonical):
                     raise ValueError("root_record_digest equality failure")
                 if "sufficient_position" not in r or "selected_ply" not in r:
                     raise ValueError("Missing reconstruction fields")
                     
                 admitted.append(r)
                 
        if len(admitted) != self.meta["admitted_root_count"]:
            raise ValueError("Admitted count mismatch")
            
        self.admitted_roots = admitted
        self.completed_roots = []
        self.engine_session_epoch = 0
        
        if self.output_path.exists():
            with open(self.output_path, "r", encoding="utf-8") as f:
                for i, line in enumerate(f):
                    if not line.strip(): continue
                    try:
                        record = json.loads(line)
                    except json.JSONDecodeError:
                        raise ValueError("Malformed JSON in resume artifact")
                        
                    canon_line = json.dumps(record, sort_keys=True, separators=(",", ":"))
                    if canon_line != line.strip():
                        raise ValueError("Non-canonical JSON line in resume artifact")
                        
                    if record.get("schema") != "CP_SOURCE_FEASIBILITY_RESULT_V2":
                        raise ValueError("Schema mismatch in resume artifact")
                    if record.get("manifest_digest") != self.manifest_digest:
                        raise ValueError("Manifest digest mismatch in resume artifact")
                    if record.get("software_revision") != self.software_revision:
                        raise ValueError("Software revision mismatch in resume artifact")
                    if record.get("instrument_id") != "CP_SOURCE_SF18_50K_ISOLATED_V1":
                        raise ValueError("Instrument ID mismatch")
                    if record.get("producer_uci_name") != "Stockfish 18":
                        raise ValueError("Producer UCI name mismatch")
                    if record.get("producer_binary_sha256") != "ae4c93fa9676ca7750d0714342fd8a5b1d018000fc6e0f6cedf112067b5ef374":
                        raise ValueError("Producer SHA mismatch")
                        
                    root_id = record["root_identity"]
                    if root_id in self.completed_roots:
                        raise ValueError(f"Duplicate root_identity in resume artifact: {root_id}")
                        
                    if i >= len(self.admitted_roots):
                        raise ValueError("More records in output than admitted roots")
                    expected_root_id = self.admitted_roots[i]["root_identity"]
                    if root_id != expected_root_id:
                        raise ValueError(f"Resume artifact root {root_id} at index {i} does not match admitted prefix {expected_root_id}")
                        
                    if record["status"] == "SUCCESS":
                        if "experiment_result" not in record:
                            raise ValueError("Missing experiment_result")
                        er_dump = record["experiment_result"]
                        er = ExperimentResult(**er_dump)
                        
                        r = self.admitted_roots[i]
                        expected_spec = build_source_v2_spec(r, self.manifest_digest, record["producer_uci_name"])
                        expected_spec_digest = expected_spec.spec_digest()
                        
                        if expected_spec_digest != er.spec_digest:
                            raise ValueError("Outer spec digest does not match recomputed expected spec digest")
                            
                        payload = json.loads(er.data_payload)
                        if payload["spec_digest"] != expected_spec_digest:
                            raise ValueError("Inner payload spec digest mismatch")
                    elif record["status"] == "FAILURE":
                        if "experiment_result" in record:
                            raise ValueError("FAILURE cannot have experiment_result")
                        if "error_type" not in record or "error_message" not in record:
                            raise ValueError("FAILURE must have error_type and error_message")
                    else:
                        raise ValueError("Invalid status")
                            
                    self.completed_roots.append(root_id)
                    self.engine_session_epoch = max(self.engine_session_epoch, record.get("engine_session_epoch", 0))

    def run(self):
        self.output_path.parent.mkdir(parents=True, exist_ok=True)
        f_out = open(self.output_path, "a", encoding="utf-8")
        
        session = None
        
        try:
            for r in self.admitted_roots:
                root_id = r["root_identity"]
                if root_id in self.completed_roots:
                    continue
                    
                if session is None:
                    session = InstrumentSession(self.stockfish_path, InstrumentRole.SOURCE)
                    session.start()
                    self.engine_session_epoch += 1
                    
                spec = build_source_v2_spec(r, self.manifest_digest, session._provenance["producer"])
                board = reconstruct_root_board(r)
                
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
                    
                line = json.dumps(rec, sort_keys=True, separators=(",", ":")) + "\n"
                f_out.write(line)
                f_out.flush()
                os.fsync(f_out.fileno())
                self.completed_roots.append(root_id)
                
                if rec["status"] == "FAILURE":
                    if session:
                        session.close()
                    session = None
                    
        finally:
            if session:
                session.close()
            f_out.close()
