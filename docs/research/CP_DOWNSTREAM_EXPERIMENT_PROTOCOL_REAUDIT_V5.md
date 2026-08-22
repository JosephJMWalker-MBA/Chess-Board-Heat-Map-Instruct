# CP Downstream Experiment Protocol Re-Audit V5

**Audited SHA**: df3dd79443fb4f067971500605eee8cfe9bc8c70
**Prior Audit SHA**: 7bbbef81fa83ff9babab6049aa7c891a53cdf948
**Authoritative Pre-Freeze SHA**: 8876f8cf2d6e1da47b2b40b818413b4095786c36
**Protocol ID**: CP_REPRESENTATION_EFFICIENCY_PROTOCOL_V5
**Claimed JSON Digest**: 9209e9a44fe2f44beb08bb36b900619f1967def3574b96d48225324281dc223c
**Recomputed JSON Digest**: 9209e9a44fe2f44beb08bb36b900619f1967def3574b96d48225324281dc223c
**SOURCE Raw SHA**: 7eb640c572dad4c6607cfb1b5ccf99597672042e5c516f131feab02223ccfa6b

## Scope and Boundary Verification
**Boundary**: Verified. TARGET remains unauthorized, no labels created, no models trained, no PyTorch installed. SOURCE evidence is untouched. Immutable historical artifacts untouched.

## Finding Matrix

### 1. V4 Blocker Repairs
- **Bootstrap Root Order**: **PASS**. V5 introduced `canonical_bootstrap_root_order` which forces lexicographical sorting of canonical root identity strings. The order-invariance test passes, proving the dependency on caller order is eliminated.
- **Learner Conv Seal**: **PASS**. `dilation=[1,1]` and `groups=1` are explicitly bound in the V5 canonical payload.
- **Shadowed Pytest Names**: **PASS**. Duplicate test names were eliminated via consolidation and enforced by an AST-level hygiene check (`test_no_duplicate_test_names_ast`).
- **allow_nan Contract**: **PASS**. Serializer properly uses `allow_nan=False` and rejects IEEE-754 injections.
- **SOURCE Raw Evidence Verifier**: **PASS**. The script cryptographically binds the artifact path to its `7eb640...` SHA256 through streaming bytes before executing JSON logic.

### 2. Preregistration Internal Consistency (MATERIAL FAIL)
- **Audit**: The V5 repair attempted to update `CP_ONLY_REPRESENTATION_EFFICIENCY_PREREGISTRATION.md` but used flawed regex/string-replacements that failed to remove critical legacy language.
- **Findings**:
  1. Section 12 states: *"We must freeze a deterministic budget schedule as a function of final training-root count..."* despite the schedule already being strictly frozen.
  2. Section 17 states: *"Training-seed sensitivity is a reported stability diagnostic until an exact seed-aggregation rule is frozen."* despite exact five-seed averaging being strictly frozen.
  3. Section 18 Blocker Table lists `\alpha level, bootstrap size` as remaining unresolved scientific choices for `CONFIDENCE_LEVEL_FROZEN_V5`.
  4. Section 19 Status claims the protocol is at `DOWNSTREAM_EXPERIMENT_PROTOCOL_V3_IMPLEMENTED_REAUDIT_REQUIRED`.
- **Verdict**: **FAIL**. A canonical machine-readable JSON seal cannot coexist with a contradictory active preregistration document that instructs future researchers that these choices remain open/diagnostic.

### 3. Canonical Scientific Seal Completeness (MATERIAL FAIL)
- **Audit**: The canonical JSON attempts to seal $M_D$ and $M_T$ construction with the string: `"mu_D": "a_X / |D| if s in deduplicated D else 0"`.
- **Findings**: The seal entirely fails to define what $D$ and $T$ are. The mathematical definitions $D = \{\text{to}(m_1), \text{to}(m_2)\}$ and $T = \{\text{from}(m_1), \text{to}(m_1), \text{from}(m_2), \text{to}(m_2)\}$ are absent from the machine-readable artifact.
- **Verdict**: **FAIL**. If the JSON payload is the complete canonical scientific seal, it cannot silently omit the topological definition of the primary spatial operators. Future execution could redefine the geometry of $D$ and claim compliance.

### 4. Outcome Seal Completeness (MATERIAL FAIL)
- **Audit**: The canonical JSON lists `"primary_contrast": "Delta_DT = AULC_D - AULC_T"`, but omits the formulas for `SUPPORT_muD`, `SUPPORT_muT`, `SPATIAL_EFFICIENCY_OPERATOR_UNRESOLVED`, and `NO_SPATIAL_EFFICIENCY_ADVANTAGE`.
- **Verdict**: **FAIL**. The exact deterministic mapping from CI bounds to outcome class is the crux of the protocol. It must be in the canonical seal, not left to an external Python classifier function.

### 5. Test Namespace Hygiene / Weak Tests
- **Findings**: `test_protocol_freeze.py` contains dual imports from `chessheat.protocol_freeze` and `src.chessheat.protocol_freeze`. Additionally, `test_promotion_validation` is a no-op test with zero assertions. 
- **Verdict**: Cosmetic / Test Adequacy warning. Not by itself a material fail since the module is stateless and no falsified coverage claim masks an active scientific bug, but poor hygiene.

### 6. B_raw Omission
- **Findings**: `B_raw` is omitted from the JSON seal.
- **Verdict**: Non-material. `B_raw` is prospectively defined as a diagnostic reference, not a protocol decision boundary.

## Overall V5 Verdict
**DOWNSTREAM_PROTOCOL_V5_REAUDIT_FAIL**

**Resulting Status**: `DOWNSTREAM_EXPERIMENT_PROTOCOL_V5_REAUDIT_FAILED`
**Next Blocker**: `DOWNSTREAM_EXPERIMENT_PROTOCOL_REPAIR_REQUIRED_V6`

**Material Blockers**:
1. `PREREGISTRATION_INTERNAL_CONTRADICTIONS`
2. `CANONICAL_SEAL_OMITS_M_TOPOLOGY_DEFINITION`
3. `CANONICAL_SEAL_OMITS_OUTCOME_CLASSIFIER_LOGIC`
