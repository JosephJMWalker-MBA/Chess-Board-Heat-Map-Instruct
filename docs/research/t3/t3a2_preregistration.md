# T3a-2 Preregistration: Immediate-Continuation Consequence Association

This document preregisters an exact `EvidenceLevel.CONSEQUENCE_ASSOCIATION` experiment testing branch-local future evidence against typed root consequence.

This document must be frozen before any Stockfish evaluation of the specified position occurs.

## 1. Research Question

Does the immediate branch-local future event `(d4, capture)` at ply 2 associate with objectively worse root consequence when branch identity is preserved?

**Constraints:**
- This is an `EvidenceLevel.CONSEQUENCE_ASSOCIATION` experiment only.
- No intervention, causal, Heat, or prevalence claim is authorized.

## 2. Exact Fixture

**FEN:**
`4k3/8/1b6/8/3R4/8/8/4K3 w - - 0 1`

**Candidate Policy:**
`{}` (The complete legal-root universe must be evaluated).

**Preregistered Legal-Root Count:**
19

**Contextual Preflight (Not PV Evidence):**
A rule-exact preflight confirms two valid mechanism classes based strictly on standard chess geometry (not engine outcomes):
- **Exposed-to-Bxd4 (5 roots):** White King moves (`e1f2`, `e1e2`, `e1d2`, `e1f1`, `e1d1`) leave the White Rook on `d4` and allow a legal `Bxd4` reply.
- **Not-exposed-to-Bxd4 (14 roots):** White Rook moves remove the rook from `d4`, making the immediate `Bxd4` mechanism unavailable.

*Note: These mechanism classes are contextual metadata only. They are not equivalent to observed PV event membership.*

## 3. Exact Spatial Event

**Definition:**
- **Square:** `d4`
- **Role:** `capture`
- **Horizon:** ply 2 only

**Variable $X_i$:**
$$
X_i = \begin{cases}
1, & \text{if a } \texttt{SpatialEvent(square="d4", role="capture", ply=2)} \text{ occurs} \\
0, & \text{otherwise}
\end{cases}
$$

**Strict Observational Boundary:**
Only the actual frozen branch continuation may determine $X_i$. 
Do NOT use:
- Root move identity;
- Whether `Bxd4` is merely legal;
- Mechanism-class membership;
- SAN;
- Root origin/destination;
- Candidate ordering;
- Score;
- Regret.

## 4. Expected Consequence Direction

**Direction:** `BAD / HIGHER_REGRET`

**Rationale:**
The manually constructed mechanism predicts that branches whose immediate continuation actually captures the hanging rook on `d4` should arise from objectively worse White root choices than branches without that future event. 
*(This is a hypothesis, not an established fact.)*

## 5. Exact Instrument

**Producer Identity & Config:**
- **Producer:** Stockfish 18
- **Threads:** 1
- **Hash:** 16 MB
- **Search Budget:** 100000 nodes
- **Line Source:** `pv`
- **Comparison Perspective:** `white`

*If execution cannot verify the exact frozen producer and configuration, the experiment must become `INCONCLUSIVE`. Do not silently substitute another configuration.*

## 6. Observation Completeness

Every legal root must expose at least one continuation ply after the root (i.e., parsed ply 2). 

If any root lacks a parsed ply 2, classify as `INCONCLUSIVE` with the failure reason:
`INSUFFICIENT_OBSERVED_PV_LENGTH`.

Do not change the horizon, budget, or fixture afterward.

## 7. Typed Consequence Contract

- Compute typed regret over the complete legal-root universe using the existing authoritative `compute_regrets()` semantics.
- All evaluated regrets must be `cp` (centipawns).
- If any mate/CP mixture is observed, classify as `INCONCLUSIVE`.

**Strict Invariants:**
- Do not convert mate to CP, rank-normalize, threshold regret, select top-N roots, or otherwise normalize the consequence variable.
- Require partition cardinalities $|X=1| \ge 2$ and $|X=0| \ge 2$. Otherwise, classify as `INCONCLUSIVE`.

## 8. Frozen Statistics

Because the event is preregistered as `BAD`, we define:

- **Median Separation (D):**
  $$D = \text{median}(R \mid X=1) - \text{median}(R \mid X=0)$$
- **Complete Separation Margin (M):**
  $$M = \text{min}(R \mid X=1) - \text{max}(R \mid X=0)$$

**Classification logic:**
- `SUPPORTED` if $D > 0$ and $M > 0$;
- `WEAK_SUPPORT` if $D > 0$ and $M \le 0$;
- `FALSIFIED` if valid partitions exist and $D \le 0$;
- `INCONCLUSIVE` for incomplete ply-2 observation, mixed typed consequence, insufficient partition cardinality, invalid legal-root universe, instrument mismatch, or invalid provenance.

*No threshold may be added after observing the data.*

## 9. Aggregate Comparison

If the complete $X_i$ vector is observable, preserve:
$$A(x) = \sum_i X_i$$

**Explicit Statement:**
The aggregate count preserves the prevalence of the event across branches, but not the mapping from legal root to event membership. The already-established aggregation irreversibility lemma explains why $A(x)$ alone cannot recover root-conditioned consequence association. *(This lemma itself is not claimed as empirical support for T3a-2.)*

## 10. Required Execution Invariants

The eventual execution must mechanically verify:
1. Observed root UCI set exactly equals `python-chess` legal-root set.
2. Legal-root count is exactly 19.
3. Ply 1 is excluded from evidence membership.
4. Only ply 2 determines $X_i$.
5. Evaluation is invariant under original, reversed, and deterministic sorted branch order.
6. The actual fixture digest, S0 semantic digest, S1 suite/spec/result identities, producer/options/budget, typed regrets, partitions, D, M, aggregate membership count, and classification are persisted to a deterministic artifact.

## 11. Blinding / No-Rescue Rule

- This fixture was selected from rule-exact chess structure *before* Stockfish evaluation.
- No Stockfish output for this position may be inspected before this preregistration is committed and pushed.
- The event, horizon, direction, fixture, budget, and classification rules **must not be changed** after engine output.
- A falsified or inconclusive result must be preserved as-is.
- T3a-1 outcomes must not be used to tune this fixture beyond the already-decided methodological change to a fresh fixture and ply-2-only horizon.
