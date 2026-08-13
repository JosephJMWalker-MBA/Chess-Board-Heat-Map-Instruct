# Chess Board Heat Map — Instruct

ChessHeat is an experimental chess visualization and teaching project built around one question:

> **Which squares matter most to what happens next?**

The project aims to render a chess position as a spatial map of **control, leverage, hazard, and pivotality** rather than simply presenting an engine's best move.

> **The mathematics needs to earn the color.**

## Core idea

Traditional engine interfaces answer questions such as:

- What is the evaluation?
- What is the best move?
- How large was the centipawn loss?

ChessHeat asks a different class of questions:

- Which squares are structurally important in this position?
- Where can a small board-state change create a large positional consequence?
- Which squares are dangerous to interact with carelessly — the "lava" squares?
- Which squares recur across plausible strong continuations?
- What changed in the board's leverage structure after a move?

The intended output is not merely a weighted attack map. **Control and importance are separate concepts.** A square can be evenly contested yet highly pivotal, or heavily controlled yet strategically unimportant.

## Long-term teaching goal

ChessHeat should eventually teach openings by showing how the board's consequence structure changes move by move.

Instead of teaching only:

> `1. e4 e5 2. Nf3 Nc6 3. Bb5`

it should help a learner see:

- which squares became more or less important,
- what strategic objective a move advanced,
- what changed when theory was followed or departed from,
- and whether the learner can reconstruct the logic after forgetting the memorized sequence.

A central primitive is therefore comparison between consecutive positions:

`Heat(P[t+1]) - Heat(P[t])`

The exact meaning of `Heat` remains a research question rather than a finalized scalar formula.

## Working vocabulary

- **Control** — who attacks or defends a square.
- **Leverage** — how much meaningful changes involving a square can alter the position.
- **Hazard** — how costly interaction with a square can be for a given side.
- **Pivotality** — how central a square or region is across plausible consequential futures.
- **Heat delta** — how measured spatial properties change from one board state to the next.
- **Amplitude** — how much decision leverage exists in the position as a whole.
- **Shape** — where spatial evidence is located, separately from how large the position-level leverage is.

These remain working research definitions.

## Engine role

Stockfish is a **measurement instrument**, not the product itself. Engine search and evaluation provide reproducible evidence about candidate continuations and positional sensitivity; ChessHeat's contribution is turning that evidence into an inspectable spatial model.

Generative AI may eventually explain measured changes, but it must not invent the underlying chess evidence.

Mate-sensitive outcomes remain typed rather than being converted into fake centipawn values.

## Reference architecture

The reference measurement pipeline is deliberately engine-first and headless:

`legal chess position -> Python analysis core -> Stockfish adapter -> typed measurement records -> spatial evidence layers -> web visualization`

The Python core owns chess measurement semantics. The web interface consumes evidence rather than recreating engine or scoring logic in the browser.

## Current research state

The first research sprint progressed through Milestones 1–8 and produced a substantial implementation and experimental record.

Established or strongly supported so far:

- root-move regret is a useful decision-sensitivity quantity but not a causal delta;
- direct square attribution is useful for tactical endpoints but incomplete for indirect structure;
- principal-variation recurrence adds a distinct future-path signal but can remain diffuse;
- structural geometry delta can expose rays, pathways, attacks, defenses, blockers, and mobility changes away from move endpoints;
- event bundles are more honest than isolated causal claims when structural events are confounded;
- **where leverage is** and **how much leverage exists** are distinct questions;
- severity and decision leverage are not the same thing;
- no fixed Direct/Recurrence/Bundle fusion has yet earned the status of a universal pivotality model.

The hostile W-suite is preserved as development / hostile-validation evidence, **not** as pristine one-shot final validation. Several fixture and execution-protocol failures were retained rather than rewritten.

### Immediate next step — M8.6.4

Before any new threshold tuning, perform a semantic-integrity audit of Recurrence and `ShapeSelectivity-v1`.

The audit must resolve:

- exact per-channel observed / rejected / selected states;
- the invariant `distinct_line_count <= admitted_candidate_count`;
- historical reports of recurrence counts larger than the admitted candidate set;
- the distinction between legal root moves, admitted recurrence candidates, PV length, distinct candidate lines, and total visits;
- the fact that the current selectivity helper returns one prioritized channel source and one prioritized rejection reason rather than a complete independent multi-channel state record.

Do not retune `ShapeSelectivity-v1` during this audit.

## Future research

A separate **Temporal Ledger** research track is proposed to study how a position was formed through temporal investment, constraint, conversion, and persistence.

History must not contaminate objective current-state semantics. Two different histories that arrive at the same complete legal state should produce the same current-state ChessHeat evidence while being allowed to produce different historical ledgers.

Opening instruction remains a long-term goal, but it is downstream of measurement integrity.

## Research record

Start with:

- [`docs/RESEARCH_REPORT_M1_M8.md`](docs/RESEARCH_REPORT_M1_M8.md) — mathematical evolution, experimental findings, failures, open questions, and future research
- [`docs/CONCEPT.md`](docs/CONCEPT.md)
- [`docs/MEASUREMENT_MODEL.md`](docs/MEASUREMENT_MODEL.md)
- [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md)
- [`docs/ROADMAP.md`](docs/ROADMAP.md)
- [`docs/DECISIONS.md`](docs/DECISIONS.md)
- [`docs/MILESTONE_1.md`](docs/MILESTONE_1.md)
- [`GEMINI.md`](GEMINI.md)

The raw development and validation artifacts are intentionally preserved under `tests/fixtures/`, including experiments that later proved invalid, contaminated, or weaker than originally described.
