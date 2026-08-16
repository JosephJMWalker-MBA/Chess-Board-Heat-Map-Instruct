# ChessHeat Next Work Map

## Purpose

This plan consolidates the completed external-research track into an execution order for the next phase of ChessHeat.

The governing rule remains:

> **The mathematics needs to earn the color.**

The document serves as a current-state execution map, recording completed milestones and establishing strict constraints for the active research phase.

---

## Completed Phases

### Issue #4 — Typed evidence and branch-preserved future semantics
**Status: Complete**
Established the additive branch-preserved evidence spine and mechanically demonstrated that root-conditioned consequence structure cannot in general be reconstructed after branch identity is collapsed into ordinary recurrence counts.

### S0 — Semantic Freeze v1
**Status: Complete and Frozen**
Froze the semantic contract defining:
- Sufficient state identity;
- Evidence epistemic guarantee;
- Evidence-level ladder (occurrence vs recurrence vs branch discrimination, etc.);
- Subject identity;
- Relation shape and state;
- Branch identity;
- Instrument semantics and observation validity;
- Projection semantics (canonical evidence != square projection != visualization);
- Objective/human boundary.

### S1 — Thin experimental spine
**Status: Complete**
`ExperimentSpec`, `ExperimentResult`, `SuiteManifest`, and `ComparisonResult` now exist as frozen reproducibility and integrity primitives for robust branch-preserved consequence testing.

### Issue #6 — Ray-blocker information-loss preflight
**Status: Complete (Historical)**
Demonstrated that the old lossy `SpatialEvent` projection discarded move-semantic information and could not recover exact chess histories.

### Issue #7 — Branch Move-Semantic Sufficiency
**Status: Complete**
Proved that exact ordered `future_moves` restore deterministic replay of standard-chess branch states, falsifying primitive ray/blocker irreversibility relative to sufficient state + exact move history.

