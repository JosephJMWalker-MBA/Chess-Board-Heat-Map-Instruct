# Independent Protocol-vs-Implementation Re-Audit: CP-Only Isolated Instrument

**Implementation Candidate:** `dfd4845681d2ea765da29c12971ce3cce24dc124`
**Repository HEAD:** `8dd4725ab40d7715b1e4afa814932c09d3896063`
**Verification:** No implementation code or frozen protocol semantics changed after the candidate commit.

**Frozen Protocol:** `INSTRUMENT_CONFIG_FROZEN_SF18_50K_250K_V1`
**Audit Scope:** `src/chessheat/cp_instrument.py` and `tests/test_cp_instrument.py`

**Execution Boundary:**
This audit was performed mechanically and statically via pure-Python probes, AST inspection, and logic tracing. NO chess-position search was executed. NO July corpus was downloaded. NO source/target study acquisition occurred.

---

## 1. Original Audit Findings (A-M) Disposition

| Finding | Disposition | Note |
|---|---|---|
| A. Option API (`.value`) | **PASS** | Removed. `is_managed()`, `default` and serialization correctly use Option metadata. |
| B. History Preservation | **PASS** | `root_board.copy(stack=True)` correctly preserves parent history. |
| C. Executable Identity | **PARTIAL** | Pre/post-spawn checks run, but provenance records expected SHA constants rather than actual observed pre/post digests. |
| D. Managed UCI Semantics | **PARTIAL** | `is_managed()` enforced, but tests mock the library logic rather than asserting real python-chess behavior. |
| E. EvalFile / EvalFileSmall | **PASS** | Evaluated for existence and unconfigured explicitly. Defaults extracted. |
| F. Complete Option Provenance | **PARTIAL** | Complete surface is retrieved, but non-deterministic iteration over the `MANAGED_OPTIONS` set makes the payload nondeterministic. |
| G. Spec/Result Binding | **PASS** | Correctly bound through `ExperimentResult.create()`. |
| H. Fresh Game Tokens | **PASS** | Verified token uniqueness across child evaluations. |
| I. Score Validation/Perspective | **PASS** | `result["score"]` perspective correctly mapped, scalarized safely. |
| J. Node Provenance | **PASS** | Fallback removed, defaults to `None` if engine drops `nodes`. |
| K. Role/Process Isolation | **PASS** | `InstrumentRole` enum and read-only properties prevent mutable reuse. |
| L. Child Identity | **PARTIAL** | Derived FENs recorded, but child derivation provenance is just a hardcoded string literal assertion rather than a mechanically bound derivation proof. |
| M. Test Adequacy | **FAIL** | Tests were rewritten, but they omit critical validations (budget mismatch, candidate policy mismatch, history checks, real Option behavior). |

---

## 2. New Findings (N-Z) Disposition

| Finding | Disposition | Description |
|---|---|---|
| N. Budget Schema | **FAIL** | The implementation expects `spec.budget_config.get("nodes") == expected`, but existing `ExperimentSpec v2` artifacts use `{"type": "nodes", "value": 100000}`. |
| O. En-passant Schema | **FAIL** | Implementation expects `"-"` for missing `ep_square`, but `SufficientPosition` schema and existing artifacts use `None`/`null`. |
| P. Deterministic Serialization | **FAIL** | `list(MANAGED_OPTIONS)` casts a Python `set`, resulting in non-deterministic ordering and fragile `ExperimentResult` payload hashes. |
| Q. Pre/Post SHA Truthfulness | **FAIL** | `verify_executable()` returns a path, not a digest. Provenance blindly records `STOCKFISH_BINARY_SHA256` instead of actual observed hashes. |
| R. Real `is_managed` Testing | **FAIL** | `test_cp_instrument.py` completely mocks `is_managed()` out of existence via `FakeOption`. The real python-chess behavior is never proven mechanically. |
| S. History vs Move Stack | **FAIL** | The instrument accepts the corpus-provided `history_identity` blindly without mechanically verifying it corresponds to the `root_board.move_stack`. |
| T. Root Validity | **FAIL** | `root_board.is_valid()` was removed. The instrument now accepts invalid board structures as long as they have >0 pseudo-legal moves. |
| U. Role Immutability Depth | **PASS** | Python property getters adequately protect `session.role` from external mutation at the API boundary. |
| V. Static Option Compatibility | **NOT_MECHANICALLY_PROVEN** | Tests use fake options with `spin` or `string` but never mechanically verify Stockfish 18's actual option bounds or parseability. |
| W. Syzygy `<empty>` Semantics | **PASS** | Explicitly configuring `"<empty>"` disables the tablebase in Stockfish UCI, but it is not formally proven by tests. |
| X. Candidate Policy Schema | **FAIL** | Implementation validates `ordered_legal_root_ucis` but ignores `scope`, permitting a semantically different policy to impersonate `cp_all_legal_root_moves_v1`. |
| Y. Instrument Config Completeness| **FAIL** | Implementation only checks `instrument_id` in `instrument_config`, ignoring all other keys (like arbitrary `Threads` values) that might conflict with the frozen protocol. |
| Z. Child Derivation Provenance | **FAIL** | Recorded derivation is a hardcoded literal `child_history derives from parent + root_move` rather than an explicit verifiable child history identity. |
| Boolean Nodes Handling | **FAIL** | `isinstance(True, int)` evaluates to True in Python, so a malformed engine returning `nodes=True` would bypass validation and be recorded as 1 node. |

---

## 3. Test Adequacy Summary

188 tests exist, but critical execution boundaries lack assertions:
- Missing EvalFile missing network options rejection.
- Budget mismatch rejection.
- Candidate policy mismatch rejection.
- Unexpected PV/list results from the engine.
- Invalid root board layouts (e.g. 3 kings).
- TOCTOU (Time-of-check to time-of-use) executable hash mutation.
- Artifact integrity/determinism across processes.

---

## 4. Verdict

**REAUDIT_FAIL**

The implementation candidate contains execution-critical violations of the frozen protocol regarding schema conformance, deterministic provenance, validation depth, and test proofs.

**Strongest Blocker:** `PROTOCOL_IMPLEMENTATION_REPAIR_REQUIRED_V2`
**Source Acquisition Status:** UNAUTHORIZED
**Target Acquisition Status:** UNAUTHORIZED

