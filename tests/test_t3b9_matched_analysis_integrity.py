import json
import hashlib
from fractions import Fraction
import sys
import os
import math

sys.path.insert(0, os.path.abspath("src"))
from chessheat.experiment import ExperimentSpec, ExperimentResult

def get_file_sha(path):
    with open(path, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()

def serialize_rational(r: Fraction):
    if r is None:
        return None
    return {"numerator": r.numerator, "denominator": r.denominator}

def compute_D(G, T, m):
    return Fraction(2 * G + T - m, m)

def reject_keys(obj, bad_keys):
    if isinstance(obj, dict):
        for k, v in obj.items():
            assert k not in bad_keys, f"Found rejected key {k}"
            reject_keys(v, bad_keys)
    elif isinstance(obj, list):
        for item in obj:
            reject_keys(item, bad_keys)

def test_t3b9_matched_analysis_integrity():
    assert compute_D(0, 0, 5) == Fraction(-1, 1)
    assert compute_D(5, 0, 5) == Fraction(1, 1)
    assert compute_D(1, 0, 2) == Fraction(0, 1)
    assert compute_D(0, 1, 2) == Fraction(-1, 2)
    
    raw_path = "tests/fixtures/t3b8/t3b8_raw_acquisition.json"
    manifest_path = "docs/research/t3/t3b7_matched_fixture_manifest.json"
    bundle_path = "docs/research/t3/t3b8_presearch_spec_bundle.json"
    analysis_path = "docs/research/t3/t3b9_matched_analysis.json"
    
    with open(raw_path) as f: raw = json.load(f)
    with open(manifest_path) as f: manifest = json.load(f)
    with open(bundle_path) as f: bundle = json.load(f)
    with open(analysis_path) as f: analysis = json.load(f)
        
    fixtures_results = []
    
    evaluable_Q = []
    
    for f_idx, raw_fix in enumerate(raw["fixtures"]):
        man_fix = manifest["fixtures"][f_idx]
        bun_fix = bundle["specs"][f_idx]
        
        result_model = ExperimentResult(**raw_fix["experiment_result"])
        payload = json.loads(result_model.data_payload)
        outcome_map = {obs["uci"]: obs["outcome"] for obs in payload["observed_replies"]}
        
        c_1 = man_fix["c_1"]
        c_2 = man_fix["c_2"]
        M_1_ucis = man_fix["M_1_ucis"]
        M_2_ucis = man_fix["M_2_ucis"]
        H_1_ucis = man_fix["H_1_ucis"]
        H_2_ucis = man_fix["H_2_ucis"]
        
        m_1 = len(M_1_ucis)
        m_2 = len(M_2_ucis)
        
        # Check evaluability
        evaluable = True
        reason = None
        for uci in H_1_ucis + H_2_ucis:
            if outcome_map[uci]["type"] == "mate":
                evaluable = False
                reason = "NON_CP_MATCHED_CHILD_PRESENT"
                break
                
        fix_rec = {
            "fixture_identity": man_fix["fixture_identity"],
            "fixture_index": f_idx,
            "spec_digest": bun_fix["spec_digest"],
            "experiment_result_artifact_digest": result_model.artifact_digest,
            "c_1": c_1,
            "c_2": c_2,
            "M_1_ucis": M_1_ucis,
            "M_2_ucis": M_2_ucis,
            "H_1_ucis": H_1_ucis,
            "H_2_ucis": H_2_ucis,
            "m_1": m_1,
            "m_2": m_2,
            "evaluable": evaluable,
            "evaluability_reason": reason
        }
        
        if not evaluable:
            fix_rec.update({
                "G_1": None, "T_1": None, "D_1": None, "S_1": None,
                "G_2": None, "T_2": None, "D_2": None, "S_2": None,
                "S_match": None, "omega_size": None, "L": None, "E": None, "Q": None
            })
        else:
            def get_cp(u): return outcome_map[u]["value"]
            
            def calc_z(z, H_j_ucis):
                G = 0
                T = 0
                mz = len(H_j_ucis) - 1
                Y_z = get_cp(z)
                for n in H_j_ucis:
                    if n == z: continue
                    Y_n = get_cp(n)
                    if Y_z > Y_n: G += 1
                    elif Y_z == Y_n: T += 1
                D = compute_D(G, T, mz)
                S = abs(D)
                return G, T, D, S
            
            G_1, T_1, D_1, S_1 = calc_z(c_1, H_1_ucis)
            G_2, T_2, D_2, S_2 = calc_z(c_2, H_2_ucis)
            
            S_match = Fraction(S_1 + S_2, 2)
            
            # Calibration
            omega_size = len(H_1_ucis) * len(H_2_ucis)
            L = 0
            E = 0
            
            for z1 in H_1_ucis:
                _, _, _, sz1 = calc_z(z1, H_1_ucis)
                for z2 in H_2_ucis:
                    _, _, _, sz2 = calc_z(z2, H_2_ucis)
                    S_u = Fraction(sz1 + sz2, 2)
                    if S_u < S_match:
                        L += 1
                    elif S_u == S_match:
                        E += 1
            
            Q = Fraction(2 * L + E, 2 * omega_size)
            evaluable_Q.append(Q)
            
            fix_rec.update({
                "G_1": G_1, "T_1": T_1, "D_1": serialize_rational(D_1), "S_1": serialize_rational(S_1),
                "G_2": G_2, "T_2": T_2, "D_2": serialize_rational(D_2), "S_2": serialize_rational(S_2),
                "S_match": serialize_rational(S_match), "omega_size": omega_size, "L": L, "E": E, "Q": serialize_rational(Q)
            })
            
            # Additional assertions required by the prompt
            assert D_1.denominator > 0
            assert S_1.denominator > 0
            assert D_2.denominator > 0
            assert S_2.denominator > 0
            assert S_match.denominator > 0
            assert Q.denominator > 0
            assert math.gcd(D_1.numerator, D_1.denominator) == 1
            assert math.gcd(S_1.numerator, S_1.denominator) == 1
            assert math.gcd(D_2.numerator, D_2.denominator) == 1
            assert math.gcd(S_2.numerator, S_2.denominator) == 1
            assert math.gcd(S_match.numerator, S_match.denominator) == 1
            assert math.gcd(Q.numerator, Q.denominator) == 1
            
        fixtures_results.append(fix_rec)
        
    K = len(evaluable_Q)
    K_min = 12
    
    Q_suite = None
    if K >= K_min:
        sorted_Q = sorted(evaluable_Q)
        if K % 2 == 1:
            Q_suite = sorted_Q[K // 2]
        else:
            Q_suite = Fraction(sorted_Q[K // 2 - 1] + sorted_Q[K // 2], 2)
            
    H_0_75 = sum(1 for q in evaluable_Q if q >= Fraction(3, 4)) if K > 0 else 0
    H_required = (3 * K + 3) // 4 if K > 0 else 0
    
    classification = "INCONCLUSIVE"
    reason = None
    
    if K < K_min:
        classification = "INCONCLUSIVE"
        reason = "INSUFFICIENT_TYPED_MATCHED_FIXTURES"
    else:
        if Q_suite >= Fraction(3, 4) and H_0_75 >= H_required:
            classification = "SUPPORTED"
        elif Q_suite > Fraction(1, 2):
            classification = "WEAK_SUPPORT"
        else:
            classification = "FALSIFIED"
            
    expected_artifact = {
        "schema_version": 1,
        "phase": "T3B9_FROZEN_MATCHED_ANALYSIS",
        "mathematics_commit": "100e4f20b41b260875fb14901b61bbe51c4fe74e",
        "protocol_commit": "fd54ad04c54e4756ad904f17454b9e70e881afea",
        "raw_acquisition_commit": "ee31be200a1d1dcb6049892ce14cb3c74767694f",
        "raw_integrity_commit": "e69348f4ef943cae55f423d52e924f6fe92800d0",
        "mathematics_file_sha256": "7f395355e2505db8cc24468e541db5f9618d81c206a8f489c30a09607b0ac8a8",
        "protocol_file_sha256": "2b9377a46b5ff54453ec1796b9a5ce8ca3f1e7bf36a112820d9390b69ed819b9",
        "raw_acquisition_sha256": "5d89d9efde0b140bd134a4e9e3e57092120619acf335c05fcbd2bb9bf1d09b2e",
        "manifest_sha256": "40949ceeaa5ff1cd1c8a083df45f0dbe0f252d3f1637a692dbf96ae98156ad13",
        "presearch_bundle_sha256": "6ce6b91d3839998f2b9f24c3c6368cbb30cf799c1e8ddaeb9a9a3dcfc54e957b",
        "s1_suite_digest": "b483e152cbfd51704f62befabdfd2a9f7880999a199409b63253802a965ed6d7",
        "fixture_count": 16,
        "K_min": 12,
        "K": K,
        "non_evaluable_fixture_count": 16 - K,
        "Q_suite": serialize_rational(Q_suite),
        "H_0_75": H_0_75,
        "H_required": H_required,
        "classification": classification,
        "classification_reason": reason,
        "evidence_ceiling": "INTERVENTION_SENSITIVITY",
        "allowed_interpretation_ceiling": "consequence estimates are sensitive to legal destination variation within exact same-origin move-form strata.",
        "denied_claims": {
            "isolated_destination_causality": False,
            "objective_causal_effect": False,
            "natural_prevalence": False,
            "producer_independence": False,
            "heat_contribution": False,
            "statistical_significance_claim": False
        },
        "correction_provenance": {
            "supersedes_analysis_commit": "ee3e51a09b4bdad94b34444d943c28b1de07d995",
            "supersedes_analysis_sha256": "fdf58c4cce072fd1d4caf0bebb473c2abbf9fe5baaf8b3b6b574514e22f1c305",
            "correction_reason": "FROZEN_D_DENOMINATOR_IMPLEMENTATION_ERROR_AND_FILE_DIGEST_TYPE_ERROR",
            "classification_changed": False
        },
        "fixtures": fixtures_results
    }
    
    # Required explicit suite assertions
    assert Q_suite == Fraction(5, 13)
    assert H_0_75 == 2
    assert H_required == 12
    assert classification == "FALSIFIED"
    
    # Required explicit fixture anchors
    def find_fix(ident):
        for f in fixtures_results:
            if f["fixture_identity"] == ident: return f
    
    f00 = find_fix("t3b7_f00")
    assert f00["D_1"] == serialize_rational(Fraction(-1, 1))
    assert f00["D_2"] == serialize_rational(Fraction(0, 1))
    assert f00["S_match"] == serialize_rational(Fraction(1, 2))
    assert f00["Q"] == serialize_rational(Fraction(5, 18))

    f06 = find_fix("t3b7_f06")
    assert f06["D_1"] == serialize_rational(Fraction(-1, 1))
    assert f06["D_2"] == serialize_rational(Fraction(1, 1))
    assert f06["S_match"] == serialize_rational(Fraction(1, 1))
    assert f06["Q"] == serialize_rational(Fraction(7, 9))

    f09 = find_fix("t3b7_f09")
    assert f09["D_1"] == serialize_rational(Fraction(-1, 1))
    assert f09["D_2"] == serialize_rational(Fraction(-1, 1))
    assert f09["S_match"] == serialize_rational(Fraction(1, 1))
    assert f09["Q"] == serialize_rational(Fraction(23, 25))

    f15 = find_fix("t3b7_f15")
    assert f15["D_1"] == serialize_rational(Fraction(3, 5))
    assert f15["D_2"] == serialize_rational(Fraction(1, 4))
    assert f15["S_match"] == serialize_rational(Fraction(17, 40))
    assert f15["Q"] == serialize_rational(Fraction(7, 27))
    
    assert analysis == expected_artifact
    
    bad_keys = {
        "alternative_Q", "tuned_threshold", "optimized_matcher", "weighted_match",
        "pooled_primary", "p_value", "confidence_interval", "significance",
        "effect_size", "replacement_fixture", "rescue_fixture"
    }
    reject_keys(analysis, bad_keys)
    
    # Assert canonical serialization
    with open(analysis_path, "rb") as f:
        actual_bytes = f.read()
    expected_bytes = json.dumps(expected_artifact, sort_keys=True, indent=2, ensure_ascii=False).encode("utf-8") + b"\n"
    assert actual_bytes == expected_bytes
    
    # Hard-bind new artifact SHA
    assert get_file_sha(analysis_path) == "b550f0a5f56a011e66b8e6efdcf50c786453e115b9990b4f1ca4247a521c17db"

if __name__ == "__main__":
    test_t3b9_matched_analysis_integrity()
    print("Test passed.")
