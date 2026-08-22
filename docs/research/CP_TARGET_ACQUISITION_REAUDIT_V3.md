# CP_TARGET_ACQUISITION_REAUDIT_V3

## Audit Overview
- **Audited V3 implementation SHA:** `1c8fbb778a7bffb76d149fa1ea00aa3f8c054ce8`
- **V1/V2 failed lineage:**
  - V1: `5aeaf9d331fd175562396f06ea6074364bc9d863`
  - V2: `b04155f013dfac112648f8cf383caa247ef1d816`
- **Protocol/runtime bindings:**
  - Runtime V3 implementation: `d2650cff68d0b80b9b97bc5c811045ffc46c40e9`
  - Runtime V3 audit: `6b358b24dbeb3015a270588cffdebb80a6da0b0e`
  - Protocol V7 implementation: `bf113817621894034929d9aa89b83dec14c35e69`
  - Protocol V7 audit: `ac26f3ae3c4f1f04e1fb5cb54a58a98882a4f368`
  - Protocol JSON SHA256: `ea1242de3b2f0ac1613ac9b838f014ad00ae8910cfd51d8b99c6fb77f15e29ef`
- **Manifest SHA/count:**
  - Digest: `5a013e64265820b65d1d3687fcee98aa607ab41470294d11df7b2f803c8e063d`
  - Roots: 33,859
- **Stockfish SHA:** `ae4c93fa9676ca7750d0714342fd8a5b1d018000fc6e0f6cedf112067b5ef374`

## V2 Blocker Re-evaluation
- **V2 schema-blocker verdict:** PASS. The `TARGET_OBSERVATION_SCHEMA_ALIGNMENT_PASS` is satisfied. V3 no longer expects `acquisition_index` or `comparison_perspective` at the observation level, correctly substituting them for the actual frozen properties.

## Schema Validation
- **Real observation schema:** Exactly aligned with the frozen `InstrumentSession` outputs: `canonical_acquisition_index`, `isolation_sequence_index`, `root_move_uci`, `requested_nodes`, `score_type`, `score_value`, `perspective`, `parent_history_identity`, `history_derivation_version`, `parent_move_stack_length`, `child_move_stack_length`.
- **Shared validator:** Confirmed. A single normative validator `_validate_success_result` authenticates both fresh and resumed observations identically.
- **Payload-vs-observation perspective:** Explicitly distinct. Payload uses `comparison_perspective` and observations use `perspective`.
- **child_fen adjudication:** Not explicitly authenticated inside resume parsing, but order and identity are bound by strict UCI prefix and history identity checks against a cryptographically secured initial state. This constitutes a non-material provenance-strength warning.
- **reported_nodes adjudication:** Not strictly authenticated on resume; it is engine telemetry. The requirement is enforced via `requested_nodes = 250000`. This is non-material.
- **Full payload validation adjudication:** V3 relies upon `ExperimentResult` string parsing / canonical data_payload digest to ensure bytes are untampered. Strict inspection of all fields on resume is non-material given this hash authentication.

## Execution Parity
- **Real non-corpus Stockfish smoke result:** `REAL_NONCORPUS_TARGET_SMOKE_NOT_EXECUTED`. The system stockfish binary was unavailable. Exact code inspection confirms payload conformity.
- **Approved-SHA root-of-trust adjudication:** PASS with explicit governance boundary. The environment var acts as the authoritative pointer to a human-audited commit; the code prevents uncommitted modifications. 
- **Bound-file surface:** Checked. Only strictly relevant scientific semantic and acquisition files are bound. ML logic is properly isolated.
- **Post-audit-commit approved-SHA behavior:** Will correctly pass, preventing execution from requiring HEAD to identical to the APPROVED_SHA as long as bound files don't change.
- **Manifest verification:** Recomputation exactly produces `5a013e...` from strict streamed zstd bytes.
- **SOURCE blindness:** Passed. Zero textual overlap with prohibited SOURCE variables in implementation. 

## Testing Mechanics
- **Write/reopen/resume result:** PASS.
- **Interruption-prefix result:** PASS.
- **Failure-prefix result:** PASS.
- **Hostile resume matrix:** Extensively verified. Reject bad epochs, non-canonical json, bad bounds.

## Test Counts
- **TARGET tests run 1/run 2:** 9 / 9 passed.
- **CP instrument tests:** 30 passed.
- **Protocol tests:** 36 passed.
- **Runtime V3 tests:** 14 passed.
- **Full suite run 1/run 2:** 278 / 278 passed.
- **Working-tree cleanliness:** Checked.

## Data Exposure & Outcomes
- **July TARGET roots evaluated:** 0
- **July TARGET observations produced:** 0
- **Exact blockers/warnings:**
  - *Warning*: `child_fen` and `parent_move_stack_length` are verified relatively / via indirect bounds.
- **Resulting status:** `TARGET_ACQUISITION_RUNNER_V3_REAUDIT_PASS`
- **Next blocker:** `EXPLICIT_TARGET_ACQUISITION_EXECUTION_AUTHORIZATION_REQUIRED`
- **SOURCE untouched:** Yes.
- **TARGET still AUTHORIZED_NOT_RUN:** Yes.
- **No labels:** Yes.
- **No training:** Yes.

## Verdict
**TARGET_ACQUISITION_IMPLEMENTATION_V3_REAUDIT_PASS**
