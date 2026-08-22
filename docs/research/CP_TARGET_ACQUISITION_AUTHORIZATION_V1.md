# CP TARGET Acquisition Authorization V1

**Authorization Date**: 2026-08-22
**Status**: TARGET_ACQUISITION_AUTHORIZED_NOT_YET_RUN

Explicit human authorization has been granted for TARGET acquisition.

## Scope
This authorization is STRICTLY limited to the acquisition of the TARGET dataset.
It DOES NOT authorize:
- Protocol changes
- Target-based root selection
- Source-based target filtering
- Label derivation
- Pair-analysis results
- Model training on real chess data

## Protocol & Environment
- **Protocol**: `CP_REPRESENTATION_EFFICIENCY_PROTOCOL_V7`
- **Protocol JSON SHA256**: `ea1242de3b2f0ac1613ac9b838f014ad00ae8910cfd51d8b99c6fb77f15e29ef`
- **Runtime Version**: `CHESSHEAT_ML_RUNTIME_V3`
- **Target Instrument**: `CP_TARGET_SF18_250K_ISOLATED_V1`
- **Producer / Stockfish**: `Stockfish 18`
- **Stockfish Binary SHA256**: `ae4c93fa9676ca7750d0714342fd8a5b1d018000fc6e0f6cedf112067b5ef374`

## Dataset Constraints
- **Manifest Digest**: `5a013e64265820b65d1d3687fcee98aa607ab41470294d11df7b2f803c8e063d`
- **Admitted Root Count**: Exactly `33859` roots.

Acquisition must be performed strictly using `scripts/run_cp_target_acquisition.py` which will produce deterministic `CP_TARGET_ACQUISITION_RESULT_V1` artifacts in the frozen data directories without accessing SOURCE results.
