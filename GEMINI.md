# Gemini Development Instructions — ChessHeat

## Read first

Before changing code or architecture, read in full:

1. `README.md`
2. `docs/CONCEPT.md`
3. `docs/MEASUREMENT_MODEL.md`
4. `docs/ROADMAP.md`
5. `docs/DECISIONS.md`

If implementation and documentation disagree about the product concept, stop and surface the conflict rather than silently redefining the concept.

## Product invariant

ChessHeat is a **square-level consequence and leverage visualization system**.

It is not a weighted attack map.

Never use any of these as a substitute for square importance:

- number of attackers,
- sum of attacking piece values,
- mobility count,
- legal destination count,
- Stockfish evaluation of a destination move alone.

Those may be evidence layers, but none independently defines leverage or pivotality.

## Critical distinction

**Control != importance.**

A square can be evenly controlled yet pivotal. A heavily controlled square can be strategically irrelevant. Preserve this distinction in data models, naming, tests, and UI.

## Current implementation authority

Follow the active milestone in `docs/ROADMAP.md`.

Do not jump ahead because a later feature is easy to scaffold.

In particular, do not add:

- generative chess analysis,
- opening lessons,
- user accounts,
- nonstandard chess variants,
- a composite pivotality score,
- or polished product infrastructure

until the roadmap reaches those milestones or the maintainer explicitly changes scope.

## Measurement rules

1. Preserve raw engine evidence before aggregation.
2. Preserve move-level evidence even when rendering square-level results.
3. Keep engine evaluation perspective explicit.
4. Keep mate-score normalization explicit and versioned.
5. Record engine/search settings required to reproduce an analysis.
6. Keep control data separate from consequence data.
7. Keep opportunity and downside distinguishable rather than immediately averaging them together.
8. Mark unsupported attribution as unsupported instead of inventing causal explanations.
9. Prefer inspectable intermediate representations over clever opaque scoring.
10. Do not introduce a composite heat formula without an explicit documented decision.

## Engine role

Stockfish is a measurement source.

Treat engine output as evidence about legal continuations and position evaluation. ChessHeat is responsible for transforming that evidence into a spatial model.

Do not ask a generative model to estimate move quality, square heat, pivotality, or tactical correctness when deterministic chess/engine evidence is available.

## AI role

Generative AI is deferred from the core measurement pipeline.

When eventually introduced, it may:

- explain structured evidence,
- summarize changes,
- adapt instructional language.

It may not:

- fabricate measurements,
- replace Stockfish evaluations,
- invent causal attribution and present it as measured fact,
- or silently alter the underlying heat model.

## Testing philosophy

Tests should protect meaning, not only syntax.

Important categories include:

- legal move correctness,
- evaluation perspective,
- mate-score handling,
- special moves,
- stable square attribution,
- repeatability under fixed analysis settings,
- separation of control and consequence,
- known tactical and positional fixtures.

For research fixtures, write the expected qualitative hypothesis before tuning the algorithm against the result where practical.

## Data model preference

Prefer structures that retain provenance.

A square-level result should be able to point back to the move records, engine records, and transformations that produced it.

Avoid storing only a final color or scalar.

## UI rules

The board is the primary object.

A user should be able to inspect a square and understand:

- what layer is being viewed,
- what evidence contributes to it,
- which moves are implicated,
- which side the value is relative to,
- and whether the signal is measured, derived, provisional, or unsupported.

Visual intensity must never imply more certainty than the underlying data supports.

## Development discipline

- Make small, reviewable changes.
- Do not redesign the project while implementing a narrow milestone.
- Prefer pure functions around measurement transforms.
- Keep engine integration behind an adapter boundary.
- Avoid coupling UI color logic to measurement logic.
- Version formulas or normalization rules when they change.
- Update `docs/DECISIONS.md` when a consequential architectural or measurement choice is accepted.
- If a shortcut risks changing the meaning of "heat," do not take it silently.

## Current goal

The first meaningful implementation target is:

> Given a legal FEN, return an inspectable set of legal-move engine consequences under a controlled analysis budget, with enough metadata to reproduce and compare the results.

No heatmap is required until that evidence layer is trustworthy.
