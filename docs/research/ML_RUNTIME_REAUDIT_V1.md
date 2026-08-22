# ML Runtime Re-Audit V1

**Audited SHA**: 20e77095f8c188a9d2694451fd4e9d0e0c91dd64
**V7 Protocol Binding**: CP_REPRESENTATION_EFFICIENCY_PROTOCOL_V7
**V7 Protocol Audit SHA**: ac26f3ae3c4f1f04e1fb5cb54a58a98882a4f368

## Live Inventory
- **Python**: 3.13.5 (CPython, SOABI cpython-313-darwin)
- **OS**: macOS 26.6.2 (build 25G83)
- **Hardware**: Mac16,10 (Apple M4, arm64, 16 GB Memory)
- **Torch**: 2.13.0 (Git cf30153c4c131c8164ee7798e5022d810682e2cb)
- **Device**: mps

## Artifact Hashes
- **Pin JSON (`artifacts/research/ml_runtime_pin_v1.json`)**: e035b5acb13e713c3e444e8ad529e0444c8a204070951932d27252b97603f88f
- **Wheel Manifest**: 6427cb2a43e5a1d3971933ef2a246b1df4af6b591c047c9d7ccd4f4eb4cf24ec (Matches pin exactly).
- **Package Freeze**: 1330debffc73292cd27d72f92eda2b1d652165a4952ceb92a8ab828cc665fc30 (Matches pin exactly).

## Required Audit Verdicts

### Exact Identity Enforcement Guard
**Verdict: FAIL** (MATERIAL BLOCKER: `ML_RUNTIME_EXACT_IDENTITY_NOT_ENFORCED`)
`src/chessheat/ml_runtime.py` only validates `torch.__version__ == 2.13.0`, `Darwin`, and `arm64`. It fails to validate Python version (3.13.5), macOS version, specific Mac chip, or PyTorch git SHA. It would incorrectly permit execution on materially different pinned hardware/software combinations.

### Pre-Import Environment Binding
**Verdict: FAIL** (MATERIAL BLOCKER: `ML_RUNTIME_MPS_PREIMPORT_ENV_NOT_BOUND`)
`src/chessheat/ml_runtime.py` performs `import torch` at the top of the file *before* `validate_runtime_environment()` checks `PYTORCH_MPS_FAST_MATH` and others. Since MPS environment variables are cached at initialization, setting them after `import torch` does not reliably configure the backend.

### CPU vs MPS Initialization Device
**Verdict: FAIL** (MATERIAL BLOCKER: `ML_RUNTIME_INITIALIZATION_DEVICE_NOT_FROZEN`)
V7 froze initialization mathematics but did not specify whether initialization occurs on CPU before `.to("mps")` or directly on MPS. The synthetic validation script instantiates on CPU and moves to MPS. Because identical random seeds can yield different parameter streams depending on the device, this degree of freedom must be frozen to guarantee bitwise reproducibility.

### Package Lock Reproducibility
**Verdict: WARNING**
`pyproject.toml` pins only `torch==2.13.0` under the `[ml]` extra. A fresh `pip install .[ml]` would resolve new transitive dependencies rather than enforcing the exact environment specified by `ml_runtime_pip_freeze_v1.txt`. This creates an enforcement gap for transitive packages.

### Editable Package Provenance
**Verdict: WARNING**
The package freeze line references `Chess-Board-Heat-Map-Instruct.git` rather than `ChessHeat`. This is a cosmetic reflection of the repository rename during cloning, but not a material defection.

### Synthetic 15-Run Reproduction
**Verdict: PASS**
Hashes produced for the model across 15 processes strictly match the committed values in `ml_runtime_validation_hashes_v1.json` (e.g. `26a5f5...` for Seed 1729).

### Optimizer / RNG State Determinism
**Verdict: PASS**
Extended audit probes confirmed that not only the model state, but the Adam optimizer state, CPU RNG state, and MPS RNG state are strictly identical across repeated processes under the current CPU-then-MPS initialization sequence. 

### Tests and Suite Adequacy
- **Protocol Tests**: 36 passed (No regression).
- **Runtime Tests**: 7 passed. However, the tests are inadequate to enforce the strict pin schema, testing only a subset of necessary restrictions.
- **Full Suite**: 262 passed.

### Claim Boundary
**Verdict: ACCEPTABLE**
"MPS determinism across process boundaries is strictly proven" is acceptable within the bounds of the synthetic tensor representation on this exact hardware, but the lack of identity enforcement weakens this claim for future runs.

## Final Verdict
**ML_RUNTIME_V1_REAUDIT_FAIL**

**Resulting Status**: ML_RUNTIME_DEPENDENCY_PIN_REAUDIT_FAILED
**Next Blocker**: ML_RUNTIME_DEPENDENCY_REPAIR_REQUIRED_V2
