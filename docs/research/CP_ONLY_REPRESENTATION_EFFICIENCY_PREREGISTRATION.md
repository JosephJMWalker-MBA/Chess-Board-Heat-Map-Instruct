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

## 3. Prediction Unit and Canonical Serialization

**Frozen Unit:**
$$u = (P, \{m, n\})$$
for distinct legal root alternatives.

**Canonical Serialization:**
$$c(\{m, n\}) = (m_1, m_2)$$
where $UCI(m_1) < UCI(m_2)$ under ordinary bytewise/lexicographic ordering of canonical UCI strings.
Serialization exists only for identity/orientation. It is **not** a scientific reference move.

## 4. Exact Root-Population Contract

The future root population must be defined independently of target $Y$. 
Currently: **ROOT_POPULATION_NOT_YET_FROZEN**
This is execution-blocking. We must prospectively define: root source, inclusion rule, exclusion rule, sufficient-position identity, duplicate handling, transposition/equivalent-state handling, variant, history semantics, development-data overlap policy, and manifest construction. Previously examined/tuned/frozen M8/T3 fixtures must not become untouched validation evidence merely by being copied.

Once acquired, report base roots, source-evaluable roots, roots with $\ge 2$ CP-typed legal alternatives, legal-move count distribution, CP-eligible move count distribution, and CP-pair count distribution with no target-based replacement.

## 5. Source and Target Acquisition Instrument Concept

Currently: **INSTRUMENT_CONFIG_NOT_YET_FROZEN**
This is execution-blocking. We must prospectively specify producer/version identity, comparison perspective, exact deterministic acquisition method for all legal alternatives, source budget type/value, target budget type/value, UCI/config settings, process lifecycle, hash reset semantics, threads, hash size, MultiPV/searchmoves behavior, and any randomness. Top-k acquisition is incompatible. The target must use a strictly greater independently acquired budget. Source and target observations must not inherit uncontrolled TT/search state from one another.

## 6. Source and Target Evaluability

**Source Pair Eligibility:**
A pair is source-evaluable only when: both alternatives are legal, have distinct UCI identities, both source observations are valid, both source observations are CP-typed, common frozen perspective is maintained, and provenance is valid. Mate/WDL/non-valid source cases are prospectively non-evaluable and must not be replaced.

**Target Labels:**
- `FIRST_BETTER`: $O_Y(m_1) > O_Y(m_2)$ under frozen CompareTyped semantics
- `EQUAL`: Perfect tie
- `SECOND_BETTER`: $O_Y(m_1) < O_Y(m_2)$ under frozen CompareTyped semantics

**Non-Evaluable Target Cases (retained in coverage accounting, no replacement):**
- `UNORDERED`: Target-non-evaluable mixed type (if applicable)
- `TARGET_ACQUISITION_FAILURE`: Evaluation could not be produced

If target attrition leaves a root with zero evaluable pairs, that root is excluded. Do not backfill another root.

## 7. Spatial Encodings

**Frozen Operations:**
$$D = \{to(m_1), to(m_2)\}$$ (deduplicated)
$$T = \{from(m_1), to(m_1), from(m_2), to(m_2)\}$$ (deduplicated)
$$a_X = |CP_X(m_1) - CP_X(m_2)|$$
$$d_X = \text{Compare}(CP_X(m_1), CP_X(m_2))$$

$$M_D(s) = \begin{cases} a_X / |D| & s \in D \\ 0 & \text{otherwise} \end{cases}$$

$$M_T(s) = \begin{cases} a_X / |T| & s \in T \\ 0 & \text{otherwise} \end{cases}$$
No tuning or normalization beyond these frozen operators.

## 8. Information-Equalized Interface and Controls

**Frozen Side Information:**
$$S^\star = (UCI(m_1), UCI(m_2))$$

Every spatial model receives the identical interface:
$$R(P, S^\star, d_X, a_X, M_\mu) \to Y$$
We explicitly supply $a_X$ to the spatial models so the representation is not rewarded merely for making amplitude easier to recover.

**Mandatory Non-Spatial Baseline ($B_{daS}$):**
$$B_{daS} = R(P, S^\star, d_X, a_X, M_0)$$
where $M_0$ is the exact null/zero spatial channel required to preserve the same learner input schema and parameterization.

**Raw Source Reference ($B_{raw}$):**
Includes $P, m_1/m_2 \text{ identities}, CP_X(m_1), CP_X(m_2), d_X, a_X, \rho$ under the same learner/resource procedure where schema permits. *Raw source is an information-rich diagnostic reference, not a guaranteed empirical-performance upper bound.*

**Matched Comparator:**
Currently: **MATCHED_COMPARATOR_NOT_YET_FROZEN**
We require exactly one simple same-pair rule-derived non-spatial representation that answers a distinct control question, receiving the exact same $P, S^\star, d_X, a_X$ and using the same learner/resource budget.

## 9. Representation of P

Currently: **P_REPRESENTATION_NOT_YET_FROZEN**
This must be frozen using only already-earned sufficient-state semantics (piece placement, side to move, castling rights, en-passant state, rule-50, history, variant). Do not silently reduce to piece-placement-only FEN.

## 10. Learner Family

Currently: **LEARNER_FAMILY_NOT_YET_FROZEN**
We must choose one deliberately modest learner family using identical architecture, parameterization, optimizer, regularization, initialization, batch construction, and stopping rule for $\mu_D, \mu_T, B_{daS}$, and the matched control (masking/zeroing input slots explicitly). No representation-specific tuning.

