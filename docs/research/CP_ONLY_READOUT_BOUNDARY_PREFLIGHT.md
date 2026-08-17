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
$$R(M_\mu, d_X, \rho_0) \to Y$$
Differences here may legitimately include information retention, origin/destination preservation, coordinate organization, and inductive bias.
*Claim ceiling:* Utility of the complete delivered representation under the frozen interface. Do not describe success as pure spatial-organization utility.

**B. Information-equalized organization**
Readout receives sufficient common side information $S^\star$:
$$R(M_\mu, S^\star, d_X, \rho_0) \to Y$$
The operators are informationally interconvertible. Any remaining difference is scoped to:
- Learner inductive bias
- Sample efficiency
- Capacity efficiency
- Optimization behavior
- Robustness under constrained learner/resource class
*Claim ceiling:* Never call this additional consequence information.

## 4. Which Estimand is Relevant to ChessHeat?

- **Representation-as-delivered:**
  - *Scientific hypothesis:* Delivering destination/transition spatial maps natively alters the available consequence-related information.
  - *Strongest claim:* One operator inherently preserves more useful task-relevant information.
  - *Strongest non-claim:* Does not isolate purely spatial layout organization.
  - *Architecture relevance:* Validates the raw encoding output as a standalone consequence token.
  - *Dominant confound:* We are just measuring the fact that $T$ encodes origins and $D$ does not.

- **Information-equalized organization:**
  - *Scientific hypothesis:* Specific spatial organization of identical information improves learning efficiency or robustness.
  - *Strongest claim:* One spatial map structure is a more efficient/robust inductive bias for a specific learner class.
  - *Strongest non-claim:* Operators do not contain different total information.
  - *Architecture relevance:* Validates the geometric layout for downstream neural architectures.
  - *Dominant confound:* Results depend entirely on the chosen learner constraints.

*We do not yet choose one as the stronger first research question; both remain logically distinct and valid depending on the desired product goal.*

## 5. Audit of Board-State Access ($P$)

Does the readout need $P$ to make claims about chess spatial organization meaningful?
- **No $P$:** Square coordinates are merely spatial labels. The learner must infer board context entirely from the training distribution. This tests pure spatial coordinate geometry.
- **Sufficient $P$ only:** Provides full context. The learner evaluates the spatial map against the board state. This tests context-aware spatial organization.
- **$P$ + move identities:** Supplies everything. The learner receives substantial chess information independent of $M_\mu$. Tests constrained efficiency.

## 6. Preserving Orientation Controls

For orientation-aware studies, every representation must receive identical $d_X$.
We preserve:
- $B_d = (d_X, \rho)$
- $B_{da} = (d_X, a_X, \rho)$

**Explicit Note on $a_X$:**
$a_X$ is fully recoverable from $\sum_s M_\mu(s)$. Therefore, a spatial map must not receive credit merely for transmitting $a_X$. Performance must beat $B_{da}$ to claim any structural or spatial utility.

## 7. Defining the Raw-Information Comparator ($B_{raw}$)

$B_{raw}$ must be specified exactly. It receives:
- $P$: Yes (if the readout receives it)
- $m_1 / m_2$ identities: Yes
- $CP_X(m_1)$: Yes
- $CP_X(m_2)$: Yes
- $d_X$: Yes (derived)
- $a_X$: Yes (derived)
- $\rho$: Yes (derived)

*What it can/cannot establish:*
$B_{raw}$ acts as the theoretical ceiling for information content from the source instrument. Beating it is extremely unlikely and would imply the spatial map somehow filters noise or provides an exceptionally strong inductive bias. Failing to beat it merely confirms the data processing inequality.

## 8. Matched Controls ($B_{matched}$)

- **Same-pair non-spatial rule-derived encoding:** Appropriate for both.
- **Flattened representation:** Appropriate for both (tests pure spatial organization vs 1D vectors).
- **Coordinate-scrambled map:** Appropriate for both (tests spatial topology).
- **Value multiset without coordinate identity:** Appropriate for both (tests identity vs distribution).

*We do not finalize $B_{matched}$ until the readout boundary is decisively chosen.*

## 9. Audit Pair/Root Weighting

Root-level train/tune/test separation is preserved.

Future utility statistics must define their weighting:
- **Each pair weighted equally:** High-mobility roots dominate the evaluation. Tests overall pair discrimination.
- **Each root weighted equally:** Every root contributes $1/N$ to the loss/statistic regardless of pair count $\binom{k}{2}$. Tests root-position level generalization.

If the primary scientific unit is ultimately the root, root-weighted evaluation is strongly preferred. Do not choose merely based on which yields a stronger effect.

## 10. Deferring the Learner

If the information-equalized question is pursued (testing sample/capacity efficiency), the future learner family must satisfy:
- Identical architecture/class across encodings
- Identical parameter/resource budget
- Identical fitting procedure
- No operator-specific feature engineering
- Frozen selection/stopping rule

*We do not pick hyperparameters or train anything here.*

## 11. Go/No-Go Test

**Is there any readout boundary under which $\mu_D$ versus $\mu_T$ answers a scientifically useful question that cannot be reduced either to unequal information access or to an arbitrary learner choice?**

Yes. The *Information-equalized organization* estimand provides a scientifically useful question regarding sample efficiency, capacity efficiency, and robustness. Even though the operators are interconvertible, testing which one provides a superior inductive bias for standard neural architectures is highly relevant for spatial modeling. 

Alternatively, the *Representation-as-delivered* estimand with minimal $\rho_0$ tests the utility of the standalone spatial token, explicitly acknowledging that unequal information access (origin preservation) is *part of the tested utility*.

Both boundaries define scientifically useful, non-circular questions, provided their claim ceilings are strictly respected.

## 12. Conclusion

**READOUT_BOUNDARY_REQUIRES_UTILITY_ESTIMAND**

*(The choice of readout boundary fundamentally dictates whether the experiment tests representation-as-delivered utility or information-equalized inductive bias. The experiment cannot proceed until the project explicitly chooses which of these two distinct scientific questions to answer).*
