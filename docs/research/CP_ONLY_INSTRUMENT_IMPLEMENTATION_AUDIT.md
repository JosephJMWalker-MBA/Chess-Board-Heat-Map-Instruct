# CP-Only Instrument Implementation Audit

**Audited Commit SHA:** b4d10462b39fa9844649aacbab82f18c3de8b71f
**Frozen Protocol Identity:** INSTRUMENT_CONFIG_FROZEN_SF18_50K_250K_V1
**Audit Scope:** Hostile, falsification-oriented audit of `src/chessheat/cp_instrument.py` against Section 5 of the active preregistration.
**Execution Note:** Explicitly NO engine execution, NO model training, NO corpus download occurred during this audit.

## Verdict
**AUDIT_FAIL**

Source acquisition remains unauthorized.

## Findings Summary
- CRITICAL: 4
- MAJOR: 3
- MODERATE: 1
- MINOR: 1

## Requirement Matrix

| Requirement | Status | Notes |
|---|---|---|
| Producer Identity (Stockfish 18) | PARTIAL | Name is checked, but post-spawn SHA verification is missing. |
| Binary Identity (SHA) | PARTIAL | Pre-spawn SHA checked, but post-spawn SHA re-verification missing. |
| Static Options | FAIL | `Option.value` is accessed, which doesn't exist in `python-chess`, causing crashes. |
| Managed Options | PARTIAL | Checked by name, but doesn't actually use `Option.is_managed()`. |
| Source/Target Budget | PASS | Budgets correctly assigned by role. |
| All-legal Acquisition | FAIL | `chess.Board(child_fen)` discards move history, violating `SufficientPosition`. |
| Canonical Order | PASS | Lexicographical sort on UCI strings. |
| No Baseline | PASS | Plan generation does not invoke engine. |
| Root Perspective | PASS | Frozen before iteration, converted via `pov()`. |
| Typed Outcomes | PASS | Mate distance preserved, not scalarized to CP. |
| Per-child Fresh Game Token | NOT_MECHANICALLY_PROVEN | Tests only verify the `game` token on the final call, not uniqueness across all calls. |
| Source/Target Process Ownership | FAIL | Parallel `Observation` objects bypass the frozen `ExperimentSpec/Result` spine. Roles are trivially mutable in Python. |
| NNUE Policy | FAIL | Uses non-existent `Option.value` to check override, which will crash in production. |
| Tablebase Policy | FAIL | Uses non-existent `Option.value` to check `SyzygyPath`, causing a crash. |
| Fail-Closed Behavior | FAIL | `result.get("nodes", self.nodes)` manufactures fake node provenance if missing. |
| Provenance Surface | FAIL | Does not record the complete observed UCI option surface, only the statically configured ones. |

## Seeded Leads Confirmed

### A. Real python-chess Option interface
**Confirmed / CRITICAL:** `chess.engine.Option` does not have a `.value` attribute. It only holds metadata (`name`, `type`, `default`, `min`, `max`, `var`). The implementation crashes with an `AttributeError` on line 121 (`val = options[k].value`). The test suite passed only because it mocked an invented option interface.

### B. History preservation
**Confirmed / CRITICAL:** `child_board = chess.Board(entry.child_fen)` completely discards the board's move stack. This destroys `SufficientPosition` constraints (repetition history and 50-move bounds).

### C. Executable identity
**Confirmed / MAJOR:** Pre-spawn SHA check exists, but the mandated post-spawn SHA re-verification is missing. Additionally, `resolved_path` records the unexpanded string passed by the caller, not the absolute resolved path.

### D. UCI option semantics
**Confirmed / MAJOR:** `MANAGED_OPTIONS` checks name inclusion but does not actually test `options[k].is_managed()`.

### E. EvalFile / EvalFileSmall
**Confirmed / FAIL:** Validating the network requires reading `.value`, which fails.

### F. Complete option-surface provenance
**Confirmed / MAJOR:** The implementation does not record the complete observed UCI option surface, only the subset it configured.

### G. ExperimentSpec v2 / ExperimentResult spine
**Confirmed / CRITICAL:** The implementation ignores `src/chessheat/experiment.py` entirely, inventing a parallel `Observation` dataclass and a primitive `_provenance` dictionary rather than binding into the frozen experimental spine.

### H. Fresh per-child reset proof
**Confirmed / NOT MECHANICALLY PROVEN:** The test `test_session_start_and_acquire` asserts `call_kwargs["game"]` on the last mock call. It does not prove that every legal move received a uniquely instantiated token.

### I. Root perspective and score typing
**Confirmed / PARTIAL:** Uses `PovScore.pov()`. But malformed scores (e.g. `None`) could pass the `"score" in result` check and crash.

### J. Node-budget enforcement / provenance
**Confirmed / MODERATE:** `result.get("nodes", self.nodes)` silently manufactures fake provenance if the engine fails to report nodes.

### K. Role immutability / process ownership
**Confirmed / MINOR:** `self.role` is a public mutable attribute, not mechanically protected.

### L. Child identity
**Confirmed / FAIL:** Tied to the history deletion issue (B). `child_fen` alone is insufficient to reconstruct the exact child `SufficientPosition`.

### M. Test adequacy
**Confirmed / CRITICAL:** The test suite is inadequate. It mocks the engine so aggressively that it hides `AttributeError`s and fails to verify critical loop invariants (like token uniqueness).

## Independently Discovered Defects
None further.

## Blockers Required Before Re-audit
```text
PROTOCOL_IMPLEMENTATION_REPAIR_REQUIRED
```

## Precision Erratum

The `chess.Board(child_fen)` finding requires precision: FEN reconstruction *does* preserve the halfmove clock and fullmove number. The protocol failure was that it discards the `move_stack` (prior-position history), thereby failing to preserve repetition-sensitive history and the complete history-aware S0 state. Legal-move enumeration itself was complete; the failed requirement was acquisition of the correct history-bearing child state.

Additionally, the `ExperimentSpec/ExperimentResult` bypass is a provenance-spine failure distinct from the process ownership / role mutability finding.

These clarifications do not alter the `AUDIT_FAIL` verdict.
