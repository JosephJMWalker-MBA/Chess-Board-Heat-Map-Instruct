# ChessHeat

ChessHeat is an experimental chess research system built around one question:

> **Which squares or spatial structures matter most to what happens next in a chess position?**

The project uses legal chess, typed engine evidence, reproducible experiments, and explicit research boundaries to investigate spatial consequence, leverage, geometry, and temporal structure before promoting any of them into a finished heat-map model.

> **The mathematics needs to earn the color.**

ChessHeat began as a visualization and teaching idea. The current work is more fundamental: determine what spatial claims are actually supported, which are merely useful conventions, and what must remain unresolved.

## What exists today

The repository contains a substantial Python measurement and research system plus a separate browser viewer.

The reference pipeline is deliberately engine-first and headless:

`legal chess position -> Python analysis core -> Stockfish adapter -> typed measurement records -> spatial evidence layers -> web visualization`

Implemented research surfaces include:

- reproducible Stockfish-backed legal-position analysis;
- typed CP and mate-sensitive outcomes rather than fake cross-type scalar conversion;
- root-move opportunity-cost / regret measurements;
- direct square-attribution evidence;
- principal-variation recurrence evidence with candidate provenance;
- paired-position and structural geometry deltas;
- event bundles for observationally confounded structural changes;
- branch-preserved experimental evidence;
- sufficient-state and experiment identity/provenance infrastructure;
- Temporal Ledger research artifacts for persistence, reappearance, censoring, and history-sensitive analysis;
- experiment specifications, manifests, comparison records, execution seals, and preserved validation artifacts;
- a web viewer that consumes generated evidence records rather than reimplementing chess measurement semantics in JavaScript.

The viewer is an implemented inspection surface. It is **not** evidence that a final public Heat projection has been scientifically validated.

## What has not been earned

ChessHeat does **not** currently claim a validated universal Heat scalar, a discovered objective allocation of consequence to squares, or a single privileged spatial representation.

Several distinctions are now central to the research:

- **Control != importance**
- **Future frequency != leverage**
- **Association != causality**
- **Intervention sensitivity != causal identification**
- **Where leverage is != how much leverage exists**
- **Shape != amplitude**
- **Severity != decision leverage**
- **Legal opportunity != search realization != consequence**
- **Empirical utility of an attribution convention != truth of square ownership**
- **Information gain != representation utility**
- **Source orientation != source magnitude != spatial support**
- **Non-significance != equivalence**

The project intentionally preserves attractive hypotheses that were falsified, inconclusive, contaminated, underidentified, or blocked. Those outcomes narrow the scientific question; they are not rewritten into successes.

## Core idea

Traditional engine interfaces answer questions such as:

- What is the evaluation?
- What is the best move?
- How large was the centipawn loss?

ChessHeat asks a different class of questions:

- Which squares or regions are structurally important in this position?
- Where can a small board-state change create a large positional consequence?
- Which spatial patterns recur across plausible strong continuations?
- What changed in the board's leverage structure after a move?
- Which spatial representation makes consequence-related structure more accessible without pretending that accessibility proves objective ownership?

The intended output is not merely a weighted attack map. A square can be heavily controlled yet strategically unimportant, or evenly contested while participating in a consequential structure.

## Working vocabulary

- **Control** — who attacks or defends a square.
- **Leverage** — decision sensitivity or opportunity associated with meaningful alternatives; not synonymous with attack count.
- **Hazard** — how costly interaction with a square may be for a given side.
- **Pivotality** — a historical working term for how central a square or region appears across consequential futures; no universal pivotality model has been earned.
- **Heat delta** — change in a defined spatial measurement between board states; not one universal scalar until a measurement definition earns that status.
- **Amplitude** — how much position-level decision leverage is present, kept separate from where evidence is spatially organized.
- **Shape** — where spatial evidence is organized, separate from amplitude.

These remain research definitions, not claims of discovered chess ontology.

## Engine role

Stockfish is a **measurement instrument**, not the product itself.

Engine search and evaluation provide reproducible evidence about legal alternatives and typed outcomes. ChessHeat is responsible for preserving that evidence, stating the comparison perspective, recording instrument configuration, and testing what spatial transformations are justified.

Generative AI may explain structured evidence downstream, but it must not invent the underlying chess measurements or silently promote an unsupported causal interpretation.

## Research progression

The first research sprint through Milestones 1–8 established the implementation foundation and exposed several important limitations:

- root-move regret is useful as an opportunity-cost quantity but is not a causal move delta;
- direct square attribution is useful for tactical endpoints but incomplete for indirect structure;
- principal-variation recurrence adds a distinct future-path signal but can be diffuse and producer-conditioned;
- structural geometry delta can expose rays, pathways, attacks, defenses, blockers, and mobility changes away from move endpoints;
- event bundles can be more honest than isolated causal claims when structural events are confounded;
- **where leverage is** and **how much leverage exists** are distinct questions;
- no fixed Direct/Recurrence/Bundle fusion earned status as a universal pivotality model.

The hostile W-suite is retained as development / hostile-validation evidence, **not** pristine one-shot final validation. Invalid fixtures, execution contamination, and failed expectations remain visible in the record.

Later tracks narrowed the question further:

