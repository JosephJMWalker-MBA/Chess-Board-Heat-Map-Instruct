# CP Downstream Experiment Protocol Freeze V6

**Protocol Identifier**: CP_REPRESENTATION_EFFICIENCY_PROTOCOL_V6
**Authoritative Pre-Freeze SHA**: 8876f8cf2d6e1da47b2b40b818413b4095786c36
**V5 Audit SHA**: ef56b140aa9cc192a7ad8c571235dd4676066ffe
**Canonical V6 JSON Path**: `artifacts/research/cp_representation_efficiency_protocol_v6.json`
**Canonical V6 SHA**: 67fb9be58159dee1f6c47bb5c8b0b482756f93cd2fc738e448005f10c1081b04

## History and Lineage
- **V1**: Failed independent audit due to floating point and dimensional drift.
- **V2**: Failed independent re-audit due to incomplete JSON bindings, target attrition contradictions, and test omissions.
- **V3**: Failed independent re-audit due to stale hardcoded split counts and an unimplemented bootstrap procedure.
- **V4**: Failed independent re-audit due to unfrozen bootstrap root order, omitted Conv dilation/groups, shadowed pytest assertions, omitted `allow_nan=False`, and SOURCE verifier gaps.
- **V5**: Failed independent re-audit because, despite successfully fixing all V4 implementation blockers, the V5 repair left material contradictions in the preregistration document and omitted critical mathematical definitions of $D$, $T$, and the outcome classifier from the canonical JSON seal.
- **V6**: Hardening repair injecting missing D/T spatial definitions and outcome classifier logic into the canonical machine-readable seal, and manually resolving preregistration contradictions. No scientific redesign.

## Resolved Material Blockers
1. **Preregistration Internal Contradictions**: Manually eliminated legacy language stating that the budget schedule, seed-aggregation rule, alpha level, and split sizes remained unresolved choices.
2. **D and T Topological Definitions**: The V6 JSON explicitly states $D = \{to(m_1), to(m_2)\}$ and $T = \{from(m_1), to(m_1), from(m_2), to(m_2)\}$ with exact set deduplication.
3. **Outcome Classifier Logic**: The V6 JSON explicitly binds the deterministic outcome logic rules (e.g. `SUPPORT_muD`, `NO_SPATIAL_EFFICIENCY_ADVANTAGE`) and their evaluation precedence.

## Runtime Status
- **TARGET Data**: STRICTLY UNAUTHORIZED
- **Model Training**: STRICTLY UNAUTHORIZED
- **ML Runtime**: ML_RUNTIME_DEPENDENCY_NOT_YET_SATISFIED (PyTorch is deliberately uninstalled).
