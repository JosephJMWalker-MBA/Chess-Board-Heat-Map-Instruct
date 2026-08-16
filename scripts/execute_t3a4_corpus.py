import json
import hashlib
import os
import chess

from chessheat.engine import StockfishAdapter, analyze
from chessheat.models import AnalysisRecord, Score
from chessheat.consequence import compute_regrets
from chessheat.branch import extract_branches
from chessheat.semantics import SemanticSignatureV1, SufficientPosition
from chessheat.experiment import SuiteManifest, SuiteKind, ExperimentSpec, ExperimentResult

PROTOCOL_SHA = "6c599dc2b2705f3958274aef06d8aab15bd8e616"
MANIFEST_SHA = "4337dd0c8ef2579a1b15eb58f5cb00f4bb566c6fdde6ef612f09b2bab2e1ecc7"
AUDIT_SHA = "6c8b38431f73f606145abfdcac5e6e37f2313dc5"
RAW_DIR = "tests/fixtures/t3a4/raw"
RESULTS_DIR = "tests/fixtures/t3a4/results"

def get_hash(filepath):
    sha256 = hashlib.sha256()
    with open(filepath, "rb") as f:
        sha256.update(f.read())
    return sha256.hexdigest()

def verify_manifest():
    manifest_path = "docs/research/t3/t3a4_corpus_manifest.json"
    actual_sha = get_hash(manifest_path)
    if actual_sha != MANIFEST_SHA:
        raise ValueError(f"Manifest SHA mismatch: {actual_sha} != {MANIFEST_SHA}")

    with open(manifest_path, "r", encoding="utf-8") as f:
        manifest = json.load(f)

    if manifest["fixture_count"] != 12:
        raise ValueError("Fixture count != 12")
    if manifest["protocol_commit_sha"] != PROTOCOL_SHA:
        raise ValueError("Protocol SHA mismatch")
    if manifest.get("engine_observations_present") is not False:
        raise ValueError("engine_observations_present is not False")

    # verify order
    for i, fix in enumerate(manifest["fixtures"]):
        if fix["fixture_index"] != i:
            raise ValueError(f"Fixture order mismatch at index {i}")

    return manifest

