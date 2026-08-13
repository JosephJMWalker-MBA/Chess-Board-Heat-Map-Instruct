# ChessHeat Architecture

## Purpose

ChessHeat is a measurement system first and a visualization product second.

The architecture therefore separates chess truth/evidence from presentation:

`Position -> Python analysis core -> Stockfish -> typed measurement records -> spatial evidence layers -> visualization`

The web layer is not allowed to redefine measurement semantics.

> **The mathematics needs to earn the color.**

## 1. Python analysis core

The Python package is the reference implementation for chess analysis and ChessHeat measurements.

Current responsibilities include:

- validate and load legal chess positions;
- preserve complete FEN state;
- generate legal root moves;
- communicate with Stockfish through a narrow adapter;
- preserve raw engine evidence required for reproducibility;
- maintain explicit comparison perspective;
- preserve typed CP / mate outcomes;
- compute root-choice regret where semantics permit;
- produce direct square attribution;
- preserve principal-variation recurrence and candidate provenance;
- extract deterministic structural geometry;
- compute geometry deltas;
- associate geometry events / bundles with root-move outcome distributions;
- expose experimental fusion and selectivity layers without hiding raw inputs;
- support paired-position / delta analysis;
- emit inspectable JSON research artifacts;
- remain runnable from tests and command line without a browser or generative model.

The core must remain the authority for measurement semantics.

## 2. Stockfish adapter

Stockfish is an external evidence source behind an interface owned by ChessHeat.

The adapter accepts explicit analysis settings and returns structured engine observations. ChessHeat code outside the adapter should not depend directly on UCI details.

Reference properties include:

- native Stockfish process;
- explicit executable / engine identity when available;
- explicit search budget;
- explicit score perspective;
- principal variation evidence;
- clean startup / shutdown behavior;
- adapter seam for tests.

Future WASM or remote-engine implementations may satisfy the same logical interface, but they must not silently alter measurement meaning.

## 3. Measurement record layers

The system now contains multiple evidence layers. They must remain inspectable rather than being collapsed prematurely.

### Analysis metadata

Preserve:

- schema version where applicable;
- input FEN;
- side to move;
- comparison perspective;
- engine identity / version;
- search settings;
- candidate policy;
- legal root count;
- admitted recurrence candidate count;
- implementation / experiment identity where sealed.

### Move evidence

For every analyzed legal root move, preserve:

- UCI;
- SAN;
- origin / destination;
- special-move metadata;
- resulting FEN;
- typed score;
- root-choice regret where defined;
- parsed principal variation;
- directly implicated squares / roles.

### Recurrence evidence

Preserve:

- total legal moves;
- admitted candidate count;
- admitted root moves;
- candidate score / regret provenance;
- distinct line count;
- line fraction;
- visit count;
- earliest ply;
- role-specific recurrence.

### Structural geometry evidence

Preserve deterministic board relationships such as:

- attacks;
- defenses;
- rays;
- paths;
- blockers;
- mobility;
- geometry deltas across root moves.

### Event-bundle evidence

When structural events share the same producing-move set, preserve them together with:

- constituent events;
- producing / non-producing moves;
- implicated region;
- outcome / regret distributions;
- association statistics;
- confounding state.

### Shape / amplitude separation

Do not treat spatial ranking as absolute leverage magnitude.

Keep conceptually distinct:

`S(s | P)` — spatial shape / localization

`A(P)` — position-level decision-leverage amplitude

Typed amplitude must preserve CP / mate semantics and zero-optionality state.

## 4. Selectivity layer

`ShapeSelectivity-v1` is an experimental attention policy over raw spatial evidence.

Its thresholds are development-tuned and must remain versioned.

Rejected evidence is not deleted.

The current helper is an ordered first-pass selector, not a full independent multi-channel state recorder. M8.6.4 must reconcile that implementation detail with forensic reporting before further tuning.

## 5. Visualization layer

The viewer is a consumer of measurement records.

Responsibilities may include:

- board rendering;
- evidence-layer selection;
- spatial overlays;
- before / after delta inspection;
- square / region provenance inspection;
- future instructional interactions.

It must not independently calculate legal chess truth or redefine ChessHeat measurements.

If UI logic needs new measurement information, extend the analysis schema rather than recreating the calculation in JavaScript.

## 6. Dependency direction

Desired dependency direction:

`UI -> measurement records <- analysis core -> engine adapter -> Stockfish`

Within the analysis core, keep evidence transforms layered:

`root engine evidence`

`-> direct attribution / recurrence / geometry`

`-> event association / bundles`

`-> experimental selectivity / fusion`

`-> visualization consumers`

Do not allow downstream rendering choices to mutate upstream evidence meaning.

## 7. Reproducibility

An analysis should be reproducible from enough information to identify:

- input legal state;
- ChessHeat implementation version;
- Stockfish executable / version;
- engine settings / search budget;
- comparison perspective;
- candidate policy;
- attribution / recurrence / geometry rules;
- selectivity / fusion version when used.

Visual appearance is not part of measurement reproducibility.

## 8. Experimental integrity

Research fixtures are part of the architecture because the model is still provisional.

Required principles:

- validate board legality, not only FEN parseability;
- preserve invalid fixtures rather than silently repairing them;
- preserve failed holdouts / seals with corrected status;
- distinguish fixture failure, protocol failure, representation failure, selectivity failure, and projection failure;
- never convert hostile-validation evidence into a marketing accuracy claim;
- do not retune a frozen rule on the same hostile evidence used to expose its blind spots.

## 9. Temporal Ledger boundary

A future historical layer may consume sequences of legal positions and existing deterministic deltas.

It must remain separate from current-state semantics until independently validated.

For true transpositions reaching the same complete legal state:

`CurrentState(H_A, P) = CurrentState(H_B, P)`

while:

`TemporalLedger(H_A) != TemporalLedger(H_B)`

may be legitimate.

History must not become an excuse to inject narrative causality into state-based evidence.

## 10. Current non-goals

Do not prioritize yet:

- production accounts / auth;
- cloud persistence;
- large opening databases;
- generative chess truth;
- a final composite pivotality score;
- browser-side Stockfish as the reference engine;
- multiplayer infrastructure;
- nonstandard rule variants;
- polished product scaling.

## 11. Design test

A useful architecture check remains:

> Could ChessHeat analyze a directory of legal fixtures, emit inspectable evidence records, reproduce the research transforms, and be scientifically audited without starting the web app?

For the reference implementation, the answer should remain yes.
