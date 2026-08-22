import json
import os
import zstandard
import hashlib
import subprocess
from typing import Dict, Any, List
from pathlib import Path

from chessheat.cp_instrument import InstrumentSession, InstrumentRole, get_canonical_instrument_config
from chessheat.experiment import ExperimentSpec, ExperimentResult
from chessheat.semantics import SemanticSignatureV1
from chessheat.cp_root_population import reconstruct_root_board, canonical_json_digest

def build_target_v2_spec(root_record: Dict[str, Any], manifest_digest: str, producer: str) -> ExperimentSpec:
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
        instrument_config=get_canonical_instrument_config(InstrumentRole.TARGET),
        budget_config={"type": "nodes", "value": 250000},
        line_source="cp_target_acquisition_v2",
        hypothesis_identifier="CP_TARGET_ACQUISITION_V2",
        spec_version=2,
        comparison_perspective="white" if root_record["sufficient_position"]["side_to_move"] == "w" else "black"
    )

class TargetAcquisitionRunnerV2:
    def __init__(self, manifest_path: str, output_path: str, stockfish_path: str, meta_path: str):
        self.manifest_path = Path(manifest_path)
        self.output_path = Path(output_path)
        self.stockfish_path = stockfish_path
        self.meta_path = Path(meta_path)
        
        # Verify approved SHA
        self.target_acquisition_software_revision = os.environ.get("CHESSHEAT_TARGET_ACQUISITION_APPROVED_SHA")
        if not self.target_acquisition_software_revision:
            raise ValueError("CHESSHEAT_TARGET_ACQUISITION_APPROVED_SHA must be set")
            
        try:
            res = subprocess.run(["git", "cat-file", "-t", self.target_acquisition_software_revision], capture_output=True, text=True, check=True)
            if res.stdout.strip() != "commit":
                raise ValueError("Approved SHA must be a commit")
        except subprocess.CalledProcessError:
            raise ValueError(f"Approved SHA not found: {self.target_acquisition_software_revision}")
            
        bound_files = [
            "src/chessheat/cp_instrument.py",
            "src/chessheat/cp_root_population.py",
            "src/chessheat/cp_target_acquisition.py",
            "scripts/run_cp_target_acquisition.py"
        ]
        
        for fpath in bound_files:
            res = subprocess.run(["git", "diff", "--quiet", self.target_acquisition_software_revision, "--", fpath])
            if res.returncode != 0:
                raise ValueError(f"Bound file {fpath} differs from approved SHA")
            res_working = subprocess.run(["git", "diff", "--quiet", "--", fpath])
            if res_working.returncode != 0:
                raise ValueError(f"Uncommitted changes in bound file {fpath}")
                
        # META verification
        with open(self.meta_path, "r", encoding="utf-8") as f:
            meta = json.load(f)
            self.manifest_digest = meta["manifest_digest"]
            self.software_revision = meta["software_revision"]
            
            if self.manifest_digest != "5a013e64265820b65d1d3687fcee98aa607ab41470294d11df7b2f803c8e063d":
                raise ValueError("Target acquisition must use the exact frozen source manifest digest")
            if meta["admitted_root_count"] != 33859:
                raise ValueError("Manifest meta admitted_root_count mismatch")
            if meta["record_count"] != 40038:
                raise ValueError("Manifest meta record_count mismatch")
            if meta["manifest_schema"] != "CP_ROOT_POPULATION_JULY_2026_MANIFEST_V2":
                raise ValueError("Meta schema mismatch")
            if meta["software_revision"] != "a49b6ce62a59cc056b67aefc94b121799d950045":
                raise ValueError("Meta software_revision mismatch")
            if meta["corpus_checksum"] != "714d0eb99f99fca8d791142038b6c59b5ca6a51b3339bd3891a92f4bdffcbf0c":
                raise ValueError("Meta corpus_checksum mismatch")
                
        # Validate manifest content
        self.admitted_roots = []
        dctx = zstandard.ZstdDecompressor()
        sha_hasher = hashlib.sha256()
        
        seen_roots = set()
        
        with open(self.manifest_path, "rb") as f:
            with dctx.stream_reader(f) as reader:
                buffer = b""
                while True:
                    chunk = reader.read(65536)
                    if not chunk:
                        break
                    buffer += chunk
                    while b"\n" in buffer:
                        line, buffer = buffer.split(b"\n", 1)
                        if not line:
                            raise ValueError("Blank line in manifest")
                            
                        encoded_line = line + b"\n"
                        sha_hasher.update(encoded_line)
                        
                        raw = line.decode("utf-8")
                        rec = json.loads(raw)
                        canonical = json.dumps(rec, sort_keys=True, separators=(",", ":"))
                        if raw != canonical:
                            raise ValueError("Non-canonical JSON in manifest")
                            
                        if rec["manifest_schema"] != "CP_ROOT_POPULATION_JULY_2026_MANIFEST_V2":
                            raise ValueError("Record schema mismatch")
                        if rec["software_revision"] != self.software_revision:
                            raise ValueError("Record software_revision mismatch")
                            
                        if rec.get("inclusion") == "ADMITTED":
                            root_id = rec["root_identity"]
                            if root_id in seen_roots:
                                raise ValueError("Duplicate root_identity in manifest")
                            seen_roots.add(root_id)
                            
                            c_rec = rec.copy()
                            del c_rec["root_record_digest"]
                            if canonical_json_digest(c_rec) != rec["root_record_digest"]:
                                raise ValueError("root_record_digest validation failed")
                                
                            reconstruct_root_board(rec)
                            self.admitted_roots.append(rec)
                            
                if buffer:
                    raise ValueError("Manifest does not end with a newline")
                    
        computed_digest = sha_hasher.hexdigest()
        if computed_digest != "5a013e64265820b65d1d3687fcee98aa607ab41470294d11df7b2f803c8e063d":
            raise ValueError(f"Recomputed manifest digest mismatch: {computed_digest}")
        if computed_digest != self.manifest_digest:
            raise ValueError("Manifest digest mismatch with meta")
            
        if len(self.admitted_roots) != 33859:
            raise ValueError(f"Parsed admitted roots {len(self.admitted_roots)} does not match 33859")
            
        self.completed_roots = []
        self.engine_session_epoch = 0
        self._parse_resume()
        
    def _parse_resume(self):
        if self.output_path.exists():
            with open(self.output_path, "r", encoding="utf-8") as f:
                for i, line in enumerate(f):
                    raw = line.rstrip("\n")
                    if not raw:
                        raise ValueError("Blank line in resume artifact")
                        
                    record = json.loads(raw)
                    canonical = json.dumps(record, sort_keys=True, separators=(",", ":"))
                    if raw != canonical:
                        raise ValueError("NONCANONICAL_TARGET_RESULT_JSON")
                        
                    if record.get("schema") != "CP_TARGET_ACQUISITION_RESULT_V2":
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
                        
                        expected_spec = build_target_v2_spec(expected_r, self.manifest_digest, record["producer_uci_name"])
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
                        if payload.get("comparison_perspective") != expected_spec.comparison_perspective:
                            raise ValueError("comparison_perspective mismatch")
                            
                        obs_list = payload.get("observations")
                        if type(obs_list) is not list:
                            raise ValueError("observations must be a list")
                            
                        expected_ucis = expected_spec.candidate_policy["ordered_legal_root_ucis"]
                        expected_count = expected_spec.candidate_policy["required_search_count"]
                        if len(obs_list) != expected_count:
                            raise ValueError("observations length mismatch")
                            
                        acq_ucis = []
                        for obs_idx, obs in enumerate(obs_list):
                            if obs.get("requested_nodes") != 250000:
                                raise ValueError("requested_nodes mismatch in successful observation")
                            if "score_type" not in obs or obs["score_type"] not in ("cp", "mate"):
                                raise ValueError("invalid score_type")
                            if "root_move_uci" not in obs:
                                raise ValueError("missing root_move_uci")
                            if obs.get("acquisition_index") != obs_idx:
                                raise ValueError("invalid acquisition_index")
                            if obs.get("comparison_perspective") != expected_spec.comparison_perspective:
                                raise ValueError("observation comparison_perspective mismatch")
                            acq_ucis.append(obs["root_move_uci"])
                            
                        if acq_ucis != expected_ucis:
                            raise ValueError("canonical acquisition order mismatch")
                                
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
                    session = InstrumentSession(self.stockfish_path, InstrumentRole.TARGET)
                    session.start()
                    self.engine_session_epoch += 1
                    
                spec = build_target_v2_spec(r, self.manifest_digest, session._provenance["producer"])
                board = reconstruct_root_board(r)
                
                try:
                    result = session.acquire(spec, board)
                    
                    payload = result.data
                    
                    if payload.get("instrument_role") != "TARGET":
                        raise ValueError("instrument_role mismatch")
                    if payload.get("instrument_id") != "CP_TARGET_SF18_250K_ISOLATED_V1":
                        raise ValueError("instrument_id mismatch")
                        
                    obs_list = payload.get("observations")
                    if type(obs_list) is not list:
                        raise ValueError("observations must be a list")
                        
                    expected_ucis = spec.candidate_policy["ordered_legal_root_ucis"]
                    if len(obs_list) != spec.candidate_policy["required_search_count"]:
                        raise ValueError("observations length mismatch")
                        
                    acq_ucis = []
                    for obs_idx, obs in enumerate(obs_list):
                        if obs.get("requested_nodes") != 250000:
                            raise ValueError(f"Acquired observation has wrong requested nodes: {obs.get('requested_nodes')}")
                        if "root_move_uci" not in obs:
                            raise ValueError("Observation missing root_move_uci")
                        acq_ucis.append(obs["root_move_uci"])
                        
                    if acq_ucis != expected_ucis:
                        raise ValueError("canonical acquisition order mismatch")
                            
                    rec = {
                        "schema": "CP_TARGET_ACQUISITION_RESULT_V2",
                        "manifest_digest": self.manifest_digest,
                        "root_manifest_schema": r["manifest_schema"],
                        "root_population_software_revision": self.software_revision,
                        "target_acquisition_software_revision": self.target_acquisition_software_revision,
                        "instrument_id": "CP_TARGET_SF18_250K_ISOLATED_V1",
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
                        "schema": "CP_TARGET_ACQUISITION_RESULT_V2",
                        "manifest_digest": self.manifest_digest,
                        "root_manifest_schema": r["manifest_schema"],
                        "root_population_software_revision": self.software_revision,
                        "target_acquisition_software_revision": self.target_acquisition_software_revision,
                        "instrument_id": "CP_TARGET_SF18_250K_ISOLATED_V1",
                        "producer_uci_name": session._provenance["producer"] if session else "Stockfish 18",
                        "producer_binary_sha256": session._provenance["pre_spawn_sha256"] if session else "ae4c93fa9676ca7750d0714342fd8a5b1d018000fc6e0f6cedf112067b5ef374",
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
