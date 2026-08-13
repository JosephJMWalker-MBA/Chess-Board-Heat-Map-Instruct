# Gemini Development Instructions — ChessHeat

## Read first

Before changing code or architecture, read in full:

1. `README.md`
2. `docs/CONCEPT.md`
3. `docs/RESEARCH_REPORT_M1_M8.md`
4. `docs/MEASUREMENT_MODEL.md`
5. `docs/ARCHITECTURE.md`
6. `docs/ROADMAP.md`
7. `docs/DECISIONS.md`

Read `docs/MILESTONE_1.md` as historical implementation context, not as the current active milestone.

If implementation, research artifacts, and documentation disagree, stop and surface the conflict. Do not silently choose the interpretation that makes the project look cleaner.

## Product invariant

ChessHeat is a **spatial consequence and leverage research system** that may eventually support instructional visualization.

It is not a weighted attack map.

Never use any of these as a substitute for square importance:

- attacker count;
- sum of attacking piece values;
- mobility count;
- legal destination count;
- Stockfish evaluation of a destination move alone;
- PV frequency alone.

Those may be evidence layers, but none independently defines leverage or pivotality.

## Critical distinctions

Preserve these distinctions in data models, naming, tests, reports, and UI:

- **Control != importance**
- **Future frequency != leverage**
- **Association != causality**
- **Where leverage is != how much leverage exists**
- **Severity != decision leverage**
- **Missing evidence != zero**
- **Selection != deletion**
- **Parseable FEN != legal state != valid experimental fixture**

## Architecture invariant

The reference measurement pipeline is:

`legal position -> Python analysis core -> Stockfish adapter -> typed measurement records -> spatial evidence layers -> visualization`

The Python analysis core must remain runnable and testable without the web layer.

The viewer is a consumer of measurement records. Do not move legal move generation, engine execution, score semantics, direct attribution, recurrence, geometry, bundle association, amplitude, or selectivity semantics into frontend code for convenience.

## Current research authority

The current next step is **M8.6.4 — Recurrence & Selectivity Semantic Integrity Audit** in `docs/ROADMAP.md`.

Do not tune thresholds or add a new pivotality formula before completing that audit.

In particular, M8.6.4 must:

- reconstruct W2/W3/W4/W12 expected-square provenance channel by channel;
- distinguish not observed / observed-rejected / observed-selected;
- assert `distinct_line_count <= admitted_candidate_count` mechanically;
- resolve historical reports of recurrence counts larger than the admitted candidate set;
- distinguish legal roots, admitted candidates, PV length, distinct candidate lines, and total visits;
- audit the current ordered first-pass `ShapeSelectivity-v1` helper and its prioritized rejection-reason semantics;
- add invariant tests;
- stop without retuning `ShapeSelectivity-v1`.

## Measurement rules

1. Preserve raw engine evidence before aggregation.
2. Preserve move-level provenance even when producing square- or region-level outputs.
3. Keep comparison perspective explicit.
4. Keep CP and mate outcomes typed; do not convert mate to fake centipawns.
5. Treat root regret as opportunity cost, not causal move delta.
6. Record engine/search settings required to reproduce analysis.
7. Preserve candidate policy and admitted candidate provenance for Recurrence.
8. Keep `visit_count` distinct from `distinct_line_count`.
9. Keep control data separate from consequence data.
10. Mark unsupported causality as unsupported.
11. Preserve event bundles when constituent geometry events are observationally confounded.
12. Keep spatial shape separate from position-level amplitude.
13. Preserve rejected evidence; selectivity is an attention policy, not evidence deletion.
14. Prefer inspectable intermediate representations over clever opaque scoring.
15. Do not introduce a composite heat formula without an explicit documented decision and comparative evidence.

## Current frozen selectivity policy

`ShapeSelectivity-v1` uses development-tuned predicates:

```text
Direct:
  candidate_fraction >= 0.15

Recurrence:
  earliest_ply <= 2
  AND distinct_line_count >= 3

Bundle:
  producing_move_count >= 3
  AND implicated_region_size <= 15
```

Do not alter these thresholds during M8.6.4.

