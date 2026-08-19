# Development and Research Instructions — ChessHeat

## Read first

Before changing research semantics, measurement code, experiment infrastructure, or architecture, read these in order:

1. `README.md`
2. `docs/research/RESEARCH_CONTINUITY_CHECKPOINT_2026-08-16.md`
3. `docs/research/NEXT_WORK_MAP.md`
4. `docs/research/CP_ONLY_REPRESENTATION_EFFICIENCY_PREREGISTRATION.md`
5. `docs/research/SEMANTIC_CONTRACT_V1.md`
6. `docs/MEASUREMENT_MODEL.md`
7. `docs/ARCHITECTURE.md`
8. `docs/DECISIONS.md`
9. `docs/ROADMAP.md`
10. `docs/RESEARCH_REPORT_M1_M8.md` for historical synthesis

Read `docs/MILESTONE_1.md` as historical implementation context, not as the active research milestone.

If implementation, research artifacts, preregistration, and documentation disagree, stop and surface the conflict. Do not silently choose the interpretation that makes the project look cleaner or produces the preferred result.

## Current research authority

ChessHeat is an active research program, not a sequence of prompts to advance automatically.

The current operational map is `docs/research/NEXT_WORK_MAP.md`. The broader restart/handoff state is preserved in `docs/research/RESEARCH_CONTINUITY_CHECKPOINT_2026-08-16.md`. The active CP-only experiment is governed by `docs/research/CP_ONLY_REPRESENTATION_EFFICIENCY_PREREGISTRATION.md`.

At the current repository frontier, that preregistration remains a draft. Engine execution and model training are not authorized until the documented blockers are resolved and the protocol is explicitly frozen.

Do not infer permission to execute an experiment merely because supporting engine or model code already exists.

## Governing invariant

> **The mathematics needs to earn the color.**

ChessHeat is a spatial consequence and leverage research system that may eventually support instructional visualization. It is not a weighted attack map, and it does not currently possess a validated universal Heat scalar.

Never use any of these as a substitute for square importance:

- attacker count;
- sum of attacking piece values;
- mobility count;
- legal destination count;
- Stockfish evaluation of a destination move alone;
- PV frequency alone.

Those may be evidence layers. None independently defines leverage, pivotality, consequence, or objective square ownership.

## Critical distinctions

Preserve these distinctions in data models, naming, tests, reports, experiments, and UI:

- **Control != importance**
- **Future frequency != leverage**
- **Association != causality**
- **Intervention sensitivity != causal identification**
- **Where leverage is != how much leverage exists**
- **Shape != amplitude**
- **Severity != decision leverage**
- **Missing evidence != zero**
- **Selection != deletion**
- **Legal opportunity != search realization != consequence**
- **Empirical utility of an attribution convention != truth of square ownership**
- **Information gain != representation utility**
- **Source orientation != unsigned source magnitude != spatial support**
- **Non-significance != equivalence**
- **Parseable FEN != legal state != valid experimental fixture**

## Architecture invariant

The reference measurement pipeline is:

`legal position -> Python analysis core -> Stockfish adapter -> typed measurement records -> spatial evidence layers -> visualization`

The Python analysis core must remain runnable and testable without the web layer.

The viewer is a consumer of measurement records. Do not move legal move generation, engine execution, score semantics, attribution, recurrence, geometry, bundle association, amplitude, selectivity, experiment semantics, or provenance into frontend code for convenience.

Visualization is downstream of evidence. A working viewer does not by itself validate the semantics of a public Heat projection.

## Measurement rules

1. Preserve raw engine evidence before aggregation.
2. Preserve move-level and branch-level provenance when consequence comparisons require it.
3. Keep comparison perspective explicit.
4. Keep CP, mate, and other outcome types typed; do not convert mate to fake centipawns.
5. Treat root regret as opportunity cost, not causal move delta.
6. Record engine/search settings required to reproduce analysis.
7. Preserve candidate policy and admitted candidate provenance for recurrence.
8. Keep `visit_count` distinct from `distinct_line_count`.
9. Keep control data separate from consequence data.
10. Mark unsupported causality as unsupported.
11. Preserve event bundles when constituent geometry events are observationally confounded.
12. Keep spatial shape separate from position-level amplitude.
13. Preserve rejected evidence; selectivity is an attention policy, not evidence deletion.
14. Prefer inspectable intermediate representations over clever opaque scoring.
15. Do not introduce a composite Heat formula without an explicit documented decision and comparative evidence.
16. Do not promote an attribution convention into objective square ownership merely because it is useful.
17. Do not collapse source orientation, source magnitude, and spatial support into one scientific object without earned justification.
18. Do not treat failure to detect a difference as evidence of equivalence unless an equivalence margin was scientifically justified and preregistered.

## Frozen and historical research

Earlier research phases remain evidence, including phases that ended `FALSIFIED`, `INCONCLUSIVE`, `WEAK_SUPPORT`, `NOT_IDENTIFIED`, or `NOT_YET_EARNED`.

