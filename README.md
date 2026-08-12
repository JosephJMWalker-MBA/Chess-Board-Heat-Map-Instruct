# Chess Board Heat Map — Instruct

ChessHeat is an experimental chess visualization and teaching project built around one question:

> **Which squares matter most to what happens next?**

The project aims to render a chess position as a spatial map of **control, leverage, hazard, and pivotality** rather than simply presenting an engine's best move.

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

A central future primitive is therefore **heat delta between consecutive positions**:

`Heat(P[t+1]) - Heat(P[t])`

## Initial vocabulary

- **Control** — who attacks or defends a square.
- **Leverage** — how much meaningful changes involving a square can alter the position.
- **Hazard** — how costly interaction with a square can be for a given side.
- **Pivotality** — how central a square is across plausible consequential futures.
- **Heat delta** — how those properties change from one board state to the next.

These are working research definitions, not finalized formulas.

## Engine role

Stockfish is intended to serve as a **measurement instrument**, not as the product itself. Engine search and evaluation can provide evidence about candidate continuations and positional sensitivity; ChessHeat's contribution is turning that evidence into a human-readable spatial model.

Generative AI may eventually explain measured changes, but it must not invent the underlying chess evidence.

## Current phase

This repository begins with conceptual and measurement design before implementation. The first milestone is to produce a deterministic, inspectable prototype that can answer:

> **Given a legal chess position, can we produce a useful square-level leverage map whose meaning is defensible and testable?**

See:

- [`docs/CONCEPT.md`](docs/CONCEPT.md)
- [`docs/MEASUREMENT_MODEL.md`](docs/MEASUREMENT_MODEL.md)
- [`docs/ROADMAP.md`](docs/ROADMAP.md)
- [`GEMINI.md`](GEMINI.md)
