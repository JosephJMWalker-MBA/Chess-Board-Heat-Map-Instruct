from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
import statistics

from chessheat.temporal import TemporalLedger, SuccessionCounterfactualEvidence
from chessheat.engine import EngineAdapter, analyze, AnalysisRecord, Score
from chessheat.models import MoveObservation

class PartitionOutcomes(BaseModel):
    moves: List[str] = Field(default_factory=list)
    regrets: List[Score] = Field(default_factory=list)
    outcomes: List[Score] = Field(default_factory=list)
    
    @property
    def cp_regrets(self) -> List[int]:
        return [r.value for r in self.regrets if r.type == 'cp']

    @property
    def median_cp_regret(self) -> Optional[float]:
        cprs = self.cp_regrets
        if not cprs:
            return None
        return float(statistics.median(cprs))

class ConversionCandidateEvidence(BaseModel):
    structural_evidence: SuccessionCounterfactualEvidence
    analysis_record: AnalysisRecord
    
    m11_outcomes: PartitionOutcomes = Field(default_factory=PartitionOutcomes)
    m10_outcomes: PartitionOutcomes = Field(default_factory=PartitionOutcomes)
    m01_outcomes: PartitionOutcomes = Field(default_factory=PartitionOutcomes)
    m00_outcomes: PartitionOutcomes = Field(default_factory=PartitionOutcomes)
    
    confounded: bool = False
    
    @property
    def median_diff_11_10(self) -> Optional[float]:
        m11_med = self.m11_outcomes.median_cp_regret
        m10_med = self.m10_outcomes.median_cp_regret
        if m11_med is not None and m10_med is not None:
            return m11_med - m10_med
        return None

    @property
    def median_diff_11_01(self) -> Optional[float]:
        m11_med = self.m11_outcomes.median_cp_regret
        m01_med = self.m01_outcomes.median_cp_regret
        if m11_med is not None and m01_med is not None:
            return m11_med - m01_med
        return None

    @property
    def independent_birth_observed(self) -> bool:
        return self.structural_evidence.n_01 > 0

    @property
    def independent_death_exceeds_joint(self) -> bool:
        return self.structural_evidence.n_10 > self.structural_evidence.n_11

    @property
    def equal_median_cp_regret(self) -> bool:
        diff = self.median_diff_11_10
        if diff is not None:
            return abs(diff) == 0.0
        return False

    @property
    def joint_class_higher_median_regret(self) -> bool:
        diff = self.median_diff_11_10
        if diff is not None:
            return diff > 0.0
        return False

    @property
    def ephemeral_successor(self) -> bool:
        duration = self.structural_evidence.observed_duration_of_born_episode
        if duration is not None:
            return duration <= 1
        return False

    @property
    def right_censored(self) -> bool:
        return bool(self.structural_evidence.is_born_right_censored)

    @property
    def missing_comparison_class(self) -> bool:
        return self.structural_evidence.n_00 == 0

class ConversionEvidenceBundle(BaseModel):
    candidates: List[ConversionCandidateEvidence] = Field(default_factory=list)
    
    @property
    def is_isolated(self) -> bool:
        return len(self.candidates) == 1

def compute_regrets(scores: Dict[str, Score]) -> Dict[str, Score]:
    """
    Authoritative primitive for computing typed regrets across a legal root universe.
    E^* = max(E(m)) over CP-comparable roots.
    R(m) = E^* - E(m) >= 0.
    Mate outcomes preserve typing.
    """
    # 1. Identify E^* strictly from CP-comparable outcomes
    cp_scores = [s.value for s in scores.values() if s.type == 'cp']
    e_star = max(cp_scores) if cp_scores else None

    regrets = {}
    for m, s in scores.items():
        if s.type == 'mate':
            # Preserve mate typing
            regrets[m] = Score(type='mate', value=s.value, perspective=s.perspective)
        else:
            if e_star is None:
                # This should not happen unless there are no CP comparable roots (all-mate position)
                # But if all are mate, then s.type would be 'mate' and we wouldn't be in this else block.
                raise ValueError(f"No CP scores found but processing a CP move {m}.")
            r = e_star - s.value
            if r < 0:
                raise ValueError(f"Regret invariant violated! R(m)={r} < 0 for {m}")
            regrets[m] = Score(type='cp', value=r, perspective=s.perspective)
            
    return regrets
def couple_consequences(ledger: TemporalLedger, adapter: EngineAdapter, budget_type: str, budget_value: int, comparison_perspective: Optional[str] = None) -> List[ConversionEvidenceBundle]:
    all_candidates = []
    analysis_cache: Dict[str, AnalysisRecord] = {}

    for transition in ledger.transitions:
        if not transition.counterfactual_evidence:
            continue
            
        fen = transition.fen_before
        if fen not in analysis_cache:
            record = analyze(fen, adapter, budget_type, budget_value, comparison_perspective=comparison_perspective)
            analysis_cache[fen] = record
            
        record = analysis_cache[fen]
        baseline = record.baseline_observation
        
        move_obs_dict: Dict[str, MoveObservation] = {obs.san: obs for obs in record.move_observations}
        all_scores = {m: obs.score for m, obs in move_obs_dict.items()}
        all_regrets = compute_regrets(all_scores)
        
        for cf in transition.counterfactual_evidence:
            candidate = ConversionCandidateEvidence(
                structural_evidence=cf,
                analysis_record=record
            )
            
            def populate_partition(moves: List[str], partition: PartitionOutcomes):
                for m in moves:
                    if m in move_obs_dict:
                        obs = move_obs_dict[m]
                        partition.moves.append(m)
                        partition.outcomes.append(obs.score)
                        partition.regrets.append(all_regrets[m])
                        
            populate_partition(cf.m_11, candidate.m11_outcomes)
            populate_partition(cf.m_10, candidate.m10_outcomes)
            populate_partition(cf.m_01, candidate.m01_outcomes)
            populate_partition(cf.m_00, candidate.m00_outcomes)
            
            all_candidates.append(candidate)
            
    # Bundle inseparable candidates
    bundles: List[ConversionEvidenceBundle] = []
    
    # We group candidates by transition ply and their support partition structure
    # Since candidates are from transitions across the whole game, we need to partition them safely.
    # Group by ply first.
    ply_groups = {}
    for c in all_candidates:
        ply = c.structural_evidence.fen_before # Unique pre-move state
        if ply not in ply_groups:
            ply_groups[ply] = []
        ply_groups[ply].append(c)
        
    for ply, candidates in ply_groups.items():
        # Group by identical support subsets
        # Support is defined by the exact contents of M11, M10, M01, M00.
        bundle_map = {}
        for c in candidates:
            m11 = tuple(sorted(c.structural_evidence.m_11))
            m10 = tuple(sorted(c.structural_evidence.m_10))
            m01 = tuple(sorted(c.structural_evidence.m_01))
            m00 = tuple(sorted(c.structural_evidence.m_00))
            key = (m11, m10, m01, m00)
            if key not in bundle_map:
                bundle_map[key] = []
            bundle_map[key].append(c)
            
        for key, bundle_cands in bundle_map.items():
            is_confounded = len(bundle_cands) > 1
            for bc in bundle_cands:
                bc.confounded = is_confounded
            bundles.append(ConversionEvidenceBundle(candidates=bundle_cands))
            
    return bundles
