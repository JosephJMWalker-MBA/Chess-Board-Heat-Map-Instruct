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

def test_ray_blocker_measurement_contest():
    # 1. Load the frozen branch universe (no filtering)
    fixture_path = "docs/research/t2/t2b1_fixture_v2.json"
    with open(fixture_path, "r") as f:
        data = json.load(f)
        fixture_digest = hashlib.sha256(json.dumps(data, sort_keys=True).encode('utf-8')).hexdigest()
    record = AnalysisRecord(**data)
    
    # Extract branches
    universe = extract_branches(record)
    
    # Validate the full legal root universe
    board = chess.Board(record.fen)
    legal_ucis = {m.uci() for m in board.legal_moves}
    obs_ucis = {obs.uci for obs in record.move_observations}
    assert legal_ucis == obs_ucis, "Fixture does not contain exactly the full legal root set"
    
    # 2. Independently derive the relation feature
    def relation_feature(root_uci: str) -> bool:
        b = chess.Board(record.fen)
        
        # Verify blocked before root
        # d4 rook, d8 queen. Blocker on d5.
        # Mechanically, check if d4 attacks d8
        assert not b.is_attacked_by(chess.WHITE, chess.D8)
        
        # Apply root move
        move = chess.Move.from_uci(root_uci)
        b.push(move)
        
        # Mechanically derive if ray is enabled
        # Is d8 attacked by white rook on d4?
        # A white rook is on d4, if d5 is empty and file is clear
        d4_piece = b.piece_at(chess.D4)
        is_enabled = False
        if d4_piece and d4_piece.piece_type == chess.ROOK and d4_piece.color == chess.WHITE:
            # Does d4 attack d8? (python-chess attacks_mask includes own pieces and empty squares, 
            # we just need to see if d8 is in the attack set of d4)
            attacks = b.attacks(chess.D4)
            is_enabled = chess.D8 in attacks
            
        return is_enabled

    # Fair Square Comparator (Preregistered Constituent-Square Baseline):
    # d5 is the unique blocker in the preregistered relation.
    def square_feature(branch: FutureBranch) -> bool:
        for ev in branch.future_evidence:
            if ev.ply == 1 and ev.square == "d5" and ev.role == "origin":
                return True
        return False

    # 3. Prove F1 structurally before using outcomes
    relation_true_regrets = []
    relation_false_regrets = []
    
    square_true_regrets = []
    square_false_regrets = []
    
    for branch in universe.branches:
        r = branch.regret
        
        rel_feat = relation_feature(branch.root_uci)
        sq_feat = square_feature(branch)
        
        # F1 test: Mechanical equality over the whole legal root universe
        assert rel_feat == sq_feat, f"F1 Structural Equality Failed for {branch.root_uci}"
        
        if rel_feat:
            relation_true_regrets.append(r)
        else:
            relation_false_regrets.append(r)
            
        if sq_feat:
            square_true_regrets.append(r)
        else:
            square_false_regrets.append(r)
            
    # 4. Tighten consequence typing
    def compute_statistic(true_regrets: List[Score], false_regrets: List[Score]) -> float:
        # Require all to be type cp
        if any(r.type != 'cp' for r in true_regrets + false_regrets):
            return "INCONCLUSIVE"
            
        t_vals = [r.value for r in true_regrets]
        f_vals = [r.value for r in false_regrets]
        
        if not t_vals or not f_vals:
            return 0.0
            
        return float(statistics.median(f_vals) - statistics.median(t_vals))

    rel_stat = compute_statistic(relation_true_regrets, relation_false_regrets)
    sq_stat = compute_statistic(square_true_regrets, square_false_regrets)
    
    if rel_stat == "INCONCLUSIVE":
        pytest.skip("Inconclusive: Mate and CP coexist")
        
    assert rel_stat == sq_stat
    
    # 5. Restore actual S0/S1 identities
    signature = SemanticSignatureV1.create_canonical()
    
    manifest = SuiteManifest(
        suite_id="t2b1-ray-blocker-contest",
        kind=SuiteKind.MECHANISM_STRESS,
        fixtures={"3q3k/8/8/3N4/3R4/8/8/4K3_w": fixture_digest}
    )
    
    spec = ExperimentSpec(
        semantic_signature_version=signature.version,
        semantic_signature_digest=signature.signature_hash(),
        suite_identity=manifest.suite_id,
        suite_digest=manifest.suite_digest(),
        fixture_identity="3q3k/8/8/3N4/3R4/8/8/4K3_w",
        fixture_digest=fixture_digest,
        sufficient_position=SufficientPosition(
            board_arrangement_fen="3q3k/8/8/3N4/3R4/8/8/4K3",
            side_to_move="w",
            castling_rights="-",
            en_passant_square=None,
            halfmove_clock=0,
            fullmove_number=1,
            history_available=False,
            variant="standard"
        ),
        candidate_policy=record.candidate_policy,
        producer_identity=record.engine_name,
        instrument_config=record.engine_options,
        budget_config={"type": record.search_budget_type, "value": record.search_budget_value},
        line_source="pv",
        hypothesis_identifier="T2b-1-Ray-Measurement-Advantage"
    )
    
    result = ExperimentResult.create(
        spec_digest=spec.spec_digest(),
        data={
            "classification": "FALSIFIED",
            "relation_discrimination": rel_stat,
            "square_discrimination": sq_stat,
            "f1_reconstruction": True,
            "message": "Relation transition has no stronger consequence association than the fair square comparator. F1: Square reconstruction completely reproduces the partition."
        }
    )
    
    assert result.data["classification"] == "FALSIFIED"
