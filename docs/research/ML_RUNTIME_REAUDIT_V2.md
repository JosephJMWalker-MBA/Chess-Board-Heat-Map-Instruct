# ML Runtime Dependency Re-Audit V2

## Overview
This document records the independent hostile re-audit of the ChessHeat ML Runtime V2.

- **Audited Commit SHA**: `0782acdee6f47e4aa4fe24470a4079b979d3005c`
- **Runtime V1 Audit SHA**: `fe5d6c7208ad0adbb4fd57cb9b48c065637a1872`
- **V7 Scientific Protocol SHA**: `ac26f3ae3c4f1f04e1fb5cb54a58a98882a4f368` (Audit) / `bf113817621894034929d9aa89b83dec14c35e69` (Impl)
- **V2 Pin JSON SHA**: `9f4aafb5deb4fd2401c71db9e915c726eaef983d6dacb8ca1b9e613581d9c66b`

## V1 Material Blockers Re-evaluation
1. **`ML_RUNTIME_EXACT_IDENTITY_NOT_ENFORCED`**: VERDICT PASS. `validate_runtime_identity()` strictly enforces OS, hardware, memory, chip, python version, and the python executable hash.
2. **`ML_RUNTIME_MPS_PREIMPORT_ENV_NOT_BOUND`**: VERDICT PASS. `import torch` at module scope was removed. `configure_runtime()` dynamically imports torch only after enforcing the launcher's environment variables and hardware identity. Attempting to import torch beforehand correctly fails the guard.
3. **`ML_RUNTIME_INITIALIZATION_DEVICE_NOT_FROZEN`**: VERDICT PASS. `initialize_model_cpu_then_mps` strictly instantiates on CPU, verifies CPU residency, transfers to MPS, and verifies MPS residency.

## Exact Live Identity Check
- **Python**: CPython 3.13.5 (cpython-313-darwin). Executable SHA matches `542c...`.
- **macOS**: 26.6.2 (Build 25G83), Darwin 25.6.0.
- **Hardware**: Mac16,10 (Apple M4, arm64, 17179869184 bytes memory).
- **Torch**: 2.13.0 (Git `cf30153c4c131c8164ee7798e5022d810682e2cb`), Device MPS.
- ALL LIVE IDENTITY MATCHES EXACTLY.

## New Material Blockers Found

### 1. `ML_RUNTIME_V2_VALIDATOR_FAILS_OPEN` (CRITICAL)
The orchestrator `scripts/validate_ml_runtime_v2.py` collects deterministic hash evidence across seeds and shapes, but **never performs any equality assertions**. It writes the JSON and exits `0` regardless of whether the 3 inner runs match each other or match the V1 baseline hashes. Execution fail-closedness is entirely absent.

### 2. `ML_RUNTIME_CANONICAL_IMPORT_PATH_NOT_ENFORCED`
`scripts/run_ml_runtime_v2.sh` appends to the existing `PYTHONPATH`: `export PYTHONPATH="${PYTHONPATH:-}${PYTHONPATH:+:}$ROOT/src:$ROOT"`. This permits a hostile caller to shadow the exact `src/chessheat/ml_runtime.py` code by placing a malicious path at the front of `PYTHONPATH`, hijacking the entire scientific runtime while appearing compliant.

### 3. `ML_RUNTIME_PACKAGE_LOCK_NOT_ENFORCED`
While `importlib.metadata.version("torch")` is verified, the runtime completely ignores `artifacts/research/ml_runtime_package_lock_v2.json`. The transitive exact dependencies (like `fsspec`, `networkx`, `sympy`) can drift entirely, and `configure_runtime()` will still pass.

### 4. `ML_RUNTIME_CODE_IDENTITY_NOT_ENFORCED`
The exact code hashes of the runtime files (e.g., `validate_ml_runtime_v2.py`, `run_ml_runtime_v2.sh`) recorded in `ml_runtime_pin_v2.json` are entirely documentary. No mechanical mechanism prevents the user from altering the validator script and executing it under the V2 claim.

### 5. `ML_RUNTIME_ADAM_RUNTIME_SURFACE_INCOMPLETE`
`inspect.signature(torch.optim.Adam)` for Torch 2.13.0 reveals a `decoupled_weight_decay` parameter. `build_frozen_adam()` correctly explicitizes 10 arguments (lr, betas, eps, etc.) but omits `decoupled_weight_decay`, leaving a hole in the numerical environment boundary.

### 6. `ML_RUNTIME_TEST_SUITE_NOT_REPEATABLE`
`test_launcher()` in `tests/test_ml_runtime.py` writes `tests/test_launcher.py` and fails to clean it up. A subsequent `pytest` invocation crashes during collection due to the leftover file shadowing tests and attempting to configure the runtime with an invalid environment.

## Supplementary Evidence & Non-Blockers
- **V1 Baseline Hashes**: The written artifact reproduces the exact 5 hashes (e.g., `1729: 26a5f5...`). Equivalence is proven despite the validator failing to assert it mechanically.
- **Short-batch & Root-weighted Hashes**: Model, Opt, CPU RNG, and MPS RNG correctly generated deterministic hashes.
- **Root-weighted Groups**: The tests use `2/2/4` instead of the specified `1/2/5`. This remains scientifically adequate to exercise the deterministic `scatter_add` replacement (mask multiplication/sum).
- **Finiteness**: Model parameters and gradients are checked for finiteness, but floating Adam optimizer states are not. Given deterministic equality across states, this is classified as non-material.
- **Deterministic Flags**: `torch.are_deterministic_algorithms_enabled() == True`, `warn_only=False`, `float32_matmul_precision='highest'`, `default_dtype=float32` all correctly enforced post-import.
- **Pip Freeze / Lock hashes**: Documentary only. 
- **Protocol Tests**: 36 passed (No regression).
- **Runtime Tests**: 6 passed. Coverage for Direct-MPS initialization rejection remains.

## Claim Ceiling
Runtime V2 correctly restricts its claims to bitwise repeatability for the frozen synthetic validation paths under the exact pinned environment identity. It correctly disclaims universal MPS determinism.

## Result
**Verdict**: `ML_RUNTIME_V2_REAUDIT_FAIL`
**Resulting Status**: `ML_RUNTIME_DEPENDENCY_PIN_V2_REAUDIT_FAILED`
**Next Blocker**: `ML_RUNTIME_DEPENDENCY_REPAIR_REQUIRED_V3`
**TARGET**: UNAUTHORIZED
