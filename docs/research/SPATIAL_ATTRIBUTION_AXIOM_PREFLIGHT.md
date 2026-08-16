# Spatial Attribution Axiom Preflight

## 1. Core Problem

The previous preflight proved that given a fixed legal-alternative comparison and supplied consequence magnitude $a > 0$, the spatial attribution operator is mathematically underdetermined by chess legality, sufficient-state invariance, branch preservation, positive homogeneity, visualization independence, and conservation. 

Specifically, destination ownership ($\mu_D$) and transition-touch ownership ($\mu_T$) both satisfy the current axioms but distribute mass differently.

**Goal:** What additional ownership/responsibility assumptions could distinguish admissible spatial attribution operators, and which of those assumptions are semantic definitions versus empirically falsifiable claims?

## 2. The Critical Distinction

**Empirical utility of an attribution operator $\neq$ truth of its ownership semantics.**

An explicitly conventional attribution rule is not falsified merely because it performs poorly on a downstream task.

Poor performance may falsify:
*"operator $\mu$ is useful for predicting target $Y$ under protocol $\Pi$"*

but not:
*"$\mu$ is the declared attribution convention."*

Conversely, strong predictive performance does not prove:
*"consequence objectively belongs to the squares selected by $\mu$."*

## 3. Candidate Attribution Principles

### A. Destination Ownership
- **Assigns ownership to:** The exact target squares of the alternative transitions.
- **Information required:** Target squares.
- **Chess legality determines:** The set $D(x)$, but not the mass assignment.
- **Off-manifold counterfactuals:** No.
- **Branch identity:** Preserved.
- **Sufficient state:** Respected.
- **Relation ontology:** None introduced.
- **Implementation ambiguity:** Low.
- **Ownership identifiability:** NOT IDENTIFIED / CONVENTIONAL
- **Empirical utility test:** Destination-based attribution predicts independent target $Y$ better/worse than comparator operators.
- **Claim ceiling:** Explicitly declared destination-based attribution.
- **Classification:** SEMANTIC CONVENTION / EXPLANATORY CONVENTION.

### B. Transition-Touch Ownership
- **Assigns ownership to:** Origin and target squares of the transitions.
- **Information required:** Origin and target squares.
- **Chess legality determines:** The set $T(x)$, but not the mass assignment.
- **Off-manifold counterfactuals:** No.
- **Branch identity:** Preserved.
- **Sufficient state:** Respected.
- **Relation ontology:** None introduced.
- **Implementation ambiguity:** Low.
- **Ownership identifiability:** NOT IDENTIFIED / CONVENTIONAL
- **Empirical utility test:** Transition-footprint attribution predicts independent target $Y$ better/worse than comparator operators.
- **Claim ceiling:** Explicitly declared transition-footprint attribution.
- **Classification:** SEMANTIC CONVENTION.

### C. Changed-State Ownership
- **Assigns ownership to:** Squares where the board state differs between alternative resulting positions.
- **Information required:** Full board difference.
- **Chess legality determines:** The state difference mapping.
- **Off-manifold counterfactuals:** No.
- **Branch identity:** Preserved.
- **Sufficient state:** Respected.
- **Relation ontology:** None introduced.
- **Implementation ambiguity:** Low.
- **Ownership identifiability:** NOT IDENTIFIED / CONVENTIONAL
- **Empirical utility test:** Predicts independent target $Y$ better/worse than comparator operators. (Unchanged relationally important squares represent a structural limitation/failure mode, not a falsifier of the semantic convention.)
- **Claim ceiling:** Diff-based convention.
- **Classification:** SEMANTIC CONVENTION.

### D. Mechanistic-Dependency Ownership
- **Assigns ownership to:** Relational features (pins, blocks, discovered attacks) driving the consequence.
- **Information required:** Causal dependency graph / relation ontology.
- **Chess legality determines:** No, requires explicit causal modeling mapping.
- **Off-manifold counterfactuals:** Possibly, if modeling sub-legal dependencies.
- **Branch identity:** Potentially reduced depending on relation extraction.
- **Sufficient state:** Respected if relation graph is state-derived.
- **Relation ontology:** Introduced and heavily relied upon.
- **Implementation ambiguity:** High (two causal models can disagree).
- **Ownership identifiability:** NOT IDENTIFIED / CONVENTIONAL
- **Empirical utility test:** Cross-instrument robustness, intervention prediction.
- **Claim ceiling:** Mechanistic/dependency representation with whatever intervention or predictive entitlement is independently earned.
- **Classification:** EXPLANATORY CONVENTION (plus EMPIRICAL HYPOTHESIS only for separately stated predictions about independent observations).

### E. Legal-Intervention Ownership
- **Assigns ownership to:** Locus of sensitivity under legal interventions.
- **Information required:** Intervention distribution and response.
- **Chess legality determines:** Legal intervention set may be rule-derived; intervention distribution/weighting/ownership interpretation is not.
- **Off-manifold counterfactuals:** No, if strictly legal.
- **Branch identity:** Reduced to state sensitivity.
- **Sufficient state:** Respected.
- **Relation ontology:** None strictly necessary, but intervention set could embed one.
- **Implementation ambiguity:** High (weighting distribution).
- **Ownership identifiability:** NOT IDENTIFIED / CONVENTIONAL
- **Empirical utility test:** Held-out consequence discrimination.
- **Claim ceiling:** Intervention-sensitivity map under an explicitly declared legal-intervention set and weighting distribution.
- **Classification:** EMPIRICAL HYPOTHESIS.

### F. Coalition/Value-Allocation Ownership (Shapley)
- **Assigns ownership to:** Square/feature coalitions based on marginal contribution.
- **Information required:** Value function over partial feature sets.
- **Chess legality determines:** No.
- **Off-manifold counterfactuals:** Off-manifold risk depends on coalition semantics; naïve square/feature deletion commonly creates illegal or insufficient chess states.
- **Branch identity:** Reduced/Destroyed.
- **Sufficient state:** Violated (requires state abstractions).
- **Relation ontology:** Feature definitions.
- **Implementation ambiguity:** High (feature selection and reference baseline).
- **Ownership identifiability:** NOT IDENTIFIED / CONVENTIONAL
- **Empirical utility test:** Utility may be compared against independent legal-state targets, but coalition-value semantics themselves require explicit justification.
- **Claim ceiling:** Axiomatic fairness allocation.
- **Classification:** MATHEMATICAL AXIOM / SEMANTIC CONVENTION.

## 4. The Central Validation Problem

How can an attribution axiom be scientifically selected without circularly validating it against itself?

An attribution operator can be empirically compared using an independent target $Y$ without proving that $Y$ is spatial ground truth. Such a study can establish predictive or intervention utility relative to $Y$. It cannot, by itself, establish that the operator's squares objectively own consequence.

We must distinguish:
- $Y = \text{independent validation target}$
- $V = \text{ultimate consequence target}$
- $\mu = \text{spatial attribution operator}$

## 5. Conclusion

**SPATIAL_OWNERSHIP_IS_CONVENTIONAL_NOT_IDENTIFIED**

Current chess semantics and adopted invariants do not identify a unique objective square-ownership interpretation. Any C2$\to$C4 ownership rule therefore remains an explicit attribution convention unless additional independently justified semantics are supplied.

Operator-specific predictive, robustness, or intervention properties remain empirically testable. Success on those properties can earn utility claims, but does not convert the underlying ownership convention into discovered spatial ground truth.

## 6. Next Planning Question

Which independent validation target could compare attribution operators without pretending to provide spatial ground truth?