## 11. Pair Subsampling

We use **all** source-eligible pairs within selected training/evaluation roots. Every selected root contributes all prospectively source-eligible unordered CP/CP pairs. Root weighting handles mobility imbalance; post-hoc pair subsampling is explicitly rejected unless computational necessity is proven before target acquisition.

## 12. Split Construction and Learning Budgets

Currently: **SPLIT_AND_BUDGET_NOT_YET_FROZEN**
We must split by canonical root identity only using a deterministic, target-blind procedure. All pairs from one root remain in one partition. Training-root sample-efficiency subsets must be nested and shared across every representation/baseline. We must freeze a deterministic budget schedule as a function of final training-root count, tuning-root partition, and held-out test-root partition.

## 13. Prediction Loss and Root Aggregation

The learner predicts probabilities over `FIRST_BETTER`, `EQUAL`, `SECOND_BETTER`.
The loss is multiclass negative log likelihood.

For a held-out root $P_i$ with target-evaluable pair set $Q_i$:
$$L_{i,\mu}(n) = \frac{1}{|Q_i|} \sum_{u \in Q_i} - \log p_\mu(Y_u | u, n)$$
where $n$ is the number of unique training roots.

The root-weighted statistic across $N_{test}$ roots is:
$$U_\mu(n) = - \frac{1}{N_{test}} \sum_{i} L_{i,\mu}(n)$$
Thus: larger $U$ = better, every root has equal weight, and pairs are averaged within root.

## 14. Primary Sample-Efficiency Statistic

The primary statistic is the normalized trapezoidal area under the held-out root-weighted learning curve (AULC) across the frozen nested root-budget schedule.
The x-axis is linear $n$ (unique training roots).

The primary operator contrast is:
$$\Delta_{DT} = AULC_D - AULC_T$$

Also computed:
$$\Delta_{D0} = AULC_D - AULC_{B_{daS}}$$
$$\Delta_{T0} = AULC_T - AULC_{B_{daS}}$$

## 15. Randomness and Hyperparameter Policy

Currently: **SEED_SET_NOT_YET_FROZEN**
If stochastic, we must preregister fixed seed sets applied symmetrically across representations. No dropping bad seeds. Training seeds $\neq$ root-split identity. Hyperparameters must be identical across all representations (either fixed or a shared, preregistered tuning budget disjoint from test roots).

## 16. Inference and Outcome Classification

We use a prospectively frozen paired root bootstrap over held-out roots (treating roots, not seeds or pairs, as the sampling unit) to determine reliability.
Currently: **CONFIDENCE_LEVEL_NOT_YET_FROZEN**

**Outcome Logic:**
- `SUPPORT_muD`: $\mu_D$ reliably > $\mu_T$ AND $\mu_D$ reliably > $B_{daS}$
- `SUPPORT_muT`: $\mu_T$ reliably > $\mu_D$ AND $\mu_T$ reliably > $B_{daS}$
- `SPATIAL_EFFICIENCY_NO_OPERATOR_PREFERENCE`: spatial condition(s) reliably > $B_{daS}$ but $\mu_D$ vs $\mu_T$ not resolved
- `NO_SPATIAL_EFFICIENCY_ADVANTAGE`: no spatial condition earns improvement over $B_{daS}$
- `INCONCLUSIVE`: intervals/diagnostics do not support another scientific class
- `PROTOCOL_INVALID`: preregistered integrity/leakage/evaluability conditions fail

If no practical-effect margin exists, a zero superiority boundary is used (statistical resolution is sufficient for the scoped protocol-relative efficiency claim).

## 17. Essential Falsifiers and Protocol Invalidity

The spatial-efficiency thesis is not supported if: neither map beats $B_{daS}$, advantage exists at only one budget, ranking reverses materially across budgets, advantage disappears under paired seeds, result depends on pair weighting, or one encoding receives extra tuning capacity.

**PROTOCOL_INVALID** if:
- target leakage
- source/target instrument mismatch from frozen spec
- uncontrolled TT/process-state contamination
- root crosses train/tune/test partitions
- representation-specific tuning/resource differences
- malformed sufficient-position state
- corpus construction inconsistent with frozen rule
- software/provenance digest mismatch
- post-hoc replacement of non-evaluable cases

## 18. Provenance

Bound to: S0 semantic signature, ExperimentSpec v2, source/target instruments, manifest digest, split digest, operator version, learner/config digest, seed set, and software revision. Uses existing S1 semantics.

## 19. Status

**PREREGISTRATION_DRAFT_ONLY**
**ENGINE_EXECUTION_NOT_AUTHORIZED**
**MODEL_TRAINING_NOT_AUTHORIZED**

Remaining Execution Blockers:
- ROOT_POPULATION_NOT_YET_FROZEN
- INSTRUMENT_CONFIG_NOT_YET_FROZEN
- P_REPRESENTATION_NOT_YET_FROZEN
- LEARNER_FAMILY_NOT_YET_FROZEN
- MATCHED_COMPARATOR_NOT_YET_FROZEN
- SPLIT_AND_BUDGET_NOT_YET_FROZEN
- SEED_SET_NOT_YET_FROZEN
- CONFIDENCE_LEVEL_NOT_YET_FROZEN
