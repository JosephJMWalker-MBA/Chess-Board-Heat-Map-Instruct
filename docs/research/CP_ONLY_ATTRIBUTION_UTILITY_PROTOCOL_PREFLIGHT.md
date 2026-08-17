# CP-Only Attribution Utility Protocol Feasibility Preflight

## Central Question

Is there a non-circular, fair, preregistrable CP-only experiment capable of distinguishing representation utility of $\mu_D$ and $\mu_T$, or would the outcome be determined primarily by side-information, reference-policy, learner, or baseline choices?

This is a go/no-go protocol-feasibility audit. Do not design an experiment merely because CP-only execution is now semantically admissible.

**Preserved Semantics:**
- $a_X^{CP} = |CP_X(r) - CP_X(q)|$
- $d_X = \text{sign/order}(CP_X(r) - CP_X(q))$
- $M_\mu = a_X^{CP} G_\mu$
- $Y_u = \text{CompareTyped}(O_Y(r), O_Y(q))$

We restrict this preflight prospectively to source comparisons where both source outcomes are CP-typed. Mate cases are non-evaluable by construction, not failures to replace with friendlier fixtures.

## 1. Choosing the Primary Scientific Question

We evaluate possible primary questions (do not combine metrics):

- **A. Orientation-aware held-out discrimination:**
  - *Hypothesis:* Spatial organization provides superior target discrimination given identical source ordering.
  - *Constant:* Readout receives $d_X$.
  - *Teaches:* Whether the specific geometric mapping $G_\mu$ contains inductive/predictive utility for consequence.
  - *Confound:* $d_X$ may saturate $Y$, leaving little residual signal.
  - *Success justifies:* A specific spatial mapping as a useful consequence representation.
  - *Failure justifies:* Rejection of the specific spatial mapping for predictive utility.

- **B. Orientation-withheld held-out discrimination:**
  - *Hypothesis:* Representation/readout can recover target ordering without source preference.
  - *Constant:* Readout receives only $M_\mu, \rho(q)$.
  - *Teaches:* Whether $M_\mu$ leaks enough source orientation/origin info to recover the ordering.
  - *Confound:* Measures origin-information preservation / missing orientation rather than intended consequence utility.
  - *Success justifies:* The representation's capacity to leak/encode order.
  - *Failure justifies:* Nothing (it might just be effectively unoriented).

- **C. Sample-efficiency advantage:**
  - *Hypothesis:* Spatial maps allow faster learning of target consequence.
  - *Constant:* Performance ceiling.
  - *Teaches:* Inductive bias strength of the spatial coordinate system.
  - *Confound:* Overfitting or inappropriate learner selection.
  - *Success justifies:* Spatial organization as an efficient encoding.
  - *Failure justifies:* Spatial organization is no better than flattened vectors.

- **D. Readout-capacity/compute efficiency:**
  - *Hypothesis:* A smaller/simpler readout can achieve the same performance with spatial maps.
  - *Constant:* Performance ceiling, training data.
  - *Teaches:* Compression and task-relevant sufficiency.
  - *Confound:* Model architecture mismatch.
  - *Success justifies:* Spatial maps as computationally efficient representations.
  - *Failure justifies:* Spatial maps offer no readout efficiency.

- **E. Robustness/transfer:**
  - *Hypothesis:* Spatial representations transfer better across instruments.
  - *Constant:* Learner, training data.
  - *Teaches:* Instrument-agnostic utility of the spatial map.
  - *Confound:* Engine consensus bias.
  - *Success justifies:* Robustness.
  - *Failure justifies:* Instrument-specific overfitting.

**Chosen first protocol candidate:** *Not chosen yet.* We must resolve the confounds before selecting the primary question.

## 2. Orientation-Aware Interface

The orientation-aware task is:
$$R(M_\mu, d_X, \rho(q)) \to Y$$

*Advantage:* Every operator receives identical source ordering, focusing the experiment narrowly on spatial organization.
*Danger:* $d_X$ may already solve so much of $Y$ that little discriminative signal remains for $M_\mu$.

We require orientation-only and magnitude baselines:
- $R_d(d_X, \rho(q))$
- $R_{da}(d_X, a_X, \rho(q))$

Any claimed spatial utility must be evaluated relative to these baselines, so spatial maps are not rewarded merely for making the conserved magnitude recoverable.

## 3. Orientation-Withheld Interface

The orientation-withheld task is:
$$R(M_\mu, \rho(q)) \to Y$$

This primarily measures origin-information preservation or source-orientation recoverability rather than the intended consequence representation utility. Because those factors cannot be easily separated from the intended utility, **this task is unsuitable as the first spatial-utility protocol.**

## 4. Freezing Candidate Reference-Policy Semantics

One $r(P)$ must remain fixed across all $q$ at a root unless varying $r$ preserves the estimand.

- **Fixed lexicographic $r(P)$:**
  - *Target Leakage:* None
  - *Producer Dependence:* None
  - *Equivariance/Arbitrariness:* Arbitrary, breaks permutation equivariance.
  - *Evaluable CP/CP implications:* Random distribution of CP evaluability.
  - *Interpretation:* Arbitrary baseline contrast.
  - *Structural Favoritism:* None.

