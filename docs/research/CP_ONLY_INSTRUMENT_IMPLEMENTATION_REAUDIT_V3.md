# ChessHeat CP-Only Isolated Instrument — Independent Implementation Re-Audit V3

**Date:** 2026-08-20
**Instrument Contract:** `INSTRUMENT_CONFIG_FROZEN_SF18_50K_250K_V1`

## Repositories & Execution Bounds
**Production Implementation Audited:** `5a1c61d5895e0d7001f2e93d98d2b5f0ee287791`
**Proof Harness Audited:** `e982366a63151651a2e360fcec995488bb0b357c`
**Repository HEAD at audit start:** `938256a68f1b5a0208e9c6ddbc8ea254f08dcdf6`

**Execution Boundary Adherence:**
- No Stockfish processes were executed.
- No chess-position searches occurred.
- No July corpus was downloaded.
- No source or target study acquisition was authorized or performed.
- No model training was executed.

---

## Verdict

**VERDICT: V3_REAUDIT_PASS**

All execution-critical frozen instrument requirements are sufficiently mechanically established. The production implementation (`5a1c61d5...`) cleanly and accurately represents the `INSTRUMENT_CONFIG_FROZEN_SF18_50K_250K_V1` scientific boundaries without error, while the strengthened V3 proof harness (`e982366a...`) comprehensively protects against mechanical regressions, establishing clear structural proofs for lifecycle, provenance, state isolation, and child derivations.

---

## Historical Findings Re-evaluated

| Finding | Prior Disposition | V3 Evidence | V3 Disposition |
|---|---|---|---|
| Opaque History Upstream | FAIL | Instrument delegates history creation upstream to S0 S1 | PASS |
| Child Derivation Informality | FAIL | Explicit `copy(stack=True)` enforces S_CHILD derivation | PASS |
| Syzygy `<empty>` Precision | PARTIAL | `python-chess` literal `<empty>` equates formally to empty tablebase path in Stockfish | PASS |
| Process Leakage | FAIL | Independent fake MagicMock process objects mechanically verified | PASS |
| Failed-Child Continuation | FAIL | Re-audit V3 asserts exactly `call_count == 3` halting correctly after failure | PASS |
| Missing Score/Node Types | FAIL | Exact `test_score_output_proofs` mapping established | PASS |
| Lifecycle Assertions | FAIL | `test_failed_child_acquisition` + startup teardown asserts `mock_engine.quit()` | PASS |

---

## Complete Proof Matrix Summary

### 1. Producer Identity & Semantics
- **Requirement:** Stockfish 18 UCI, distinct SHA, isolated paths.
- **Evidence:** `test_verify_executable_resolved_path`, `test_wrong_uci_name`. S0 provenance tracks authoritative SHAs securely.
- **Status:** PASS

### 2. Configuration & Network Semantics
- **Requirement:** Fixed Threads, Hash, Skill Level, false limits/WDL. SyzygyProbeLimit 0. No NNUE configs applied.
- **Evidence:** `test_configure_call_proof` verifies options mapping. `test_static_option_parse_failure` guarantees failure traps.
- **Status:** PASS

### 3. S0 / Root Validity
- **Requirement:** Valid non-terminal position, standard chess.
- **Evidence:** `test_root_validity` explicitly catches terminal/invalid states. `test_en_passant_canonicalization` strips S0 transients securely.
- **Status:** PASS

### 4. Process Isolation
- **Requirement:** SOURCE (50k) and TARGET (250k) operate independently.
- **Evidence:** `test_source_target_process_independence` tests parallel instantiations.
- **Status:** PASS

### 5. Acquisition / Child Mechanics
- **Requirement:** Scope exactly `cp_all_legal_root_moves_v1`, identical count, exact lexicographical order, fresh tokens, exact stack propagation, root unmutated.
- **Evidence:** `test_acquisition_mechanics_and_child_proofs` asserts precise sequence length, tokens (`game`), and `Limit.nodes == role_budget`.
- **Status:** PASS

### 6. Failure / Lifecycle
- **Requirement:** Fail-closed process. Startup, teardown, mid-acquisition failure halts all operation.
- **Evidence:** `test_failed_child_acquisition` ensures single immediate quit. `test_configuration_failure_cleanup` proves session destruction.
- **Status:** PASS

### 7. Authoritative Provenance
- **Requirement:** Accurate payload serialization, exact option surface recorded, immutable structural artifact.
- **Evidence:** `test_acquisition_mechanics_and_child_proofs`, `test_deterministic_provenance`.
- **Status:** PASS

---

## Independent Hostile Search
No independent flaws or logical regressions were discovered beyond historical findings. The `ExperimentResult` artifact precisely reflects the frozen configuration in both test schemas and production logic.

---

## Remaining Limitations & Next Stage

**Limitations:**
- Actual implementation coverage feasibility over the July 2026 Corpus depends on future empirical testing, which may uncover execution-time timeouts outside the instrument's logic bounds.
- Source feasibility analysis is structurally authorized but pending exact execution.

**Next Immediate Stage:**
`SOURCE_ONLY_FEASIBILITY_COVERAGE_ACQUISITION`
*(Measures CP eligibility and pair counts after root/instrument are frozen. May not inspect held-out target labels).*

**Dependencies:**
- `SPLIT_AND_BUDGET_NOT_YET_FROZEN`
- `P_NUMERIC_ENCODING_NOT_YET_FROZEN`
- `LEARNER_FAMILY_NOT_YET_FROZEN`
Target acquisition and Model training remain strictly UNAUTHORIZED.
