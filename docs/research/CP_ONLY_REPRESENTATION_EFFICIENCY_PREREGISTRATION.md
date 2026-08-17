# CP-Only Representation Efficiency Preregistration

## 1. Scientific Question

**Primary Question:**
Under one frozen learner/training regime and equalized underlying move information, does destination-only spatial organization $\mu_D$ or transition-touch organization $\mu_T$ yield greater sample efficiency for predicting held-out target-instrument ordering of CP/CP-source legal-alternative pairs?

This is the strictly singular, only primary utility question. We do not add capacity efficiency or robustness as co-primary outcomes.

## 2. Claim Ceiling

**Maximum Positive Claim:**
Under the frozen source instrument, target instrument, data population, information boundary, learner class, training procedure, and root-budget schedule, one spatial encoding permits more sample-efficient prediction of held-out target ordering than the specified comparator.

**Explicit Non-Claims:**
- no objective square ownership
- no objective consequence $V$
- no universal Heat amplitude
- no additional information beyond $X$
- no universal superiority of one representation
- no causal square importance
- no instrument independence
- no human navigability claim

## 3. Prediction Unit

**Frozen Unit:**
$$u = (P, \{m, n\})$$
for distinct legal root alternatives.

**Canonical Serialization:**
$$c(\{m, n\}) = (m_1, m_2)$$
using one deterministic rule specified exactly prior to execution. Serialization exists only for identity/orientation. It is **not** a scientific reference move.

## 4. Source Eligibility

A pair is source-evaluable only when, under frozen $J_X, \theta_X$, both $O_X(m_1), O_X(m_2)$ are valid CP-typed observations from the same frozen comparison perspective.

**Definitions:**
$$a_X = |CP_X(m_1) - CP_X(m_2)|$$
$$d_X = \text{Compare}(CP_X(m_1), CP_X(m_2))$$

Mate/WDL/non-valid source cases are prospectively non-evaluable. They must **not** be replaced after acquisition.

## 5. Spatial Encodings

**Frozen Operations:**
$$D = \{to(m_1), to(m_2)\}$$ (deduplicated)
$$T = \{from(m_1), to(m_1), from(m_2), to(m_2)\}$$ (deduplicated)

$$M_D(s) = \begin{cases} a_X / |D| & s \in D \\ 0 & \text{otherwise} \end{cases}$$

$$M_T(s) = \begin{cases} a_X / |T| & s \in T \\ 0 & \text{otherwise} \end{cases}$$

No tuning or normalization beyond these frozen operators.

## 6. Information-Equalized Interface

**Frozen Side Information:**
$$S^\star = (UCI(m_1), UCI(m_2))$$

Every operator receives the identical context:
- $S^\star$
- $d_X$
- Board state $P$
- Plus its own spatial encoding $M_D$ or $M_T$.

**Rationale for $P$:**
The intended question concerns context-aware chess-spatial representation. Without $P$, the task measures position-agnostic coordinate regularities rather than use of spatial organization relative to the actual chess position. $P$ must preserve sufficient-state semantics required by S0. Its exact representation will be specified, but we do not invent a new learned chess ontology.

## 7. Mandatory Non-Spatial Controls

- **Orientation/magnitude/move-information baseline ($B_{daS}$):**
  $$B_{daS} = (d_X, a_X, S^\star, P)$$
  with no spatial map.

- **Raw source reference:**
  Includes $P, m_1/m_2 \text{ identities}, CP_X(m_1), CP_X(m_2), d_X, a_X, \rho$ under the same learner/resource procedure where schema permits. *Raw source is an information-rich reference, not a guaranteed empirical-performance upper bound.*

At least one matched non-spatial representation must also be frozen before execution. We prefer the simplest defensible same-pair rule-derived/non-spatial encoding. We do not add a large baseline zoo to the primary protocol.

## 8. Target

**Frozen Target Relationship:**
Same producer at a strictly greater independently acquired search budget (unless an existing project constraint makes that impossible).
*Rationale:* Isolates the representation question, avoids cross-producer scale/semantic differences in the first study, and preserves a clear held-out target.

**Exact Claim Ceiling:**
Prediction of deeper held-out behavior of the specified producer/configuration family. Never call this objective consequence.

