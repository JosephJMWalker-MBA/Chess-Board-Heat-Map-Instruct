import json
import hashlib
import fractions
import sys
import os
from chessheat.semantics import SufficientPosition
from chessheat.experiment import ExperimentSpec, ExperimentResult, SuiteManifest, SuiteKind

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

def analyze():
    # Load raw
    with open("tests/fixtures/t3b3/t3b3_raw_execution.json", "rb") as f:
        raw_bytes = f.read()
    raw_sha = hashlib.sha256(raw_bytes).hexdigest()
    raw = json.loads(raw_bytes.decode("utf-8"))
    
    # Load manifest
    with open("docs/research/t3/t3b2_fixture_manifest.json", "r", encoding="utf-8") as f:
        manifest = json.load(f)
        
    fixtures_by_index = {f["fixture_index"]: f for f in manifest["fixtures"]}
    
    # Step 1: Validate and compute statistics
    results = []
    
    for raw_f in raw["fixtures"]:
        idx = raw_f["fixture_index"]
        man_f = fixtures_by_index[idx]
        
        # Validation
        obs_ucis = [r["uci"] for r in raw_f["observed_replies"]]
        assert obs_ucis == man_f["legal_reply_ucis"], f"Observed replies mismatch for index {idx}"
        assert raw_f["C_reply_ucis"] == man_f["C_reply_ucis"]
        assert raw_f["N_reply_ucis"] == man_f["N_reply_ucis"]
        
        for r_obs in raw_f["observed_replies"]:
            man_r = next(r for r in man_f["replies"] if r["uci"] == r_obs["uci"])
            assert r_obs["child_fen"] == man_r["child_fen"]
            
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
            L = 0
            E = 0
            total_Z = 0
            for z_keys in itertools.combinations(all_keys, 2):
                total_Z += 1
                z_c = [y_all[k] for k in z_keys]
                z_n = [y_all[k] for k in all_keys if k not in z_keys]
                s_z = compute_S(z_c, z_n)
                
                if s_z < s_u:
                    L += 1
                elif s_z == s_u:
                    E += 1
                    
            q_u = fractions.Fraction(2 * L + E, 2 * total_Z)
            
            delta_u = exact_median(y_c) - exact_median(y_n)
            
        results.append({
            "fixture_index": idx,
            "evaluable": evaluable,
            "failure_reason": failure_reason,
            "s_u": s_u,
            "q_u": q_u,
            "delta_u": delta_u,
            "man_f": man_f,
            "raw_f": raw_f,
            "y_all": y_all if evaluable else None
        })

    # Step 2: Suite Classification
    evaluable_results = [r for r in results if r["evaluable"]]
    K = len(evaluable_results)
    
    classification = None
    q_suite = None
    h_75 = None
    suite_failure = None
    
    if K < 8:
        classification = "INCONCLUSIVE"
        suite_failure = "INSUFFICIENT_TYPED_INTERVENTION_FIXTURES"
    else:
        q_vals = [r["q_u"] for r in evaluable_results]
        q_suite = exact_median(q_vals)
        h_75 = sum(1 for q in q_vals if q >= fractions.Fraction(3, 4))
        import math
        if q_suite >= fractions.Fraction(3, 4) and h_75 >= math.ceil(0.75 * K):
            classification = "SUPPORTED"
        elif q_suite > fractions.Fraction(1, 2):
            classification = "WEAK_SUPPORT"
        else:
            classification = "FALSIFIED"
            
    # Step 3: Build S1 identity
    manifest_digests = {}
    for man_f in manifest["fixtures"]:
        fixture_id = f"t3b2_f{man_f['fixture_index']:02d}"
        f_bytes = json.dumps(man_f, sort_keys=True, separators=(',', ':')).encode('utf-8')
        manifest_digests[fixture_id] = hashlib.sha256(f_bytes).hexdigest()
        
    suite_manifest = SuiteManifest(
        suite_id="t3b2_rule_only_intervention_suite",
        kind=SuiteKind.MECHANISM_STRESS,
        fixtures=manifest_digests
    )
    # Use standard pydantic to dict then hash
    suite_json = json.dumps(suite_manifest.model_dump(), sort_keys=True, separators=(',', ':'))
    suite_digest = hashlib.sha256(suite_json.encode('utf-8')).hexdigest()
    
    S0_DIGEST = "5fa4d57cf43c673fa31874ce5d19e777acf0ea695fd032412b193c2123461080"
    
    os.makedirs("tests/fixtures/t3b3/results", exist_ok=True)
    
    spec_digests = []
    result_digests = []
    
    for r in results:
        man_f = r["man_f"]
        idx = r["fixture_index"]
        fixture_id = f"t3b2_f{idx:02d}"
        
        # Build SufficientPosition from Pi
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
            semantic_signature_version="1",
            semantic_signature_digest=S0_DIGEST,
            suite_identity="t3b2_rule_only_intervention_suite",
            suite_digest=suite_digest,
            fixture_identity=fixture_id,
            fixture_digest=manifest_digests[fixture_id],
            sufficient_position=sp,
            candidate_policy={"scope": "all_legal_replies"},
            producer_identity=raw["actual_uci_engine_name"],
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
        
        spec_json = json.dumps(spec.model_dump(), sort_keys=True, separators=(',', ':'))
        spec_digest = hashlib.sha256(spec_json.encode('utf-8')).hexdigest()
        spec_digests.append(spec_digest)
        
        def frac_to_dict(f):
            if f is None:
                return None
            return {
                "numerator": f.numerator,
                "denominator": f.denominator,
                "decimal": float(f)
            }
            
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
            "evaluable": r["evaluable"],
            "failure_reason": r["failure_reason"],
            "s_u": frac_to_dict(r["s_u"]),
            "q_u": frac_to_dict(r["q_u"]),
            "delta_u": frac_to_dict(r["delta_u"]),
            "typed_outcomes": [obs["outcome"] for obs in r["raw_f"]["observed_replies"]],
            "actual_engine_identity": raw["actual_uci_engine_name"],
            "engine_binary_sha": raw["engine_binary_sha256"],
            "options": {"Threads": raw["threads"], "Hash": raw["hash"]},
            "budget": raw["node_budget"],
            "suite_digest": suite_digest,
            "spec_digest": spec_digest,
            "evidence_level": "intervention_sensitivity"
        }
        
        # Make a deterministic observation subset digest based on the typed outcomes
        out_json = json.dumps(payload["typed_outcomes"], sort_keys=True, separators=(',', ':'))
        payload["observation_subset_digest"] = hashlib.sha256(out_json.encode('utf-8')).hexdigest()
        
        result_obj = ExperimentResult.create(spec_digest, payload)
        
        result_file_path = f"tests/fixtures/t3b3/results/t3b3_f{idx:02d}_result.json"
        with open(result_file_path, "w", encoding="utf-8") as f:
            f.write(result_obj.model_dump_json(indent=2))
            
        # compute digest of the result string for aggregate
        result_json_str = result_obj.model_dump_json(indent=2)
        result_digests.append(hashlib.sha256(result_json_str.encode("utf-8")).hexdigest())

    # Create aggregate
    aggregate = {
        "raw_execution_sha": raw_sha,
        "manifest_fixture_digests": list(manifest_digests.values()),
        "suite_digest": suite_digest,
        "spec_digests": spec_digests,
        "result_digests": result_digests,
        "fixture_summaries": [
            {
                "fixture_index": r["fixture_index"],
                "evaluable": r["evaluable"],
                "s_u": frac_to_dict(r["s_u"]),
                "q_u": frac_to_dict(r["q_u"]),
                "delta_u": frac_to_dict(r["delta_u"])
            }
            for r in results
        ],
        "K": K,
        "q_suite": frac_to_dict(q_suite),
        "H_0_75": h_75,
        "classification": classification,
        "failure_reason": suite_failure
    }
    
    agg_json = json.dumps(aggregate, sort_keys=True, indent=2, ensure_ascii=False) + "\n"
    agg_sha = hashlib.sha256(agg_json.encode("utf-8")).hexdigest()
    
    with open("tests/fixtures/t3b3/t3b3_corpus_result.json", "w", encoding="utf-8") as f:
        f.write(agg_json)
        
    print(f"Aggregate SHA: {agg_sha}")
    
if __name__ == "__main__":
    analyze()
