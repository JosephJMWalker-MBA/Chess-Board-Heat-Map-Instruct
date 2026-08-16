import json
import hashlib
import pytest
from chessheat.semantics import SemanticSignatureV1, SufficientPosition
from chessheat.experiment import SuiteManifest, SuiteKind, ExperimentSpec, ExperimentResult

MANIFEST_SHA = "4337dd0c8ef2579a1b15eb58f5cb00f4bb566c6fdde6ef612f09b2bab2e1ecc7"
CORPUS_ARTIFACT_DIGEST = "676dedd34a51fc08aea59b57143295115c0e21c884980125f605c33cd8d17ee3"

def get_hash(filepath):
    sha256 = hashlib.sha256()
    with open(filepath, "rb") as f:
        sha256.update(f.read())
    return sha256.hexdigest()

def median(l):
    if not l: return None
    n = len(l)
    if n % 2 == 1:
        return l[n // 2]
    else:
        return (l[n // 2 - 1] + l[n // 2]) / 2.0

def test_t3a4_provenance_closeout():
    # 1. Verify frozen manifest SHA remains unchanged
    assert get_hash("docs/research/t3/t3a4_corpus_manifest.json") == MANIFEST_SHA

    with open("tests/fixtures/t3a4/t3a4_corpus_result.json", "r") as f:
        corpus = json.load(f)

    # 2. Verify all 12 committed raw SHA-256 digests still match
    for idx, expected_sha in enumerate(corpus["raw_fixture_digests"]):
        actual_sha = get_hash(f"tests/fixtures/t3a4/raw/t3a4_f{idx:02d}.json")
        assert actual_sha == expected_sha

    # 3. Recompute corpus artifact digest
    payload_copy = dict(corpus)
    del payload_copy["corpus_artifact_digest"]
    canonical_json = json.dumps(payload_copy, sort_keys=True, separators=(',', ':')).encode("utf-8")
    actual_corpus_digest = hashlib.sha256(canonical_json).hexdigest()
    assert actual_corpus_digest == CORPUS_ARTIFACT_DIGEST
    assert corpus["corpus_artifact_digest"] == CORPUS_ARTIFACT_DIGEST

    # 4. Reconstruct each ExperimentSpec v2 and verify spec digests exactly
    canonical_sig = SemanticSignatureV1.create_canonical()
    s0_digest = canonical_sig.signature_hash()

    suite = SuiteManifest(
        suite_id="t3a4_suite",
        kind=SuiteKind.MECHANISM_STRESS,
        fixtures={f"t3a4_f{idx:02d}": sha for idx, sha in enumerate(corpus["raw_fixture_digests"])}
    )
    assert suite.suite_digest() == corpus["suite_digest"]

    with open("docs/research/t3/t3a4_corpus_manifest.json", "r") as f:
        manifest = json.load(f)

    for idx, fixture in enumerate(manifest["fixtures"]):
        raw_path = f"tests/fixtures/t3a4/raw/t3a4_f{idx:02d}.json"
        with open(raw_path, "r") as f:
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
            suite_digest=suite.suite_digest(),
            fixture_identity=f"t3a4_f{idx:02d}",
            fixture_digest=corpus["raw_fixture_digests"][idx],
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
        assert spec.spec_digest() == corpus["spec_digests"][idx]

        # 5. Reload ExperimentResults and verify artifact integrity
        result_path = f"tests/fixtures/t3a4/results/t3a4_f{idx:02d}_result.json"
        with open(result_path, "r") as f:
            res_data = json.load(f)
            
        loaded_result = ExperimentResult(**res_data)
        assert loaded_result.spec_digest == spec.spec_digest()
        assert loaded_result.artifact_digest == corpus["artifact_digests"][idx]

    # 6. Verify seven valid P_f's
    valid_p_fs = [r["P_f"] for r in corpus["fixture_results"] if r["evaluable_status"] and r["P_f"] is not None]
    expected_p_fs = [-125.0, -411.0, 257.5, -8.0, -67.5, -98.0, -88.0]
    # Verify exactly those 7 numbers
    assert sorted(valid_p_fs) == sorted(expected_p_fs)

    # Reproduce D_suite and M_suite mechanically
    d_suite = median(sorted(valid_p_fs))
    m_suite = min(valid_p_fs)
    
    assert d_suite == -88.0
    assert m_suite == -411.0

    if d_suite > 0 and m_suite > 0:
        conditional_classification = "SUPPORTED"
    elif d_suite > 0 and m_suite <= 0:
        conditional_classification = "WEAK_SUPPORT"
    else:
        conditional_classification = "FALSIFIED"
        
    assert conditional_classification == "FALSIFIED"

    # 7. Verify closeout classification
    with open("tests/fixtures/t3a4/t3a4_provenance_closeout.json", "r") as f:
        closeout = json.load(f)
        
    assert closeout["scientific_classification"] == "INCONCLUSIVE"
    assert closeout["scientific_failure_reason"] == "ACQUISITION_PROVENANCE_NOT_CLOSED"
    assert closeout["conditional_numeric_classification"] == "FALSIFIED"

if __name__ == "__main__":
    pytest.main([__file__])
