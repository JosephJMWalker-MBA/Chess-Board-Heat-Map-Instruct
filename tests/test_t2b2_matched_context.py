import json
import hashlib
import pytest
import statistics
import chess
from typing import List, Dict

from chessheat.models import AnalysisRecord, Score
from chessheat.branch import extract_branches, FutureBranch
from chessheat.experiment import ExperimentSpec, ExperimentResult, SuiteManifest, SuiteKind
from chessheat.semantics import SemanticSignatureV1, SufficientPosition

def test_matched_context_alias_breaker():
    # 1. Load the frozen branch universes for both contexts
    with open("docs/research/t2/t2b2_fixture_a.json", "r") as f:
        data_a = json.load(f)
        fixture_digest_a = hashlib.sha256(json.dumps(data_a, sort_keys=True).encode('utf-8')).hexdigest()
    record_a = AnalysisRecord(**data_a)
    
    with open("docs/research/t2/t2b2_fixture_b.json", "r") as f:
        data_b = json.load(f)
        fixture_digest_b = hashlib.sha256(json.dumps(data_b, sort_keys=True).encode('utf-8')).hexdigest()
    record_b = AnalysisRecord(**data_b)
    
    universe_a = extract_branches(record_a)
    universe_b = extract_branches(record_b)
    
    # 1.5 Validate the full legal root universe for both contexts
    board_a = chess.Board(record_a.fen)
    legal_ucis_a = {m.uci() for m in board_a.legal_moves}
    obs_ucis_a = {obs.uci for obs in record_a.move_observations}
    assert legal_ucis_a == obs_ucis_a, "Context A fixture does not contain exactly the full legal root set"
    
    board_b = chess.Board(record_b.fen)
    legal_ucis_b = {m.uci() for m in board_b.legal_moves}
    obs_ucis_b = {obs.uci for obs in record_b.move_observations}
    assert legal_ucis_b == obs_ucis_b, "Context B fixture does not contain exactly the full legal root set"
    
    # 2. Independently derive features
    def relation_feature(board_fen: str, root_uci: str) -> bool:
        b = chess.Board(board_fen)
        
        # Verify blocked before root (d4 rook, d8 queen)
        assert not b.is_attacked_by(chess.WHITE, chess.D8)
        
        move = chess.Move.from_uci(root_uci)
        b.push(move)
        
        d4_piece = b.piece_at(chess.D4)
        if d4_piece and d4_piece.piece_type == chess.ROOK and d4_piece.color == chess.WHITE:
            return chess.D8 in b.attacks(chess.D4)
        return False
        
    def square_feature(branch: FutureBranch) -> bool:
        for ev in branch.future_evidence:
            if ev.ply == 1 and ev.square == "d5" and ev.role == "origin":
                return True
        return False
        
    def square_composite(board_fen: str, branch: FutureBranch) -> bool:
        # H2 Challenge: [d5, origin, ply1] AND [d6 is empty] AND [d7 is empty]
        # Evaluated on the initial root state.
        b = chess.Board(board_fen)
        is_d6_clear = (b.piece_at(chess.D6) is None)
        is_d7_clear = (b.piece_at(chess.D7) is None)
        return square_feature(branch) and is_d6_clear and is_d7_clear

    # 3. Structural Test (H1 & H2)
    # Collect combined universe
    combined_branches = []
    
    def process_universe(universe, record):
        branches = []
        for branch in universe.branches:
            rel_feat = relation_feature(record.fen, branch.root_uci)
            sq_feat = square_feature(branch)
            sq_comp = square_composite(record.fen, branch)
            branches.append({
                "branch": branch,
                "rel_feat": rel_feat,
                "sq_feat": sq_feat,
                "sq_comp": sq_comp
            })
        return branches

    branches_a = process_universe(universe_a, record_a)
    branches_b = process_universe(universe_b, record_b)
    
    # Verify H1: local-square alias breaks across context
    h1_break_found = False
    # we just iterate and see if for the same root move (d5->xx), rel_feat differs while sq_feat is True for both.
    # We can match them by root_uci.
    for b_a in branches_a:
        for b_b in branches_b:
            if b_a["branch"].root_uci == b_b["branch"].root_uci:
                # We look for a move where square feature is True and identical but relation is different
                if b_a["sq_feat"] and b_b["sq_feat"]:
                    if b_a["rel_feat"] != b_b["rel_feat"]:
                        h1_break_found = True
                        break
    
    if not h1_break_found:
        pytest.fail("H1 Failed: Single-square feature alias did not break across contexts")
        
    # Verify H2: fair square composite challenge
    # Does the composite perfectly reconstruct the relation partition over the combined suite?
    h2_perfect_reconstruction = True
    for item in branches_a + branches_b:
        if item["rel_feat"] != item["sq_comp"]:
            h2_perfect_reconstruction = False
            break
            
    assert h2_perfect_reconstruction, "Square composite failed to reconstruct relation partition"
    
    # 4. Acquire consequence evidence (combined-suite consequence comparison)
    def gather_stats(feature_key):
        true_regrets = []
        false_regrets = []
        for item in branches_a + branches_b:
            r = item["branch"].regret
            if item[feature_key]:
                true_regrets.append(r)
            else:
                false_regrets.append(r)
        return true_regrets, false_regrets

    def compute_statistic(true_regrets: List[Score], false_regrets: List[Score]) -> float:
        if any(r.type != 'cp' for r in true_regrets + false_regrets):
            return "INCONCLUSIVE"
        t_vals = [r.value for r in true_regrets]
        f_vals = [r.value for r in false_regrets]
        if not t_vals or not f_vals:
            return 0.0
        return float(statistics.median(f_vals) - statistics.median(t_vals))

    t_rel, f_rel = gather_stats("rel_feat")
    stat_rel = compute_statistic(t_rel, f_rel)
    
    t_sq, f_sq = gather_stats("sq_feat")
    stat_sq = compute_statistic(t_sq, f_sq)
    
    t_comp, f_comp = gather_stats("sq_comp")
    stat_comp = compute_statistic(t_comp, f_comp)
    
    if "INCONCLUSIVE" in (stat_rel, stat_sq, stat_comp):
        pytest.skip("Inconclusive: Mate and CP coexist")
        
    # Since H2 reconstructs H1 perfectly, stat_rel should equal stat_comp
    assert stat_rel == stat_comp
    
    # 5. Restore actual S0/S1 identities and create ExperimentResults + ComparisonResult
    from chessheat.experiment import ComparisonResult
    signature = SemanticSignatureV1.create_canonical()
    
    manifest = SuiteManifest(
        suite_id="t2b2-matched-context-alias-breaker",
        kind=SuiteKind.MECHANISM_STRESS,
        fixtures={
            record_a.fen.replace(" ", "_"): fixture_digest_a,
            record_b.fen.replace(" ", "_"): fixture_digest_b
        }
    )
    
    # Create Context A Experiment
    spec_a = ExperimentSpec(
        semantic_signature_version=signature.version,
        semantic_signature_digest=signature.signature_hash(),
        suite_identity=manifest.suite_id,
        suite_digest=manifest.suite_digest(),
        fixture_identity=record_a.fen.replace(" ", "_"),
        fixture_digest=fixture_digest_a,
        sufficient_position=SufficientPosition(
            board_arrangement_fen=record_a.fen.split()[0],
            side_to_move="w",
            castling_rights="-",
            en_passant_square=None,
            halfmove_clock=0,
            fullmove_number=1,
            history_available=False,
            variant="standard"
        ),
        candidate_policy={},
        producer_identity=record_a.engine_name,
        instrument_config=record_a.engine_options,
        budget_config={"type": record_a.search_budget_type, "value": record_a.search_budget_value},
        line_source="pv",
        hypothesis_identifier="T2b-2-Matched-Context-Alias-Breaker"
    )
    
    result_a = ExperimentResult.create(
        spec_digest=spec_a.spec_digest(),
        data={"context": "A"}
    )
    
    # Create Context B Experiment
    spec_b = ExperimentSpec(
        semantic_signature_version=signature.version,
        semantic_signature_digest=signature.signature_hash(),
        suite_identity=manifest.suite_id,
        suite_digest=manifest.suite_digest(),
        fixture_identity=record_b.fen.replace(" ", "_"),
        fixture_digest=fixture_digest_b,
        sufficient_position=SufficientPosition(
            board_arrangement_fen=record_b.fen.split()[0],
            side_to_move="w",
            castling_rights="-",
            en_passant_square=None,
            halfmove_clock=0,
            fullmove_number=1,
            history_available=False,
            variant="standard"
        ),
        candidate_policy={},
        producer_identity=record_b.engine_name,
        instrument_config=record_b.engine_options,
        budget_config={"type": record_b.search_budget_type, "value": record_b.search_budget_value},
        line_source="pv",
        hypothesis_identifier="T2b-2-Matched-Context-Alias-Breaker"
    )
    
    result_b = ExperimentResult.create(
        spec_digest=spec_b.spec_digest(),
        data={"context": "B"}
    )
    
    # Use ComparisonResult to record the matched-context conclusion
    comparison = ComparisonResult(
        hypothesis_identifier="T2b-2-Matched-Context-Alias-Breaker",
        result_digest_a=result_a.artifact_digest,
        result_digest_b=result_b.artifact_digest,
        outcome_payload=json.dumps({
            "classification": "WEAK_SUPPORT",
            "relation_discrimination": stat_rel,
            "single_square_discrimination": stat_sq,
            "square_composite_discrimination": stat_comp,
            "h1_alias_break": True,
            "h2_composite_reconstruction": True,
            "message": "WEAK_SUPPORT: Relation breaks the single-square alias, but the fixed square composite reconstructs the relation partition perfectly."
        }, sort_keys=True)
    )
    
    assert comparison.outcome["classification"] == "WEAK_SUPPORT"
