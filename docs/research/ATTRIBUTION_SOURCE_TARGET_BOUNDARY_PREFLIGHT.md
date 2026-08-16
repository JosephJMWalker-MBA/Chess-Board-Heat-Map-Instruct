# Attribution Source–Target Boundary Preflight

## 1. Central Question
What exact source observation may be spatialized into $M_\mu$, and what exact held-out target may subsequently test its representation utility, without target leakage, fake outcome conversion, or silently inventing a production amplitude?

We provisionally preserve the prediction unit:
$$u = (P, r, q)$$
where:
- $P = \text{sufficient root state}$
- $r = \text{operator-blind, target-blind reference legal alternative}$
- $q = \text{legal query alternative}$

*(Do not assume $u$ is final).*

## 2. Actual Source-Bundle Ledger

Let $X_u$ be the exact information available before target acquisition. 

| Property | X0 (Rule-only) | X1 (Source-instrument comparison) | X2 (Source branch evidence) |
|---|---|---|---|
| **Can $G_{\mu_D}$ be instantiated?** | Yes | Yes | Yes |
| **Can $G_{\mu_T}$ be instantiated?** | Yes | Yes | Yes |
| **Can consequence-weighted $M_{\mu_D}$ be instantiated?** | No | Yes (subject to typed weighting semantics) | Yes |
| **Can consequence-weighted $M_{\mu_T}$ be instantiated?** | No | Yes (subject to typed weighting semantics) | Yes |
| **$q$ source outcome known?** | No | Yes (under $J_X, \theta_X$) | Yes |
| **Target $Y$ outcome withheld?** | Yes | Yes | Yes |
| **Producer dependence** | None | Source instrument ($J_X$) | Source instrument ($J_X$) |
| **Information entering representation** | Move/state geometry, provenance | X0 + typed source observations for $r$ and $q$ | X1 + branch evidence |
| **Information withheld** | Any source/target evaluation | Target evaluations ($J_Y, \theta_Y$) | Target evaluations ($J_Y, \theta_Y$) |
| **Strongest claim ceiling** | Geometry/support representation utility | Source-score-weighted representation utility | Branch-conditioned source-score utility |
| **Principal leakage/confound** | Reference policy bias | Source/target conflation | Overfitting to source branch depth |

X2 adds branch evidence but must not be assumed superior merely because it is richer.

## 3. Defining the Source Comparison Separately from Objective $V$

We introduce $O_X(r)$ and $O_X(q)$ as typed observations under $\hat{V}_{J_X, \theta_X}$.

We define a source comparison object abstractly:
$$C_X(P; r, q)$$
We do not assume it is a scalar. It preserves CP, mate, WDL, tie/order, perspective, and provenance exactly as typed.
- **No mate-to-CP coercion.**
- **No assertion that $C_X = C_V$.**

## 4. The Amplitude Problem and Magnitude Statuses

We explicitly separate three magnitude statuses:

**A. Unit mass**
$$a_X = 1$$
This is an admissible geometry/support experimental convention. It does not encode consequence magnitude.

**B. CP-only source-score magnitude**
For CP/CP source observations under one frozen perspective/instrument:
$$a_X^{CP} = |\Delta CP_X|$$
This is classified as a mathematically defined, instrument-conditioned, task-local source-score magnitude. It is **not** an objective consequence amplitude or universal Heat amplitude. It is admissible for a future CP-only source-score-weighted representation study, provided prospective CP-only evaluability semantics are required and no replacement/tuning occurs around mate cases. Do not call this production Heat.

**C. Universal cross-typed consequence amplitude**
CP/mate/WDL scalarization is **NOT IDENTIFIED / NOT EARNED**. No fake conversion is permitted.

## 5. Typed Multi-Channel Option

If we preserve CP, mate, and WDL/order as separate channels without scalarization, this defines a materially new vector-valued representation family:
$$M_\mu^{typed}$$
This is distinct from $M_\mu = a_X G_\mu$. It is materially new and must not be used to rescue the current scalar attribution design.

## 6. Target Object for $u=(P,r,q)$

The target candidate $Y_u$ is defined as the **pairwise typed ordering of $r$ versus $q$ under frozen $\hat{V}_{J_Y, \theta_Y}$**.
A full legal-move ranking at $P$ is not the direct target because $u=(P,r,q)$ natively frames a pairwise contrast. 

Abstractly:
$$Y_u = \text{CompareTyped}(O_Y(r), O_Y(q))$$
under one frozen perspective. 
There is no mate-to-CP scalar.
Handling semantics:
- CP/CP: Standard numerical ordering.
- Mate/Mate: Distance-to-mate ordering.
- CP/Mate: Mate always strictly dominates CP.
- Ties: Explicitly handled as equality/undecidable.
Any cases not covered must be explicitly declared as unordered. We do not invent missing semantics.

## 7. Audit of Source→Target Relationships

