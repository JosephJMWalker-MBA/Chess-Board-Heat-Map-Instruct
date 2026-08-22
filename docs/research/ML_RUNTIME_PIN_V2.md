# ML Runtime Pin V2

## Rationale
Runtime V1 numerical determinism evidence PASSed. However, the V1 hostile audit failed because identity enforcement and pre-import contracts were incomplete. Runtime V2 does NOT choose a new numerical runtime or redesign the scientific protocol. It closes the execution contract around the already-demonstrated numerical environment.

## Repaired Blockers
1. `ML_RUNTIME_EXACT_IDENTITY_NOT_ENFORCED`: The runtime preflight now exhaustively validates Python, macOS, and hardware parameters, as well as the SHA256 of the `sys.executable`.
2. `ML_RUNTIME_MPS_PREIMPORT_ENV_NOT_BOUND`: `src/chessheat/ml_runtime.py` no longer imports `torch` at the module level. It asserts `torch` is not imported, tests identity, and verifies all required MPS environment variables *before* performing a runtime import of `torch`. A canonical launcher (`scripts/run_ml_runtime_v2.sh`) provides the only authorized pre-import entrypoint.
3. `ML_RUNTIME_INITIALIZATION_DEVICE_NOT_FROZEN`: Initialization logic is fully frozen to construct models initially on CPU to utilize CPU RNG and PyTorch CPU defaults, verify parameters are on CPU, then transfer to MPS before optimizer construction.

## Exact Identity
- **Python**: 3.13.5 (CPython, cpython-313-darwin) [SHA256: `542c879fdc2cfe0be223e4729082bac529780d90c6d811c853de852765b35a35`]
- **macOS**: 26.6.2 (build 25G83), Darwin 25.6.0
- **Hardware**: Mac16,10 (Apple M4, arm64, 16 GB)
- **Torch**: 2.13.0 (Git cf30153c4c131c8164ee7798e5022d810682e2cb)
- **Device**: mps

## Pre-Import Launcher
Canonical scientific runs MUST launch via `scripts/run_ml_runtime_v2.sh`. Running training scripts directly via `.venv/bin/python` is prohibited as it bypasses critical pre-import backend settings.

## Package Lock
A new `artifacts/research/ml_runtime_package_lock_v2.json` freezes all critical transitive dependencies of PyTorch to lock the environment effectively against silent upgrades.

## Determinism Evidence
- V1 hash equivalence: PASSED. All five seeds reproduce the exact model-state hashes generated in V1.
- V2 expanded states (optimizer, CPU RNG, MPS RNG): Verified identically deterministic across fresh processes.
- Short-batch sequences: PASSED.
- Root-weighted reduction determinism: PASSED.

## Artifact Hashes
- **Runtime Pin V2 SHA**: 9f4aafb5deb4fd2401c71db9e915c726eaef983d6dacb8ca1b9e613581d9c66b

## Status
- SOURCE: Untouched
- TARGET: Unauthorized
- Model Training: No real chess data trained. Synthetic deterministic execution only.

## Claim Ceiling
Runtime V2 demonstrated bitwise repeatability for the frozen synthetic validation paths under the exact pinned software/hardware/environment identity.