Do not revive a closed hypothesis simply to search for a favorable fixture, retune thresholds after seeing outcomes, relax a matcher to rescue a result, or reinterpret a contaminated experiment as pristine validation.

The M1–M8 record, T1 Temporal Ledger work, T2 representation studies, T3a branch-conditioned association work, T3b legal-reply intervention work, and spatial-attribution preflights are part of the provenance chain. Consult the continuity checkpoint and next-work map for their exact current status.

Historical `ShapeSelectivity-v1` thresholds and channel semantics must not be silently changed if code touching that subsystem is modified. Read the historical decisions and tests first; do not treat those development-tuned thresholds as discovered laws.

## Engine role

Stockfish is a measurement source.

Treat engine output as evidence about legal continuations and typed position outcomes. ChessHeat is responsible for transforming that evidence into inspectable research artifacts and, where justified, spatial representations.

Do not ask a generative model to estimate move quality, square heat, pivotality, tactical correctness, or experimental outcomes when deterministic chess or engine evidence is available.

For new experiments, engine-state boundaries, source/target independence, budgets, root sampling, split logic, and other acquisition details must be explicitly frozen when the protocol requires them. Existing engine capability is not evidence that a new acquisition protocol is already valid.

## Generative AI role

Generative AI remains outside the core measurement pipeline.

It may:

- explain structured evidence;
- summarize measured changes;
- help draft research documentation;
- adapt instructional language downstream.

It may not:

- fabricate measurements;
- replace Stockfish evaluations;
- invent causal attribution and present it as measured fact;
- silently alter the Heat model;
- repair failed experiments by rewriting their interpretation;
- convert unresolved scientific questions into implementation assumptions.

## Testing philosophy

Tests protect semantics, not only syntax.

Important categories include:

- legal board validity where fixtures represent standard chess states;
- legal root-move correctness;
- score perspective;
- typed mate handling;
- special moves;
- engine lifecycle cleanup;
- attribution provenance;
- recurrence candidate admission and denominator correctness;
- `distinct_line_count <= admitted_candidate_count`;
- root-move non-duplication in parsed PVs;
- geometry-delta correctness;
- event-bundle provenance;
- no-data and zero-optionality semantics;
- experiment-seal and fixture-integrity checks;
- sufficient-state identity;
- branch identity where required;
- train/tune/test separation at the correct statistical sampling unit;
- preregistered protocol-invalidity conditions.

For research fixtures, preregister qualitative expectations before inspecting ChessHeat outputs whenever the experiment is intended to function as validation.

## Research integrity

The repository intentionally preserves failed assumptions, invalid fixtures, contaminated runs, falsified hypotheses, and blocked experiments.

Do not rename, delete, rewrite, or reinterpret those artifacts merely to make the project history look cleaner.

A development or hostile-validation suite must not be summarized as representative model accuracy or pristine held-out validation.

When an experiment is blocked, preserve the blocker. When a result is unresolved, call it unresolved. When a hypothesis is falsified, do not rescue it without a new prospectively justified question.

## Data model preference

Prefer structures that retain provenance.

A square-, region-, relation-, or position-level result should be able to point back to the evidence that produced it, including as applicable:

- sufficient root state;
- legal alternatives;
- root moves;
- typed engine evidence;
- candidate admission;
- branch identity and PV lines;
- geometry events;
- event bundles;
- selectivity predicates;
- source orientation;
- source magnitude;
- spatial-support convention;
- amplitude state;
- experiment identity and execution seal.

Avoid storing only a final color or scalar.

## UI rules

The board is the primary visual object, but visualization remains downstream.

A user should be able to inspect a square or region and understand:

- what evidence layer is being viewed;
- what contributed to it;
- which moves, branches, or lines are implicated;
- which side and comparison perspective apply;
- whether the signal is measured, derived, selected, rejected, provisional, conventional, unresolved, or unsupported.

Visual intensity must never imply more certainty than the underlying data supports.

## Instructional boundary

Opening instruction, human navigation, explanation, and teaching are downstream applications.

Do not optimize the objective measurement model for pedagogical attractiveness before the relevant representation and projection semantics have earned support. Generative explanation must consume measured evidence rather than become the evidence source.

## Development discipline

- Make small, reviewable changes.
- Follow the active dependency order in `docs/research/NEXT_WORK_MAP.md`.
- Do not execute a preregistered study while its own document says execution is blocked.
- Do not redesign the project while implementing a narrow audit.
- Prefer pure functions around measurement transforms.
- Keep engine integration behind the adapter boundary.
- Avoid coupling UI color logic to measurement logic.
- Version formulas, policies, normalization rules, schemas, and experiment protocols when they change.
- Update `docs/DECISIONS.md` when a consequential measurement or architecture choice is accepted.
- Preserve research artifacts and exact failure status.
- If a shortcut risks changing the meaning of `Heat`, do not take it silently.

## Current goal

Do **not** infer a new current goal from this file. This file contains durable constraints.

For the active task, read `docs/research/NEXT_WORK_MAP.md` and the active preregistration. At the current documented frontier, the immediate work remains protocol/documentation repair and blocker resolution before any engine execution or model training is authorized.