- the Temporal Ledger work established a reproducible history-sensitive research layer while keeping historical state separate from objective current-state evidence;
- representation studies showed that tested ray/blocker relations did not earn privileged or irreducible status over sufficiently capable square/state representations;
- branch-conditioned search-realization studies did not earn search frequency as a monotonic primitive of objective consequence;
- the strict matched legal-reply intervention study was falsified under its preregistered protocol;
- spatial-consequence preflight showed that objective square attribution is **not identified by the current axioms**;
- subsequent attribution work separated source orientation, source magnitude, and spatial-support convention rather than silently collapsing them into one Heat quantity.

The strongest progress is therefore methodological as much as visual: the project increasingly knows what it is **not yet entitled to claim**.

## Current frontier — CP-only representation efficiency

The active research question is now deliberately narrower:

> Under one frozen learner/training regime and equalized underlying move information, does destination-only spatial organization or transition-touch organization yield greater sample efficiency for predicting held-out target-instrument ordering of CP/CP-source legal-alternative pairs?

The active document is:

[`docs/research/CP_ONLY_REPRESENTATION_EFFICIENCY_PREREGISTRATION.md`](docs/research/CP_ONLY_REPRESENTATION_EFFICIENCY_PREREGISTRATION.md)

Its current status is intentionally:

```text
PREREGISTRATION_DRAFT_ONLY
ENGINE_EXECUTION_NOT_AUTHORIZED
MODEL_TRAINING_NOT_AUTHORIZED
```

Several protocol choices and statistical boundaries remain to be resolved and frozen before execution. In particular, the current preregistration must not treat failure to resolve a difference as evidence of equivalence. Engine capability already present in the repository does not constitute permission to run the study before those blockers are closed.

The current objective is therefore **protocol integrity and blocker resolution**, not obtaining a favorable experimental result.

## Research integrity

ChessHeat preserves failed and negative evidence as first-class research history.

Examples across the repository include hypotheses or experimental paths classified as:

- `FALSIFIED`;
- `INCONCLUSIVE`;
- `WEAK_SUPPORT`;
- `NOT_IDENTIFIED`;
- `NOT_YET_EARNED`;
- contaminated or invalid for the intended claim.

No further fixture hunting, threshold retuning, matcher relaxation, rescue corpus, or reinterpretation is justified merely because an earlier result was unfavorable.

A development or hostile-validation corpus is not presented as representative accuracy. A useful attribution convention is not promoted into objective square ownership. An implemented visualization is not treated as proof that its projection is scientifically faithful.

## Instructional goal — downstream

Teaching remains a meaningful downstream application, not the current authority for the measurement model.

The long-term instructional idea is to help a learner understand how consequence-related board structure changes move by move rather than memorizing only notation such as:

> `1. e4 e5 2. Nf3 Nc6 3. Bb5`

A future teaching system could help a learner inspect:

- which measured structures changed;
- what strategic objective a move may have advanced;
- what changed when theory was followed or departed from;
- whether the learner can reconstruct the logic after forgetting the memorized sequence.

But pedagogical attractiveness must not decide what counts as objective Heat. Human navigability and explanation remain downstream of the scientific representation problem.

## Research record

For the current state, start here:

1. [`docs/research/RESEARCH_CONTINUITY_CHECKPOINT_2026-08-16.md`](docs/research/RESEARCH_CONTINUITY_CHECKPOINT_2026-08-16.md) — broad restart/handoff state, earned and rejected claims, and current blockers.
2. [`docs/research/NEXT_WORK_MAP.md`](docs/research/NEXT_WORK_MAP.md) — current operational dependency order.
3. [`docs/research/CP_ONLY_REPRESENTATION_EFFICIENCY_PREREGISTRATION.md`](docs/research/CP_ONLY_REPRESENTATION_EFFICIENCY_PREREGISTRATION.md) — active preregistration draft; execution currently blocked.
4. [`docs/research/SEMANTIC_CONTRACT_V1.md`](docs/research/SEMANTIC_CONTRACT_V1.md) — frozen semantic contract.
5. [`docs/RESEARCH_REPORT_M1_M8.md`](docs/RESEARCH_REPORT_M1_M8.md) — historical M1–M8 synthesis.

Additional design and implementation context:

- [`docs/CONCEPT.md`](docs/CONCEPT.md)
- [`docs/MEASUREMENT_MODEL.md`](docs/MEASUREMENT_MODEL.md)
- [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md)
- [`docs/ROADMAP.md`](docs/ROADMAP.md)
- [`docs/DECISIONS.md`](docs/DECISIONS.md)
- [`docs/MILESTONE_1.md`](docs/MILESTONE_1.md) — historical implementation context
- [`AGENTS.md`](AGENTS.md) — vendor-neutral durable development and research constraints

The raw development and validation artifacts are intentionally preserved under `tests/fixtures/` and elsewhere in the research record, including experiments that later proved invalid, contaminated, falsified, or weaker than initially expected.

## Status

**Active research system.**

The measurement infrastructure, typed evidence layers, experiment/provenance spine, Temporal Ledger research surface, and inspection viewer are substantial and real. The universal Heat model is not finished, objective square ownership is not established, and the current CP-only representation-efficiency experiment remains preregistration-only until its blockers are resolved.

That boundary is intentional.
