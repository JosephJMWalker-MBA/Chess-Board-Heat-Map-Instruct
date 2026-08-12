# Milestone 1 — Position + Engine Harness

## Objective

Build the smallest headless ChessHeat implementation that can answer one reproducible question:

> Given a legal chess position, what engine evidence is associated with each legal move under the same declared search budget?

This milestone does **not** calculate square heat.

## Required architecture

Follow `docs/ARCHITECTURE.md` and `docs/DECISIONS.md`.

The implementation must be Python-first and runnable without a web application.

Recommended logical separation:

- position/legal-chess layer,
- engine interface,
- Stockfish UCI adapter,
- structured analysis models,
- serialization,
- minimal CLI,
- tests/fixtures.

Exact filenames may differ if the dependency direction remains clear.

## Input

At minimum:

- a legal FEN,
- Stockfish executable location/configuration,
- an explicit search budget.

Reject invalid or illegal positions clearly rather than attempting to repair them silently.

## Root perspective

Every analysis has a declared `root_side`: the side to move in the input FEN.

Engine observations for the baseline position and every resulting legal move must preserve an explicit point of view. For Milestone 1, make it possible to inspect scores from the original `root_side` perspective so a side-to-move flip after a candidate move cannot silently invert meaning.

Do not collapse centipawn and mate scores into one invented scalar. Preserve their types until O-003 is resolved.

## Search budget

The harness must accept an explicit controlled search budget. Fixed-node analysis is preferred for the initial comparison harness because the intended comparison is search-effort controlled rather than wall-clock controlled.

Do not hide the budget in implementation defaults. Emit it in every analysis record.

O-002 remains open regarding the eventual production/research default budget.

## Required analysis record

The exact serialization model may evolve, but the emitted record must include enough information to reproduce the run.

### Metadata

- schema version,
- ChessHeat version/measurement version where available,
- input FEN,
- root side,
- engine name/version when obtainable,
- engine options that materially affect analysis,
- search budget type and value.

### Baseline observation

Preserve the engine's evaluation of the input position with explicit score type and perspective.

### Legal move observations

For every legal root move, preserve at least:

- UCI,
- SAN,
- origin square,
- destination square,
- capture status and captured square when applicable,
- promotion metadata when applicable,
- castling/en-passant metadata when applicable,
- resulting FEN,
- engine observation of the resulting position,
- score perspective,
- score type (`cp` / `mate` or equivalent structured representation),
- principal variation when available under the chosen analysis call.

Do **not** yet produce:

- leverage,
- hazard,
- pivotality,
- heat,
- color values,
- opening explanations.

## Engine adapter contract

ChessHeat code outside the Stockfish adapter should not need to parse UCI text directly.

The adapter should expose a narrow conceptual operation similar to:

`analyze(position, budget, perspective, optional_root_move) -> engine observation`

The exact Python API is not prescribed, but tests should be able to substitute a fake adapter so measurement and serialization behavior are not dependent on launching Stockfish.

## CLI contract

Provide a minimal headless path to exercise the harness, conceptually:

`chessheat analyze --fen "..." --stockfish-path /path/to/stockfish --nodes N`

The exact command syntax may differ, but it must be possible to emit structured JSON to stdout or a requested file.

Human-oriented pretty output is optional. Structured output is required.

## Tests

At minimum protect:

1. FEN validation.
2. Side-to-move preservation.
3. Legal move enumeration.
4. Starting position yields 20 legal moves.
5. SAN and UCI are preserved distinctly.
6. Resulting FEN corresponds to each candidate move.
7. Score perspective does not invert silently after making a move.
8. Centipawn and mate observations remain type-distinct.
9. Special-move metadata for castling, promotion, capture, and en passant.
10. Engine search budget is recorded in serialized results.
11. Fake engine adapter can drive deterministic unit tests.
12. JSON output validates against the project's analysis model/schema.

A small real-Stockfish integration test may be included but should be separable/skippable when Stockfish is unavailable.

## Fixture discipline

Create a small fixture set, but do not tune ChessHeat concepts yet.

Useful Milestone 1 fixtures include:

- starting position,
- a simple tactical position,
- a forced-mate position,
- a castling position,
- a promotion position,
- an en-passant position.

The purpose is engine/data correctness, not proving the heat hypothesis.

## Exit criteria

Milestone 1 is complete when:

1. A legal FEN can be analyzed headlessly.
2. Every legal root move receives structured engine evidence under the same declared budget.
3. The output preserves provenance and explicit score perspective.
4. Unit tests pass without requiring Stockfish through a fake adapter.
5. A real Stockfish run produces a versioned JSON analysis record.
6. No square-level heat or composite scoring has been introduced.

At that point, stop and review the evidence model before beginning Milestone 2 square attribution.
