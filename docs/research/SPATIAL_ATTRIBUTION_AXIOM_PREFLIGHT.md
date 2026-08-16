# Spatial Attribution Axiom Preflight

## 1. Core Problem

The previous preflight proved that given a fixed legal-alternative comparison and supplied consequence magnitude $a > 0$, the spatial attribution operator is mathematically underdetermined by chess legality, sufficient-state invariance, branch preservation, positive homogeneity, visualization independence, and conservation. 

Specifically, destination ownership ($\mu_D$) and transition-touch ownership ($\mu_T$) both satisfy the current axioms but distribute mass differently.

**Goal:** What additional ownership/responsibility assumptions could distinguish admissible spatial attribution operators, and which of those assumptions are semantic definitions versus empirically falsifiable claims?

## 2. Candidate Attribution Principles

### A. Destination Ownership
- **Assigns ownership to:** The exact target squares of the alternative transitions.
- **Information required:** Target squares.
- **Chess legality determines:** The set $D(x)$, but not the mass assignment.
- **Off-manifold counterfactuals:** No.
- **Branch identity:** Preserved.
- **Sufficient state:** Respected.
- **Relation ontology:** None introduced.
- **Implementation ambiguity:** Low.
- **Possible falsifier:** Predictive incremental value, invariance under equivalent histories.
- **Claim ceiling:** Simplest geometric attribution convention.
- **Changes Heat Architecture:** Formalizes current projection.
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
- **Possible falsifier:** Predictive incremental value.
- **Claim ceiling:** Full movement footprint convention.
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
- **Possible falsifier:** Fails to capture static relational importance.
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
- **Possible falsifier:** Cross-instrument robustness, intervention prediction.
- **Claim ceiling:** Explanatory causal representation.
- **Classification:** EMPIRICAL HYPOTHESIS / EXPLANATORY CONVENTION.

### E. Legal-Intervention Ownership
- **Assigns ownership to:** Locus of sensitivity under legal interventions.
- **Information required:** Intervention distribution and response.
- **Chess legality determines:** Legal intervention set, not the weighting.
- **Off-manifold counterfactuals:** No, if strictly legal.
- **Branch identity:** Reduced to state sensitivity.
- **Sufficient state:** Respected.
- **Relation ontology:** None strictly necessary, but intervention set could embed one.
- **Implementation ambiguity:** High (weighting distribution).
- **Possible falsifier:** Held-out consequence discrimination.
- **Claim ceiling:** Causal sensitivity map.
- **Classification:** EMPIRICAL HYPOTHESIS.

### F. Coalition/Value-Allocation Ownership (Shapley)
- **Assigns ownership to:** Square/feature coalitions based on marginal contribution.
- **Information required:** Value function over partial feature sets.
- **Chess legality determines:** No.
- **Off-manifold counterfactuals:** Yes, heavily (evaluating illegal partial boards).
- **Branch identity:** Reduced/Destroyed.
- **Sufficient state:** Violated (requires state abstractions).
- **Relation ontology:** Feature definitions.
- **Implementation ambiguity:** High (feature selection and reference baseline).
- **Possible falsifier:** Cannot be validated via legal engine paths.
- **Claim ceiling:** Axiomatic fairness allocation.
- **Classification:** MATHEMATICAL AXIOM / SEMANTIC CONVENTION.

## 3. The Central Identifiability Problem

How can an attribution axiom be scientifically selected without circularly validating it against itself?

Explicitly examine whether an ownership principle can be validated without already possessing the objective spatial ground truth it is supposed to define. If $\mu_D$ and $\mu_T$ distribute $a$ differently, validating $\mu_D$ against a downstream task requires proving it objectively better tracks $V$.

**Independent constraints for validation:**
- intervention prediction
- held-out consequence discrimination
- cross-instrument robustness
- minimal sufficient representation
- invariance under equivalent legal histories
- perturbation locality
- predictive incremental value

*Note: Selecting an attribution because it predicts consequence better is an empirical endeavor. Proving that consequence objectively "belongs" to those squares is a much stronger philosophical/non-identifiable claim.*

## 4. Conclusion

**SPATIAL_OWNERSHIP_IS_CONVENTIONAL_NOT_IDENTIFIED**

Without an independent empirical target, explicit spatial ownership assumptions (like destination vs. transition-touch) remain scientifically untestable semantic conventions. To promote them to empirically falsifiable hypotheses, they require an independent validation target (e.g., intervention prediction or cross-instrument robustness) that does not circularly rely on the attribution axiom itself. Until such a target is established, any declared spatial attribution operator is fundamentally a conventional projection, not a natively discovered property of chess consequence.
