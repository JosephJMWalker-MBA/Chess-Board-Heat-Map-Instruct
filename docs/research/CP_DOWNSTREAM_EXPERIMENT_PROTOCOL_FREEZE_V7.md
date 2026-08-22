# CP Downstream Experiment Protocol Freeze V7

**Protocol Identifier**: CP_REPRESENTATION_EFFICIENCY_PROTOCOL_V7
**Authoritative Pre-Freeze SHA**: 8876f8cf2d6e1da47b2b40b818413b4095786c36
**V6 Audit SHA**: 2ebeb4123da7425c570eed3b903e7f0b94e54e85
**Canonical V7 JSON Path**: `artifacts/research/cp_representation_efficiency_protocol_v7.json`
**Canonical V7 SHA**: ea1242de3b2f0ac1613ac9b838f014ad00ae8910cfd51d8b99c6fb77f15e29ef

## History and Lineage
- **V1-V5**: See historic immutable audit documents.
- **V6**: Failed independent re-audit due to omission of multiplicity policy seal.
- **V7**: Minimal canonical-seal repair. Explicitly sealed the multiplicity policy (NO multiplicity correction is applied, Delta_DT is sole primary contrast). Added complete lineage to authoritative references. NO scientific mechanics changed.

## Resolved Material Blockers
1. **CANONICAL_SEAL_OMITS_MULTIPLICITY_POLICY**: The V7 JSON explicitly seals the `inference_policy` with `multiplicity_correction.applied = False`. It specifies that `Delta_DT` is the sole primary contrast, and `Delta_D0` and `Delta_T0` are prespecified gating/control contrasts.

## Resolved Warnings
1. **Canonical Lineage Omission**: V7 authoritative references now include V5 implementation, V5 audit, V6 implementation, and V6 audit SHAs.
2. **Promotion Test Correctness**: Fixed `test_promotion_validation` in `tests/test_protocol_freeze.py` to correctly test the actual one-hot slots (261-265) produced by the correct production encoding.

## Runtime Status
- **TARGET Data**: STRICTLY UNAUTHORIZED
- **Model Training**: STRICTLY UNAUTHORIZED
- **ML Runtime**: ML_RUNTIME_DEPENDENCY_NOT_YET_SATISFIED (PyTorch is deliberately uninstalled).
