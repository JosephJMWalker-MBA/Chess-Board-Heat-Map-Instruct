import json
import hashlib
import fractions
import sys
import os
from chessheat.semantics import SufficientPosition, SemanticSignatureV1
from chessheat.experiment import ExperimentSpec, ExperimentResult, SuiteManifest, SuiteKind

RAW_SHA = "9333f9d26480f43f4d64846be498f720892d93d73da5127296e067653b476d6b"

def exact_median(values):
    if not values:
        return fractions.Fraction(0, 1)
    sorted_vals = sorted(values)
    n = len(sorted_vals)
    if n % 2 == 1:
        return fractions.Fraction(sorted_vals[n // 2], 1)
    else:
        return fractions.Fraction(sorted_vals[n // 2 - 1] + sorted_vals[n // 2], 2)

def compute_S(y_c, y_n):
    P = len(y_c) * len(y_n)
    if P == 0:
        return fractions.Fraction(0, 1)
    G = sum(1 for c in y_c for n in y_n if c > n)
    T = sum(1 for c in y_c for n in y_n if c == n)
    return fractions.Fraction(abs(2 * G + T - P), P)

def run_closeout():
    with open("tests/fixtures/t3b3/t3b3_raw_execution.json", "rb") as f:
        raw_bytes = f.read()
    raw_sha = hashlib.sha256(raw_bytes).hexdigest()
    assert raw_sha == RAW_SHA
    raw = json.loads(raw_bytes.decode("utf-8"))
    
    with open("docs/research/t3/t3b2_fixture_manifest.json", "r", encoding="utf-8") as f:
        manifest = json.load(f)
        
    fixtures_by_index = {f["fixture_index"]: f for f in manifest["fixtures"]}
    
    manifest_digests = {}
    for man_f in manifest["fixtures"]:
        fixture_id = f"t3b2_f{man_f['fixture_index']:02d}"
        f_bytes = json.dumps(man_f, sort_keys=True, separators=(',', ':')).encode('utf-8')
        manifest_digests[fixture_id] = hashlib.sha256(f_bytes).hexdigest()
        
    suite = SuiteManifest(
        suite_id="t3b2_rule_only_intervention_suite",
        kind=SuiteKind.MECHANISM_STRESS,
        fixtures=manifest_digests
    )
    suite_digest = suite.suite_digest()
    assert suite_digest == "2eb662fbe081c82e325f41bf387c509383567b9a9f084fa7baff56e7e26cc70a", suite_digest
    
    canonical_sig = SemanticSignatureV1.create_canonical()
    assert canonical_sig.version == "1.0"
    assert canonical_sig.signature_hash() == "5fa4d57cf43c673fa31874ce5d19e777acf0ea695fd032412b193c2123461080"
    
    os.makedirs("tests/fixtures/t3b3/s1_corrected/results", exist_ok=True)
    
    results = []
    
    spec_digests = []
    result_artifact_digests = []
    result_file_shas = []
    
    for raw_f in raw["fixtures"]:
        idx = raw_f["fixture_index"]
        man_f = fixtures_by_index[idx]
        
        evaluable = True
        failure_reason = None
        y_all = {}
        for r_obs in raw_f["observed_replies"]:
            outcome = r_obs["outcome"]
            if outcome["type"] == "mate":
                evaluable = False
                failure_reason = "NON_CP_CHILD_PRESENT"
                break
            y_all[r_obs["uci"]] = outcome["value"]
            
        s_u = None
        q_u = None
        delta_u = None
        
        if evaluable:
            c_keys = man_f["C_reply_ucis"]
            all_keys = sorted(y_all.keys())
            y_c = [y_all[k] for k in c_keys]
            y_n = [y_all[k] for k in all_keys if k not in c_keys]
            
            s_u = compute_S(y_c, y_n)
            import itertools
            L = 0; E = 0; total_Z = 0
            for z_keys in itertools.combinations(all_keys, 2):
                total_Z += 1
                z_c = [y_all[k] for k in z_keys]
                z_n = [y_all[k] for k in all_keys if k not in z_keys]
                s_z = compute_S(z_c, z_n)
                if s_z < s_u: L += 1
                elif s_z == s_u: E += 1
            q_u = fractions.Fraction(2 * L + E, 2 * total_Z)
            delta_u = exact_median(y_c) - exact_median(y_n)
            
        results.append({
            "fixture_index": idx,
            "evaluable": evaluable,
            "failure_reason": failure_reason,
            "s_u": s_u, "q_u": q_u, "delta_u": delta_u,
            "raw_f": raw_f, "man_f": man_f
        })
        
        # Build ExperimentSpec
        fixture_id = f"t3b2_f{idx:02d}"
        pi_fen = man_f["intervention_fen"]
        parts = pi_fen.split()
        sp = SufficientPosition(
            board_arrangement_fen=parts[0],
            side_to_move="black",
            castling_rights=parts[2],
            en_passant_square=parts[3] if parts[3] != "-" else None,
            halfmove_clock=int(parts[4]),
            fullmove_number=int(parts[5]),
            history_available=False,
            history_identity=None,
            variant="standard"
        )
        
        spec = ExperimentSpec(
            semantic_signature_version=canonical_sig.version,
            semantic_signature_digest=canonical_sig.signature_hash(),
            suite_identity="t3b2_rule_only_intervention_suite",
            suite_digest=suite_digest,
            fixture_identity=fixture_id,
            fixture_digest=manifest_digests[fixture_id],
            sufficient_position=sp,
            candidate_policy={"scope": "all_legal_replies"},
            producer_identity="Stockfish 18",
            instrument_config={
                "binary_sha256": raw["engine_binary_sha256"],
                "Threads": raw["threads"],
                "Hash": raw["hash"],
                "policy": raw["game_state_policy"]
            },
            budget_config={"type": "nodes", "value": raw["node_budget"]},
            line_source="none",
            hypothesis_identifier="T3b-2",
            spec_version=2,
            comparison_perspective="white"
        )
        spec_digest = spec.spec_digest()
        spec_digests.append(spec_digest)
        
        def frac_to_dict(f):
            if f is None: return None
            return {"numerator": f.numerator, "denominator": f.denominator, "decimal": float(f)}
            
        identity_obs = []
        for obs in raw_f["observed_replies"]:
            identity_obs.append({
                "uci": obs["uci"],
                "child_fen": obs["child_fen"],
                "outcome": obs["outcome"]
            })
            
        obs_subset_json = json.dumps(identity_obs, sort_keys=True, separators=(',', ':'))
        obs_subset_digest = hashlib.sha256(obs_subset_json.encode('utf-8')).hexdigest()
        
        payload = {
            "protocol_commit": raw["protocol_commit"],
            "manifest_commit": raw["manifest_commit"],
            "integrity_commit": raw["integrity_commit"],
            "execution_code_commit": raw["execution_code_commit"],
            "raw_execution_sha": raw_sha,
            "manifest_fixture_digest": manifest_digests[fixture_id],
            "target_destination_event": man_f["target_event"]["square"],
            "R": man_f["legal_reply_ucis"],
            "C": man_f["C_reply_ucis"],
            "N": man_f["N_reply_ucis"],
            "evaluable": evaluable,
            "failure_reason": failure_reason,
            "s_u": frac_to_dict(s_u),
            "q_u": frac_to_dict(q_u),
            "delta_u": frac_to_dict(delta_u),
            "typed_observations_with_identity": identity_obs,
            "observation_subset_digest": obs_subset_digest,
            "actual_engine_identity": raw["actual_uci_engine_name"],
            "engine_binary_sha": raw["engine_binary_sha256"],
            "options": {"Threads": raw["threads"], "Hash": raw["hash"]},
            "budget": raw["node_budget"],
            "suite_digest": suite_digest,
            "spec_digest": spec_digest,
            "evidence_level": "intervention_sensitivity"
        }
        
        result_obj = ExperimentResult.create(spec_digest=spec_digest, data=payload)
        result_artifact_digests.append(result_obj.artifact_digest)
        
        res_file = f"tests/fixtures/t3b3/s1_corrected/results/t3b3_f{idx:02d}_result.json"
        res_json_str = result_obj.model_dump_json(indent=2)
        with open(res_file, "w", encoding="utf-8") as f:
            f.write(res_json_str)
        result_file_shas.append(hashlib.sha256(res_json_str.encode('utf-8')).hexdigest())

    evaluable_results = [r for r in results if r["evaluable"]]
    K = len(evaluable_results)
    q_vals = [r["q_u"] for r in evaluable_results]
    q_suite = exact_median(q_vals)
    h_75 = sum(1 for q in q_vals if q >= fractions.Fraction(3, 4))
    
    assert K == 11
    assert q_suite == fractions.Fraction(148, 253)
    assert h_75 == 4
    classification = "WEAK_SUPPORT"
    
    aggregate_payload = {
        "historical_execution_commit": "567c40232d0b4d6a7de0c68c2aebb7d0acec0876",
        "raw_execution_sha": raw_sha,
        "frozen_manifest_sha": "27321ceb4bf5c48716d836f9d4433c017be3a127e94b6d1508bd8973e0d23bc0",
        "canonical_suite_digest": suite_digest,
        "spec_digests": spec_digests,
        "result_artifact_digests": result_artifact_digests,
        "result_file_shas": result_file_shas,
        "fixture_summaries": [
            {
                "fixture_index": r["fixture_index"],
                "evaluable": r["evaluable"],
                "s_u": {"numerator": r["s_u"].numerator, "denominator": r["s_u"].denominator, "decimal": float(r["s_u"])} if r["s_u"] else None,
                "q_u": {"numerator": r["q_u"].numerator, "denominator": r["q_u"].denominator, "decimal": float(r["q_u"])} if r["q_u"] else None,
                "delta_u": {"numerator": r["delta_u"].numerator, "denominator": r["delta_u"].denominator, "decimal": float(r["delta_u"])} if r["delta_u"] else None
            }
            for r in results
        ],
        "K": K,
        "q_suite": {"numerator": q_suite.numerator, "denominator": q_suite.denominator, "decimal": float(q_suite)},
        "H_0_75": h_75,
        "classification": classification
    }
    
    agg_payload_json = json.dumps(aggregate_payload, sort_keys=True, separators=(',', ':'))
    agg_payload_digest = hashlib.sha256(agg_payload_json.encode('utf-8')).hexdigest()
    
    aggregate_full = {
        "aggregate_payload_digest": agg_payload_digest,
        "payload": aggregate_payload
    }
    
    agg_json_str = json.dumps(aggregate_full, sort_keys=True, indent=2, ensure_ascii=False) + "\n"
    with open("tests/fixtures/t3b3/s1_corrected/t3b3_corpus_result.json", "w", encoding="utf-8") as f:
        f.write(agg_json_str)

    print("Canonical Suite Digest:", suite_digest)
    print("Aggregate Payload Digest:", agg_payload_digest)
    print("Spec Digests:")
    for d in spec_digests: print(d)
    print("Artifact Digests:")
    for d in result_artifact_digests: print(d)

if __name__ == "__main__":
    run_closeout()
