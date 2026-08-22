# CP Downstream Experiment Protocol Re-Audit V4

**Audited SHA**: a0356fd80c61aeb9264a77962a4e00e151d2d2b4
**Prior Audit SHA**: f0d0db9450b032aae6b7726606bf8042ac488d0b
**Authoritative Pre-Freeze SHA**: 8876f8cf2d6e1da47b2b40b818413b4095786c36
**Protocol ID**: CP_REPRESENTATION_EFFICIENCY_PROTOCOL_V4
**Claimed JSON Digest**: 997530af1b61bc512670e1a64d4935e49c0332f54d78acf5528362bcb61751da
**Recomputed JSON Digest**: 997530af1b61bc512670e1a64d4935e49c0332f54d78acf5528362bcb61751da

## Scope and Boundary Verification
**Changed Files**:
- `src/chessheat/protocol_freeze.py`
- `tests/test_protocol_freeze.py`
- `scripts/verify_protocol_v4_source_counts.py`
- `artifacts/research/cp_representation_efficiency_protocol_v4.json`
- `docs/research/CP_DOWNSTREAM_EXPERIMENT_PROTOCOL_FREEZE_V4.md`
- `docs/research/CP_ONLY_REPRESENTATION_EFFICIENCY_PREREGISTRATION.md`
- `docs/research/NEXT_WORK_MAP.md`
- `docs/research/RESEARCH_CONTINUITY_CHECKPOINT_2026-08-16.md`

**Boundary**: Verified. TARGET remains unauthorized, no labels created, no models trained, no PyTorch installed. SOURCE evidence is untouched.

## Finding Matrix

### 1. Stale Split Counts Repair
- **Verdict**: **PASS**. The exactly measured SOURCE split counts (TRAIN 23,639, etc.) are now correctly bound into the V4 canonical payload. The payload is no longer factually stale.

### 2. Full Bootstrap Implementation Repair
- **Verdict**: **PASS** (Methodology). The `full_bootstrap_procedure` is no longer a `pass` stub. It implements the exact 10,000 replicate loop, root resampling, $U$-geometry re-averaging, and `AULC` recalculation specified.

### 3. BOOTSTRAP_ROOT_ORDER_NOT_FROZEN (MATERIAL FAIL)
- **Audit**: `full_bootstrap_procedure` processes the provided `root_ids: List[str]` sequentially and derives the index $i$ by mapping the SHA output modulo $N$ back into this list (`sampled_roots = [root_ids[i] for i in sample_indices]`).
- **Test Result**: Mechanically evaluating the identical loss matrix under a reversed list of `root_ids` produced entirely different Lower Confidence Bounds ($\Delta_{DT}$ LCB changed from `-12.05` to `-12.0`).
- **Verdict**: **FAIL**. Because the deterministic hash maps to list index positions rather than root identities, an unfrozen root input ordering leads to uncontrolled instability in the final scientific estimate.

### 4. Source Verifier vs Raw SHA
- **Verdict**: **FAIL (Provenance Gap)**. The V4 `scripts/verify_protocol_v4_source_counts.py` successfully validates that the counts inside the artifact match the payload. However, it never mechanically checks the SHA-256 of the artifact itself against the `7eb640...` claim. A modified local file with the same counts would erroneously pass the script, weakening the cryptographic binding.

### 5. CompareTyped Exact Binding
- **Verdict**: **PASS**. Bound durably to `src/chessheat/attribution.py:compare_scores`. This is sufficient for protocol execution provided the file is checked out at the current commit.

### 6. Learner Specification: Omitted Conv Fields (MATERIAL FAIL)
- **Verdict**: **FAIL**. The canonical V4 JSON omitted the `dilation=[1,1]` and `groups=1` constraints from the Conv2D layers. This allows future implementers to adopt non-standard convolution architectures while remaining technically "V4 compliant".

### 7. Output Class Ordering
- **Verdict**: **PASS**. The output activation correctly dictates `Linear 128 -> 3`, but the logit index ordering (`FIRST_BETTER`, `EQUAL`, `SECOND_BETTER`) is missing from the explicit learner layers section, risking categorical inversion. However, it is stated implicitly in `s_numeric_encoding`.

### 8. allow_nan Serialization Contract
- **Verdict**: **FAIL**. `json.dumps` defaults to `allow_nan=True`. The V4 implementation `canonical_protocol_bytes_v4()` does not explicitly assert `allow_nan=False`, permitting future undetected injections of non-finite values into the seal.

### 9. Markdown Digest Placeholder
- **Verdict**: **FAIL (Documentation)**. `CP_DOWNSTREAM_EXPERIMENT_PROTOCOL_FREEZE_V4.md` literally contains `(Will be captured upon commit)` for the SHA instead of the required `997530af1b61...` digest.

### 10. Duplicate/Shadowed Tests (MATERIAL FAIL)
- **Verdict**: **FAIL**. The V4 test expansion was hastily appended to `tests/test_protocol_freeze.py` with duplicate function names: `test_aulc`, `test_budget`, `test_coordinates`, `test_outcome`, `test_protocol_seal`, `test_split`. Pytest silently overwrites the original V3 tests with the V4 ones. 21 tests were run, but critical V3 assertions were shadowed and skipped.

### 11. Preregistration Consistency
- **Verdict**: **PASS**. The preregistration correctly unbound the unresolved alpha and split clauses.

## Overall V4 Verdict
**DOWNSTREAM_PROTOCOL_V4_REAUDIT_FAIL**

**Resulting Status**: `DOWNSTREAM_EXPERIMENT_PROTOCOL_V4_REAUDIT_FAILED`
**Next Blocker**: `DOWNSTREAM_EXPERIMENT_PROTOCOL_REPAIR_REQUIRED_V5`

**Material Blockers**:
1. `BOOTSTRAP_ROOT_ORDER_NOT_FROZEN`
2. `LEARNER_SEAL_CONV_DILATION_GROUPS_OMITTED`
3. `SHADOWED_PYTEST_ASSERTIONS`
