# T3a-3 Preregistration: Independent Consequence-Association Replication

## 1. Replication Purpose

T3a-3 is an independent conceptual replication of the positive T3a-2 consequence-association result.

T3a-2 tested:
- hanging rook;
- bishop sliding/ray attack;
- future capture event at ply 2.

T3a-3 instead tests:
- hanging bishop;
- knight discrete/L-shaped attack;
- future capture event at ply 2.

The scientific hypothesis remains the same:
A preregistered immediate branch-local capture event should associate with higher root regret when legal-root branch identity is preserved.

This experiment may earn at most:
`EvidenceLevel.CONSEQUENCE_ASSOCIATION`

It is not intervention sensitivity, causal validation, Heat validation, or prevalence evidence.

## 2. Exact Position and Legal Universe

**Freeze FEN:**
`4k3/8/1n6/8/2B5/8/8/4K3 w - - 0 1`

**Candidate Policy:**
`{}`
(Meaning all legal White roots.)

**Preregistered Legal-Root Count:**
`16`

**Exact Legal-Root Set (from rule-exact preflight):**
```
c4g8
c4f7
c4e6
c4a6
c4d5
c4b5
c4d3
c4b3
c4e2
c4a2
c4f1
e1f2
e1e2
e1d2
e1f1
e1d1
```

## 3. Rule-Exact Mechanism Context

Preserve as contextual metadata only:

**Exposed-to-Nxc4:**
```
e1f2
e1e2
e1d2
e1f1
e1d1
```

**Saved/not-exposed:**
```
c4g8
c4f7
c4e6
c4a6
c4d5
c4b5
c4d3
c4b3
c4e2
c4a2
c4f1
```

**State Explicitly:**
These are rule-exact mechanism classes and must never be substituted for observed PV event membership. `Nxc4` being legal does not imply $X_i = 1$.

## 4. Exact Observed Event

**Freeze Event:**
- square: c4
- role: capture
- ply: 2
- horizon: ply 2 only

**Define Indicator:**
$X_i = 1$ if `SpatialEvent(c4,capture,ply=2)` occurs, otherwise $0$.

Only actual branch-local continuation evidence may determine $X_i$.

**Explicitly Prohibit Using:**
- root UCI identity;
- preflight mechanism class;
- legality of Nxc4;
- SAN;
- root origin/destination;
- candidate ordering;
- score;
- regret;
- T3a-2 partition membership or effect size.

## 5. Expected Direction

**Freeze:**
`BAD / HIGHER_REGRET`

**Rationale:**
The manually constructed chess mechanism predicts that roots whose immediate continuation actually contains the capture of the hanging bishop on c4 should have worse White consequence than roots whose continuation does not. This remains a hypothesis.

## 6. Exact Instrument

**Freeze Exactly:**
- producer: Stockfish 18
- Threads: 1
- Hash: 16 MB
- search budget: 100000 nodes
- line source: pv
- comparison perspective: white
- candidate policy: {}

Do not change these after observing output.

## 7. Experiment Identity Contract

This is the first T3 experiment that must use the hardened S1 identity contract.

**Freeze:**
- `spec_version = 2`
- `comparison_perspective = "white"`

The eventual `ExperimentSpec` must mechanically include both and must fail validation if perspective is absent or invalid. Historical v1 compatibility is irrelevant to this new experiment; do not use v1 for T3a-3.

## 8. Observation Completeness

Every one of the 16 legal roots must expose parsed ply 2.

If any root lacks ply 2:
- classification = `INCONCLUSIVE`
- failure_reason = `INSUFFICIENT_OBSERVED_PV_LENGTH`

Do not shorten/change the horizon, increase the budget, or rerun to rescue the result.

## 9. Typed Consequence Contract

Compute regret over the complete 16-root universe using existing authoritative `compute_regrets()`.
Require all regrets to be CP.

Any mate/CP mixture: `INCONCLUSIVE`.

**No:**
- mate-to-CP conversion;
- rank normalization;
- regret threshold;
- best/worst-N selection;
- post-output exclusion;
- alternate consequence statistic.

**Require:**
$|X=1| \ge 2$, $|X=0| \ge 2$.
Otherwise: `INCONCLUSIVE`.

## 10. Frozen Statistics

For preregistered BAD direction:
$D = \text{median}(R \mid X=1) - \text{median}(R \mid X=0)$
$M = \text{min}(R \mid X=1) - \text{max}(R \mid X=0)$

**Freeze Exactly:**
- `SUPPORTED` if $D > 0$ and $M > 0$;
- `WEAK_SUPPORT` if $D > 0$ and $M \le 0$;
- `FALSIFIED` if valid partitions exist and $D \le 0$;
- `INCONCLUSIVE` for incomplete observation, mixed typed consequences, insufficient partition cardinality, invalid root universe, instrument/config mismatch, invalid v2 identity, or invalid provenance.

No threshold may be added later.

## 11. Aggregate Evidence

If all $X_i$ are observable, preserve:
$A(x) = \sum X_i$

State that this scalar retains event prevalence but destroys root→event assignment and therefore cannot itself recover root-conditioned consequence association. The aggregation irreversibility lemma is prior methodology, not new evidence from T3a-3.

## 12. Required Eventual Execution Invariants

Execution must mechanically verify:
- exact producer/config/budget;
- exact 16-root legal universe;
- observed root UCI set equals python-chess legal-root set;
- ply 1 excluded;
- only ply 2 determines $X_i$;
- all branches complete through ply 2;
- permutation invariance under original, reversed, and deterministic root-sorted order;
- CP-only typed regret;
- actual canonical S0 digest;
- actual fixture digest;
- real SuiteManifest;
- real SufficientPosition;
- `ExperimentSpec(spec_version=2, comparison_perspective="white")`;
- real immutable `ExperimentResult`;
- artifact reload/integrity validation.

Persist the complete legal-root set, root→$X_i$ mapping, typed scores/regrets, partitions, D, M, A(x), all identity digests, exact instrument configuration, and classification.

## 13. Independence / No-Rescue Rule

- This fixture was manually chosen from chess rules before Stockfish evaluation;
- T3a-2's numerical scores, regrets, D=27, M=3, or 5-vs-14 observed partition must not be used to tune T3a-3;
- T3a-3 does not need to reproduce T3a-2's effect size;
- the fixture/event/direction/horizon/config/statistics cannot change after output;
- SUPPORTED, WEAK_SUPPORT, FALSIFIED, and INCONCLUSIVE are all acceptable frozen outcomes;
- no replacement fixture may be run after seeing this one's result.
