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
| **Can CP-only scalar $M_{\mu_D}$ be instantiated?** | No | Yes (on prospectively CP/CP-eligible source comparisons) | Yes (on prospectively CP/CP-eligible source comparisons) |
| **Can universal all-outcome scalar $M_{\mu_D}$ be instantiated?** | No | NO / NOT IDENTIFIED | NO / NOT IDENTIFIED |
| **Can CP-only scalar $M_{\mu_T}$ be instantiated?** | No | Yes (on prospectively CP/CP-eligible source comparisons) | Yes (on prospectively CP/CP-eligible source comparisons) |
| **Can universal all-outcome scalar $M_{\mu_T}$ be instantiated?** | No | NO / NOT IDENTIFIED | NO / NOT IDENTIFIED |
| **Can typed multichannel be instantiated?** | No | Only through separate $M_\mu^{typed}$ family | Only through separate $M_\mu^{typed}$ family |
| **$q$ source outcome known?** | No | Yes (under $J_X, \theta_X$) | Yes |
| **Target $Y$ outcome withheld?** | Yes | Yes | Yes |
| **Producer dependence** | None | Source instrument ($J_X$) | Source instrument ($J_X$) |
| **Information entering representation** | Move/state geometry, provenance | X0 + typed source observations for $r$ and $q$ | X1 + branch evidence |
| **Information withheld** | Any source/target evaluation | Target evaluations ($J_Y, \theta_Y$) | Target evaluations ($J_Y, \theta_Y$) |
| **Strongest claim ceiling** | Geometry/support representation utility | Source-score-weighted representation utility | Branch-conditioned source-score utility |
| **Principal leakage/confound** | Reference policy bias | Source/target conflation | Overfitting to source branch depth |

X2 adds branch evidence but must not be assumed to solve amplitude or be superior merely because it is richer.

## 3. Defining the Source Comparison Separately from Objective $V$

We introduce $O_X(r)$ and $O_X(q)$ as typed observations under $\hat{V}_{J_X, \theta_X}$.

We define a source comparison object abstractly:
$$C_X(P; r, q)$$
We do not assume it is a scalar. It preserves CP, mate, WDL, tie/order, perspective, and provenance exactly as typed.
- **No mate-to-CP coercion.**
- **No assertion that $C_X = C_V$.**

## 4. The Amplitude Problem and Magnitude Statuses

We explicitly separate three magnitude statuses:

**A. Unit mass ($a_X = 1$)**
This is an admissible geometry/support experimental convention. It does not encode consequence magnitude.

**B. CP-only source-score magnitude ($a_X^{CP} = |\Delta CP_X|$)**
For CP/CP source observations under one frozen perspective/instrument. This is classified as a mathematically defined, instrument-conditioned, task-local source-score magnitude. It is **not** an objective consequence amplitude or universal Heat amplitude. It is admissible for a future CP-only source-score-weighted representation study, provided prospective CP-only evaluability semantics are required and no replacement/tuning occurs around mate cases. Do not call this production Heat.

**C. Universal cross-typed consequence amplitude**
CP/mate/WDL scalarization is **NOT IDENTIFIED / NOT EARNED**. No fake conversion is permitted. 

**Architectural / Protocol Distinction:**
The lack of a universal amplitude blocks promotion to a universal scalar consequence-weighted Heat architecture. It does not, by itself, prohibit a narrowly scoped CP-only representation-utility experiment or a geometry/support experiment, provided their claim ceilings are frozen accordingly. *(No experiments are authorized here).*

## 5. Typed Multi-Channel Option

If we preserve CP, mate, and WDL/order as separate channels without scalarization, this defines a materially separate vector-valued representation family:
$$M_\mu^{typed}$$
This is distinct from $M_\mu = a_X G_\mu$. It is materially new and must not be used to rescue the current scalar attribution design.

## 6. Target Object for $u=(P,r,q)$