### T2b — Measurement-basis contest (Ray/Blocker representation inquiry)
**Status: Complete**
- **T2b-1 (Issue #8): FALSIFIED** — Sole-blocker ray transition is exactly reproduced by the constituent-square event.
- **T2b-2 (Issue #9): WEAK_SUPPORT** — Relation breaks a single local-square alias across contexts, but a fixed context-aware square/state composite reconstructs it exactly.
- **T2b-3 (Issue #10): FALSIFIED** — A strong canonical square-native geometry representation matches the relation at the same information boundary, schema count, binding count, and held-out transfer cost.

**T2 Conclusion**: Rule-exact relations remain legitimate derived chess semantics and may be convenient explanatory coordinates, but the tested ray/blocker family did not earn privileged status as a nonredundant or more compact measurement basis over sufficiently capable canonical square/state geometry.

**Broad T2a graph/ontology construction is explicitly parked**. Deterministic chess semantics remain valid, but a broad first-class relation graph is not currently earned as the next implementation step.

---

## Active Phase: T3a Branch-Conditioned Consequence Discrimination

**Status: CLOSED**

- **T3a-1**: INCONCLUSIVE — PV horizon
- **T3a-2**: SUPPORTED — single fixture
- **T3a-3**: INCONCLUSIVE — zero realized support
- **T3a-4**: INCONCLUSIVE — provenance; conditional numeric result strongly **FALSIFIED**

**T3a Conclusion**: $E_i(x;\mathcal{J},\theta)$ has earned status as producer-conditioned observational evidence, but $E_i$ has not earned status as a monotonic primitive of objective consequence. Six of the seven informative T3a-4 $P_f$'s ran opposite the preregistered direction. Even with the provenance ceiling, that is enough reason to stop trying to promote single-PV realization through more T3a experiments. No additional T3a experiment may be introduced merely to obtain a favorable single-PV realization result.

---

## Active Research Track

**Phase:** T3b Legal Reply Intervention
**Status:** CLOSED / FALSIFIED
**Next Scientific Step:** Representation Audit (Next Candidate)

## T3b Queue

1. ~~T3b-0 — Intervention Semantics & Scope~~ COMPLETE
2. ~~T3b-1 — Comparator Identity~~ COMPLETE
3. ~~T3b-2 — Rule-Only Fixture & Statistic Preregistration~~ COMPLETE/FROZEN
4. ~~T3b-3 — Frozen legal-reply intervention execution~~ COMPLETE / WEAK_SUPPORT / INTERVENTION_SENSITIVITY
5. ~~T3b-4 — Matched-Control Identifiability Feasibility Audit~~ COMPLETE / strict matcher semantically admissible
6. ~~T3b-5 — Strict Matchability Coverage Audit~~ COMPLETE / FEASIBLE_FOR_MATCHED_PROTOCOL_DESIGN / RULE-ONLY
7. ~~T3b-6 — Matched-Control Estimand & Calibration Preregistration~~ COMPLETE / MATCHED ESTIMAND & CALIBRATION FROZEN
8. ~~T3b-7 — Rule-Only Matched Intervention Fixture Protocol~~ COMPLETE / FROZEN
9. ~~T3b-8 — Acquisition~~ COMPLETE / 171 observations / integrity passed
10. ~~T3b-9 — Matched Analysis~~ COMPLETE / FALSIFIED

**Note**: No further T3b fixture hunting, matcher relaxation, alternative calibration, rescue corpus, or outcome-driven retuning is authorized.

---

## Later work, intentionally gated

### Representation Audit
**Priority: P2 (Next Candidate)**
Test whether independently meaningful chess concepts are recoverable from the representation. `decodable != causally used != useful for Heat`.

### Projection Audit
**Priority: P2**
Validate the lossy mapping from rich evidence to the 64-square public heatmap. The projection itself must earn faithfulness.

### Multi-Instrument robustness / T1.12
**Priority: P2**
Compare Stockfish, LC0, Syzygy, and test robustness against root-evaluation ordering and transposition-table state.

### Pathways / Evidence Fusion / Amplitude Revisit
**Priority: P3**
Treat amplitude as a separate research problem. Do not assume it is merely the norm/sum of spatial or relational evidence.

### Human navigation / teacher / explanation
**Priority: DEFER**
Remain downstream and outside objective Heat.

---

## Current Ordered Queue

1. **DONE** — Issue #4 branch-preserved evidence
2. **DONE** — S0 semantic freeze
3. **DONE** — S1 experiment spine
4. **CLOSED** — T2b ray/blocker representation inquiry; no privileged relation basis earned
5. **CLOSED** — T3a consequence-association (T3a-1, T3a-2, T3a-3, T3a-4)
6. **DONE** — T3b-0 Intervention Semantics Contract
7. **DONE** — T3b-1 Comparator Design / Identifiability
8. **DONE** — T3b-2 Rule-Only Fixture and Statistic Preregistration
9. **CLOSED** — T3b-3 Frozen legal-reply intervention execution
10. **DONE** — T3b-4 Matched-Control Identifiability Feasibility Audit
11. **DONE** — T3b-5 Strict Matchability Coverage Audit
12. **DONE** — T3b-6 Matched-Control Estimand & Calibration Preregistration (COMPLETE / MATCHED ESTIMAND & CALIBRATION FROZEN)
13. **CLOSED** — T3b-7 Rule-Only Matched Intervention Fixture Protocol
14. **CLOSED** — T3b-8 Acquisition
15. **CLOSED** — T3b-9 Matched Analysis (FALSIFIED)
16. **NEXT CANDIDATE P2** — Representation Audit
17. **P2** — Projection Audit
18. **P2** — Multi-Instrument / T1.12 robustness
19. **P3** — Pathways / Evidence Fusion / Amplitude
20. **DEFER** — Human Navigation / Teacher / Explanation

---

## Active-Phase Constraints

The following freeze rules apply during the active T3 research phase:

- No new Heat scalar;
- No M8 or ShapeSelectivity retuning;
- No broad relational graph architecture;
- No relation-rescue experiments unless new evidence independently motivates them;
- No causal language beyond the evidence level actually earned; T3b intervention sensitivity is not causal identification;
- No T1.12 execution yet;
- No human-policy quantity entering objective Heat;
- Negative, falsified, and inconclusive experiments remain preserved rather than tuned around.
