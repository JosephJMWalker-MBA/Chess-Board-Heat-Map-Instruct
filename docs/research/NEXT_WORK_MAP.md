# ChessHeat Next Work Map

## Purpose

This plan consolidates the completed external-research track into an execution order for the next phase of ChessHeat.

The governing rule remains:

> **The mathematics needs to earn the color.**

The immediate risk is no longer lack of architectural possibilities. The research now gives several plausible ones. The risk is allowing implementation to grow faster than the semantics that determine what state, evidence, branch identity, intervention, relation, consequence, and projection actually mean.

Therefore the next phase begins with a **semantic freeze**, not a new Heat model.

---

## Completed prerequisite

### Issue #4 — Typed evidence and branch-preserved future semantics

**Status: Complete**

Issue #4 established the additive branch-preserved evidence spine and mechanically demonstrated both:

1. current aggregate square recurrence can be reconstructed from branch-preserved evidence; and
2. root-conditioned consequence structure cannot in general be reconstructed after branch identity is collapsed into ordinary recurrence counts.

This establishes the ordering constraint:

> Preserve legal-root branch identity before consequence comparison; aggregate only downstream.

---

# Execution gates

## S0 — Semantic Freeze v1

**Priority: P1 — next work**

Freeze the semantics that later architecture must obey without freezing the final mathematical ontology or scoring model.

### Freeze now

#### 1. Sufficient position identity

`P` must mean sufficient legal chess state, not only piece placement.

The semantic contract must be able to represent, where relevant:

- board arrangement;
- side to move;
- castling rights;
- en-passant state;
- rule-50 state;
- repetition/history availability;
- variant identity where relevant.

Measurements may declare weaker history requirements, but missing history must remain explicit rather than fabricated.

#### 2. Evidence epistemic type

Freeze a typed vocabulary capable of distinguishing at minimum:

- `RULE_EXACT`;
- `ENGINE_DERIVED`;
- `SEARCH_DERIVED`;
- `EMPIRICAL`;
- `HEURISTIC`.

Evidence types must not silently upgrade into stronger claims.

#### 3. Evidence-level ladder

Freeze the distinction among:

1. occurrence;
2. recurrence;
3. branch discrimination;
4. consequence association;
5. intervention sensitivity;
6. causal / subject validation.

These are separate evidence levels. Difficulty of inference does not erase the distinction.

#### 4. Subject identity

Freeze an extensible subject system capable of representing:

- square;
- piece;
- move;
- relation;
- path / ray;
- region;
- interaction component;
- global / non-spatial state.

Do **not** freeze a complete chess-concept taxonomy.

#### 5. Relation contract

Freeze the shape of a relation record, not the final relation list.

A relation must be able to carry:

- relation type;
- participants;
- participant roles;
- optional geometry/path;
- relation state;
- provenance.

The model must allow higher-order relations and mediators rather than assuming every meaningful chess relation is a pairwise edge.

Relation state transitions must remain expressible, including cases conceptually like:

`latent -> enabled -> realized`.

#### 6. Branch identity

Freeze the ordering:

`root move -> branch-local future evidence -> typed root consequence/regret`.

Branch identity must never be inferred from rank alone and must remain available until after consequence comparison.

#### 7. Observation / instrument semantics

Freeze the distinction among:

- board-state intervention;
- candidate conditioning;
- instrument/search conditioning.

Observation identity must be able to include instrument, instrument version/configuration, search epoch/state, candidate scope, budget, and provenance.

Independent observations intended for comparison must begin from equivalent instrument state where instrument state can contaminate results.

#### 8. Projection semantics

Freeze:

`canonical evidence != square projection != visualization`.

Visualization cannot create evidence. A square heatmap is a downstream projection and must not be the only durable scientific artifact.

#### 9. Objective / human boundary

Freeze the architectural distinction among:

- objective consequence structure;
- decision leverage/amplitude;
- human navigability/policy;
- natural-language explanation.

Human-policy or explanatory layers must not redefine objective Heat.

### Do not freeze in S0

Do **not** freeze:

- the final T2 relation taxonomy;
- a graph/hypergraph implementation;
- a consequence-discrimination formula;
- thresholds;
- recurrence weighting;
- amplitude formula;
- evidence fusion;
- Heat fusion;
- projection formula;
- causal claims;
- region taxonomy;
- a human-difficulty scalar.

### SemanticSignature-v1

S0 should establish a tiny frozen deterministic corpus producing a canonical semantic signature.

A change claiming no semantic effect must reproduce the signature exactly. A deliberate semantic change requires an explicit version bump and rationale.

### Exit condition

A future developer can determine from the semantic contract exactly what a position, subject, relation, branch, observation, intervention, consequence association, and projection mean without reading implementation code, while no unearned scoring formula or speculative ontology has been frozen.

---

## S1 — Thin experimental spine

**Priority: P1 — after S0**

Build only the minimum infrastructure required to compare competing mathematical formulations reproducibly.

Candidate first-class artifacts:

- `ExperimentSpec`;
- `ExperimentArtifact` / `ExperimentResult`;
- `SuiteManifest`;
- `ComparisonResult`;
- parameter-sweep support.

