# ML Runtime Pin V3

## Overview
V2 numerical evidence passed, but the V2 hostile audit exposed 6 enforcement gaps in the runtime and validator.
V3 does NOT change the numerical runtime, but implements strict exact-identity enforcement.

## Repaired Blockers
1. **`ML_RUNTIME_V2_VALIDATOR_FAILS_OPEN`**: CLOSED. `scripts/validate_ml_runtime_v3.py` now explicitly requires exact string matches for all generated hashes. It strictly compares baseline models to expected V1 baselines and throws `ValueError` on any divergence.
2. **`ML_RUNTIME_CANONICAL_IMPORT_PATH_NOT_ENFORCED`**: CLOSED. The launcher unset inherited `PYTHONPATH` and only points to the canonical `$ROOT/src:$ROOT`. The runtime checks `__file__` matches the expected path explicitly.
3. **`ML_RUNTIME_PACKAGE_LOCK_NOT_ENFORCED`**: CLOSED. Runtime preflight loads `ml_runtime_package_lock_v3.json` and asserts `importlib.metadata.version()` exact matches for every package inside it.
4. **`ML_RUNTIME_CODE_IDENTITY_NOT_ENFORCED`**: CLOSED. Runtime preflight loads `ml_runtime_code_lock_v3.json`, verifies SHAs mechanically, and tests working tree modifications using `git diff --quiet` and `git diff --cached --quiet`.
5. **`ML_RUNTIME_ADAM_RUNTIME_SURFACE_INCOMPLETE`**: CLOSED. `decoupled_weight_decay=False` was added explicitly to `build_frozen_adam()`.
6. **`ML_RUNTIME_TEST_SUITE_NOT_REPEATABLE`**: CLOSED. Test environment cleanup was handled via `tempfile.TemporaryDirectory()`.

## Artifact SHAs
- **V3 Pin SHA**: `e69ae6bcbf96a327b021665b5ac21b63c269cd821be84d567867058b09e98932`
- **Package Lock V3 SHA**: `2127b9709ef8786f47b9306040a56706ff3a7f6535d2439d692c67bac5fac54d`
- **Code Lock V3 SHA**: `9eebefd15c6c1fe93340a69f270f9bf02f7572b4a307d174307f786355a4ec84`
- **Requirements V3 SHA**: `79ea33529376312052c7f98d0e19e812029697d4ff15a2e93106f94f023bf7c9`

## Verification Evidence
- Exact V1 Baseline hash equivalence strictly enforced (for all 5 seeds).
- Extended determinism: Model, optimizer, CPU-RNG, and MPS-RNG proven across batches (1, 2, 8, 17, 63, 64).
- Reduced reduction equivalence tested identically via 2/2/4 short-batching root weighted loss masking.
- Test Suite repeatability validated. Full suite passes cleanly without manual cleanup.

## Claim Ceiling
Runtime V3 demonstrated bitwise repeatability for the frozen synthetic validation paths under the exact pinned software/hardware/environment/code identity. It does NOT claim universal determinism.
