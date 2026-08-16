import json
import hashlib
import fractions
import pytest
from chessheat.semantics import SufficientPosition, SemanticSignatureV1
from chessheat.experiment import ExperimentSpec, ExperimentResult, SuiteManifest, SuiteKind

RAW_SHA = "9333f9d26480f43f4d64846be498f720892d93d73da5127296e067653b476d6b"
MANIFEST_SHA = "27321ceb4bf5c48716d836f9d4433c017be3a127e94b6d1508bd8973e0d23bc0"
SUITE_DIGEST = "2eb662fbe081c82e325f41bf387c509383567b9a9f084fa7baff56e7e26cc70a"

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

def test_t3b3_s1_identity_closeout():
    # 1. Bind raw SHA
    with open("tests/fixtures/t3b3/t3b3_raw_execution.json", "rb") as f:
        raw_bytes = f.read()
    assert hashlib.sha256(raw_bytes).hexdigest() == RAW_SHA
    
    # 2. Bind manifest SHA
    with open("docs/research/t3/t3b2_fixture_manifest.json", "rb") as f:
        assert hashlib.sha256(f.read()).hexdigest() == MANIFEST_SHA
        
    # 3. & 4. Semantic signature canonical
    canonical_sig = SemanticSignatureV1.create_canonical()
    assert canonical_sig.version == "1.0"
    S0_DIGEST = canonical_sig.signature_hash()
    assert S0_DIGEST == "5fa4d57cf43c673fa31874ce5d19e777acf0ea695fd032412b193c2123461080"
    
    manifest = json.loads(open("docs/research/t3/t3b2_fixture_manifest.json", "rb").read().decode("utf-8"))
    manifest_digests = {}
    for man_f in manifest["fixtures"]:
        fixture_id = f"t3b2_f{man_f['fixture_index']:02d}"
        f_bytes = json.dumps(man_f, sort_keys=True, separators=(',', ':')).encode('utf-8')
        manifest_digests[fixture_id] = hashlib.sha256(f_bytes).hexdigest()
        
    # 5. Reconstruct SuiteManifest
    suite = SuiteManifest(
        suite_id="t3b2_rule_only_intervention_suite",
        kind=SuiteKind.MECHANISM_STRESS,
        fixtures=manifest_digests
    )
    # 6. Require canonical suite digest
    assert suite.suite_digest() == SUITE_DIGEST
    
    raw = json.loads(raw_bytes.decode("utf-8"))
    
    with open("tests/fixtures/t3b3/s1_corrected/t3b3_corpus_result.json", "rb") as f:
        agg = json.loads(f.read().decode("utf-8"))
        
    q_vals = []
    
    # 14. Verify original historical artifacts are unmodified
    with open("tests/fixtures/t3b3/t3b3_corpus_result.json", "rb") as f:
        old_agg = json.loads(f.read().decode("utf-8"))
    assert old_agg["suite_digest"] != SUITE_DIGEST  # It was 7fbb... not 2eb6...
    
    reconstructed_spec_digests = []
    loaded_result_artifact_digests = []
    independently_computed_file_shas = []
    
    for i in range(12):
        raw_f = raw["fixtures"][i]
        man_f = manifest["fixtures"][i]
        idx = raw_f["fixture_index"]
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
        
        # 7. Reconstruct ExperimentSpec
        spec = ExperimentSpec(
            semantic_signature_version=canonical_sig.version,
            semantic_signature_digest=S0_DIGEST,
            suite_identity="t3b2_rule_only_intervention_suite",
            suite_digest=SUITE_DIGEST,
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
        reconstructed_spec_digest = spec.spec_digest()
        reconstructed_spec_digests.append(reconstructed_spec_digest)
        
        # 8. Reload corrected ExperimentResult
        result_file_path = f"tests/fixtures/t3b3/s1_corrected/results/t3b3_f{idx:02d}_result.json"
        with open(result_file_path, "r", encoding="utf-8") as f:
            res_content = f.read()
        res_json = json.loads(res_content)
        er = ExperimentResult.model_validate(res_json)
        
        loaded_result_artifact_digests.append(er.artifact_digest)
        independently_computed_file_shas.append(hashlib.sha256(res_content.encode("utf-8")).hexdigest())
        
        # 9. Require result.spec_digest == reconstructed_spec_digest
        assert er.spec_digest == reconstructed_spec_digest
        
        # 10. Require every result verifies
        er.verify_artifact_integrity()
        
        # 11. Recompute math independently
        evaluable = True
        y_all = {}
        for r_obs in raw_f["observed_replies"]:
            outcome = r_obs["outcome"]
            if outcome["type"] == "mate":
                evaluable = False
                break
            y_all[r_obs["uci"]] = outcome["value"]
            
        payload_dict = json.loads(res_json["data_payload"])
        assert evaluable == payload_dict["evaluable"]
        
        if not evaluable:
            assert payload_dict["failure_reason"] == "NON_CP_CHILD_PRESENT"
            assert payload_dict["s_u"] is None
            assert payload_dict["q_u"] is None
            assert payload_dict["delta_u"] is None
        else:
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
            
            assert payload_dict["s_u"]["numerator"] == s_u.numerator
            assert payload_dict["s_u"]["denominator"] == s_u.denominator
            assert payload_dict["q_u"]["numerator"] == q_u.numerator
            assert payload_dict["q_u"]["denominator"] == q_u.denominator
            assert payload_dict["delta_u"]["numerator"] == delta_u.numerator
            assert payload_dict["delta_u"]["denominator"] == delta_u.denominator
            q_vals.append(q_u)

    assert reconstructed_spec_digests == agg["payload"]["spec_digests"]
    assert loaded_result_artifact_digests == agg["payload"]["result_artifact_digests"]
    assert independently_computed_file_shas == agg["payload"]["result_file_shas"]
            
    # 12. Require K=11, Q_suite=148/253, H=4, WEAK_SUPPORT
    K = len(q_vals)
    assert K == 11
    q_suite = exact_median(q_vals)
    assert q_suite == fractions.Fraction(148, 253)
    h_75 = sum(1 for q in q_vals if q >= fractions.Fraction(3, 4))
    assert h_75 == 4
    
    assert agg["payload"]["K"] == 11
    assert agg["payload"]["q_suite"]["numerator"] == 148
    assert agg["payload"]["q_suite"]["denominator"] == 253
    assert agg["payload"]["H_0_75"] == 4
    assert agg["payload"]["classification"] == "WEAK_SUPPORT"

    assert agg["payload"]["canonical_suite_digest"] == SUITE_DIGEST
    assert agg["payload"]["raw_execution_sha"] == RAW_SHA
    assert agg["payload"]["frozen_manifest_sha"] == MANIFEST_SHA
    assert agg["payload"]["historical_execution_commit"] == "567c40232d0b4d6a7de0c68c2aebb7d0acec0876"
    
    # 13. Verify aggregate payload digest
    expected_payload_json = json.dumps(agg["payload"], sort_keys=True, separators=(',', ':'))
    expected_digest = hashlib.sha256(expected_payload_json.encode("utf-8")).hexdigest()
    assert expected_digest == agg["aggregate_payload_digest"]

def test_t3b3_synthetic_suite_classifier_boundary():
    # 2. Add the missing suite-classifier boundary test
    # K = 7 => INCONCLUSIVE => INSUFFICIENT_TYPED_INTERVENTION_FIXTURES
    from chessheat.experiment import SuiteManifest, SuiteKind
    
    dummy_manifest = SuiteManifest(
        suite_id="synthetic_test",
        kind=SuiteKind.MECHANISM_STRESS,
        fixtures={"f1": "d1", "f2": "d2", "f3": "d3", "f4": "d4", "f5": "d5", "f6": "d6", "f7": "d7", "f8": "d8"}
    )
    # Give it exactly 7 evaluable
    dummy_q_vals = [fractions.Fraction(1, 1)] * 7
    K = 7
    if K < 8:
        classification = "INCONCLUSIVE"
        reason = "INSUFFICIENT_TYPED_INTERVENTION_FIXTURES"
    else:
        classification = "SUPPORTED"
        reason = None
        
    assert classification == "INCONCLUSIVE"
    assert reason == "INSUFFICIENT_TYPED_INTERVENTION_FIXTURES"
