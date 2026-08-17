# CP-Only Attribution Utility Protocol Feasibility Preflight

## Central Question

Is there a non-circular, fair, preregistrable CP-only experiment capable of distinguishing representation utility of $\mu_D$ and $\mu_T$, or would the outcome be determined primarily by side-information, reference-policy, learner, or baseline choices?

This is a go/no-go protocol-feasibility audit. Do not design an experiment merely because CP-only execution is now semantically admissible.

We restrict this preflight prospectively to source comparisons where both source outcomes are CP-typed. Mate cases are non-evaluable by construction, not failures to replace with friendlier fixtures.

## 1. Do Not Assume a Fixed Reference is Required

We must compare two prediction-unit families before accepting a privileged reference policy as mandatory.

**A. Fixed-reference family**
$$u_r = (P, r(P), q)$$
with one reference move fixed across all $q$ at a root.

**B. Unordered-pair family**
$$u_{pair} = (P, \{m, n\})$$
for distinct legal alternatives $m, n$.

In the unordered-pair family, we introduce a deterministic canonical serialization:
$$c(\{m, n\}) = (m_1, m_2)$$
solely so orientation labels can be represented reproducibly.
*Canonical serialization $\neq$ scientific reference move.*

We define:
$$a_X^{CP} = |CP_X(m_1) - CP_X(m_2)|$$
$$d_X = \text{CompareTyped}(CP_X(m_1), CP_X(m_2))$$
The attribution maps remain comparison-order invariant.

## 2. Audit of Prediction-Unit Families

We compare the fixed-reference versus unordered-pair designs:

| Property | Fixed-reference ($u_r$) | Unordered-pair ($u_{pair}$) |
|---|---|---|
| **Arbitrary baseline dependence** | High (if lexicographic/rule) | None (evaluates all valid pairs symmetrically) |
| **Producer-preference dependence** | High (if best-move reference) | None (evaluates pairs symmetrically) |
| **Symmetry/Equivariance** | Breaks permutation equivariance depending on $r$ | Preserves unordered symmetry (canonical order is for labels only) |
| **CP/CP evaluability** | Empirically unknown before acquisition | All prospectively valid CP/CP pairs are evaluable |
| **Number/Dependence of units** | $|L(P)| - 1$ per root | $O(|L(P)|^2)$ per root |
| **Interpretation of estimand** | Target consequence *relative to $r$* | Pairwise consequence separation between alternatives |
| **Leakage risk** | Depends heavily on $r$'s origin | Zero leakage from a privileged reference choice |
| **Structural favoritism toward $\mu_D$ or $\mu_T$** | Requires audit (rule-only $r$ can induce systematic spatial distributions) | Requires audit (but avoids single-reference anchoring) |

Because unordered pairs provide a coherent pairwise separation estimand without privileging one move arbitrarily, a **REFERENCE_POLICY is not a fundamental requirement.** The unordered-pair family removes the reference-policy blocker.

## 3. Mandatory Root-Level Dependence

For unordered pairs, pairs sharing the same root state $P$ are statistically dependent.
Any future data split must operate strictly at the root-position level: **no pair from a held-out root may occur in training/tuning.**
Individual move-pairs are *not* independent observations.

## 4. Reassessing the Readout Boundary

The scientific meaning of the protocol changes drastically depending on whether full move identities are supplied to the readout.

Compare two interfaces:
**A. Minimal common interface:**
$$R(M_\mu, d_X, \rho(\{m, n\}))$$

**B. Sufficient move-identity interface:**
$$R(M_\mu, S, \rho(\{m, n\}))$$
where $S = (P, m, n)$.

- **With sufficient $S$:** $\mu_D$ and $\mu_T$ are conditionally interconvertible. Any measured difference can only concern learner, resource, or inductive-bias behavior.
- **Without sufficient $S$:** The operators may expose genuinely different move information (e.g., transition touches may leak origin identity when $\mu_D$ does not). A performance difference cannot automatically be called pure "spatial organization utility."

Because this boundary determines whether we are testing spatial organization or unequal information access, the **readout information boundary is the fundamental remaining blocker.**

## 5. Freezing the Utility Notion

We cannot select a primary utility question until the information boundary is settled.

If supplying $S$ makes asymptotic predictive accuracy trivial or equivalent for both operators, then unconstrained predictive accuracy is the wrong test. A sample-efficiency or capacity-efficiency question is only interpretable relative to a frozen learner/resource class. If withholding $S$ changes information content, then "orientation-withheld" tests missing orientation, not organizational utility.

## 6. Repairing Claim Ceilings

Claims must be strictly protocol-scoped rather than globally broad:
- **Success:** Superior utility *under the frozen target, learner, side-information, and resource regime*. Finite cross-instrument success establishes robustness *across the tested instruments*, not instrument-agnostic utility.
- **Failure:** Failing utility *under the frozen target, learner, side-information, and resource regime*. Failure under one protocol does not globally reject the attribution convention.

## 7. Repairing the CP-Only Population Statement

Forced-mate source cases are systematically excluded by CP-only filtering. Therefore, the CP/CP-evaluable population may differ systematically from the full legal-position population. Its empirical composition must be *measured* rather than assumed. Any eventual claim must be scoped exclusively to this CP/CP-evaluable population.

## 8. Baseline Implications

We preserve fundamental baselines under the same readout resource constraints:
- **Orientation-only:** $B_d = (d_X, \rho(\{m, n\}))$
- **Orientation + magnitude:** $B_{da} = (d_X, a_X, \rho(\{m, n\}))$
- **Raw source:** $B_{raw} = X_1$

However, $B_{\text{matched}}$ cannot be finalized until the readout side-information boundary and prediction-unit family are frozen. For an unordered-pair design, a rule-derived non-spatial representation of the same pair must be included as an especially important comparator.

## 9. Defining Source/Target Instrument Relationships

For completeness:
- **Same producer, deeper target budget:** (Predicts deeper search behavior of same engine).
- **Same producer, independently configured target:** (Predicts alternative configuration outcomes).
- **Different producer target:** (Robustness across specific tested instruments).

We do not call different-producer agreement "objective consequence".

## 10. Protocol-Identifiability Falsifiers

Reject the protocol family if:
- side-information choice determines the winner
- $B_{\text{matched}}$ cannot be defined without favoring an operator
- $d_X / a_X$ alone saturate $Y$
- unrestricted learner makes operators trivially equivalent
- CP-only filtering destroys the intended population
- source and target are too dependent to support the desired claim
- orientation-withheld performance mostly measures missing orientation

*(Negative feasibility is an acceptable result).*

## 11. Conclusion

**CP_ONLY_UTILITY_REQUIRES_READOUT_BOUNDARY**
