# ML Runtime Pin V1

**Runtime ID**: CHESSHEAT_ML_RUNTIME_V1
**Protocol Binding**: CP_REPRESENTATION_EFFICIENCY_PROTOCOL_V7
**Protocol Audit SHA**: ac26f3ae3c4f1f04e1fb5cb54a58a98882a4f368

## Environment Inventory
- **Python**: 3.13.5 (CPython)
- **OS**: macOS 26.6.2 (Darwin 25.6.0)
- **Hardware**: Apple M4 (arm64, 16 GB Memory)
- **Device**: mps

## Why Runtime Pin is Separate from Protocol Seal
The scientific protocol (V7) establishes the mathematical, geometric, and logical mechanics of the experiment, alongside the strict TARGET-blindness rules. However, numerical ML systems are subject to hardware-dependent execution variance, platform differences, and backend silent fallbacks. Pinning the runtime separately freezes the numerical execution engine without rewriting the mathematical definitions, ensuring that determinism is strictly proven on the physical environment before TARGET acquisition.

## Exact Wheel Manifest
PyTorch was pinned precisely to `2.13.0` and downloaded locally before installation without source compilation.
The full cryptographic manifest of all wheel dependencies is recorded in `artifacts/research/ml_runtime_wheel_manifest_v1.json`.

## Deterministic Settings
The `mps` environment is locked with strictly deterministic PyTorch features:
- `torch.use_deterministic_algorithms(True, warn_only=False)`
- `torch.set_deterministic_debug_mode("error")`
- `torch.set_default_dtype(torch.float32)`
- `torch.set_float32_matmul_precision("highest")`
- Environment constraints: `PYTHONHASHSEED=0`, `PYTORCH_MPS_FAST_MATH=0`, `PYTORCH_ENABLE_MPS_FALLBACK=0`, `PYTORCH_MPS_PREFER_METAL=0`

## Determinism Validation Results
The frozen architecture was tested synthetically across 3 independent Python processes for each of the 5 canonical seeds (1729, 2718, 31415, 65537, 104729).
**Result**: 15 identical state-dict hashes in each seed group. 
MPS determinism across process boundaries is strictly proven.

## Data Status
- **SOURCE Data**: UNTOUCHED
- **TARGET Data**: NOT RUN / NOT INSPECTED
- **Model Training**: No chess data training occurred.

## Resulting Status
**ML_RUNTIME_DEPENDENCY_PINNED_REAUDIT_REQUIRED**