def median(l):
    if not l: return None
    n = len(l)
    if n % 2 == 1:
        return l[n // 2]
    else:
        return (l[n // 2 - 1] + l[n // 2]) / 2.0

def evaluate_fixture(branches, target_sq, event_role="capture", event_ply=2):
    # Mechanical permutation checks will be done in the test file, but we need a deterministic evaluation here.
    classification = "UNCLASSIFIED"
    failure_reason = None
    short_roots = {}
    all_regrets = {}
    is_evaluable_set_incomplete = False

    # Pass A: Pre-check all horizons to ensure observational completeness and typed-consequence validity
    for b in branches:
        all_regrets[b.root_uci] = {"type": b.regret.type, "value": b.regret.value}
        if b.regret.type != "cp":
            classification = "INCONCLUSIVE"
            failure_reason = "MIXED_MATE_CP"
            is_evaluable_set_incomplete = True

        has_ply_2 = False
        for ev in b.future_evidence:
            if ev.ply == event_ply:
                has_ply_2 = True
                break

        if not has_ply_2:
            short_roots[b.root_uci] = len(b.future_moves)
            classification = "INCONCLUSIVE"
            failure_reason = "INSUFFICIENT_OBSERVED_PV_LENGTH"
            is_evaluable_set_incomplete = True

    root_event_membership = {}
    partition_1 = []
    partition_0 = []
    d = None
    m = None
    p_f = None

    if not is_evaluable_set_incomplete and classification != "INCONCLUSIVE":
        # Pass B: assign E_i for every root
        for b in branches:
            e_i = 0
            for ev in b.future_evidence:
                if ev.ply == event_ply and ev.square == target_sq and ev.role == event_role:
                    e_i = 1
            root_event_membership[b.root_uci] = e_i
            if e_i == 1:
                partition_1.append(b)
            else:
                partition_0.append(b)

        if len(partition_1) < 2 or len(partition_0) < 2:
            classification = "INCONCLUSIVE"
            failure_reason = "INSUFFICIENT_PARTITION_CARDINALITY"
        else:
            r_1 = sorted([b.regret.value for b in partition_1])
            r_0 = sorted([b.regret.value for b in partition_0])

            median_1 = median(r_1)
            median_0 = median(r_0)
            d = median_1 - median_0
            m = min(r_1) - max(r_0)

            diffs = []
            for b1 in partition_1:
                for b0 in partition_0:
                    diffs.append(b1.regret.value - b0.regret.value)
            p_f = median(sorted(diffs))

            classification = "EVALUABLE"

    return {
        "evaluable_status": classification == "EVALUABLE",
        "failure_reason": failure_reason,
        "D_f": d,
        "M_f": m,
        "P_f": p_f,
        "short_roots": short_roots,
        "typed_root_regrets": all_regrets,
        "root_event_membership": root_event_membership,
        "legal_root_ucis": sorted([b.root_uci for b in branches]),
        "unevaluable_roots": sorted(list(short_roots.keys())),
        "evaluable_event_present_roots": sorted([b.root_uci for b in partition_1]),
        "evaluable_event_absent_roots": sorted([b.root_uci for b in partition_0]),
        "is_evaluable_set_incomplete": is_evaluable_set_incomplete
    }

def main():
    os.makedirs(RAW_DIR, exist_ok=True)
    os.makedirs(RESULTS_DIR, exist_ok=True)

    manifest = verify_manifest()

    # Step 2: Acquire exactly one frozen observation for every fixture
    engine = StockfishAdapter(stockfish_path="stockfish", options={"Threads": 1, "Hash": 16})

    raw_files = []
    raw_shas = []

    for idx, fixture in enumerate(manifest["fixtures"]):
        fen = fixture["fen"]
        raw_path = f"{RAW_DIR}/t3a4_f{idx:02d}.json"
        
        if not os.path.exists(raw_path):
            record = analyze(
                fen=fen,
                adapter=engine,
                budget_type="nodes",
                budget_value=100000,
                comparison_perspective="white",
                candidate_policy={}
            )

            raw_data = {
                "fen": fen,
                "fixture_index": idx,
                "target_event": fixture["event"],
                "protocol_sha": PROTOCOL_SHA,
                "manifest_sha": MANIFEST_SHA,
                "engine_name": "Stockfish 18",
                "engine_options": {"Threads": 1, "Hash": 16},
                "search_budget_type": "nodes",
                "search_budget_value": 100000,
                "candidate_policy": {},
                "comparison_perspective": "white",
                "baseline_observation": record.baseline_observation.model_dump(mode="json"),
                "move_observations": [obs.model_dump(mode="json") for obs in record.move_observations]
            }

            with open(raw_path, "w", encoding="utf-8") as f:
                json.dump(raw_data, f, indent=2)

        raw_files.append(raw_path)
        raw_shas.append(get_hash(raw_path))

    # Step 4: Build one genuine S1-v2 identity per fixture
    canonical_sig = SemanticSignatureV1.create_canonical()
    s0_digest = canonical_sig.signature_hash()

    suite = SuiteManifest(
        suite_id="t3a4_suite",
        kind=SuiteKind.MECHANISM_STRESS,
        fixtures={f"t3a4_f{idx:02d}": raw_sha for idx, raw_sha in enumerate(raw_shas)}
    )
    suite_digest = suite.suite_digest()

    fixture_results = []
    spec_digests = []
    artifact_digests = []

    for idx, fixture in enumerate(manifest["fixtures"]):
        raw_path = raw_files[idx]
        raw_sha = raw_shas[idx]

        with open(raw_path, "r", encoding="utf-8") as f:
            raw_data = json.load(f)

        sp_fields = fixture["sufficient_position_fields"]
        sp = SufficientPosition(
            board_arrangement_fen=sp_fields["board_arrangement"],
            side_to_move=sp_fields["side_to_move"],
            castling_rights=sp_fields["castling"],
            en_passant_square=None if sp_fields["en_passant"] == "-" else sp_fields["en_passant"],
            halfmove_clock=sp_fields["halfmove"],
            fullmove_number=sp_fields["fullmove"],
            history_available=False,
            history_identity=None,
            variant="standard"
        )

        spec = ExperimentSpec(
            semantic_signature_version=canonical_sig.version,
            semantic_signature_digest=s0_digest,
            suite_identity="t3a4_suite",
            suite_digest=suite_digest,
            fixture_identity=f"t3a4_f{idx:02d}",
            fixture_digest=raw_sha,
            sufficient_position=sp,
            candidate_policy={},
            producer_identity=raw_data["engine_name"],
            instrument_config=raw_data["engine_options"],
            budget_config={"type": raw_data["search_budget_type"], "value": raw_data["search_budget_value"]},
            line_source="pv",
            hypothesis_identifier="T3a-4",
            spec_version=2,
            comparison_perspective="white"
        )
        spec_digests.append(spec.spec_digest())

        # Step 5: Compute consequence
        move_obs = [Score(**obs["score"]) for obs in raw_data["move_observations"]]
        scores_dict = {obs["uci"]: Score(**obs["score"]) for obs in raw_data["move_observations"]}
        regrets_dict = compute_regrets(scores_dict)

        record_obs = []
        from chessheat.models import MoveObservation
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

        # Two-pass evaluation
        target_sq = fixture["target_square"]
        res = evaluate_fixture(branches, target_sq=target_sq)

        fully_typed_scores = {k: {"type": v.type, "value": v.value, "perspective": v.perspective} for k,v in scores_dict.items()}
        fully_typed_regrets = {k: {"type": v.type, "value": v.value, "perspective": v.perspective} for k,v in regrets_dict.items()}

        payload = {
            "evaluable_status": res["evaluable_status"],
            "failure_reason": res["failure_reason"],
            "protocol_commit": PROTOCOL_SHA,
            "fen": raw_data["fen"],
            "event": raw_data["target_event"],
            "expected_direction": "BAD / HIGHER_REGRET",
            "legal_root_count": len(res["legal_root_ucis"]),
            "evaluable_event_present_roots": res["evaluable_event_present_roots"],
            "evaluable_event_absent_roots": res["evaluable_event_absent_roots"],
            "unevaluable_roots": res["unevaluable_roots"],
            "root_event_membership": res["root_event_membership"],
            "root_uci_to_L_fi_mapping": fixture["root_uci_to_L_fi_mapping"],
            "legal_root_ucis": res["legal_root_ucis"],
            "typed_scores": fully_typed_scores,
            "typed_regrets": fully_typed_regrets,
            "D_f": res["D_f"],
            "M_f": res["M_f"],
            "P_f": res["P_f"],
            "fixture_digest": raw_sha,
            "semantic_signature_digest": s0_digest,
            "suite_identity": "t3a4_suite",
            "suite_digest": suite_digest,
            "spec_digest": spec.spec_digest(),
            "spec_version": 2,
            "comparison_perspective": "white",
            "exact_producer": raw_data["engine_name"],
            "exact_options": raw_data["engine_options"],
            "exact_budget": {"type": raw_data["search_budget_type"], "value": raw_data["search_budget_value"]}
        }

        result_obj = ExperimentResult.create(spec_digest=spec.spec_digest(), data=payload)
        artifact_digests.append(result_obj.artifact_digest)

        with open(f"{RESULTS_DIR}/t3a4_f{idx:02d}_result.json", "w") as f:
            json.dump(result_obj.model_dump(mode="json"), f, indent=2)

        fixture_results.append({
            "fixture_index": idx,
            "target_event": raw_data["target_event"],
            "|L=1|": fixture["L_equals_1_count"],
            "|L=0|": fixture["L_equals_0_count"],
            "|E=1|": len(res["evaluable_event_present_roots"]),
            "|E=0|": len(res["evaluable_event_absent_roots"]),
            "evaluable_status": res["evaluable_status"],
            "failure_reason": res["failure_reason"],
            "D_f": res["D_f"],
            "M_f": res["M_f"],
            "P_f": res["P_f"]
        })

    # Corpus aggregation
    valid_p_fs = [r["P_f"] for r in fixture_results if r["evaluable_status"] and r["P_f"] is not None]
    k = len(valid_p_fs)

    if k < 3:
        d_suite = None
        m_suite = None
        classification = "INCONCLUSIVE"
        failure_reason = "INSUFFICIENT_REALIZED_EVENT_SUPPORT_ACROSS_CORPUS"
    else:
        d_suite = median(sorted(valid_p_fs))
        m_suite = min(valid_p_fs)
        failure_reason = None
        if d_suite > 0 and m_suite > 0:
            classification = "SUPPORTED"
        elif d_suite > 0 and m_suite <= 0:
            classification = "WEAK_SUPPORT"
        else:
            classification = "FALSIFIED"

    corpus_payload = {
        "protocol_sha": PROTOCOL_SHA,
        "manifest_commit": "70fe6bd7a970732b44ec8117e6327569ac84140a",
        "manifest_sha": MANIFEST_SHA,
        "audit_sha": AUDIT_SHA,
        "suite_digest": suite_digest,
        "raw_fixture_digests": raw_shas,
        "spec_digests": spec_digests,
        "artifact_digests": artifact_digests,
        "fixture_results": fixture_results,
        "informative_fixture_count": k,
        "D_suite": d_suite,
        "M_suite": m_suite,
        "final_classification": classification,
        "final_failure_reason": failure_reason,
        "interpretation_constraint": "A preregistered deterministic rule-selected 12-position corpus drawn from one generated trajectory."
    }

    # Canonicalize and hash corpus artifact
    corpus_json = json.dumps(corpus_payload, sort_keys=True, separators=(',', ':')).encode("utf-8")
    corpus_artifact_digest = hashlib.sha256(corpus_json).hexdigest()
    
    corpus_payload["corpus_artifact_digest"] = corpus_artifact_digest

    with open("tests/fixtures/t3a4/t3a4_corpus_result.json", "w") as f:
        json.dump(corpus_payload, f, indent=2)

    print("--- T3a-4 Execution Report ---")
    print(f"Shared suite digest: {suite_digest}")
    print(f"Corpus result artifact digest: {corpus_artifact_digest}")
    print(f"Informative fixture count K: {k}")
    print(f"D_suite: {d_suite}")
    print(f"M_suite: {m_suite}")
    print(f"Classification: {classification}")
    print(f"Failure reason: {failure_reason}")

if __name__ == "__main__":
    main()
