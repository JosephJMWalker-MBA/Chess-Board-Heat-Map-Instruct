# Attribution Validation Target Preflight

## 1. Central Question
Which independent target $Y$ could compare spatial attribution operators for empirical utility without defining spatial ownership by construction?

We preserve the separation:
- $V = \text{unresolved ultimate consequence target}$
- $Y = \text{independent empirical validation target}$
- $\mu = \text{spatial attribution operator}$

We add the comparative structure variables:
- $X = \text{frozen upstream evidence available before } Y$
- $\rho = \text{frozen operator-neutral query encoding}$
- $R = \text{frozen operator-neutral readout/prediction rule}$
- $B_{\text{raw}} = \text{raw-evidence reference predictor}$
- $B_{\text{matched}} = \text{matched non-spatial representation baseline}$

The comparative utility question is not merely:
**Does $\mu$ correlate with $Y$?**

It is:
**Does $R(\mu(X), \rho(q))$ predict held-out $Y$ better than comparators, $B_{\text{matched}}$, and $B_{\text{raw}}$ under declared constraints?**
(where $q$ is the held-out query/alternative when needed).

## 2. The Deterministic Representation Boundary

Let $M_\mu = \mu(X)$.

Because the tested attribution operators are deterministic functions of the frozen upstream evidence, $X \to M_\mu$ is a deterministic transformation.

Therefore, for held-out target $Y$ and an independently supplied query representation $q$, by the data-processing inequality:
$$I(Y; M_\mu, q) \le I(Y; X, q)$$

**Spatial attribution cannot create information about $Y$ that was not already present in $X$.**

This is a mathematical boundary, not an empirical hypothesis. An attribution operator cannot earn a claim of "incremental information beyond $X$" when the comparator receives full $X$.

## 3. Information vs. Representation Utility

We must explicitly distinguish:
**Information gain $\neq$ representation utility.**

A spatial representation may provide better:
- predictive performance
- generalization under held-out data
- sample efficiency
- computational/readout efficiency
- robustness/transfer
- compression or task-relevant sufficiency

A spatial representation may improve one or more of these under a frozen comparison even though it cannot increase $I(Y; X)$.

## 4. Dual Baselines

Instead of a single baseline, we require two conceptually distinct controls.

**$B_{\text{raw}}$** is a predictor receiving the full upstream evidence $X$ plus the same operator-neutral query representation $\rho(q)$.
Its purpose is to ask: How much task performance is lost or gained by passing through the spatial representation under the declared learner/resource constraints? Do not call $\mu$'s advantage over this baseline "additional information."

**$B_{\text{matched}}$** is a non-spatial lossy representation of $X$ under a preregistered matched representation/resource budget. Matching may later involve things such as output dimensionality/schema, readout model class/capacity, training sample count, optimization budget, or compute budget. (Do not pretend these constitute equal Shannon-information content).
Its purpose is to ask whether spatialization is a useful representation relative to another constrained encoding.

## 5. Readout Independence Audit

Target independence ($Y$ independent of $\mu$) is necessary but insufficient. The prediction/readout rule $R$ must not encode the tested ownership semantics.

The comparison becomes conceptually: $R(M_\mu, \rho(q)) \to Y$.
We require every attribution operator to receive the identical query encoding.

Reject designs where:
- destination-specific $q$ encoding is used for $\mu_D$
- transition-footprint-specific $q$ encoding is used for $\mu_T$
- each operator gets custom feature engineering or prediction head/capacity
- operator identity determines which squares/features the scorer examines
- $R$ is chosen after seeing $Y$ performance

A fair comparison requires either:
- one fixed deterministic $R$
- separately fitted instances of the same preregistered model class with identical capacity, training data, optimization budget, stopping rule, and selection procedure. (Learned parameter values may differ; the learning procedure and resource budget may not).

Do not choose the production $R$ or $\rho$ yet.

## 6. Leakage Model

We separate leakage types:
- target leakage
- sample-selection leakage
- readout leakage
- upstream-information leakage
- hyperparameter/model-selection leakage

Require:
- fixture/sample construction frozen without $\mu$
- $Y$ branches unavailable to $\mu$ instantiation
- $R$ frozen without held-out outcomes
- same tuning budget across operators
- no choosing the winning target after comparing operators

“Unselected alternative” is not automatically “held out.” Define held out relative to all of:
- $\mu$ construction/instantiation
- $R$ fitting
- operator selection
- threshold/model selection
- fixture selection

## 7. Independence Levels
We define an independence ladder for candidate targets:
- **Y0** — operator-derived target: invalid for comparative validation
- **Y1** — operator-independent but same-instrument target
- **Y2** — operator-independent held-out target
- **Y3** — independently produced/instrumented target
- **Y4** — cross-instrument / cross-producer replicated target

Higher levels are not automatically feasible or necessary, but the level must be explicitly identified.

## 8. Candidate Target Families

*(Note: Target notation uses $Y_{J, \theta}$ or $\hat{V}_{J, \theta}$ where generated by an instrument, not the unearned ultimate consequence $V$. No universal CP/mate/WDL scalar conversion is assumed.)*

