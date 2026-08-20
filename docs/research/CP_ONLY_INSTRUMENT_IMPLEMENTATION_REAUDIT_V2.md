# Independent Protocol-vs-Implementation Re-Audit: V2 Repair

**Implementation Candidate Audited:** `5a1c61d5895e0d7001f2e93d98d2b5f0ee287791`

**Frozen Protocol:** `INSTRUMENT_CONFIG_FROZEN_SF18_50K_250K_V1`

**Execution Boundary:**
Pure Python code inspection and execution via mock engine logic. No July corpus downloaded. No Stockfish process executed. No Target/Source acquisition run. No model training.

---

## 1. Prior Finding Dispositions (V1 Audit)

| Finding | Disposition | Note |
|---|---|---|
| A. Option API (`.value`) | **PASS** | Removed previously. |
| B. History Preservation | **PASS** | `root_board.copy(stack=True)` used correctly. |
| C. Executable Identity | **PASS** | Replaced with `ExecutableIdentity` capturing actual digests. |
| D. Managed UCI Semantics | **PASS** | Test framework uses real `chess.engine.Option` classes. |
| E. EvalFile / EvalFileSmall | **PASS** | Missing option tested and rejected. |
| F. Complete Option Provenance | **PASS** | `MANAGED_OPTIONS` cast to sorted list; keys sorted. |
| G. Spec/Result Binding | **PASS** | Bound via `ExperimentResult.create()`. |
| H. Fresh Game Tokens | **PASS** | Unique `object()` per analysis. |
| I. Score Validation/Perspective | **PASS** | Handled natively. |
| J. Node Provenance | **PASS** | Boolean nodes are rejected. |
| K. Role/Process Isolation | **PASS** | `InstrumentRole` enum properties correctly guard modification. |
| L. Child Identity | **PASS** | Uses precise stack length counts rather than hardcoded string logic. |

---

## 2. Prior Finding Dispositions (V1 Re-Audit / N-Z)

| Finding | Disposition | Description |
|---|---|---|
| N. Budget Schema | **PASS** | Validates against precise `{"type": "nodes", "value": X}` schema via `get_canonical_budget_config`. |
| O. En-passant Schema | **PASS** | Validates missing ep squares against `None` explicitly. |
| P. Deterministic Serialization | **PASS** | Tests mechanically demonstrate matching payload/artifact hashes across repeated executions. |
| Q. Pre/Post SHA Truthfulness | **PASS** | Observed digests bound natively via `ExecutableIdentity`. |
| R. Real `is_managed` Testing | **PASS** | Simulated with actual `python-chess` API logic rather than overrides. |
| S. History Trust Boundary | **PASS** | Empty constraints (`True` / non-empty string) bound safely without inventing new hashing schemes. |
| T. Root Validity | **PASS** | Properly filters `is_valid()`, standard non-terminal, and `len(legal_moves) >= 2`. |
| V. Option Compatibility | **PASS** | Ensures unmanaged `STATIC_UCI_CONFIG` bindings route through `parse()`. |
| W. Syzygy `<empty>` Semantics | **PASS** | Uses native `<empty>` which correctly suppresses Stockfish 18 tablebases. |
| X. Candidate Policy Schema | **PASS** | Rigidly enforces complete expected dictionary including `scope` strings. |
| Y. Instrument Config Completeness | **PASS** | Full dict comparison rejecting arbitrary mismatched fields (Threads/Hash/network). |
| Z. Child Derivation | **PASS** | Tracks structural integer length progressions (`child == parent + 1`). |
| Boolean Nodes Handling | **PASS** | Explicit `type(nodes) is not int` inspection implemented. |

---

## 3. Syzygy `<empty>` Precision

The `<empty>` value was audited against real `python-chess` serialization.
`Option.parse("<empty>")` correctly outputs the string `"<empty>"`.
The library sets the option by concatenating `setoption name SyzygyPath value <empty>`.
The UCI protocol officially designates `<empty>` as the command to clear a string option. Therefore, sending `<empty>` successfully commands Stockfish to clear its tablebase path, proving NO EXTERNAL TABLEBASE ACCESS.

---

## 4. Test Adequacy Matrix (Hostile Inspection)

While the V2 repair claims "comprehensive tests", mechanical hostile inspection reveals critical missing test proofs:

| Required Test Proof | Status | Description |
|---|---|---|
| **Acquisition Mechanics** | **ABSENT** | Tests do not use `assert_called_with` to prove `multipv=None` or `root_moves=None`. |
| **Child Board Passed** | **ABSENT** | Tests do not verify the mocked engine actually received the cloned/pushed board. |
| **Target/Source Process Independence**| **PARTIAL** | The test for determinism calls `start()` on two separate sessions, but `@patch` returns the EXACT SAME `mock_engine` object for both. Process separation is not mechanically proven. |
| **History Validation Rejections** | **PARTIAL** | Tests `history_available=False` but entirely skips testing missing/empty `history_identity` strings. |
| **History Provenance Flow** | **IMPLEMENTATION-GUARANTEED-BUT-UNTESTED** | `parent_move_stack_length` truthfulness and `history_identity` persistence are not asserted in test payloads. |
| **Lifecycle Rejections** | **ABSENT** | No tests for `close()` idempotency, acquire-before-start, acquire-after-close, or engine quit on post-spawn failure. |

---

## 5. ExperimentResult Integrity

The instrument binds `spec_digest` both as a top-level `ExperimentResult.create()` argument and as an internal key inside the `data` dictionary payload. While harmless in this closed system, `ExperimentResult.create` does not assert that the dictionary payload `spec_digest` equals the argument `spec_digest`. It is accepted because the implementation guarantees equality, but is not strictly verified.

---

## 6. Verdict

**V2_REAUDIT_FAIL**

While the implementation code correctly repaired all semantic protocol boundaries, the test suite falls dramatically short of the required execution-critical proofs. Specifically, the test suite fails to prove independent process ownership (mocking the same engine instance), fails to assert the specific arguments passed to `analyse()`, and omits lifecycle constraints completely.

**Strongest Blocker:** `PROTOCOL_IMPLEMENTATION_REPAIR_REQUIRED_V3`
**Source Acquisition Status:** UNAUTHORIZED
**Target Acquisition Status:** UNAUTHORIZED
