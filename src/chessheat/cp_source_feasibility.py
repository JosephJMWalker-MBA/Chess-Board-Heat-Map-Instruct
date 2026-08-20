import json
import zstandard
import io
from pathlib import Path
from typing import Dict, Any
import chess
from chessheat.cp_instrument import InstrumentSession, InstrumentRole, ProtocolError, get_canonical_instrument_config
from chessheat.experiment import ExperimentSpec
from chessheat.semantics import ObservationIdentity

class SourceFeasibilityRunner:
    def __init__(self, manifest_path: str, output_path: str, stockfish_path: str):
        self.manifest_path = Path(manifest_path)
        self.output_path = Path(output_path)
        self.stockfish_path = stockfish_path
        
        self.output_path.parent.mkdir(parents=True, exist_ok=True)
        self.completed_roots = set()
        
        if self.output_path.exists():
            with open(self.output_path, "rb") as f:
                dctx = zstandard.ZstdDecompressor()
                try:
                    with dctx.stream_reader(f) as reader:
                        for line in io.TextIOWrapper(reader, encoding="utf-8"):
                            if not line.strip(): continue
                            record = json.loads(line)
                            if record.get("status") in ["SUCCESS", "SOURCE_ACQUISITION_FAILURE"]:
                                self.completed_roots.add(record["root_identity"])
                except Exception:
                    pass

    def run(self):
        # Read manifest
        manifest_records = []
        with open(self.manifest_path, "rb") as f:
            dctx = zstandard.ZstdDecompressor()
            with dctx.stream_reader(f) as reader:
                for line in io.TextIOWrapper(reader, encoding="utf-8"):
                    if not line.strip(): continue
                    manifest_records.append(json.loads(line))
        
        admitted = [r for r in manifest_records if r.get("inclusion") == "ADMITTED"]
        
        # Start session
        session = InstrumentSession(self.stockfish_path, InstrumentRole.SOURCE)
        session.start()
        
        try:
            cctx = zstandard.ZstdCompressor()
            with open(self.output_path, "ab") as f_out:
                with cctx.stream_writer(f_out) as writer:
                    for r in admitted:
                        root_id = r["root_identity"]
                        if root_id in self.completed_roots:
                            continue
                            
                        board = chess.Board(r["sufficient_position"]["board_arrangement_fen"])
                        board.turn = chess.WHITE if r["sufficient_position"]["side_to_move"] == "w" else chess.BLACK
                        board.set_castling_fen(r["sufficient_position"]["castling_rights"])
                        if r["sufficient_position"]["en_passant_square"]:
                            board.ep_square = chess.parse_square(r["sufficient_position"]["en_passant_square"])
                        board.halfmove_clock = r["sufficient_position"]["halfmove_clock"]
                        board.fullmove_number = r["sufficient_position"]["fullmove_number"]
                        
                        sorted_moves = sorted(list(board.legal_moves), key=lambda m: m.uci())
                        sorted_ucis = [m.uci() for m in sorted_moves]
                        expected_policy = {
                            "scope": "cp_all_legal_root_moves_v1",
                            "ordered_legal_root_ucis": sorted_ucis,
                            "required_search_count": len(sorted_ucis)
                        }
                        
                        # create Spec
                        spec = ExperimentSpec(
                            semantic_signature_version="1.0",
                            semantic_signature_digest="dummy",
                            suite_identity="CP_ROOT_POPULATION_LICHESS_BROADCAST_2026_07_V1",
                            suite_digest="dummy", # Normally digest of manifest
                            fixture_identity=r["root_identity"],
                            fixture_digest=r["root_identity"],
                            sufficient_position=r["sufficient_position"],
                            candidate_policy=expected_policy,
                            producer_identity=session._provenance["producer"],
                            instrument_config=get_canonical_instrument_config(InstrumentRole.SOURCE),
                            budget_config={"type": "nodes", "value": 50000},
                            line_source="source_only",
                            hypothesis_identifier="CP_SOURCE_FEASIBILITY_COVERAGE_V1",
                            spec_version=2,
                            comparison_perspective="white" if r["sufficient_position"]["side_to_move"] == "w" else "black"
                        )
                        

                        
                        try:
                            result = session.acquire(spec, board)
                            rec = {
                                "status": "SUCCESS",
                                "root_identity": root_id,
                                "result": result.model_dump()
                            }
                        except Exception as e:
                            rec = {
                                "status": "SOURCE_ACQUISITION_FAILURE",
                                "root_identity": root_id,
                                "error": str(e)
                            }
                            # Cycle session on failure
                            session.close()
                            session = InstrumentSession(self.stockfish_path, InstrumentRole.SOURCE)
                            session.start()
                            
                        line = json.dumps(rec, separators=(",", ":")) + "\n"
                        writer.write(line.encode("utf-8"))
                        writer.flush()
                        self.completed_roots.add(root_id)
        finally:
            session.close()