### 1. Held-out legal-alternative consequence discrimination
- **Exact target subject:** Typed ordering of held-out legal alternatives under frozen $\hat{V}_{J_Y, \theta_Y}$.
- **How $Y$ is generated:** Evaluating unselected branch alternatives.
- **Independent of $\mu$:** Conditional (Yes, if branch alternatives and labels are frozen independently of $\mu$, and $\mu$ does not use those branch outcomes).
- **$\mu$ influences fixture/sample construction:** Conditional (fixture selection must be $\mu$-blind).
- **Spatial or non-spatial:** Non-spatial (ranking).
- **Depends on $\hat{V}$ / engine:** Yes.
- **Producer/instrument dependence:** High.
- **Legal-state fidelity:** High.
- **Branch preservation:** High.
- **Leakage/circularity risk:** Conditional (Low only if alternatives are strictly held out, $R$ is operator-neutral, and tuning/model selection is performed without held-out labels).
- **Policy/player dependence:** Moderate (dependent on root state).
- **Noise/confounding:** Horizon effects in unplayed branches.
- **Utility claim success could earn:** Under frozen target instrument $J_Y, \theta_Y$, attribution operator $\mu$, evaluated through a common preregistered query encoding/readout procedure, may earn superior held-out discrimination performance, generalization, efficiency, or robustness relative to specified attribution comparators and declared raw/matched baselines.
- **Success could NOT establish:** New information beyond $X$, objective spatial ownership, objective $V$, causal square importance, or instrument independence (unless separately established).
- **Strongest falsifier:** Under the preregistered utility statistic and resource budget, the attribution representation fails to outperform the specified comparator required by the claim, or its apparent advantage fails held-out/replication controls.

### 2. Held-out legal-intervention response
- **Exact target subject:** Typed change/order under frozen $\hat{V}_{J_Y, \theta_Y}$ for held-out legal interventions.
- **How $Y$ is generated:** Evaluating perturbations not used to construct $\mu$.
- **Independent of $\mu$:** Yes, if intervention set is uncoupled from $\mu$.
- **$\mu$ influences fixture/sample construction:** No, must be independently sampled.
- **Spatial or non-spatial:** Non-spatial (consequence delta).
- **Depends on $\hat{V}$ / engine:** Yes.
- **Producer/instrument dependence:** High.
- **Legal-state fidelity:** High (if interventions are legal).
- **Branch preservation:** Low (compares new branches).
- **Leakage/circularity risk:** If $\mu$ intervention model overlaps with evaluation intervention model.
- **Policy/player dependence:** Depends on sampling.
- **Noise/confounding:** Engine search instability on perturbed boards.
- **Utility claim success could earn:** $\mu$ predicts out-of-sample intervention sensitivity.
- **Success could NOT establish:** Objective ownership of those squares.
- **Strongest falsifier:** $\mu$ fails to predict which interventions actually perturb evaluation.

### 3. Cross-instrument consequence agreement
- **Exact target subject:** Agreement between multiple engines/evaluators (e.g., Stockfish vs LC0).
- **How $Y$ is generated:** Running a secondary producer on the same positions.
- **Independent of $\mu$:** Yes.
- **$\mu$ influences fixture/sample construction:** No.
- **Spatial or non-spatial:** Non-spatial (evaluation vectors).
- **Depends on $\hat{V}$ / engine:** Yes, relies on multiple $\hat{V}$.
- **Producer/instrument dependence:** Reduced (cross-producer).
- **Legal-state fidelity:** High.
- **Branch preservation:** High.
- **Leakage/circularity risk:** Low.
- **Policy/player dependence:** Low.
- **Noise/confounding:** Engine idiosyncrasies cancelling out.
- **Utility claim success could earn:** $\mu$ exhibits predictive/measurement robustness across the specifically tested instruments.
- **Success could NOT establish:** Objective ownership or universal instrument invariance (finite agreement $\neq$ invariance).
- **Strongest falsifier:** $\mu$ is highly sensitive to one instrument's specific search artifacts.

### 4. Future branch consequence prediction
- **Exact target subject:** Deep search or future trajectory outcomes ($\hat{V}_{J_Y, \theta_Y}$).
- **How $Y$ is generated:** Extending search depth or playing out lines.
- **Independent of $\mu$:** Yes.
- **$\mu$ influences fixture/sample construction:** No.
- **Spatial or non-spatial:** Non-spatial.
- **Depends on $\hat{V}$ / engine:** Yes.
- **Producer/instrument dependence:** High.
- **Legal-state fidelity:** High.
- **Branch preservation:** Preserved.
- **Leakage/circularity risk:** If $\mu$ relies on shallow search artifacts predicting deep search artifacts.
- **Policy/player dependence:** High.
- **Noise/confounding:** Search tree explosion.
- **Utility claim success could earn:** Spatial attribution is predictive of later/deeper consequence estimates.
- **Success could NOT establish:** Objective ownership (cannot establish causal drivers without an independent causal mechanism).
- **Strongest falsifier:** $\mu$ fails to correlate with deepened consequence changes.

