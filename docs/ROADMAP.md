# ChessHeat Roadmap

## Guiding rule

Build the smallest system that can test the central claim:

> **A chess position contains a useful square-level structure of leverage and hazard that can be measured from legal state changes and engine evidence.**

Do not begin with opening lessons, generative explanations, accounts, cloud infrastructure, or a polished product shell.

## Milestone 0 — Concept lock

Status: **current**

Goals:

- define control, leverage, hazard, pivotality, and heat delta,
- separate square importance from weighted attack maps,
- document what Stockfish evidence can and cannot establish,
- preserve falsification criteria,
- establish agent instructions before implementation.

Exit condition:

The repository communicates the concept clearly enough that a coding agent cannot reasonably interpret ChessHeat as a simple attack-density visualization.

## Milestone 1 — Position and engine harness

Build a deterministic analysis core with no heatmap styling requirement.

Requirements:

- accept legal FEN,
- represent side to move and complete legal state,
- generate legal moves,
- integrate Stockfish behind a narrow engine adapter,
- obtain normalized evaluations,
- evaluate all legal root moves under a controlled search budget,
- persist or expose raw analysis records,
- test score perspective and mate normalization explicitly.

Exit condition:

Given a fixture FEN, the system deterministically returns a structured list of legal moves and comparable engine consequence evidence.

## Milestone 2 — Direct square attribution

Create the first square-level measurement surface.

Requirements:

- attribute each analyzed move to origin and destination,
- correctly represent captures, promotions, castling, and en passant,
- aggregate raw consequence statistics per square,
- expose the underlying moves for inspection,
- keep control-map data separate from consequence data.

Exit condition:

For every rendered square, a developer can answer exactly why it received its current evidence values.

## Milestone 3 — First heatmap

Render the measurement surface on a board.

Requirements:

- standard legal chessboard,
- heat overlay that does not obscure pieces,
- side-to-move perspective,
- selectable measurement layer,
- square inspector with raw evidence,
- no unexplained single-number score,
- clear legend and uncertainty/state labels.

Possible initial layers:

- direct consequence magnitude,
- downside/hazard evidence,
- positive opportunity evidence,
- control geometry.

Exit condition:

The board is useful for inspecting measurements even if it is not visually polished.

## Milestone 4 — Heat delta

Make consecutive board states comparable.

Requirements:

- analyze `P[t]`,
- apply a legal move,
- analyze `P[t+1]`,
- calculate square-level deltas,
- visualize which squares gained or lost consequence significance,
- preserve before/after evidence.

Exit condition:

After a move, ChessHeat can answer:

> **What changed on the board, and where?**

This milestone is foundational for teaching.

## Milestone 5 — Validation fixtures

Before adding richer attribution, test whether the primitive model is useful.

Fixture categories should include:

- simple forks,
- pins,
- overloaded defenders,
- discovered attacks,
- open-file transformations,
- central pawn breaks,
- outpost creation/removal,
- king-safety changes,
- quiet positional moves,
- opening positions with well-understood strategic goals.

For each fixture, record an expected qualitative hypothesis before viewing the resulting heatmap.

Questions:

- Does the map identify the expected pivotal region?
- Is it stable across reasonable engine budgets?
- Does it add information beyond attack counts?
- Does it mislabel legal destinations as strategic importance?

Exit condition:

Evidence supports continuing beyond direct attribution, or the model is revised.

## Milestone 6 — Principal-variation recurrence

Add evidence about squares that recur across strong futures.

Requirements:

- capture multiple strong candidate lines,
- measure square recurrence across lines,
- distinguish forced tactical repetition from broad recurrence,
- expose recurrence as its own layer before blending it with anything else.

Exit condition:

Recurrence provides demonstrable explanatory value on validation fixtures.

## Milestone 7 — Indirect consequence research

Research how to attribute consequences that occur away from move origin/destination.

Candidate phenomena:

- opened/closed files,
- diagonals,
- discovered attacks,
- removed defenders,
- king-zone changes,
- pawn-break enablement,
- outpost access,
- piece mobility transformations.

No implementation should claim solved causal attribution without validation.

Exit condition:

At least one indirect-attribution method beats the direct-only baseline on predeclared fixtures.

## Milestone 8 — Pivotality model

Only after individual signals are validated should ChessHeat consider a composite pivotality measure.

Requirements:

- versioned formula,
- documented inputs,
- ablation tests,
- raw signals remain accessible,
- comparison against simpler baselines.

Exit condition:

The composite adds measurable value over its strongest individual component.

## Milestone 9 — Opening teacher prototype

Use heat delta and validated square signals to teach one narrowly selected opening family.

Requirements:

- move-by-move board-state comparison,
- opening objective annotations written from curated chess knowledge,
- engine evidence kept separate from instructional text,
- theory deviation analysis based on preserved strategic structure, not database mismatch alone,
- guided/reduced/prediction/blind modes considered incrementally.

Exit condition:

A learner can explain the opening's strategic logic without merely replaying memorized moves.

## Milestone 10 — Explanatory AI

Only after the measurements are trustworthy, optionally add a generative explanation layer.

Rules:

- the model receives structured evidence,
- it may explain but not fabricate measurements,
- claims should be traceable to engine or curated instructional evidence,
- deterministic templates should remain available as a baseline.

## Deferred deliberately

Do not prioritize yet:

- user accounts,
- ratings or social features,
- multiplayer,
- freeform/nonstandard chess pieces,
- arbitrary board-rule variants,
- large opening databases,
- mobile apps,
- cloud scaling,
- gamification,
- LLM-first tactical analysis.

The project earns complexity only after the central measurement works.
