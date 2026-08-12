# ChessHeat Measurement Model

## Status

This document defines the first measurement hypotheses for ChessHeat. It is intentionally provisional.

The goal is not to declare a final heat formula. The goal is to make each candidate signal explicit, inspectable, and testable.

## Design principle

A square score should be derived from evidence about how the position changes, not from color assignment or attack counts alone.

ChessHeat should preserve the raw measurements used to construct any composite score.

## Position baseline

For a legal position `P`, obtain a stable engine evaluation from the perspective of the side being analyzed.

Represent the baseline as:

`E(P)`

The implementation must normalize mate scores and centipawn scores into a documented representation before comparing values.

The exact normalization scheme is not yet fixed.

## Candidate signal A — direct move consequence

For each legal move `m` from position `P`:

1. apply `m` to create `P_m`,
2. evaluate `P_m`,
3. calculate the change relative to the baseline,
4. preserve the engine search metadata used to obtain the value.

Conceptually:

`Delta(m) = E(P_m) - E(P)`

This signal measures move consequence, not square importance by itself.

### Initial square attribution

For a first prototype, attribute evidence to:

- the move's origin square,
- the move's destination square,
- the captured square when distinct,
- castling rook origin/destination where applicable,
- en-passant captured square where applicable.

Do not assume equal attribution is correct. Preserve the move-level record so attribution rules can later change.

## Candidate signal B — consequence magnitude by square

For square `s`, aggregate the magnitude of consequential legal moves that directly involve `s`.

A simple research statistic might include:

- maximum absolute evaluation change,
- mean absolute evaluation change,
- median absolute evaluation change,
- number of consequential moves involving the square,
- positive and negative consequences separated by side.

Do not collapse these into one score until the distributions have been inspected.

## Candidate signal C — principal-variation recurrence

A square may be pivotal if it repeatedly appears across strong continuations.

For multiple engine candidate lines, record:

- squares occupied by moves in each principal variation,
- captures on each square,
- repeated contested squares,
- recurrence depth,
- recurrence across independent candidate moves.

A square that appears in many strong lines may carry strategic importance even when the immediate move consequence is modest.

This signal must distinguish repetition caused by forced tactics from broad strategic centrality.

## Candidate signal D — local state transition

Compare structural properties of each square before and after a legal move.

Possible raw properties include:

- attacking side counts,
- defending side counts,
- attacking piece identities,
- defending piece identities,
- occupancy,
- legal accessibility,
- x-ray lines opened or closed,
- pinned or overloaded defenders associated with the square,
- king-zone membership,
- passed-pawn or promotion relevance.

These are explanatory signals. They should not automatically become weights in the heat score.

## Candidate signal E — indirect impact

A move can create its primary consequence away from its origin and destination.

Example categories:

- opening a file,
- opening or closing a diagonal,
- removing a defender,
- creating a discovered attack,
- changing king safety,
- enabling a pawn break,
- changing access to an outpost.

This is the hardest attribution problem in the project and should not be faked in v1.

The first prototype may explicitly report:

`indirect attribution: unsupported`

rather than pretending destination-square attribution explains the whole move.

## Working concepts

### Control

Control is a geometric description of attacks and defenses.

Possible representation:

`Control(s) = {white_attackers, white_defenders, black_attackers, black_defenders}`

Do not reduce this immediately to a weighted scalar.

### Leverage

Working hypothesis:

> A square has high leverage when meaningful legal changes involving or depending on it are associated with large downstream changes in position value or structure.

Initial v1 approximation may use direct legal-move consequence plus recurrence evidence.

### Hazard

Working hypothesis:

> A square has high hazard for a side when plausible interactions with it have strongly asymmetric downside for that side.

Hazard must be side-specific and should preserve best-case and worst-case outcomes separately.

Potential descriptive statistics:

- worst legal consequence involving the square,
- proportion of interactions that fall below a loss threshold,
- tactical forcing-response depth,
- volatility across candidate continuations.

### Pivotality

Working hypothesis:

> A square is pivotal when it is repeatedly implicated in high-consequence changes across plausible strong futures.

Potential evidence:

- leverage magnitude,
- recurrence across principal variations,
- persistence across search depths,
- structural centrality,
- sensitivity across neighboring board states.

No composite formula is authorized yet.

## Heat delta

For consecutive legal positions `P_a` and `P_b`, compute the same raw square measurements for each and compare them.

The system should preserve:

- previous square evidence,
- current square evidence,
- signed change,
- absolute change,
- explanation metadata.

Heat delta is likely to be more useful pedagogically than a static heat value because it answers:

> **What did that move change?**

## V1 research algorithm

The first implementation should remain deliberately narrow:

1. Parse and validate a legal FEN.
2. Generate all legal moves.
3. Obtain a baseline engine evaluation.
4. Evaluate every legal move under a fixed engine budget.
5. Record origin, destination, captures, promotion, castling, and evaluation change.
6. Aggregate move-consequence evidence by directly involved square.
7. Render an inspectable board overlay.
8. Allow the user to inspect the raw evidence behind any square.
9. Compare the map before and after a move.

This is a measurement prototype, not yet the final ChessHeat model.

## Required experiment controls

Engine-derived comparisons are only meaningful if search settings are controlled.

Each measurement record should preserve at least:

- engine version,
- analysis mode,
- depth or node/time budget,
- MultiPV setting if used,
- side to move,
- FEN,
- evaluation perspective,
- timestamp or run identifier,
- score normalization version.

Deterministic or near-deterministic repeatability is preferred for experiments.

## Falsification questions

The project should actively test whether its visualization corresponds to useful chess structure.

Potential falsifiers include:

- high-heat squares consistently failing to match known tactical or strategic pivots,
- trivial attack-count maps performing just as well as the proposed model,
- severe instability under small changes in engine depth,
- maps that merely visualize legal move destinations,
- players learning to chase heat colors rather than understanding positions,
- opening instruction that rewards database conformity without transferable understanding.

If a simpler model explains the same phenomena equally well, prefer the simpler model.
