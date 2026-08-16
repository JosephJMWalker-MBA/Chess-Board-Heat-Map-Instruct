# Attribution Validation Target Preflight

## 1. Central Question
Which independent target $Y$ could compare spatial attribution operators for empirical utility without defining spatial ownership by construction?

We preserve the separation:
- $V = \text{ultimate consequence target}$
- $Y = \text{independent empirical validation target}$
- $\mu = \text{spatial attribution operator}$

A successful relationship between $\mu$ and $Y$ may establish predictive, robustness, or intervention utility. It must never be interpreted automatically as objective spatial ownership.

## 2. Independence Levels
We define an independence ladder for candidate targets:
- **Y0** — operator-derived target: invalid for comparative validation
- **Y1** — operator-independent but same-instrument target
- **Y2** — operator-independent held-out target
- **Y3** — independently produced/instrumented target
- **Y4** — cross-instrument / cross-producer replicated target

Higher levels are not automatically feasible or necessary, but the level must be explicitly identified.

## 3. Most Important Distinction
We explicitly separate:

**Does $\mu$ help predict $Y$?**

from:

**Does $Y$ prove $\mu$'s squares own consequence?**

The second does not follow from the first. We must prefer targets that do not already contain a square attribution if they can still discriminate operator utility. An attribution operator can predict magnitude or ordering of future legal consequence responses, robustness across perturbations, branch discrimination, or held-out intervention sensitivity without the target itself declaring where consequence lives.

## 4. Circularity Audit
A target must be explicitly rejected if:
- $\mu$ helps define $Y$
- $\mu$ selects the cases on which it is evaluated
- the same spatial rule defines both prediction and ground truth
- destination attribution is tested against a destination-defined target
- intervention ownership is tested only against interventions chosen by that ownership rule
- target labels are projections of the operator itself

A target may use chess rules or an independently frozen producer, but it must not inherit the tested attribution rule.

## 5. Candidate Target Families

### 1. Held-out legal-intervention response
- **Exact target subject:** Consequence change $V$ under held-out legal interventions.
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

### 2. Held-out legal-alternative consequence discrimination
- **Exact target subject:** Consequence ranking of unplayed legal alternatives.
- **How $Y$ is generated:** Evaluating unselected branch alternatives.
- **Independent of $\mu$:** Yes.
- **$\mu$ influences fixture/sample construction:** No.
- **Spatial or non-spatial:** Non-spatial (ranking).
- **Depends on $\hat{V}$ / engine:** Yes.
- **Producer/instrument dependence:** High.
- **Legal-state fidelity:** High.
- **Branch preservation:** High.
- **Leakage/circularity risk:** Low, provided alternatives are held out.
- **Policy/player dependence:** Moderate (dependent on root state).
- **Noise/confounding:** Horizon effects in unplayed branches.
- **Utility claim success could earn:** $\mu$ captures information relevant to discriminating alternative branches.
- **Success could NOT establish:** Objective spatial ownership.
- **Strongest falsifier:** Attribution assigns high mass to squares irrelevant to alternative branch evaluations.

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
- **Utility claim success could earn:** $\mu$ captures instrument-invariant consequence.
- **Success could NOT establish:** Objective ownership.
- **Strongest falsifier:** $\mu$ is highly sensitive to one instrument's specific search artifacts.

### 4. Future branch consequence prediction
- **Exact target subject:** Deep search or future trajectory outcomes.
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
- **Utility claim success could earn:** $\mu$ identifies regions that drive long-term consequence stability.
- **Success could NOT establish:** Objective ownership.
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
- **Leakage/circularity risk:** None.
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
- **Utility claim success could earn:** $\mu$ aligns with human navigational concepts.
- **Success could NOT establish:** Objective measurement of consequence (only measures human decodability).
- **Strongest falsifier:** $\mu$ wildly disagrees with grandmaster focus.

### 7. Minimal-sufficient perturbation targets
- **Exact target subject:** Minimal set of legal perturbations required to change $V$.
- **How $Y$ is generated:** Searching for minimal difference boards that flip evaluation.
- **Independent of $\mu$:** Yes.
- **$\mu$ influences fixture/sample construction:** No.
- **Spatial or non-spatial:** Spatial (implied by minimal set).
- **Depends on $\hat{V}$ / engine:** Yes.
- **Producer/instrument dependence:** High.
- **Legal-state fidelity:** High.
- **Branch preservation:** Reduced.
- **Leakage/circularity risk:** If the perturbation generation heavily biases destination logic.
- **Policy/player dependence:** Low.
- **Noise/confounding:** Multiple valid minimal sets existing.
- **Utility claim success could earn:** $\mu$ highlights necessary conditions for consequence.
- **Success could NOT establish:** Objective unique ownership (since minimal sets aren't unique).
- **Strongest falsifier:** $\mu$ ignores the provably minimal perturbation set.

## 6. Target Leakage Test

For every candidate $Y$, ask:

**Could I predict which operator wins merely from knowing how this target was constructed?**

If yes, the target is structurally biased and rejected for comparative validation.

## 7. Decision Relevance

If operator $\mu_1$ substantially and reproducibly outperforms $\mu_2$ on $Y$, what architectural decision would that justify?
- **Acceptable:** Prefer $\mu_1$ for a declared predictive/measurement purpose.
- **Not acceptable:** Conclude $\mu_1$ reveals objective square ownership.

## 8. Conclusion

**INDEPENDENT_VALIDATION_TARGET_READY_FOR_PROTOCOL_DESIGN**
