from typing import Dict, List, Optional
from pydantic import BaseModel
from .fusion import SquareFusion

class ModelEvaluation(BaseModel):
    model_name: str

    # Localization: 1 to 64 rank of expected squares
    expected_ranks: Dict[str, int]

    # Regional coverage: fraction of expected region in top 25% (rank <= 16)
    coverage: float

    # Specificity: 1 - (irrelevant squares in top 25% / total irrelevant squares)
    specificity: float

    # For F8 (negative control): max percentile separation (1.0 - lowest measured, or similar), or just max score vs mean
    # We can track the number of squares with score > 0.9
    hotspots_count: int

    # Concentration: Top-1 and Top-5 share of total mass
    top_1_share: float
    top_5_share: float

def evaluate_model(model_name: str, fused: Dict[str, SquareFusion], expected_region: List[str]) -> ModelEvaluation:
    # Extract just this model's scores
    scores = {}
    for sq, f in fused.items():
        val = getattr(f, model_name, None)
        if val is not None:
            scores[sq] = val
        else:
            scores[sq] = 0.0 # Treat no_data as 0 for ranking purposes in evaluation

    # Sort descending
    sorted_sqs = sorted(scores.items(), key=lambda x: x[1], reverse=True)

    ranks = {}
    total_mass = 0.0
    for i, (sq, val) in enumerate(sorted_sqs):
        ranks[sq] = i + 1
        total_mass += val

    expected_ranks = {sq: ranks.get(sq, 64) for sq in expected_region}

    # Coverage: how many expected squares are in the top 16 (top 25%)
    # If the region is small, maybe top 25% is too generous? We can just use it for now.
    covered = sum(1 for sq in expected_region if ranks.get(sq, 64) <= 16)
    coverage = covered / len(expected_region) if expected_region else 0.0

    # Specificity
    irrelevant = [sq for sq in scores.keys() if sq not in expected_region]
    if irrelevant:
        irrelevant_surfaced = sum(1 for sq in irrelevant if ranks.get(sq, 64) <= 16)
        specificity = 1.0 - (irrelevant_surfaced / len(irrelevant))
    else:
        specificity = 1.0

    # Hotspots
    hotspots_count = sum(1 for sq, val in scores.items() if val > 0.9)

    # Concentration
    top_1_mass = sum(val for sq, val in sorted_sqs[:1])
    top_5_mass = sum(val for sq, val in sorted_sqs[:5])

    top_1_share = (top_1_mass / total_mass) if total_mass > 0 else 0.0
    top_5_share = (top_5_mass / total_mass) if total_mass > 0 else 0.0

    return ModelEvaluation(
        model_name=model_name,
        expected_ranks=expected_ranks,
        coverage=coverage,
        specificity=specificity,
        hotspots_count=hotspots_count,
        top_1_share=top_1_share,
        top_5_share=top_5_share
    )
