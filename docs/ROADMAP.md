# ChessHeat Roadmap

## Guiding rule

Build the smallest system that can test the central claim:

> **A chess position contains a useful spatial structure of leverage and hazard that can be measured from legal state changes, engine evidence, and structural geometry.**

Do not let rendering outrun measurement.

> **The mathematics needs to earn the color.**

## Milestone 0 — Concept lock

**Status: Complete**

Established:

- control and importance are separate concepts;
- Stockfish is evidence, not the product model;
- raw evidence must remain inspectable;
- the Python analysis core owns measurement semantics;
- UI and generative explanation remain downstream.

## Milestone 1 — Position and engine harness

**Status: Complete**

Implemented:

- legal FEN input;
- legal root-move enumeration;
- Stockfish adapter;
- fixed-budget analysis;
- typed CP / mate score evidence;
- fixed comparison perspective;
- engine lifecycle cleanup;
- structured move and PV provenance.

Key mathematical correction:

`R(m) = E* - E(m)` is interpreted as root-choice regret / opportunity cost, not as a causal move delta.

## Milestone 2 — Direct square attribution

**Status: Complete as baseline evidence layer**

Implemented origin, destination, capture, en-passant, castling, and promotion-related square implication with inspectable move provenance.

Finding:

Direct attribution is useful for tactical endpoints but incomplete for indirect structure.

## Milestone 3 — Diagnostic viewer

**Status: Complete as research viewer**

A simple viewer exposes board evidence and underlying records without making a polished UI a prerequisite for measurement research.

## Milestone 4 — Paired-position / heat-delta semantics

**Status: Complete as research primitive**

Implemented before/after comparison under a fixed perspective with explicit appeared / disappeared / persisted / absent states.

Finding:

Missing evidence must remain distinct from numeric zero.

## Milestone 5 — Validation / falsification fixtures

**Status: Complete as development evidence; final validation still open**

Direct-attribution fixtures established characteristic strengths and weaknesses across controlled node budgets.

Important corrections:

- the original overloaded-defender F4 fixture was invalid for its stated chess hypothesis;
- budget stability is robustness, not proof of intrinsic spatial truth;
- failed and invalid fixtures are preserved rather than rewritten.

## Milestone 6 — Principal-variation recurrence

**Status: Implemented; semantic audit pending**

Implemented candidate-policy provenance and square recurrence across admitted PVs.

Preserved metrics include:

- admitted candidate count;
- admitted root moves;
- line fraction;
- distinct line count;
- visit count;
- earliest ply;
- role-specific recurrence.

Finding:

Recurrence adds real future-path information but frequency alone does not establish leverage.

Required invariant:

`distinct_line_count <= admitted_candidate_count`

## Milestone 7 — Structural geometry and indirect evidence

**Status: Complete as descriptive evidence layer**

Implemented deterministic geometry for attacks, defenses, rays, paths, blockers, and mobility plus geometry delta across root moves.

M7.5–M7.7 added outcome association and event bundles.

Finding:

Geometry can partition outcomes without proving isolated causality. Perfectly co-occurring events must remain bundled when the data cannot distinguish their effects.

## Milestone 8 — Pivotality research

**Status: Frozen** (as of M8.6.8 Candidate-Set Sensitivity Characterization)

Completed research work includes:

- Direct / Recurrence / Bundle ablations;
- attack-density and destination-regret baselines;
- pairwise and three-way rank-normalized fusion;
- amplitude / shape decomposition;
- typed CP / mate amplitude architecture;
- zero-optionality semantics;
- spatial selectivity profiling;
- frozen `ShapeSelectivity-v1` development policy;
- hostile W-suite construction and forensic audit.

### Findings

- no fixed fusion universally beat the strongest individual channel;
- within-position rank normalization can manufacture relative hotspots in low-amplitude positions;
- **where leverage is** and **how much leverage exists** must remain separate;
- severity != decision leverage;
- recurrence remains a major source of spatial diffuseness;
- rigid selectivity rules predictably lose rare, deep, broad, and multi-focal legitimate evidence;
- W-v2 is hostile validation / development evidence, not pristine one-shot final validation;
- **recurrence is conditional on the future set;**
- **specificity and spatial coverage trade against one another.**

### M8 exit condition

Still unmet:

> A composite pivotality model must add measurable value over its strongest individual component on a valid, preregistered, untouched evaluation protocol.

Until then, separate evidence layers remain the scientifically preferred representation.

*Update (M8 Freeze):* The first major research phase for this milestone has concluded and is now frozen. We established the critical mathematical distinctions above rather than tuning arbitrary thresholds. Future work must treat candidate-universe design as a fundamental research question. No further tuning of ShapeSelectivity-v1 or derivation of v2 is authorized in this phase.

---

## Research Track T1 — Temporal Ledger

**Status: Proposed; do not fuse into current-state heat yet**

Question:

> Can the actual move history describe how the present spatial structure was formed through investment, constraint, conversion, and persistence?

Candidate descriptive dimensions:

- **Investment** — where tempi / movable resources were repeatedly spent;
- **Constraint** — where sequences repeatedly narrowed viable choices;
- **Conversion** — where temporary activity became persistent structure;
- **Persistence** — which structural relationships survived, reversed, or reappeared.

Primary control:

Two different histories reaching the same complete legal state must produce the same objective current-state ChessHeat evidence, while their historical ledgers may differ.

Temporal Ledger must first prove it measures something distinct before any fusion with pivotality.

---

## Research Track T2 — Regional representation

**Status: Open**

Investigate whether squares are too lossy as the only spatial primitive.

Candidate first-class objects:

- files;
- diagonals;
- rays / corridors;
- king zones;
- pawn complexes;
- disjoint simultaneous tactical regions.

Broad- and multi-region hostile fixtures motivate this track.

---

## Research Track T3 — Consequence-coupled recurrence

**Status: Open**

Investigate whether recurrence relevance should depend on how strongly passage through a square distinguishes materially different root outcomes rather than on frequency / early occurrence alone.

Do not begin by simply tightening `ShapeSelectivity-v1` thresholds.

---

*Update (M8 Freeze):* The first major research phase for this milestone has concluded and is now frozen. We established critical mathematical distinctions rather than tuning arbitrary thresholds:
- control != importance
- regret != causal delta
- association != causality
- shape != amplitude
- severity != decision leverage
- recurrence is conditional on the future set
- specificity and spatial coverage trade against one another

Future work must treat candidate-universe design as a fundamental research question. No further tuning of ShapeSelectivity-v1 or derivation of v2 is authorized in this phase.

## Milestone 9 — Opening teacher prototype

**Status: Deferred until measurement integrity improves**

Long-term requirements remain:

- move-by-move board-state comparison;
- curated strategic objective annotations;
- engine evidence separate from instructional text;
- theory deviation analysis based on preserved strategic structure rather than database mismatch alone;
- guided / reduced / prediction / blind modes considered incrementally.

Exit condition:

A learner can explain strategic logic without merely replaying memorized moves.

## Milestone 10 — Explanatory AI

**Status: Deferred**

Rules remain:

- the model receives structured evidence;
- it may explain but not fabricate measurements;
- claims should be traceable to engine or curated instructional evidence;
- deterministic templates should remain available as a baseline.

## Deferred deliberately

Do not prioritize yet:

- user accounts;
- ratings or social features;
- multiplayer;
- nonstandard chess pieces / arbitrary rule variants;
- large opening databases;
- mobile apps;
- cloud scaling;
- gamification;
- LLM-first tactical analysis.

The project earns complexity only after the central measurement earns trust.
