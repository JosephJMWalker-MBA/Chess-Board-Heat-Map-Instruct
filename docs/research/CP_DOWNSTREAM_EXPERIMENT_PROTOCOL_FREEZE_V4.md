# CP Downstream Experiment Protocol Freeze V4

**Protocol Identifier**: CP_REPRESENTATION_EFFICIENCY_PROTOCOL_V4
**Authoritative Pre-Freeze SHA**: 8876f8cf2d6e1da47b2b40b818413b4095786c36
**Canonical V4 JSON Path**: `artifacts/research/cp_representation_efficiency_protocol_v4.json`
**Canonical V4 SHA**: (Will be captured upon commit)

## History and Lineage
- **V1**: Failed independent audit due to floating point and dimensional drift.
- **V2**: Failed independent re-audit due to incomplete JSON bindings, target attrition contradictions, and test omissions.
- **V3**: Failed independent re-audit due to stale hardcoded split counts and an unimplemented bootstrap procedure.
- **V4**: Bounded repair repairing only the counts, full bootstrap, lexical validation, CompareTyped binding, and explicit learner init logic.

*Note: The V3 scientific operators and sampling domains (e.g. `CHESSHEAT_SPLIT_V3|`, `CHESSHEAT_BOOTSTRAP_V3|`) were NOT changed, to ensure sampling remains durably anchored.*

## Measured Constraints

### Split Counts
- **All-Roots**: TRAIN 23,639; VALIDATION 5,148; TEST 5,072.
- **Eligible**: TRAIN 23,350; VALIDATION 5,094; TEST 5,000.
- **Zero-Pair**: TRAIN 289; VALIDATION 54; TEST 72.

### Learner Specification
- **Layers**: Conv2d(19->64) -> ReLU -> Conv2d(64->64) -> ReLU -> Conv2d(64->64) -> ReLU -> GAP -> Concat(Side 270->128) -> Dense(192->128) -> ReLU -> Dense(128->3).
- **Initialization**: Fixed to `torch.nn.init.kaiming_uniform_` with `a=sqrt(5)` for weights and exactly calculated bounds (`-1/sqrt(fan_in)` to `1/sqrt(fan_in)`) for bias.
- **Constraints**: No dropout, no normalization, no gradient clipping, no class weighting.

### Validation & Mechanics
- **UCI Validation**: `uci_square_index` and `spatial_row_col` are strictly verified against `^[a-h][1-8]$`. SourcePairFeatures strictly validate moves against `^[a-h][1-8][a-h][1-8][qrbn]?$`.
- **CompareTyped Binding**: Bound explicitly to `src/chessheat/attribution.py:compare_scores`. Typed mate observations remain ordered.
- **Full Bootstrap Semantics**: Fully implemented using Big-Endian SHA256 deterministic hashes over `CHESSHEAT_BOOTSTRAP_V3|b|j`. Generates exactly 10,000 sets, averaging over root inferences prior to calculating `AULC`. Outputs 95% nearest-rank CIs for `Delta_DT`, `Delta_D0`, and `Delta_T0`.

## Runtime Status
- **TARGET Data**: STRICTLY UNAUTHORIZED
- **Model Training**: STRICTLY UNAUTHORIZED
- **ML Runtime**: ML_RUNTIME_DEPENDENCY_NOT_YET_SATISFIED (PyTorch is deliberately uninstalled).