| Relationship | Independence Level | Producer Dependence | Genuinely Held Out | Principal Dependence/Confound | Strongest Claim Ceiling |
|---|---|---|---|---|---|
| **Deeper same producer** | Low | Absolute | Search depth increment | Horizon effects, search artifacts | Predicts deeper search behavior of same engine |
| **Independently configured same producer** | Low-Medium | Absolute | Different configuration / heuristic parameters | Shared core evaluation function | Predicts alternative configuration outcomes |
| **Different producer** | Medium-High | Shared | The entire target instrument | Cross-engine bias | Robustness across specific tested instruments |
| **Cross-producer replicated target** | High | Low | Consensus target | Ensemble bias / shared blindspots | Robustness against engine consensus |

*Do not say "instrument-independent" for finite same/different-engine agreement.*

## 8. Audit of Reference Policies ($r$)

| Reference Policy | Target Leakage Risk | Producer-Preference Dependence | Symmetry/Equivariance Implications | Stability Across $q$ | Scientific Interpretation of $C_X$ |
|---|---|---|---|---|---|
| **Fixed lexicographic** | None | None | Breaks permutation equivariance / arbitrary | High (fixed) | Arbitrary pair contrast |
| **Rule-only deterministic** | None | None | Needs complex rule to maintain symmetry | High (fixed) | Rule-based pair contrast |
| **Source-producer preferred** | None (if frozen from $X$) | Absolute | Privileges engine's top choice | High (if $r$ is $top_1$) | Consequence relative to best-play |
| **Externally frozen** | Depends on origin | Depends on origin | Depends on policy design | High (fixed) | Depends on policy |

A single fixed $r(P)$ across all $q$ at a root is strongly preferred for the proposed pairwise comparison family to ensure pairwise source contrasts remain comparable against a consistent baseline. 

*We do not choose a reference policy yet unless one is logically dominated.*

## 9. Representation Equivalence Audit

For the principal admissible source treatments:

**1. X0 + Unit Mass ($a_X = 1$)**
- $\sum_s M_\mu = a_X$ recovers the magnitude trivially (1).
- $P, r, q, \rho(q)$ plus the spatial support makes $\mu_D$ and $\mu_T$ effectively invertible/reconstructible.
- This represents different coordinate organization, not genuinely lossy differences. Both operators contain the same total information about the move geometry.

**2. X1 + CP-only source-score magnitude ($a_X^{CP} = |\Delta CP_X|$)**
- $\sum_s M_\mu = a_X^{CP}$ recovers the complete magnitude.
- $P, r, q, \rho(q)$ plus spatial support allows full reconstruction of the same scalar source signal.
- The two operators are effectively injective transforms of the same source variables.

Since these encodings are information-equivalent, **only inductive-bias/efficiency claims remain available**, not claims of capturing fundamentally different consequence information.

## 10. Matched-Control Implications

Candidate controls and what they establish/destroy:

- **Coordinate-scrambled spatial map:**
  - Destroys: Spatial semantics / geometric coherence.
  - Preserves: Total mass, sparsity, channel distributions.
  - Supports: Negative control for coordinate semantics / spatial inductive bias.
  - Cannot establish: That the control itself is "non-spatial".
- **Value multiset without square identity:**
  - Destroys: Coordinate identity and spatial location.
  - Preserves: The exact set of scalar values.
  - Supports: Utility of maintaining exact values vs structure.
  - Cannot establish: The utility of any spatial map if it matches this.
- **Non-spatial fixed-width source vector:**
  - Destroys: Spatial organization / board geometry mapping.
  - Preserves: Declared source variables.
  - Supports: Pure comparison of spatialization vs flattened encoding.
  - Cannot establish: Anything if constructed poorly to deliberately fail.
- **Rule-derived move encoding:**
  - Destroys: Source magnitude / evaluation signal (unless added).
  - Preserves: Move semantics.
  - Supports: Baseline geometry utility without consequence weighting.
  - Cannot establish: Consequence utility.

*$B_{\text{matched}}$ remains unchosen until the exact source variables entering $M_\mu$ are known.*

## 11. Source-Boundary Falsifiers

Reject a proposed boundary if:
- target $Y$ leaks into $X$
- reference $r$ depends on target $Y$
- $\mu$ cannot be instantiated from $X$ without hidden information
- a universal outcome scalar is invented without evidence
- mate is coerced into CP
- a geometry-only map is labeled consequence-weighted
- source and target instruments are conflated
- $q$'s target outcome is used during source construction

## 12. Conclusion

**SOURCE_ATTRIBUTION_MAGNITUDE_NOT_IDENTIFIED**

This means that a *universal consequence magnitude* is not identified, nor is a universal cross-typed amplitude. It does not deny the existence of admissible task-local quantities (like unit support or CP-only source-score differences), but those local quantities cannot be legitimately labeled as universal consequence-weighted "Heat". The fundamental blocker to the intended consequence-weighted architecture is the lack of an earned, universal experimental source magnitude that accommodates all outcome types without fake scalarization.