The current implementation checks channels in ordered first-pass sequence:

`Direct -> Recurrence -> Bundle`

and returns one selected source. Its fallback rejection reason also has priority semantics. Do not describe this as fully independent per-channel selection unless the implementation is explicitly changed and tested.

## Engine role

Stockfish is a measurement source.

Treat engine output as evidence about legal continuations and typed position outcome. ChessHeat is responsible for transforming that evidence into a spatial model.

Do not ask a generative model to estimate move quality, square heat, pivotality, or tactical correctness when deterministic chess/engine evidence is available.

## Generative AI role

Generative AI remains outside the core measurement pipeline.

It may eventually:

- explain structured evidence;
- summarize measured changes;
- adapt instructional language.

It may not:

- fabricate measurements;
- replace Stockfish evaluations;
- invent causal attribution and present it as measured fact;
- silently alter the heat model;
- repair failed experiments by rewriting their interpretation.

## Testing philosophy

Tests protect semantics, not only syntax.

Important categories now include:

- legal board validity, including `Board.is_valid()` where fixtures are intended to represent standard legal states;
- legal root-move correctness;
- score perspective;
- typed mate handling;
- special moves;
- engine lifecycle cleanup;
- direct attribution provenance;
- recurrence candidate admission;
- recurrence denominator correctness;
- `distinct_line_count <= admitted_candidate_count`;
- root-move non-duplication in parsed PVs;
- geometry delta correctness;
- event-bundle provenance;
- no-data semantics;
- zero-optionality semantics;
- selectivity provenance;
- experiment-seal / fixture-integrity checks where applicable.

For research fixtures, preregister qualitative expectations before inspecting ChessHeat outputs where the experiment is intended to function as validation.

## Research integrity

The repository intentionally preserves failed assumptions and compromised experiments.

Examples include:

- invalid F4 overload hypothesis;
- prior would-be holdouts that were modified after evaluation;
- W-v2 execution-driver contamination;
- invalid W10/W11 board states;
- W7 negative-control hypothesis falsification.

Do not rename, delete, or reinterpret these artifacts merely to make the project history look cleaner.

A hostile suite designed to attack known assumptions must not be summarized as representative model accuracy.

## Temporal Ledger boundary

Temporal Ledger is a proposed separate research track, not an authorized addition to current pivotality.

Potential dimensions include:

- investment;
- constraint;
- conversion;
- persistence.

Use transposition controls. Two different histories that reach the same complete legal state should produce the same objective current-state ChessHeat evidence while their historical ledgers may differ.

Do not fuse history into heat before it demonstrates a distinct measurable quantity.

## Data model preference

Prefer structures that retain provenance.

A square- or region-level result should be able to point back to:

- root moves;
- typed engine evidence;
- candidate admission;
- PV lines;
- geometry events;
- event bundles;
- selectivity predicates;
- amplitude state.

Avoid storing only a final color or scalar.

## UI rules

The board is the primary visual object, but visualization remains downstream.

A user should be able to inspect a square or region and understand:

- what evidence layer is being viewed;
- what contributed to it;
- which moves / lines are implicated;
- which side / perspective applies;
- whether the signal is measured, derived, selected, rejected, provisional, or unsupported.

Visual intensity must never imply more certainty than the underlying data supports.

## Development discipline

- Make small, reviewable changes.
- Do not redesign the project while implementing a narrow audit.
- Prefer pure functions around measurement transforms.
- Keep engine integration behind the adapter boundary.
- Avoid coupling UI color logic to measurement logic.
- Version formulas, policies, and normalization rules when they change.
- Update `docs/DECISIONS.md` when a consequential measurement or architecture choice is accepted.
- Preserve research artifacts and exact failure status.
- If a shortcut risks changing the meaning of "heat," do not take it silently.

## Current goal

Complete M8.6.4 with semantic integrity and no threshold tuning.

The immediate deliverable is not a prettier heatmap. It is a machine-checkable answer to:

> **What exactly did each evidence channel observe, what did selectivity reject or select, and do the reported recurrence counts obey the admitted-candidate semantics encoded in the implementation?**