Initial suite families should remain small and purpose-specific:

- semantic regression;
- T2 mechanism stress;
- T3 branch discrimination;
- null behavior;
- tablebase calibration.

Later suite families may include:

- invariance;
- legal perturbation;
- engine disagreement;
- projection faithfulness;
- future coupling.

Natural/representative suites and mechanism-stress suites must remain distinct.

---

## T2a — Semantic chess structure

**Priority: P1 — after S1**

Reframe T2 from “regional representation” into the first half of a two-part problem:

> What deterministic semantic structure exists in a sufficient chess state?

Define a rule-derived semantic structure capable of representing local state, typed relations, mediated/higher-order relations, global/history state, and relation transitions under legal roots.

A useful working notation is:

`G_sem(P)` — semantic chess structure

and for legal root `m`:

`Delta G_m = G_sem(P_m) - G_sem(P)`.

Start from deterministic structures ChessHeat already knows how to derive or can derive directly from chess rules, including attacks, defenses, paths/rays, blockers, mobility, king constraints, and global/history state.

Do not assign consequence weights yet.

Do not prune a semantically valid relation because it later proves redundant as a measurement channel.

---

## T2b — Measurement-basis contest

**Priority: P1 — after T2a**

Separate semantic ontology from the basis used to measure consequence.

Compare competing branch-preserved representations under the same experimental protocol:

- square/event baseline;
- typed relation evidence;
- typed relation-transition evidence.

The key question is not which visualization looks best, but which representation preserves or discriminates objectively different root consequences under frozen tests.

The richer representation must earn its complexity. If relation/transition evidence fails to add falsifiable value over a simpler square baseline, that negative result should be preserved.

---

## T3a — Branch-conditioned consequence discrimination

**Priority: P1 — after T2b**

Reframe T3 from “consequence-coupled recurrence” into the broader problem:

> Which branch-local future subjects, relations, or transitions distinguish legal roots with materially different objective consequences?

Recurrence becomes one hypothesis inside T3 rather than the definition of T3.

Specify descriptive consequence-discrimination statistics without freezing a universal formula or threshold prematurely.

Preserve:

- raw root identity;
- candidate universe;
- typed CP/mate semantics;
- line source;
- provenance;
- branch-local evidence.

No causal language is authorized at this gate.

---

## T3b — Legal matched intervention

**Priority: P2 — only if T3a earns it**

Introduce an explicit intervention contract carrying at minimum:

- subject;
- operation;
- validity;
- scope;
- preserved variables;
- changed variables;
- action-space policy;
- target metric;
- comparator;
- selection role;
- producer;
- seed where stochastic;
- artifact digest.

Prefer early material-preserving interventions and matched controls, such as blocker or defender relocation and line opening/closing, before broad piece-removal perturbations.

Intervention sensitivity is still not universal causal proof.

---

# Later work, intentionally gated

## T3c — Consequence pathways

Only after intervention semantics are stable, investigate whether validated relations/transitions form reproducible consequence pathways.

Do not import neural “reasoning pathway” claims as objective chess causality.

## Representation Audit

Test whether independently meaningful chess concepts are recoverable from the representation.

Keep the distinction:

`decodable != causally used != useful for Heat`.

## Projection Audit

Validate the lossy mapping from rich evidence to the 64-square public heatmap.

The projection itself must earn faithfulness; a persuasive visualization is not evidence.

## Multi-instrument robustness

Compare Stockfish, LC0, Syzygy where available, and later instruments without defining Heat by any single engine.

## T1.12 — Engine-State & Evaluation-Order Robustness

Remain deferred until the semantic and experimental contracts are stable enough to make the result interpretable.

Question remains:

> Are CP regret relationships stable to root-evaluation ordering and transposition-table state?

## Amplitude revisit

Treat amplitude as a separate research problem. Do not assume it is merely the norm/sum of spatial or relational evidence.

## Human navigation / teacher / explanation

Remain downstream and separate from objective Heat.

---

# Ordered queue

1. **DONE** — Issue #4: branch-preserved typed evidence preflight
2. **P1** — S0: Semantic Freeze v1
3. **P1** — S1: Thin Experiment/Suite Spine
4. **P1** — T2a: Deterministic Semantic State + Relation Transitions
5. **P1** — T2b: Square vs Relation vs Transition Representation Contest
6. **P1** — T3a: Branch-Conditioned Consequence Discrimination
7. **P2** — T3b: Legal Matched Intervention
8. **P2** — Representation Audit
9. **P2** — Projection Audit
10. **P2** — Multi-Instrument / T1.12 Robustness
11. **P3** — Pathways / Evidence Fusion / Amplitude Revisit
12. **DEFER** — Human Navigation / Teacher / Explanation

## Freeze rule for the next phase

Until S0 exits:

- no new Heat scalar;
- no M8 retuning;
- no `ShapeSelectivity-v2`;
- no T2/T3 empirical scoring experiment;
- no broad relational graph architecture;
- no T1.12 execution;
- no human-policy or explanatory quantity entering objective Heat.

The immediate task is to **freeze meaning before growing architecture**.
