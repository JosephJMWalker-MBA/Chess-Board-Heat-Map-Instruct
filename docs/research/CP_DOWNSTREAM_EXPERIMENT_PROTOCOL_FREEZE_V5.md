# CP Downstream Experiment Protocol Freeze V5

**Protocol Identifier**: CP_REPRESENTATION_EFFICIENCY_PROTOCOL_V5
**Authoritative Pre-Freeze SHA**: 8876f8cf2d6e1da47b2b40b818413b4095786c36
**Canonical V5 JSON Path**: `artifacts/research/cp_representation_efficiency_protocol_v5.json`
**Canonical V5 SHA**: 9209e9a44fe2f44beb08bb36b900619f1967def3574b96d48225324281dc223c

## History and Lineage
- **V1**: Failed independent audit due to floating point and dimensional drift.
- **V2**: Failed independent re-audit due to incomplete JSON bindings, target attrition contradictions, and test omissions.
- **V3**: Failed independent re-audit due to stale hardcoded split counts and an unimplemented bootstrap procedure.
- **V4**: Failed independent re-audit due to unfrozen bootstrap root order, omitted Conv dilation/groups, shadowed pytest assertions, omitted `allow_nan=False`, and SOURCE verifier gaps.
- **V5**: Bounded hardening repair eliminating non-determinism in bootstrap root sampling, cementing learner architecture, cleaning tests, checking strict byte bindings, and ensuring exact provenance links.

*Note: The V3 scientific operators and sampling domains (e.g., `CHESSHEAT_SPLIT_V3|`, `CHESSHEAT_BOOTSTRAP_V3|`) remain exactly preserved to avoid sampling drift.*

## Measured Constraints

### Split Counts
- **All-Roots**: TRAIN 23,639; VALIDATION 5,148; TEST 5,072.
- **Eligible**: TRAIN 23,350; VALIDATION 5,094; TEST 5,000.
- **Zero-Pair**: TRAIN 289; VALIDATION 54; TEST 72.

### Learner Specification
- **Layers**: Conv2d(19->64, dilation=[1,1], groups=1) -> ReLU -> Conv2d(64->64, dilation=[1,1], groups=1) -> ReLU -> Conv2d(64->64, dilation=[1,1], groups=1) -> ReLU -> GAP -> Concat(Side 270->128) -> Dense(192->128) -> ReLU -> Dense(128->3, class_order=["FIRST_BETTER", "EQUAL", "SECOND_BETTER"]).
- **Initialization**: Fixed to `torch.nn.init.kaiming_uniform_` with `a=sqrt(5)` for weights and exactly calculated bounds (`-1/sqrt(fan_in)` to `1/sqrt(fan_in)`) for bias.
- **Constraints**: No dropout, no normalization, no gradient clipping, no class weighting.

### Validation & Mechanics
- **Canonical Serialization**: Uses strict `allow_nan=False` inside Python's JSON dump to prohibit IEEE-754 injections.
- **SOURCE Raw Evidence Verification**: `verify_protocol_v5_source_evidence.py` strictly computes the raw JSONL evidence SHA256 (`7eb640c...`) prior to counting objects, removing any local file swap provenance gap.
- **Bootstrap Root Order**: Held-out test roots are now explicitly canonicalized via lexicographically ascending identity strings prior to hashing, resolving the order-dependent indexing defect.
- **Test Deduplication**: The unit tests have been AST-verified for uniqueness, ensuring zero shadowed assertions across V1-V5 coverage constraints.

## Runtime Status
- **TARGET Data**: STRICTLY UNAUTHORIZED
- **Model Training**: STRICTLY UNAUTHORIZED
- **ML Runtime**: ML_RUNTIME_DEPENDENCY_NOT_YET_SATISFIED (PyTorch is deliberately uninstalled).
