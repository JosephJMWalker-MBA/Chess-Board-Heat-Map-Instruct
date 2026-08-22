# CP Downstream Experiment Protocol Re-Audit V3

**Audited SHA**: af620cd1f5b5beaa850baf08baca0f8bd6b90894
**Prior Audit SHA**: 6c8acd70eed1969d38d65641ec216ceae23824b4
**Authoritative Pre-Freeze SHA**: 8876f8cf2d6e1da47b2b40b818413b4095786c36
**Protocol ID**: CP_REPRESENTATION_EFFICIENCY_PROTOCOL_V3
**Claimed JSON Digest**: 86468d4e2befbae731b0080104971536e5dbe9cfe0acce3bd5e86523365bd166
**Recomputed JSON Digest**: 86468d4e2befbae731b0080104971536e5dbe9cfe0acce3bd5e86523365bd166

## Scope and Boundary Verification
**Changed Files**:
- `src/chessheat/protocol_freeze.py`
- `tests/test_protocol_freeze.py`
- `artifacts/research/cp_representation_efficiency_protocol_v3.json`
- `docs/research/CP_DOWNSTREAM_EXPERIMENT_PROTOCOL_FREEZE_V3.md`
- `docs/research/CP_ONLY_REPRESENTATION_EFFICIENCY_PREREGISTRATION.md`
- `docs/research/NEXT_WORK_MAP.md`
- `docs/research/RESEARCH_CONTINUITY_CHECKPOINT_2026-08-16.md`

**SOURCE / TARGET / Model Boundary**: Verified. TARGET remains unauthorized, no labels created, no models trained, no PyTorch installed. SOURCE evidence is untouched.

## Finding Matrix

### Split Counts and JSON Factual Correctness (MATERIAL FAIL)
- **Exact measured SOURCE split counts**: TRAIN 23,639; VALIDATION 5,148; TEST 5,072.
- **Sealed JSON expected counts**: TRAIN 23,689; VALIDATION 5,013; TEST 5,157.
- **Verdict**: **FAIL** (`STALE_CANONICAL_V3_SPLIT_COUNTS`). While the generated JSON matches the bytes of the file precisely, the Python payload generator itself contains stale, factually false counts. A canonical seal is invalid if the parameters sealed do not match the frozen experimental evidence.

### Full Bootstrap Implementation (MATERIAL FAIL)
- **Audit**: `full_bootstrap_procedure` in `src/chessheat/protocol_freeze.py` is implemented purely as `pass` with a comment deferring work.
- **Verdict**: **FAIL** (`FULL_BOOTSTRAP_PROCEDURE_UNIMPLEMENTED`). The scientific estimand is not computationally frozen.

### V1/V2 Scientific Repair Inheritance
- **Verdict**: **PASS**. V3 retains the successful restorations of the continuous amplitude definitions ($M_D$/$M_T$), information equalization, deterministic pair matching, and correct outcome contrast signs.

### Canonical Tensor & Coordinates
- **Canonical Tensor F32**: **PASS**. Fully implemented IEEE-754 binary32 quantization without PyTorch dependency, using `struct.pack`.
- **Coordinate Systems**: **PASS**. Differentiated strictly into `uci_square_index` (a1=0) for $S^*$ and `spatial_row_col`/`spatial_flat_index` (a8=0) for $P$ and $M$.

### UCI Validation / Pair / d_X
- **Verdict**: **FAIL**. The `SourcePairFeatures` object fails to robustly validate UCI strings (it lacks regex matching for valid board coordinates) and fails to assert valid promotion pieces internally during instantiation. Malformed inputs can produce runtime failures disconnected from the constructor boundaries.

### CompareTyped Durable Binding
- **Verdict**: **PASS**. The prose bindings specifically require executing the inherited `CompareTyped` semantics to accurately evaluate mate ordering.

### TARGET-Zero Semantics
- **Verdict**: **PASS**. Training budget logic freezes prospective nominal slots while ensuring TARGET-zero pairs consume no minibatch capacity. Val/Test semantic requirements are properly durably defined.

### Learner Completeness
- **Verdict**: **FAIL**. The canonical JSON payload fails to freeze bias bounds analytically, omits precise initialization functions, and lacks concrete architectural definitions that avoid implicit PyTorch framework defaults.

### AULC & Seed Aggregation
- **Verdict**: **PASS**. `compute_aulc` checks monotonicity and enforces `math.isfinite`. Seed aggregation explicitly averages over seeds *before* computing the target AULC geometries.

### Test Adequacy
- **Test Counts**: 12 focused tests, 231 full suite tests.
- **Verdict**: **FAIL**. Tests are severely inadequate. Missing: exact split count assertions, full budget nesting tests, SOURCE-zero exclusion tests, complete outcome class boundary checks, and any verification of the full bootstrap procedure (which is `pass`).

### Preregistration Consistency
- **Verdict**: **FAIL**. `docs/research/CP_ONLY_REPRESENTATION_EFFICIENCY_PREREGISTRATION.md` contains stale V2 tokens. `SPLIT_AND_BUDGET_FROZEN_V2` remains across multiple sections, and `CONFIDENCE_LEVEL_FROZEN_V3` incorrectly lists `alpha level, bootstrap size` as remaining unresolved.

### Continuity Restoration
- **Verdict**: **PASS**. The V1/V2 historical tracking (>1,300 lines combined) was completely restored in `NEXT_WORK_MAP.md` and `RESEARCH_CONTINUITY_CHECKPOINT_2026-08-16.md` before appending the V3 status.

## Overall V3 Verdict
**DOWNSTREAM_PROTOCOL_V3_REAUDIT_FAIL**

**Resulting Status**: `DOWNSTREAM_EXPERIMENT_PROTOCOL_V3_REAUDIT_FAILED`
**Next Blocker**: `DOWNSTREAM_EXPERIMENT_PROTOCOL_REPAIR_REQUIRED_V4`

**Material Blockers**:
1. `STALE_CANONICAL_V3_SPLIT_COUNTS`
2. `FULL_BOOTSTRAP_PROCEDURE_UNIMPLEMENTED`
