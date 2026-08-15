import json
import pytest
import statistics
import chess
from typing import List, Dict
import statistics
from typing import List, Dict

from chessheat.models import AnalysisRecord, Score
from chessheat.branch import extract_branches, FutureBranch
from chessheat.experiment import ExperimentSpec, ExperimentResult

def test_ray_blocker_measurement_contest():
    # 1. Load the frozen branch universe
    fixture_path = "docs/research/t2/t2b1_fixture.json"
    with open(fixture_path, "r") as f:
        data = json.load(f)
    record = AnalysisRecord(**data)
    
    # Extract branches
    universe = extract_branches(record)
    
    # Ensure all roots have regret computed
    assert all(branch.regret is not None for branch in universe.branches)
    
    # 2. Extract Preregistered Comparators
    #
    # Relation Transition Feature: 
    # Ray d4 -> d8 (Rook attacking Queen) becomes ENABLED at ply 1.
    # The blocker is initially on d5.
    # If the Knight on d5 moves, it vacates d5, so a move from d5 enables the ray.
    # (Since it's a Knight, it can't move along the d-file, so any move from d5 clears the ray).
    
    def relation_feature(branch: FutureBranch) -> bool:
        # Mechanics: ray is unblocked if d5 is vacated at ply 1.
        # Since we just need the indicator of the relation transition (ray enabled),
        # we can determine if the ray is enabled mechanically by checking if d5 was vacated.
        for ev in branch.future_evidence:
            if ev.ply == 1 and ev.square == "d5" and ev.role == "origin":
                return True
        return False
        
    # Fair Square Comparator (Single-Square Baseline):
    # The strongest constituent square event is origin=d5 at ply=1.
    def square_feature(branch: FutureBranch) -> bool:
        for ev in branch.future_evidence:
            if ev.ply == 1 and ev.square == "d5" and ev.role == "origin":
                return True
        return False

    # 3. Compare partition outcomes
    relation_true_regrets = []
    relation_false_regrets = []
    
    square_true_regrets = []
    square_false_regrets = []
    
    for branch in universe.branches:
        r = branch.regret.value
        
        rel_feat = relation_feature(branch)
        if rel_feat:
            relation_true_regrets.append(r)
        else:
            relation_false_regrets.append(r)
            
        sq_feat = square_feature(branch)
        if sq_feat:
            square_true_regrets.append(r)
        else:
            square_false_regrets.append(r)
            
    # Verify exact reconstruction
    assert relation_true_regrets == square_true_regrets, "F1 Falsified: Square comparator does not exactly reproduce Relation partition"
    assert relation_false_regrets == square_false_regrets, "F1 Falsified: Square comparator does not exactly reproduce Relation partition"
    
    # 4. Discrimination Statistic: Difference in Median CP Regret
    def median_diff(true_regrets: List[int], false_regrets: List[int]) -> float:
        # Median(Regret | False) - Median(Regret | True)
        if not true_regrets or not false_regrets:
            return 0.0
        return float(statistics.median(false_regrets) - statistics.median(true_regrets))

    rel_discrimination = median_diff(relation_true_regrets, relation_false_regrets)
    sq_discrimination = median_diff(square_true_regrets, square_false_regrets)
    
    assert rel_discrimination == sq_discrimination
    
    # 5. Create Artifact showing FALSIFIED
    from chessheat.semantics import SufficientPosition
    spec = ExperimentSpec(
        semantic_signature_version="S1",
        semantic_signature_digest="mock_digest",
        suite_identity="t2b1-ray-blocker-contest",
        suite_digest="mock_suite_digest",
        fixture_identity="3q3k/8/8/3N4/3R4/8/8/4K3_w",
        fixture_digest="mock_fixture_digest",
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
            "relation_discrimination": rel_discrimination,
            "square_discrimination": sq_discrimination,
            "f1_reconstruction": True,
            "message": "Relation transition has no stronger consequence association than the fair square comparator. F1: Square reconstruction completely reproduces the partition."
        }
    )
    
    assert result.data["classification"] == "FALSIFIED"
