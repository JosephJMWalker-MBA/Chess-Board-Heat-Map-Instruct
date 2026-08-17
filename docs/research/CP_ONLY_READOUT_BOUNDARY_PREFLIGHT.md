# CP-Only Readout Boundary Preflight

## Central Question
What exact common information should the readout receive so that a comparison of $\mu_D$ and $\mu_T$ tests an explicitly declared representation property rather than accidental inequality of available chess information?

**Preserved Prediction Unit:**
Unordered legal-alternative pair:
$$u = (P, \{m, n\})$$
with deterministic canonical serialization $c(\{m, n\}) = (m_1, m_2)$ for label orientation only.

**Preserved Semantics:**
- $a_X = |CP_X(m_1) - CP_X(m_2)|$
- $d_X = \text{Compare}(CP_X(m_1), CP_X(m_2))$
- $M_\mu = a_X G_\mu$

## 1. Defining $\rho(\{m, n\})$ Explicitly

An encoding is not "neutral" merely because every operator receives it. It may eliminate the very information-preservation difference being tested.

Candidate encodings:
- **$\rho_0$ — Pair slot/orientation token only:** Exposes pair ordering (via canonical serialization), but no move identities, origins, destinations, or capture/promotion/castling semantics. Cannot reconstruct $D$ or $T$.
- **$\rho_1$ — Canonical UCI identities of $m_1$ and $m_2$:** Exposes move origins, destinations, and promotion identities. Exposes pair ordering. Sufficient to reconstruct $D$ and $T$.
- **$\rho_2$ — Rule-derived move forms without board state:** Exposes origins, destinations, and semantics (capture/promotion/castling). Exposes pair ordering. Sufficient to reconstruct $D$ and $T$.
- **$\rho_3$ — Full legal move identities plus declared move metadata:** Exposes everything in $\rho_2$ plus additional explicit semantics. Sufficient to reconstruct $D$ and $T$.

## 2. Smallest Sufficient Equivalence Boundary

We formally identify the sufficient side-information set $S^\star$ such that $M_{\mu_D} \leftrightarrow M_{\mu_T}$ conditional on $S^\star, a_X$.

- **$(m, n)$ alone:** Without $P$, context is missing, but UCI origins and destinations are known. Because $D$ is the set of destinations $\{dest(m), dest(n)\}$ and $T$ is $\{origin(m), dest(m), origin(n), dest(n)\}$, $(m, n)$ alone is sufficient to mathematically reconstruct $D$ and $T$.
- **$P$ alone:** Not sufficient. Knowing the root state does not identify the specific queried pair.
- **$P + \rho_0$:** Not sufficient. 
- **$P + \rho_1$:** Sufficient. $\rho_1$ gives the exact UCI moves, fully defining $D$ and $T$.
- **Canonical UCI pair ($\rho_1$):** Sufficient to define sets $D$ and $T$.
- **Full $S = (P, m, n)$:** Sufficient.

Therefore, $S^\star$ need only contain the canonical UCI move identities (or equivalently $\rho_1$ or $\rho_2$). We do not claim this is uniquely minimal without rigorous proof, but it is sufficient.

## 3. Two Scientifically Legitimate Estimands

**A. Representation-as-delivered**
Readout receives only a common minimal context plus $M_\mu$:
$$R(M_\mu, d_X, \rho_0 [, P]) \to Y$$
Differences here may legitimately include information retention, origin/destination preservation, coordinate organization, and inductive bias.
*Claim ceiling:* Utility of the complete delivered representation under the frozen interface. Under the frozen delivered interface, one encoding provides greater task utility and may preserve different task-relevant move information. "Useful" is target/protocol-relative, not inherent. Do not describe success as pure spatial-organization utility.

**B. Information-equalized organization**
Readout receives sufficient common side information $S^\star$:
$$R(M_\mu, S^\star, d_X, \rho_0 [, P]) \to Y$$
Both operators have equivalent underlying move information. Any remaining difference is scoped to:
- Learner inductive bias
- Sample efficiency
- Capacity efficiency
- Optimization behavior
- Robustness under constrained learner/resource class
*Claim ceiling:* Superior sample/capacity/robustness utility under the prospectively frozen learner regime. Never call this additional consequence information or universally superior representation.

## 4. Reassessing the Estimands for the First Protocol

- **Representation-as-delivered:**
  - *New scientific knowledge:* Minor. A $\mu_T$ win might simply teach us that the transition-touch map retains move origins while destination-only does not.
  - *Already known by construction:* $T$ structurally contains more coordinates and retains origin identity.
  - *Strongest confound:* Unequal information retention masquerading as spatial utility.
  - *Product relevance:* High (evaluates the token as actually used).
  - *Mathematical relevance to ChessHeat:* Low (confounds information with organization).

