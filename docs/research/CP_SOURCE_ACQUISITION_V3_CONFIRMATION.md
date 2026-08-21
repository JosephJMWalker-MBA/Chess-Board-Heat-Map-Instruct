# CP Source Acquisition V3 Confirmation

## SHAs and Scope
- **V2 Audit Failure being repaired:** Missing reachability of required coverage distributions due to a control flow defect in `get_median()`.
- **V3 Implementation SHA:** `a49b6ce62a59cc056b67aefc94b121799d950045`
- **Sealed Candidate SHA:** `07e219f3951ee6b205fa10825add77608f07f93b`
- **Manifest Digest:** `5a013e64265820b65d1d3687fcee98aa607ab41470294d11df7b2f803c8e063d`
- **Implementation Diff Scope:** 
  - `scripts/compute_coverage.py`: Un-nested `report_dist` and output statements from `get_median()`.
  - `tests/test_cp_source_feasibility.py`: Added explicit test `test_reporting_v3` capturing stdout distributions.

## Test Validation
- **Focused Tests:** 19 passed
- **Full Tests:** 219 passed
- **Py_compile:** All bound execution files compiled without syntax errors.

## Confirmation Proofs
1. **Distribution Reachability Proof:** Asserted explicitly in `test_reporting_v3` where stdout output (`capsys`) contains headings for legal alternatives, CP alternatives, and CP/CP pairs distributions.
2. **Options Digest Emission Proof:** The canonical `options_surface` digest is emitted and proven exactly identical to the standalone JSON hash calculation in `test_reporting_v3`.
3. **Median Proof:** `[1,2,3] -> 2`, `[1,2,3,4] -> 2.5` verified dynamically.
4. **P90/P95 Proof:** Nearest-rank correctly asserted to `9` and `10` respectively on an integer spectrum 1-10.
5. **C=1 Zero-Pair Proof:** Simulated single CP observation outputs `min: 0`, `median: 0`, `p90: 0`.
6. **Manifest Deterministic Reseal Proof:** Twin generation runs with `--software-revision a49b6ce62a59cc056b67aefc94b121799d950045` yielded identical uncompressed JSONL bytes `5a013e64...`.
7. **Population Counts:** Admitted roots precisely unchanged (33859). Registry exclusion overlap remains zero and transposition overlap 23.

## Verdict
- **Confirmation Verdict:** `SOURCE_ACQUISITION_V3_CONFIRMATION_PASS`
- **Resulting Status:** `AUTHORIZED_CORRECTED_SOURCE_ONLY_FEASIBILITY_COVERAGE_EXECUTION`
- **Next Stage:** `EXECUTE_CORRECTED_SOURCE_ONLY_50K_ACQUISITION`

## Explicit Disclaimers
- Target acquisition remains explicitly **UNAUTHORIZED**.
- Model training remains explicitly **UNAUTHORIZED**.
