# ChessHeat Architecture

## Purpose

ChessHeat is being built as a measurement system first and a visualization product second.

The architecture therefore separates chess truth/evidence from presentation:

`Position -> Python analysis core -> Stockfish -> versioned measurement records -> visualization`

The web layer is not allowed to redefine measurement semantics.

## 1. Python analysis core

The Python package is the reference implementation for chess analysis and ChessHeat measurements.

Responsibilities:

- validate and load legal chess positions,
- preserve complete FEN state,
- generate legal moves,
- communicate with Stockfish through a narrow adapter,
- preserve raw engine output needed for reproducibility,
- normalize engine evidence only through documented/versioned rules,
- produce move-level consequence records,
- later produce square-level attribution, leverage, hazard, and heat-delta records,
- serialize results into a stable schema,
- expose deterministic tests and fixture analysis.

The core must remain usable from tests and a command-line entry point without a browser, server, database, or generative model.

## 2. Stockfish adapter

Stockfish is an external evidence source behind an interface owned by ChessHeat.

The adapter should accept explicit analysis settings and return structured engine observations. ChessHeat code outside the adapter should not depend directly on UCI parsing details.

Initial implementation target:

- native Stockfish process,
- UCI communication,
- explicit engine identity/version when available,
- explicit search budget,
- explicit score perspective,
- principal variation evidence where requested,
- clean startup/shutdown behavior,
- testability through an adapter seam.

Future WASM or remote-engine implementations may satisfy the same logical interface, but they must not silently alter measurement meaning.

## 3. Measurement records

The boundary between analysis and presentation is a versioned structured record.

The exact schema will evolve, but the initial shape should preserve evidence roughly at these levels:

### Analysis metadata

- schema version,
- input FEN,
- side to move,
- engine identity/version,
- search settings,
- analysis timestamp if persistence requires it,
- normalization/version identifiers where applicable.

### Position evidence

- baseline engine observation,
- legal move count,
- optional control geometry as a separate evidence layer.

### Move evidence

For every analyzed legal root move:

- UCI move,
- SAN move,
- origin square,
- destination square,
- special-move metadata where relevant,
- raw resulting-position engine observation,
- principal variation evidence if collected,
- normalized consequence values only when the normalization rule is explicitly defined.

### Future square evidence

Square records may later include distinct fields for:

- control,
- direct consequence attribution,
- opportunity/upside,
- hazard/downside,
- recurrence across candidate lines,
- heat delta,
- supported/unsupported attribution status.

Do not collapse these into one scalar merely because the frontend wants one color.

## 4. Web visualization layer

The web application is a consumer of measurement records.

Responsibilities may eventually include:

- rendering the chessboard,
- rendering control/leverage/hazard layers,
- showing before/after heat delta,
- exploring move evidence,
- opening-teaching interactions,
- selecting positions and navigating games.

It must not independently calculate legal chess truth or redefine ChessHeat measurements.

If UI logic needs new measurement information, extend the analysis schema rather than recreating the calculation in JavaScript.

## 5. Dependency direction

Desired dependency direction:

`UI -> measurement schema <- analysis core -> engine adapter -> Stockfish`

The schema is the contract between the analysis instrument and its consumers.

Avoid architecture in which:

- React components call Stockfish directly,
- color functions contain hidden chess heuristics,
- frontend code computes alternate score normalization,
- generative AI fills missing engine evidence,
- the database becomes the only representation of analysis semantics.

## 6. Reproducibility

An analysis result should eventually be reproducible from:

- the input position,
- ChessHeat measurement version,
- Stockfish version,
- engine settings/search budget,
- normalization rules,
- attribution rules.

Visual appearance is not part of measurement reproducibility.

## 7. Current non-goals

Do not build these during the first engine-harness milestone:

- polished chessboard UI,
- accounts/authentication,
- cloud persistence,
- opening database integration,
- generative explanations,
- composite pivotality score,
- browser-side Stockfish,
- multiplayer/gameplay infrastructure.

## 8. Design test

A useful architecture check is:

> Could ChessHeat analyze a directory of FEN fixtures, emit JSON records, and be scientifically inspected without starting the web app?

For the reference implementation, the answer should always be yes.