**Acquisition Independence:**
Target observations are strictly unavailable during source eligibility, split construction, representation construction, and model/hyperparameter selection (except through the preregistered training partition).

## 9. Target Label

**Frozen Label:**
$$Y_u = \text{CompareTyped}(O_Y(m_1), O_Y(m_2))$$
Reusing the already established typed comparison semantics exactly.

**Prospectively Specified Exceptions:**
- EQUAL
- UNORDERED
- target acquisition failure
These will enter the analysis systematically. We do not invent mate-to-CP conversions.

## 10. Root is the Statistical Sampling Unit

A root with $k$ eligible alternatives produces up to $\binom{k}{2}$ dependent pairs.

**Frozen Constraints:**
- Train/tune/test split by root
- Sample-efficiency budget counted in unique training roots
- All reporting clustered/aggregated by root
- No pair-level pseudo-replication

We must prospectively define whether all eligible pairs from each selected training root are used, or whether a rule-only fixed pair-sampling procedure is used. The choice may not depend on target labels.

## 11. Sample-Efficiency Estimand

We do not use "best final accuracy" as the primary statistic.

**Learning Curve Definition:**
$$U_\mu(n)$$
where $n$ is the number of unique training roots.

The primary comparison must summarize performance across a preregistered root-budget schedule. We will choose one primary statistic (e.g., normalized area under the held-out root-weighted learning curve, or another justified monotonic sample-efficiency summary). We do not choose after observing results.
*(Direction: larger = more sample-efficient).*

## 12. Root-Weighted Evaluation

Every held-out root receives equal aggregate weight. We must prospectively define:
- pair-level predictions within root
- root-level aggregation rule
- across-root utility statistic

The root aggregation rule must be frozen before execution. We do not treat all pairs across all roots as independent observations.

## 13. Learner Family

We choose one deliberately modest learner family suitable for both $M_D$ and $M_T$.

**Requirements:**
- identical architecture
- identical parameter budget
- identical optimizer
- identical initialization policy
- identical regularization
- identical batch construction
- identical stopping rule
- identical model-selection procedure
- no operator-specific feature engineering

We must explain why the learner has enough capacity to use the representation but is bounded enough for sample-efficiency differences to remain observable. We do not optimize a separate architecture for each map.

## 14. Randomness and Replication

If learner training is stochastic, we preregister:
- fixed seed set
- same seed set for every representation/baseline
- paired comparison by seed
- no dropping bad seeds

Training stochasticity is not an independent chess sample; roots remain the primary sampling unit.

## 15. Hyperparameter Policy

We freeze either one common hyperparameter configuration, or one common preregistered tuning procedure/budget across all representations. We never provide an operator-specific tuning budget. Tuning roots must remain disjoint from test roots.

## 16. Essential Falsifiers

The spatial-efficiency thesis is not supported if:
- neither spatial map improves over $B_{daS}$
- apparent advantage exists only at one arbitrarily chosen training size
- ranking reverses materially across preregistered root budgets
- advantage disappears under paired seed analysis
- result depends on pair-level rather than root-level weighting
- one encoding receives extra information or tuning capacity
- source/target leakage is discovered

A tie/equivalence result is scientifically valid. Do not tune around failure.

## 17. Outcome Classification

Prospective classifications:
- `SUPPORT_muD`
- `SUPPORT_muT`
- `NO_SPATIAL_EFFICIENCY_ADVANTAGE`
- `INCONCLUSIVE`
- `PROTOCOL_INVALID`

We do not assign numerical thresholds unless scientifically justified in this preregistration. If unjustifiable now, we define the statistics and defer threshold freezing to an explicitly separate calibration step using zero target-test data.

## 18. Provenance

The future experiment is bound to:
- S0 semantic signature
- ExperimentSpec v2
- source instrument identity/configuration
- target instrument identity/configuration
- corpus/root manifest digest
- split digest
- representation/operator version
- learner/config digest
- seed set
- software revision

We use existing S1 artifact semantics and do not invent parallel provenance infrastructure.

## 19. No Execution

**PREREGISTRATION_DRAFT_ONLY**
**ENGINE_EXECUTION_NOT_AUTHORIZED**
**MODEL_TRAINING_NOT_AUTHORIZED**
