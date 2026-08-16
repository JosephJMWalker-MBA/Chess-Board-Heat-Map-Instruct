# Attribution Utility Semantics Preflight

## 1. Central Question

What exact source evidence, legal-alternative comparison, query encoding, representation, readout, baseline, and utility notion would make held-out legal-alternative discrimination a scientifically interpretable test of representation utility?

We preserve the following separation:
- $V = \text{unresolved ultimate consequence target}$
- $X = \text{frozen source/upstream evidence}$
- $\mu = \text{deterministic attribution representation}$
- $\rho(q) = \text{operator-neutral query encoding}$
- $Y = \text{held-out target under a separately declared target instrument}$

## 2. Defining the Prediction Unit

Because the existing attribution construction is comparison-based, we introduce an abstract prediction unit such as:
$$u = (P, r, q)$$
where:
- $P = \text{sufficient root position}$
- $r = \text{reference legal alternative}$
- $q = \text{query legal alternative}$

We require:
- $r \neq q$
- $r$ selection operator-blind
- $r$ selection target-$Y$-blind
- $q$ identity available without $q$'s held-out $Y$ label

*Analysis Point:* We must analyze whether a reference alternative is actually required by every candidate $\mu$.

## 3. Separating Source and Target Instruments

We introduce distinct notation for source and target evidence:
- $\hat{V}_{J_X, \theta_X}$ for any source evidence allowed inside $X$
- $\hat{V}_{J_Y, \theta_Y}$ for the held-out validation target $Y$

**What may $X$ know about $q$ before $Y(q)$ is observed?**
We distinguish possibilities such as:
- rule-only $q$ identity
- shallow/source-instrument evaluation of $q$
- source branch evidence
- source consequence contrast
- no outcome evidence for $q$

Do not silently call source observations objective $V$.

## 4. Preventing Target Leakage Through the Reference Rule

Candidate reference policies for analysis only:
- rule-only deterministic reference
- source-instrument preferred move
- fixed canonical/lexicographic legal alternative
- externally frozen reference policy

For each, we must ask:
- Does $r$ depend on $\mu$?
- Does $r$ depend on $Y$?
- Does $r$ encode producer preference?
- Would changing $r$ change the scientific meaning of the map?

Do not choose a reference merely because it improves performance.

## 5. Representation Information Boundary

For every candidate spatial operator, we conceptually specify:
$$M_\mu(u) = \mu(X; P, r, q)$$

We must record whether $M_\mu$ preserves or discards:
- supplied source magnitude/type
- origin identity
- destination identity
- reference/query identity
- board-state context
- branch identity
- relation/state context
- provenance

*(This is an information-boundary audit, not implementation design).*

## 6. Invertibility and Equivalence

We must ask whether, given $\rho(q)$, two candidate encodings are deterministically interconvertible or whether the upstream source magnitude can simply be recovered from $\sum_s M_\mu(s)$.

If $\mu_D$ and $\mu_T$ both conserve the same source amplitude and the query/reference identities reveal their support, an expressive readout may recover the same source signal from both. Therefore, any performance difference may reflect:
- inductive bias
- compression
- learner capacity
- sample efficiency
- coordinate organization

rather than different information content.

Do not call equivalent encodings scientifically different information sources.

## 7. Primary Utility Notion

Evaluate separately:
- held-out discrimination performance
- generalization/sample efficiency
- computational/readout efficiency
- robustness/transfer
- compression/task-relevant sufficiency

*(Do not combine them into one composite score).*

For each candidate utility notion state:
- what is held constant
- what resource budget matters
- what statistic family could represent it
- what confounds it
- what architectural decision success would justify

*No numerical threshold or final statistic yet.*

## 8. The Three Comparison Classes

**A. Raw Reference**
$$R_X(X, \rho(q))$$
This is the information-rich/raw-evidence reference. It is not guaranteed to be an empirical performance upper bound under finite learner/resource constraints.

**B. Spatial Encodings**
$$R_\mu(M_\mu, \rho(q))$$
Requires the same model family/procedure/resource budget across attribution operators.

**C. Matched Non-Spatial Encoding**
$$R_B(B_{\text{matched}}(X), \rho(q))$$
We must explain exactly what "matched" could legitimately mean.
We explicitly reject:
- matched dimensionality = matched information
- matched parameter count = matched semantic capacity
- matched compute = mathematical equivalence

## 9. Candidate Matched Controls

Without choosing one yet, useful controls might include:
- non-spatial fixed-width encoding of the same source variables
- coordinate-scrambled representation
- value multiset with square identity removed
- canonical feature vector with equal output dimension
- rule-derived non-spatial move representation

For each, we must state what property it destroys and what it accidentally preserves.
Reject a control if knowing its construction predetermines which operator should win.

## 10. The Target Ceiling

Leading $Y$: typed ordering of held-out legal alternatives under frozen $\hat{V}_{J_Y, \theta_Y}$. *(No universal mate/CP scalar conversion).*

**Success may potentially establish:**
Under the frozen source/target instruments, holdout scheme, representation, query encoding, learner, and resource budget, one encoding provides better declared representation utility for predicting held-out legal-alternative ordering than specified comparators.

**It cannot establish:**
- new information beyond $X$
- objective $V$
- objective spatial ownership
- causal square importance
- universal best attribution
- instrument independence

## 11. Falsifiers for the Representation-Utility Thesis

Examples:
- raw $X$ dominates spatial encodings without any compensating efficiency/compression benefit
- $\mu$ operators become equivalent under a sufficiently expressive fair readout
- apparent advantage disappears against $B_{\text{matched}}$
- advantage disappears on held-out roots
- advantage depends on operator-specific $\rho$ or $R$
- result reverses under an equally justified reference policy $r$

Treat negative outcomes as architectural evidence, not prompts to tune operators.

## 12. Conclusion

**UTILITY_TASK_REQUIRES_SOURCE_TARGET_BOUNDARY**

While the prediction unit $(P, r, q)$ and target family are promising, we cannot yet define a single primary utility notion or an uncontroversial $B_{\text{matched}}$. The exact boundary between source instrument $\hat{V}_{J_X, \theta_X}$ and target instrument $\hat{V}_{J_Y, \theta_Y}$ must be defined before we can evaluate whether spatialization offers generalization, compression, or inductive bias advantages over raw and matched non-spatial controls.
