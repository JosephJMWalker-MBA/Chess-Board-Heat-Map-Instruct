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

### 6. Coverage/Reporting & Known Hostile Check (FAIL)
- Core acquisition counts before the unreachable block are computable.
- Zero-pair accounting and median function mathematics are correct.
- However, the required distribution reporting and final options-surface digest reporting are unreachable because they are nested after an unconditional return in `get_median()`.
- This is an executable defect in the frozen source-feasibility evidence path.
- It does not invalidate future raw SOURCE ExperimentResults, but it prevents the stage's required evidence report from being reproducibly produced by the committed implementation.

**Materiality:** EXECUTION-BLOCKING FOR SOURCE FEASIBILITY STAGE COMPLETION

### 7. Test Adequacy (PASS)
- **Verdict:** PASS
- **Details:** All claimed tests (options-surface missing/empty/mismatched, move-order canonical mismatch, root-failure session count, C=1 zero-pair checks) assert explicitly against correct boundary errors.

## Overall Verdict
**Verdict:** `SOURCE_ACQUISITION_V2_REAUDIT_FAIL`
The V2 acquisition infrastructure is substantially validated, and the only current execution blocker identified by this re-audit is the coverage/report control-flow defect.
**Next Status:** `SOURCE_ACQUISITION_V2_REAUDIT_FAILED`
**Blocker:** `SOURCE_ACQUISITION_IMPLEMENTATION_REPAIR_REQUIRED_V3`

## Explicit Non-Authorization
- The underlying `CP` instrument remains at `V3_REAUDIT_PASS`.
- **No** source engine execution occurred during this audit.
- Target acquisition remains explicitly **UNAUTHORIZED**.
- Model training remains explicitly **UNAUTHORIZED**.
