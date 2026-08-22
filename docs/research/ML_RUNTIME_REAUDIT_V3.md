# ML Runtime V3 Hostile Re-Audit

## Overview
This document records the exact findings of the independent hostile re-audit for ML Runtime V3. The audit rigorously evaluated the four-commit implementation range to ensure all V2 material blockers were completely repaired, and exact code, environment, and state identity determinism were enforced.

## Audited Implementation Range
- **Final Audited SHA**: `d2650cff68d0b80b9b97bc5c811045ffc46c40e9`
- **Complete Four-Commit V3 Range**:
  - `d2650cff68d0b80b9b97bc5c811045ffc46c40e9` "Repair and validate ML runtime v3"
  - `6bc3c31ec040aa4ebac031b67327218baa9ddb88` "test clean"
  - `04638075143843c614f4776594be2ce940e6a835` "Update fixes"
  - `37b3fc4fa4cc355a8c6bf2000e781a49487f27c8` "Tmp commit"
- **V2 Audit SHA**: `889bc57703ac17510a7832efa5e0d84b728245d0`
- **V7 Binding SHA**: `ac26f3ae3c4f1f04e1fb5cb54a58a98882a4f368` (Audit), `bf113817621894034929d9aa89b83dec14c35e69` (Implementation)

## Artifact SHAs
- **V3 Pin SHA**: `e69ae6bcbf96a327b021665b5ac21b63c269cd821be84d567867058b09e98932`
- **Package Lock V3 SHA**: `2127b9709ef8786f47b9306040a56706ff3a7f6535d2439d692c67bac5fac54d`
- **Code Lock V3 SHA**: `9eebefd15c6c1fe93340a69f270f9bf02f7572b4a307d174307f786355a4ec84`
- **Requirements V3 SHA**: `79ea33529376312052c7f98d0e19e812029697d4ff15a2e93106f94f023bf7c9`
- **Validation Evidence SHA**: `4036dce95361b63d0fe9c0296949e0359a9f1cd71eaa10c25dcbf819e8ef2dcf`

## V2 Blocker Verdicts
1. **`ML_RUNTIME_V2_VALIDATOR_FAILS_OPEN`**: PASS. `validate_ml_runtime_v3.py` explicitly iterates over 3 records (and expects exactly 3), demanding identical lengths and strings for all hashed subsets (`MODEL`, `OPT`, `CPU`, `MPS`). It further explicitly checks MODEL hashes against the five hardcoded V1 expected constant strings. A mismatch raises `ValueError`.
2. **`ML_RUNTIME_CANONICAL_IMPORT_PATH_NOT_ENFORCED`**: PASS. `scripts/run_ml_runtime_v3.sh` unsets `PYTHONPATH` and only sets it to `$ROOT/src:$ROOT` with `PYTHONNOUSERSITE=1`. Inside Python, `ml_runtime.py` dynamically resolves its `__file__` and verifies it strictly equals `$CHESSHEAT_REPO_ROOT/src/chessheat/ml_runtime.py`, effectively blocking shadow runtime modules.
3. **`ML_RUNTIME_PACKAGE_LOCK_NOT_ENFORCED`**: PASS. The `validate_package_lock_v3()` routine explicitly retrieves installed package versions via `importlib.metadata.version(pkg)` and strictly mandates identity with values located in `ml_runtime_package_lock_v3.json` before Torch may be imported.
4. **`ML_RUNTIME_CODE_IDENTITY_NOT_ENFORCED`**: PASS. The preflight strictly verifies `ml_runtime_code_lock_v3.json` hashes with explicit python logic, ensuring matching hashes. Crucially, it runs `git diff --quiet --` and `git diff --cached --quiet --` for the target files to guarantee they correspond to the tracked repository state.
5. **`ML_RUNTIME_ADAM_RUNTIME_SURFACE_INCOMPLETE`**: PASS. `decoupled_weight_decay=False` was correctly explicitly bound to the Adam optimizer.
6. **`ML_RUNTIME_TEST_SUITE_NOT_REPEATABLE`**: PASS. Test cleanup relies on standard library `tempfile.TemporaryDirectory()`, eliminating test file footprint and allowing multiple successive valid Pytest runs.

## Root of Trust Adjudication
- **Verdict**: PASS with explicit governance boundary. The runtime enforces execution identity primarily by verifying that critical files mechanically hash to expected values and that `git diff` flags zero deviations. This requires executing from an audited code identity. It is not self-authenticating across unbounded changes, but instead binds securely to the explicitly committed versions recorded in this audit. The true root of trust is the audited Git history and the committed code locks.

## Additional Identity Verifications
- **Exact Live Identity Verdict**: PASS. CPython 3.13.5 (cpython-313-darwin), macOS 26.6.2 build 25G83 Darwin 25.6.0, Mac16,10 Apple M4 arm64, 16GB RAM, Torch 2.13.0 git cf30153c4c131c8164ee7798e5022d810682e2cb on MPS.
- **Pin Completeness Verdict**: PASS. Although the lineage entries exist as strings (e.g. "V7 implementation/audit/JSON"), the canonical `ml_runtime_pin_v3.json` incorporates direct SHA256 inclusion of the sub-components, serving as a sufficient verifiable manifest.
- **Launcher/Import-Path Verdict**: PASS. `run_ml_runtime_v3.sh` and `validate_canonical_import_path()` definitively block arbitrary execution and shadowing modules.
- **Package-Lock Enforcement**: PASS. Fails on mismatched or missing packages correctly.
- **Code-Lock Enforcement**: PASS. The SHA generation strictly matches the recorded JSON across `artifacts/research/ml_runtime_package_lock_v3.json`, `requirements/ml-runtime-v3.txt`, `scripts/run_ml_runtime_v3.sh`, `scripts/validate_ml_runtime_v3.py`, and `src/chessheat/ml_runtime.py`.
- **Adam Surface**: PASS.
- **Validator Fail-Closed Verdict**: PASS.
- **Malformed-Hash Verdict**: PASS (Test hardening). Hashes are generated mechanically in identical length hex constraints and fail closed.
- **V1 Baseline Hash Equivalence (all five seeds)**: PASS. All exactly matched expected constants.
- **Extended State Determinism** (Model/Optimizer/CPU-RNG/MPS-RNG): PASS. Validated across single instances and varied batches.
- **Short-batch / Root-weighted Determinism**: PASS. Verified exact unreduced equivalence for short-batched 2/2/4 test.
- **Finiteness/Device Result**: PASS. Explicity checked across the optimizer state tensor `exp_avg` and `exp_avg_sq`.
- **Protocol Tests**: 36 passed (zero scientific/protocol regression).
- **Runtime Tests**: Run 1 (14 passed), Run 2 (14 passed).
- **Full Suite Repeatability**: Run 1 (269 passed), Run 2 (269 passed).
- **Working-Tree Cleanliness**: `git status --porcelain` showed no debris remaining.

## Operational Constraints
- **SOURCE**: Untouched
- **TARGET**: NOT RUN / INSPECTED
- **CHESS-DATA TRAINING**: NONE
- **Resulting Status**: `ML_RUNTIME_DEPENDENCY_PIN_V3_REAUDIT_PASS`
- **Next Blocker**: `EXPLICIT_TARGET_ACQUISITION_AUTHORIZATION_REQUIRED`

## Final Verdict
`ML_RUNTIME_V3_REAUDIT_PASS`