- **Rule-only deterministic $r(P)$:**
  - *Target Leakage:* None
  - *Producer Dependence:* None
  - *Equivariance/Arbitrariness:* May preserve symmetry depending on the rule.
  - *Evaluable CP/CP implications:* Depends on the rule.
  - *Interpretation:* Rule-based baseline contrast.
  - *Structural Favoritism:* None.

- **Source-producer preferred $r(P)$:**
  - *Target Leakage:* None (if frozen from $X$)
  - *Producer Dependence:* Absolute
  - *Equivariance/Arbitrariness:* Privileges engine top choice.
  - *Evaluable CP/CP implications:* High chance of CP-evaluability if top choice is CP.
  - *Interpretation:* Consequence relative to best-play expectation.
  - *Structural Favoritism:* May favor certain geometric responses implicitly.

*We choose no reference policy yet. It must be defensible before observing target outcomes.*

## 5. Freezing the Side-Information Ledger

We must explicitly declare what the readout receives. A representation must not receive externally what another must encode internally.

| Information | Minimal Common Side Info | Sufficient $S=(P, r, q)$ Side Info |
|---|---|---|
| $P$ | No | Yes |
| $r$ identity | No | Yes |
| $q$ identity | No | Yes |
| $\rho(q)$ | Yes | Yes |
| $d_X$ | Yes (Orientation-aware) | Yes (Orientation-aware) |
| $a_X$ explicitly | No | No (unless provided as baseline control) |
| $M_\mu$ | Yes | Yes |
| Absolute $CP_X(r)$ | No | No |
| Absolute $CP_X(q)$ | No | No |

**If supplying $S$ makes $\mu_D$ and $\mu_T$ deterministically interconvertible, an unrestricted learner will asymptotically erase their difference.** The remaining empirical distinction would only be inductive bias, sample efficiency, or capacity efficiency.

## 6. Defining Raw and Matched Baselines

We define minimum baselines under the same readout resource constraints:

- **Orientation-only:** $B_d = (d_X, \rho(q))$
- **Orientation + magnitude:** $B_{da} = (d_X, a_X, \rho(q))$
- **Raw source:** $B_{raw} = X_1$ (typed source observations for $r$ and $q$)

**Candidate $B_{\text{matched}}$ Encodings:**
- *Flattened move/source vector:* Controls for pure flattened encoding vs spatial organization.
- *Coordinate-scrambled spatial map:* Controls for the specific spatial coordinate geometry.
- *Value multiset without square identity:* Controls for the exact set of scalar values.
- *Rule-derived move representation with identical scalar source signal:* Controls for move semantics without spatial attribution.

*We do not select a deliberately weak baseline.*

## 7. Defining Source/Target Instrument Relationships

- **Same producer, deeper target budget:**
  - *Meaning of $Y$:* Deeper search consensus.
  - *Genuinely held out:* The search increment.
  - *Dependence:* Very High.
  - *Expected evaluability:* High.
  - *Strongest claim ceiling:* Predicts deeper search behavior.

- **Same producer, independently configured target:**
  - *Meaning of $Y$:* Alternative configuration outcome.
  - *Genuinely held out:* The heuristic parameter changes.
  - *Dependence:* High (shared core evaluation).
  - *Expected evaluability:* High.
  - *Strongest claim ceiling:* Predicts alternative configuration outcomes.

- **Different producer target:**
  - *Meaning of $Y$:* Cross-engine agreement.
  - *Genuinely held out:* The entire target instrument.
  - *Dependence:* Medium (shared biases).
  - *Expected evaluability:* Medium (different CP scales/horizons).
  - *Strongest claim ceiling:* Robustness across specific tested instruments (NOT objective consequence).

## 8. Prospective CP-Only Evaluability

A unit is source-evaluable iff before target outcome observation:
- $O_X(r)$ is CP typed
- $O_X(q)$ is CP typed
- source perspective matches
- source observation validity/provenance passes
- $r \neq q$

Target evaluability is completely separate. We do not replace non-evaluable mate/WDL cases after acquisition.

**Population Bias Concern:**
Filtering for CP-only cases systematically removes positions involving forced mates. These often include highly tactical, forcing, or imbalanced positions near game resolution. Any eventual claim must be strictly scoped to the CP/CP-evaluable population (typically mid-game maneuvers, strategic positioning, or balanced endgames).

## 9. Is $\mu_D$ vs $\mu_T$ a Useful Contest?

Because the operators are conditionally interconvertible given $S$, a sufficiently expressive fair learner may asymptotically erase their difference.
Therefore, an unconstrained predictive accuracy contest is scientifically weak.

The scientifically meaningful first test must target **sample efficiency**, **capacity efficiency**, or **robustness**, rather than unconstrained predictive accuracy. This must be reasoned through before selecting a learner.

## 10. Protocol-Identifiability Falsifiers

Reject the protocol family if:
- reference choice determines the winner
- side-information choice determines the winner
- $B_{\text{matched}}$ cannot be defined without favoring an operator
- $d_X / a_X$ alone saturate $Y$
- unrestricted learner makes operators trivially equivalent
- CP-only filtering destroys the intended population
- source and target are too dependent to support the desired claim
- orientation-withheld performance mostly measures missing orientation

*(Negative feasibility is an acceptable result).*

## 11. Conclusion

**CP_ONLY_UTILITY_REQUIRES_REFERENCE_POLICY**