### 5. Actual-game outcome / realized continuation targets
- **Exact target subject:** Empirical win/loss/draw in human or engine databases.
- **How $Y$ is generated:** Database lookup of realized outcomes.
- **Independent of $\mu$:** Yes.
- **$\mu$ influences fixture/sample construction:** No.
- **Spatial or non-spatial:** Non-spatial.
- **Depends on $\hat{V}$ / engine:** No (pure empirical).
- **Producer/instrument dependence:** None.
- **Legal-state fidelity:** Absolute.
- **Branch preservation:** Fixed to played branch.
- **Leakage/circularity risk:** Low ownership circularity, but fixture-selection, duplicate-position, population, and temporal leakage remain possible.
- **Policy/player dependence:** Very High (contingent on specific player populations).
- **Noise/confounding:** Confounding from player skill and mismatched policies.
- **Utility claim success could earn:** $\mu$ predicts practical outcomes.
- **Success could NOT establish:** Objective ownership or pure engine/objective consequence.
- **Strongest falsifier:** Attribution fails to correlate with actual win probabilities.

### 6. Human expert spatial annotations
- **Exact target subject:** Squares identified by strong human players as critical.
- **How $Y$ is generated:** Expert labeling.
- **Independent of $\mu$:** Yes.
- **$\mu$ influences fixture/sample construction:** No.
- **Spatial or non-spatial:** Spatial.
- **Depends on $\hat{V}$ / engine:** No.
- **Producer/instrument dependence:** None.
- **Legal-state fidelity:** High.
- **Branch preservation:** Varies.
- **Leakage/circularity risk:** High, if $\mu$ (e.g. destination ownership) is implicitly preferred by human cognition.
- **Policy/player dependence:** Absolute.
- **Noise/confounding:** Human cognitive biases.
- **Utility claim success could earn:** $\mu$ aligns with human expert spatial judgments.
- **Success could NOT establish:** Objective measurement of consequence (nor "human decodability" without a decoding protocol).
- **Strongest falsifier:** $\mu$ wildly disagrees with grandmaster focus.

### 7. Minimal-sufficient perturbation targets
- **Exact target subject:** Minimal set of legal perturbations required to change $\hat{V}_{J_Y, \theta_Y}$.
- **How $Y$ is generated:** Searching for difference boards that flip evaluation.
- **Independent of $\mu$:** Yes.
- **$\mu$ influences fixture/sample construction:** No.
- **Spatial or non-spatial:** Spatial (implied by set).
- **Depends on $\hat{V}$ / engine:** Yes.
- **Producer/instrument dependence:** High.
- **Legal-state fidelity:** High.
- **Branch preservation:** Reduced.
- **Leakage/circularity risk:** If the perturbation generation heavily biases destination logic.
- **Policy/player dependence:** Low.
- **Noise/confounding:** Multiple valid minimal sets existing.
- **Utility claim success could earn:** $\mu$ highlights necessary conditions for consequence.
- **Success could NOT establish:** Objective unique ownership (since minimal sets aren't unique).
- **Strongest falsifier:** $\mu$ ignores the provably minimal perturbation set (if global minimality is guaranteed by protocol).

## 9. Three-Way Comparison Ledger

Future protocol design must distinguish:

**A. Raw-evidence reference**
$R_X(X, \rho(q))$
- $\mu$ vs raw $X$ establishes: predictive retention / inductive-bias or efficiency behavior, not information creation.

**B. Spatial representations**
$R_\mu(\mu(X), \rho(q))$ for each frozen attribution operator.
- $\mu_1$ vs $\mu_2$ establishes: relative utility of attribution conventions under matched procedure.

**C. Matched non-spatial representations**
$R_B(B_{\text{matched}}(X), \rho(q))$
- $\mu$ vs $B_{\text{matched}}$ establishes: utility of spatial organization versus a declared matched non-spatial representation.

## 10. Protocol-Readiness Gate

A target family is ready for protocol design only when all are conceptually specified:
- $X$
- frozen $\mu$ comparators
- $\rho(q)$
- $R$ / fitting procedure
- $B_{\text{raw}}$
- $B_{\text{matched}}$
- $Y$ semantics
- holdout boundary
- utility dimension/statistic
- resource budget
- leakage controls
- claim ceiling

Do not define numerical thresholds yet.

## 11. Conclusion

**VALIDATION_COMPARISON_REQUIRES_UTILITY_SEMANTICS_FIRST**

A promising non-spatial Y2 candidate family has been identified (held-out legal-alternative consequence discrimination), but a deterministic spatial attribution cannot add information beyond its upstream evidence. Before protocol design, ChessHeat must define which representation utility is being tested, together with the query encoding, readout procedure, raw-evidence reference, and matched non-spatial comparator.

## 12. Next Planning Question

Which utility notion, upstream boundary $X$, operator-neutral query encoding $\rho$, readout procedure $R$, raw reference $B_{\text{raw}}$, and matched non-spatial representation $B_{\text{matched}}$ would make held-out legal-alternative discrimination a fair representation-utility test?
