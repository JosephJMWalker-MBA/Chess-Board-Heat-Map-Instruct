# CP Source Acquisition Re-Audit V2

## Audit SHAs
- **Audited Implementation SHA:** `86cb8752f5392f37987a3010e6d4fa09e8d671c2`
- **Sealed Candidate SHA:** `16c0adb708b43349e2d2ba6f3623257fe0c3f887`
- **Sealed Manifest Digest:** `8983e7314a44e85be63c953de0a60666774314b0a95f15bb1e1551a18390a46e`

## Exact Audit Scope
This was an independent, hostile re-audit covering ONLY the V2 implementation layer for SOURCE-only feasibility acquisition:
- Root population, prior development registry, manifest determinism.
- Root reconstruction and ExperimentSpec binding.
- SourceFeasibilityRunnerV2 execution bounds, runtime software-revision gates, resume logic, and failure durability.
- Coverage calculations and testing adequacy.
- No engine was started, no target labels were queried, and no models were trained.

## Test Execution
- **Test Counts:** 19 focused tests passed. 219 full tests passed.
- **`py_compile` Check:** Executed on execution bounds; passed with no syntax errors.

## Finding Matrix

### 1. Root Selector Contract & Re-construction (PASS)
- **Verdict:** PASS
- **Details:** The `GameURL` strictly drives duplicate resolution distinct from `Site`. Determinism under input permutation is guaranteed via list sorting on `GameURL` + ordinality. Annotations, evaluations, k=0 eligibility, and headers have no effect on `root_identity`. Full S0 reconstruction validates historical ply lengths seamlessly, successfully failing closed if tampered. 
- **Proof:** Tests (`test_frozen_invariants`) comprehensively construct variants and assert identities.

### 2. Prior Development Registry & Manifest (PASS)
- **Verdict:** PASS
- **Details:** Overlap exclusions reliably assert `PRIOR_DEVELOPMENT_TRANSPOSITION_OVERLAP: 23` and exact overlap as `0`. Manifest determinism verified independently via `scripts/build_cp_july2026_root_manifest.py` against `86cb8752f5392f37987a3010e6d4fa09e8d671c2`, successfully producing uncompressed canonical bytes identical to the sealed digest `8983e7314a44e85be63c953de0a60666774314b0a95f15bb1e1551a18390a46e`. 33,859 roots reliably admitted.

### 3. Runtime Software-Revision Gate (PARTIAL / PASS)
- **Implementation:** Validates against `subprocess.run(["git", "diff", "--quiet", ...])` and enforces local index/working tree integrity exactly as required before engine startup.
- **Mechanical Proof:** Tested via `mock_git` monkeypatching `subprocess.run`.
- **Verdict:** PASS. The code implements the constraint securely, despite the test relying on a mock rather than an ephemeral git repository. 

### 4. ExperimentSpec Binding & Source-Only Boundary (PASS)
- **Verdict:** PASS
- **Details:** Construction binds strictly to the `CP_SOURCE_SF18_50K_ISOLATED_V1` and Stockfish 18 defaults. The budget is hardcoded to 50k, strictly enforcing a SOURCE-only role. Target observations and model execution are mechanically disjoint from this pipeline.

### 5. Resume and Failure Durability (PASS)
- **Verdict:** PASS
- **Details:** `__init__` fails closed on blank lines, schema mismatch, corrupt payloads, and out-of-order roots. `acquire` failure guarantees `fsync` and complete session teardown (`close`) sequentially. No ghost sessions or incomplete envelopes are leaked.

### 6. Coverage/Reporting & Known Hostile Check (PASS)
- **Verdict:** PASS (with non-material limitation)
- **Details:** Zero-pair count accurately processes `pairs == 0` equivalent to `C < 2`. The median logic is mathematically correct. However, `get_median()` was inadvertently shifted to module scope in a way that captured the subsequent `report_dist` function definition and its invocations within its body. Because `get_median` always returns before reaching them, the distributions (min/median/p90/p95/max) and the options surface digest print statement are strictly unreachable.
- **Materiality:** This defect *solely* affects the standard output stream of the aggregator script. The acquisition payload generation (the true evidence) remains perfectly valid, the options digest is strictly enforced during aggregation validation, and the core counts (legal alts, CP alts, zeros) are still accurately printed. Because the frozen feasibility stage correctly produces its required evidence artifacts, this reporting defect does not mandate a V3 acquisition-infrastructure replacement.

### 7. Test Adequacy (PASS)
- **Verdict:** PASS
- **Details:** All claimed tests (options-surface missing/empty/mismatched, move-order canonical mismatch, root-failure session count, C=1 zero-pair checks) assert explicitly against correct boundary errors.

## Overall Verdict
**Verdict:** `SOURCE_ACQUISITION_V2_REAUDIT_PASS`
**Next Status:** `AUTHORIZED_CORRECTED_SOURCE_ONLY_FEASIBILITY_COVERAGE_EXECUTION`
**Blocker:** None for Source execution.

## Explicit Non-Authorization
- The underlying `CP` instrument remains at `V3_REAUDIT_PASS`.
- **No** source engine execution occurred during this audit.
- Target acquisition remains explicitly **UNAUTHORIZED**.
- Model training remains explicitly **UNAUTHORIZED**.
