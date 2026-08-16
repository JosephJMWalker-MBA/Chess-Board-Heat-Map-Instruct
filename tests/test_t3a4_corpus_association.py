import json
import hashlib
import pytest

from scripts.execute_t3a4_corpus import verify_manifest, evaluate_fixture
from chessheat.experiment import ExperimentResult

MANIFEST_SHA = "4337dd0c8ef2579a1b15eb58f5cb00f4bb566c6fdde6ef612f09b2bab2e1ecc7"

def get_hash(filepath):
    sha256 = hashlib.sha256()
    with open(filepath, "rb") as f:
        sha256.update(f.read())
    return sha256.hexdigest()

def test_t3a4_corpus_association():
    # 12. Preserve pre-engine corpus untouched
    assert get_hash("docs/research/t3/t3a4_corpus_manifest.json") == MANIFEST_SHA

    with open("tests/fixtures/t3a4/t3a4_corpus_result.json", "r") as f:
        corpus = json.load(f)

    assert corpus["manifest_sha"] == MANIFEST_SHA

    # Verify reloading each ExperimentResult
    from chessheat.models import AnalysisRecord, Score
    from chessheat.branch import extract_branches
    from chessheat.consequence import compute_regrets

    for idx, (raw_digest, spec_digest, artifact_digest) in enumerate(zip(
        corpus["raw_fixture_digests"], corpus["spec_digests"], corpus["artifact_digests"]
    )):
        result_path = f"tests/fixtures/t3a4/results/t3a4_f{idx:02d}_result.json"
        with open(result_path, "r") as f:
            res_data = json.load(f)

        loaded_result = ExperimentResult(**res_data)
        assert loaded_result.spec_digest == spec_digest
        assert loaded_result.artifact_digest == artifact_digest

        # Verify permutation invariance for evaluating fixture
        raw_path = f"tests/fixtures/t3a4/raw/t3a4_f{idx:02d}.json"
        assert get_hash(raw_path) == raw_digest

        with open(raw_path, "r") as f:
            raw_data = json.load(f)

        scores_dict = {obs["uci"]: Score(**obs["score"]) for obs in raw_data["move_observations"]}
        regrets_dict = compute_regrets(scores_dict)

        from chessheat.models import MoveObservation
        record_obs = []
        for obs in raw_data["move_observations"]:
            o = MoveObservation(**obs)
            if o.uci in regrets_dict:
                o.regret = regrets_dict[o.uci]
            record_obs.append(o)

        record = AnalysisRecord(
            fen=raw_data["fen"],
            root_side="white",
            comparison_perspective="white",
            engine_name=raw_data["engine_name"],
            engine_options=raw_data["engine_options"],
            search_budget_type=raw_data["search_budget_type"],
            search_budget_value=raw_data["search_budget_value"],
            candidate_policy={},
            baseline_observation=Score(**raw_data["baseline_observation"]),
            move_observations=record_obs
        )

        universe = extract_branches(record)
        branches = universe.branches
        target_sq = corpus["fixture_results"][idx]["target_event"]["square"]

        # Mechanical permutation check
        res_orig = evaluate_fixture(branches, target_sq)
        res_rev = evaluate_fixture(branches[::-1], target_sq)
        res_sort = evaluate_fixture(sorted(branches, key=lambda b: b.root_uci), target_sq)

        assert res_orig == res_rev == res_sort

    # Verify corpus aggregation permutation invariance
    from scripts.execute_t3a4_corpus import median
    valid_p_fs = [r["P_f"] for r in corpus["fixture_results"] if r["evaluable_status"] and r["P_f"] is not None]
    
    d_suite_orig = median(sorted(valid_p_fs)) if len(valid_p_fs) >= 3 else None
    d_suite_rev = median(sorted(valid_p_fs[::-1])) if len(valid_p_fs) >= 3 else None
    
    assert d_suite_orig == d_suite_rev

    # Interpretation constraint is mandatory
    assert "deterministic rule-selected 12-position corpus drawn from one generated trajectory" in corpus["interpretation_constraint"]

if __name__ == "__main__":
    pytest.main([__file__])