- **Information-equalized organization:**
  - *New scientific knowledge:* Given the identical underlying move information, does spatial organization make it easier to learn?
  - *Already known by construction:* The encodings are mathematically interconvertible.
  - *Strongest confound:* Constrained exclusively by learner class choice.
  - *Product relevance:* Validates the core thesis that specifically orienting information on a spatial board provides a useful geometric prior.
  - *Mathematical relevance to ChessHeat:* High.

Because representation-as-delivered could yield a win for $\mu_T$ merely because it exposes origins (an already known structural fact), the **Information-equalized organization estimand is scientifically preferable for the first protocol**.

## 5. Audit of Board-State Access ($P$)

Does the readout need $P$ to make claims about chess spatial organization meaningful?
- **No $P$:** The readout has no instance-specific root-board context. It can learn population-level coordinate regularities but cannot condition on the actual piece arrangement unless that information is supplied elsewhere. This measures *position-agnostic coordinate-pattern utility*.
- **$P$ supplied:** Provides full context. This measures *context-aware chess-spatial utility*.

Do not call no-$P$ evaluation full chess spatial understanding.

## 6. Primary Utility Notion

Since the encodings are conditionally interconvertible given $S^\star$, unconstrained asymptotic accuracy is not the primary target. We prefer **sample efficiency** as the first utility notion because it directly tests whether one coordinate organization supplies a more useful inductive bias under one prospectively frozen learner class while holding model capacity fixed.

## 7. Preserving Orientation Controls and Splitting Baselines

For orientation-aware studies, every representation must receive identical $d_X$. We explicitly note that $a_X$ is fully recoverable from $\sum_s M_\mu(s)$, so a map must not receive credit merely for transmitting it.

We split the orientation+magnitude baseline by estimand:
- **For representation-as-delivered:** $B_{da} = (d_X, a_X, \rho_0)$. Beating it establishes incremental utility of the complete delivered encoding beyond source orientation and magnitude. It does not isolate spatial organization, because $M_\mu$ may preserve additional move identity.
- **For information-equalized organization:** $B_{daS} = (d_X, a_X, S^\star, \rho_0)$ or an exactly equivalent non-spatial representation receiving the same information. A spatial encoding must not receive move identity internally while the comparator is denied it.

## 8. Defining the Raw-Information Comparator ($B_{raw}$)

$B_{raw}$ ($X_1$) is an information-rich source reference. Because $M_\mu$ is deterministically derived from source evidence:
$$I(Y; M_\mu) \le I(Y; B_{raw})$$
under the relevant conditioning variables.

However, **information ceiling $\neq$ empirical performance ceiling.** Under a finite learner/resource budget, a transformed representation may outperform raw evidence through inductive bias, compression, denoising, or easier optimization.

Empirical performance relative to $B_{raw}$ measures the accessibility of the available information under the prospectively frozen learner/resource regime. It does not test the truth of the data-processing inequality.

## 9. Matched Controls ($B_{matched}$)

We defer $B_{matched}$ until the exact model architecture is chosen, but candidate evaluations under the information-equalized boundary:
- **Same-pair non-spatial rule-derived encoding:** Appropriate (tests pure spatial organization vs rule semantics).
- **Flattened representation:** Appropriate (tests 2D spatial topology vs 1D vectors).
- **Coordinate-scrambled map:** Appropriate (tests specific board topology).
- **Value multiset without coordinate identity:** Appropriate.

## 10. Audit Pair/Root Weighting

Root-level train/tune/test separation is strictly preserved.

Because sample efficiency is the preferred first utility notion, evaluation should conceptually be **root-weighted**. Every root contributes equally to the loss/statistic, regardless of pair count $\binom{k}{2}$. Do not treat correlated pairs as independent replicates.

## 11. Deferring the Learner

An information-equalized result is necessarily learner-class-relative. The future learner family must satisfy:
- Identical architecture/class across encodings
- Identical parameter/resource budget
- Identical fitting procedure
- No operator-specific feature engineering
- Frozen selection/stopping rule

*We do not pick hyperparameters or train anything here.*

## 12. Go/No-Go Test

**Is there any readout boundary under which $\mu_D$ versus $\mu_T$ answers a scientifically useful question that cannot be reduced either to unequal information access or to an arbitrary learner choice?**

Yes. The *Information-equalized organization* estimand, combined with a *sample-efficiency* utility measure and a prospectively frozen learner class, provides a defensible, non-circular protocol to test pure spatial inductive bias without confounding it with unequal information access. 

## 13. Conclusion

**CURRENT_OPERATORS_ONLY_SUPPORT_CONSTRAINED_EFFICIENCY_TEST**

*(This means the strongest currently earned information-equalized comparison between the frozen operators is a learner/resource-constrained efficiency test. It does not prohibit differently scoped representation-as-delivered studies. Furthermore, sample efficiency operationalizes learner-relative representation efficiency under a frozen training procedure; it is not a direct observation of an intrinsic or universal inductive bias).*
