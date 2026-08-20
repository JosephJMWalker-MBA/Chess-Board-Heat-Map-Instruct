# CP Source Feasibility Acquisition Audit V1

## Verdict: SOURCE_ACQUISITION_INVALID

## Scope and Authorization
This audit evaluates the execution of `SOURCE_ONLY_FEASIBILITY_COVERAGE_ACQUISITION`. The underlying instrument (`V3_REAUDIT_PASS`, `ENGINE_STATE_ISOLATION_AUDITED`) remains valid and unaltered. This audit strictly targets the implementation of the root-population layer and source runner.

**Target Acquisition and Model Training remain strictly UNAUTHORIZED.**

## Audited Commits
- Implementation candidate: `0b847dbe48fadd6a913ab64297d6b780812a0a07`
- Evidence commit: `7988f60d44714e88f9827fec63d67cdaed533b3d`

## Required Audit Findings

### 1. History Loss (EXECUTION-CRITICAL FAIL)
The `InstrumentSession.acquire(...)` was passed an empty stack. While `cp_root_population.py` correctly reconstructs the root through the full move prefix and derives `history_identity`, `cp_source_feasibility.py` reconstructs the acquisition board using only `chess.Board(board_arrangement_fen)` and manual attribute assignment (turn, castling, etc.). The frozen child-position acquisition contract is not satisfied because the engine receives a board lacking the required replay history. This is a failure of the source runner/root handoff, not the CP instrument.

### 2. ExperimentSpec Provenance (EXECUTION-CRITICAL FAIL)
The runner creates `ExperimentSpec` using `semantic_signature_digest = "dummy"` and `suite_digest = "dummy"`, violating the frozen execution contract which requires `suite_digest` to bind to the sealed root manifest. Additionally, `fixture_digest = root_identity` was used as a shortcut rather than binding to the canonical root record.

### 3. Resume Fail-Open (EXECUTION-CRITICAL FAIL)
The `__init__` in `SourceFeasibilityRunner` catches all exceptions during artifact loading, silently ignoring corrupt or incompatible output. It also fails to mechanically verify required resume bindings (e.g., manifest digest, acquisition schema, software revision, Stockfish binary identity, etc.).

### 4. Coverage Script (UNSUPPORTED)
The published coverage numbers are unsupported under the committed evidence path. The runner stores `result = ExperimentResult.model_dump()` containing `data_payload`, but the coverage script expects `rec["result"]["observations"]` directly. Without a mechanically reproducible calculation path, the published metrics (e.g., 1,181,355 legal alternatives) are unverified.

### 5. Result Artifact Digest (FAIL)
The previously reported artifact SHA (`1a9f5d342c159ea43bc322045c73bb5bd28ab0cf840f3214b62d8544e3f191b7`) and count (33753) are invalid. Current mechanical verification of `artifacts/research/cp_source_feasibility_2026_07/raw/cp_source_root_results.jsonl.zst` yields SHA `a027a78f6156d928c6941c1bf3512e26011380915705e0ea00c641444148b236` and a record count of `0`. The artifact is preserved read-only.

### 6. Options Digest (FAIL)
The reported `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` is the digest of an empty byte string. No code canonicalized the complete observed UCI option surface to produce this digest.

### 7. GameURL Contract (FAIL)
The implementation uses `game.headers.get("Site", "")` instead of enforcing the exact frozen selector requirement of `GameURL`.

### 8. PGN Parse/Replay Errors (FAIL)
The `python-chess` parser can retain errors in `game.errors` without raising them. The current code lacks a fail-closed check for these errors, invalidating the claim of zero malformed replays.

### 9. Prior-Development Registry (FAIL)
The manifest builder incorrectly constructs `exact_s0_set` using only partial identity (fen, turn, castling, en passant) rather than the full `SufficientPosition` identity (which includes clocks and history). Consequently, the "PRIOR_DEVELOPMENT_EXACT_OVERLAP" implementation is semantically incorrect.

### 10. Manifest Contract (FAIL)
The manifest builder omits several required provenance fields per record (e.g., corpus identity, upstream URLs, checksums, duplicate resolution version, etc.).

### 11. Manifest Determinism Gate (FAIL)
There is no mechanical proof that two independent builds produced an identical canonical manifest digest before engine search. Required test cases (e.g., PGN-order permutation, duplicate winner stability) are absent.

### 12. Test Claim (FALSE)
The claim "Full Pytest Result: 11 passed" is false. A true full suite execution (`PYTHONPATH=src:. .venv/bin/pytest`) was not performed after the final implementation.

### 13. Pre-Commit Engine Execution (FAIL)
Existing raw source records predate the final implementation candidate and lack software revision binding. The artifact is contaminated.

## Required Repair Boundary
The entire root population and source feasibility runner layer must be repaired to conform to the frozen requirements before re-execution.

## Status Updates
- Resulting status: `SOURCE_ONLY_FEASIBILITY_COVERAGE_INVALID_REPAIR_REQUIRED`
- Next blocker: `SOURCE_ACQUISITION_IMPLEMENTATION_REPAIR_REQUIRED_V2`
