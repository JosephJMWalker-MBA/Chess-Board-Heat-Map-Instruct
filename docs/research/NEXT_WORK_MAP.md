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

**Status: ACTIVE P1**

### T3a-1 (Issue #11): First preregistered consequence-association experiment
**Status: Complete — INCONCLUSIVE**
- **Preregistration SHA**: 748fb141450ae14ca489120900a520027c21ffc6
- **Final Semantic Closeout SHA**: 5f0d91b8b55bd3de92722d533918af47e72a4947
- **Classification**: `INCONCLUSIVE`
- **Failure Reason**: `INSUFFICIENT_OBSERVED_PV_LENGTH`
- **Methodological Result**: A fixed 100k-node budget does not guarantee a four-continuation-ply observable PV for every legal root.
- **Note**: This result must not be interpreted as evidence for or against the branch-conditioned consequence hypothesis.

### Next Scientific Experiment: T3a-2

**T3a-2 — Fresh preregistered immediate-continuation consequence association.**
- Must use a **new manually constructed mechanism** (ideally another immediate hanging-piece capture on a different piece/square).
- Must use a shortened horizon: `H = {ply 2}` (one continuation ply) to drastically reduce the chance of observing insufficient PV lengths, while still testing genuine future branch evidence and excluding the root move.
- **IMPORTANT**: Do not reuse the T3a-1 FEN/event as a shortened-horizon rescue because its outcomes are already observed and no longer constitute a clean preregistered test.

---

## Later work, intentionally gated

### T3b — Legal matched intervention
**Priority: GATED P2 — only if T3a earns it**
Consequence association is not intervention sensitivity or causality. T3b is gated until T3a earns escalation through interpretable and replicated association tests.

### Representation Audit
**Priority: P2**
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
5. **DONE/INCONCLUSIVE** — T3a-1 first preregistered consequence-association experiment
6. **NEXT P1** — T3a-2 fresh immediate-continuation preregistered experiment
7. **P1** — independent T3a replication if T3a-2 is interpretable
8. **GATED P2** — T3b legal matched intervention
9. **P2** — Representation Audit
10. **P2** — Projection Audit
11. **P2** — Multi-Instrument / T1.12 robustness
12. **P3** — Pathways / Evidence Fusion / Amplitude
13. **DEFER** — Human Navigation / Teacher / Explanation

---

## Active-Phase Constraints

The following freeze rules apply during the active T3a research track:

- No new Heat scalar;
- No M8 or ShapeSelectivity retuning;
- No broad relational graph architecture;
- No relation-rescue experiments unless new evidence independently motivates them;
- No intervention or causal language before T3b;
- No T1.12 execution yet;
- No human-policy quantity entering objective Heat;
- Negative, falsified, and inconclusive experiments remain preserved rather than tuned around.