The target candidate $Y_u$ is defined as the **pairwise typed ordering of $r$ versus $q$ under frozen $\hat{V}_{J_Y, \theta_Y}$**.
Abstractly:
$$Y_u = \text{CompareTyped}(O_Y(r), O_Y(q))$$
All outcomes are evaluated from one explicitly frozen comparison perspective. There is no mate-to-CP conversion.

Mate signs are defined explicitly:
- $+Mate(k)$: frozen perspective can force mate in $k$
- $-Mate(k)$: frozen perspective is forced to be mated in $k$

**Handling Semantics:**
- **CP vs. CP:** $CP_1 > CP_2$ iff the numerical CP score is greater from the frozen perspective.
- **Mate vs. CP:** $+Mate(k) > CP > -Mate(j)$ for every finite CP score.
- **Winning Mate vs. Winning Mate:** $+Mate(k) > +Mate(j) \iff k < j$.
- **Losing Mate vs. Losing Mate:** $-Mate(k) > -Mate(j) \iff k > j$. (A later forced loss is preferable to an earlier forced loss from the same frozen perspective).
- **Opposite-sign Mate vs. Mate:** Order by sign.

We explicitly separate equality from undecidable cases:
- **EQUAL:** Outcomes perfectly tie.
- **UNORDERED / NOT DEFINED BY CURRENT TYPED COMPARATOR:** Cases where the comparator lacks semantics (e.g., WDL/mixed-type cases are explicitly declared unordered for this preflight). Do not scalarize WDL into CP or mate.

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

## 9. Representation Equivalence and Readout Boundary

Let the minimal required side information be $S = (P, r, q)$.

Given $S$ and the conserved scalar source magnitude $a_X$, the destination and transition-touch representations are deterministic encodings of the same underlying source comparison, because $S$ determines their respective supports and $\sum_s M_\mu(s) = a_X$. Therefore, they are **conditionally interconvertible given $S$**. We do not claim unconditional information equivalence.

**Operational Readout Boundary:**
We distinguish:
$$R(M_\mu, \rho(q))$$
from:
$$R(M_\mu, S, \rho(q))$$

We must ask whether the future fair readout receives $P$, $r$ identity, $q$ identity, or full move origins/destinations beyond what is encoded in $M_\mu$ and $\rho(q)$. Conditional interconvertibility under $S$ does not imply equivalence at a readout interface that withholds some or all of $S$. In particular, transition-touch support may preserve origin information absent from destination-only support if that information is not independently supplied.

Therefore, the audit concludes conditional equivalence, but operational readout equivalence remains unresolved until the readout information boundary is frozen.

## 10. Matched-Control Implications

Matched-control design depends not only on $X$ but also on which side information $S$ the readout receives. A comparator must not receive origin/reference information that one spatial representation has to preserve internally while another gets it for free externally.

Candidate controls and what they establish/destroy:
- **Coordinate-scrambled spatial map:** Destroys spatial semantics; preserves total mass, sparsity, channel distributions. Supports negative control for coordinate semantics/spatial inductive bias. Cannot establish that the control itself is "non-spatial".
- **Value multiset without square identity:** Destroys coordinate identity; preserves exact scalar values. Supports utility of maintaining exact values vs structure. Cannot establish utility of any spatial map if it matches this.
- **Non-spatial fixed-width source vector:** Destroys spatial organization; preserves declared source variables. Supports pure comparison of spatialization vs flattened encoding. Cannot establish anything if constructed poorly to fail.
- **Rule-derived move encoding:** Destroys source evaluation signal; preserves move semantics. Supports baseline geometry utility without consequence weighting. Cannot establish consequence utility.

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
*(The universal cross-typed scalar consequence magnitude required by the intended all-outcome consequence-weighted architecture is not identified. We explicitly preserve $a_X = 1$ as an admissible geometry/support convention, $|\Delta CP_X|$ as an admissible task-local, instrument-conditioned CP-only source-score magnitude, and $M_\mu^{typed}$ as a materially separate vector-valued representation family).*

**CONDITIONAL_INFORMATION_EQUIVALENCE_GIVEN_MOVE_IDENTITY**

**OPERATIONAL_READOUT_EQUIVALENCE_NOT_YET_IDENTIFIED**
