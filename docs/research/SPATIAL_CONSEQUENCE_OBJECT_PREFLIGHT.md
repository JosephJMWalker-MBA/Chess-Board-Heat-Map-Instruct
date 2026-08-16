# Spatial Consequence Object Preflight

## 1. Problem Statement

**Central question:**
What mathematical object deserves to be called spatial consequence at all?

This preflight does not assume the answer is a 64-vector. It seeks to determine whether the following are naturally the same object or if they represent separate architectural layers:
- game/decision consequence
- transition consequence
- structured spatial support
- square attribution
- visualization

## 2. Target Semantics vs. Measurement Instrument

Let an abstract position-value functional representing the target notion of chess consequence be denoted:
$$V(P)$$

Stockfish evaluation is not asserted to be $V$. Rather, preserve the estimator:
$$\hat{V}_{J,\theta}(P)$$
as an instrument-conditioned estimator of whatever target is ultimately defined.

For legal alternatives $m, n \in L(P)$, define a generic decision contrast:
$$C_V(P;m,n) = V(\Phi(P,m)) - V(\Phi(P,n))$$

This is a consequence contrast, not yet a spatial attribution. CP, mate, and WDL typing must be treated abstractly; we do not invent a universal scalar conversion.

## 3. Layer Boundary

Consider the following architectural hierarchy:
- **C0** — sufficient chess state $P$
- **C1** — legal transition identity $(P,m,P_m)$
- **C2** — consequence contrast between legal alternatives
- **C3** — structured spatial difference/support between compared transitions
- **C4** — attribution measure over spatial subjects
- **C5** — 64-square projection / visualization

The core identifiability question targets the mapping **C2 $\to$ C4**: Is this mapping uniquely determined by chess semantics, or is an explicit mathematical attribution operator required?

## 4. Candidate Mathematical Object Families

### A. Pairwise Legal-Transition Consequence Object
- **Canonical subject:** $(P,m,n,C_V(P;m,n))$
- Spatial information remains attached as structured differences between the two legal transitions rather than being collapsed into square weights.

### B. Legal-Intervention Sensitivity Field
- A square/region receives consequence according to value changes under legal interventions involving it.
- **Unresolved choice:** Selection of the intervention set and the weighting distribution.

### C. Branch-Conditioned Consequence Measure
- Preserve branch identities and distribute consequence only after comparing legal branches.
- **Unresolved choice:** The additional rule that turns branch consequence into square mass.

### D. State-Difference Support Weighted by Consequence
- Spatial subjects receive support when compared legal continuations differ there, scaled by the branch consequence contrast.
- **Test:** Unchanged-but-relationally-important squares could expose a failure in this model.

### E. Cooperative/Shapley-style Attribution
- Analyzes whether coalition semantics require illegal/off-manifold chess states or arbitrary feature grouping. Not recommended merely because Shapley values possess attractive axioms.

### F. Consequence on the Legal-Transition Graph with Later Spatial Projection
- Consequence lives primarily on legal actions/transitions; square Heat is a derived, lossy view.
- **Test:** Determine whether this cleanly preserves the evidence learned from T2/T3.

## 5. Candidate Axioms / Desiderata

The following are evaluated for the spatial attribution operator:
- **Required:** sufficient-state invariance, branch identity preservation until comparison, color/perspective consistency, deterministic attribution under fixed inputs, producer/instrument separation, projection provenance, typed outcome preservation, no mate-to-CP coercion.
- **Optional/Rejected:** legal-counterfactual requirement, board-symmetry equivariance (must respect chess rules, not purely geometric symmetry), explicit reference/baseline identity.
- **Rejected:** no normalization-generated hotspot when amplitude is zero/negligible, zero-consequence behavior constraints, no dependence on visualization choices.
- **Conservation ($ \sum_s \mu(s) = |C| $):** Not adopted automatically. Forcing conservation risks smuggling in an unjustified attribution assumption.

## 6. Shape Versus Amplitude

Incorporating the M8 result: rank or normalization can manufacture artificial hotspots in low-amplitude positions. 

Therefore, a candidate object should be explicitly represented as a pair:
$$(A(P), S(\cdot|P))$$
rather than a single normalized Heat vector.

**Requirement:** $A = 0$ must not force an arbitrary normalized shape. Shape may need to be undefined/null at zero amplitude rather than uniformly or rank normalized. We do not define a new production amplitude metric here.

## 7. The Identifiability Test

Do the proposed axioms uniquely identify a spatial attribution operator?

Consider two distinct attribution operators $\mu_1$ and $\mu_2$ that both satisfy all currently defensible axioms (e.g., $A(P)$ conservation, zero-amplitude nullification, deterministic evaluation). 
- $\mu_1$ distributes spatial mass strictly to the destination square of the move difference.
- $\mu_2$ distributes spatial mass equally among all squares in the ray path (if any) or relational dependencies of the move.

Both operators map the abstract legal-transition consequence situation to valid spatial vectors without violating chess semantics. 

**SPATIAL_ATTRIBUTION_NOT_IDENTIFIED_BY_CURRENT_AXIOMS**

To distinguish them, an extra axiomatic assumption—such as an explicit causal-graph attribution rule or Shapley coalition semantics—would be required.

## 8. Test the Notion of "Where Consequence Lives"

We must distinguish at least three meanings:
1. **Where board state changes:** The literal diff between two valid board states.
2. **Where a causal/mechanistic dependency operates:** The relational features (e.g., pins, discovered attacks) driving the evaluation.
3. **Where a chosen explanation/attribution operator assigns responsibility:** The mathematically declared projection.

ChessHeat has historically conflated these. A square may remain unchanged yet participate relationally in why two legal continuations differ. Conversely, a changed destination square need not uniquely own the resulting consequence. T2/T3 constraints demonstrate that isolating a single aspect (e.g., ray blockers or isolated destination events) without the structural context is insufficient or falsified.

## 9. Non-Spatial Canonical Object

We take seriously the possibility that consequence is canonically defined on legal decision/transition contrasts, while spatial consequence is necessarily a derived attribution.

**Architectural consequences:**
- Canonical evidence remains branch/transition keyed.
- Spatial attribution becomes an explicit measurement layer.
- 64-square Heat becomes a projection layer.
- Alternative attribution operators can be compared without corrupting canonical evidence.
- Provenance must identify the attribution operator.

This preflight supports this architectural separation.

## 10. Falsifiers for Proposed Spatial Objects

A candidate should fail the preflight if:
- it requires illegal counterfactual states without explicit semantics
- it silently identifies engine score with objective consequence
- it loses branch identity before consequence comparison
- it gives nonzero/high-confidence shape when consequence amplitude is zero
- it changes under irrelevant serialization or visualization choices
- it requires arbitrary feature coalitions while claiming uniqueness
- it cannot distinguish target definition from estimator
- it merely redistributes move frequency or search preference
- it contradicts frozen T2/T3 evidence

## 11. Identifiability Ledger

| Candidate | Canonical Subject | Consequence Target | Spatial Subject | Extra Choices | Legal-State Fidelity | Branch Preservation | Instrument Dependence | Uniqueness Status | S0/S1 | T2/T3 | Strongest Claim | Principal Falsifier |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **A. Pairwise Legal-Transition** | $(P,m,n)$ | $C_V$ | Transition diff | None | High | Preserved | Estimator-bound | High | Yes | Yes | Baseline canonical measure | Loses branch identity |
| **B. Legal-Intervention Sensitivity** | $P$ | $V$ delta | Intervention locus | Intervention set | Variable | Reduced | Estimator-bound | Low | Yes | Partial | Causal sensitivity | Arbitrary coalitions |
| **C. Branch-Conditioned** | Branch sets | Branch target | Derived | Attribution operator | High | Preserved | Estimator-bound | Low | Yes | Yes | Validated C2 rep. | Redistributes search |
| **D. State-Difference Support** | Diff subset | $C_V$ | Changed squares | Scaling rule | High | Preserved | Estimator-bound | Low | Yes | Fails | Spatial mapping heuristic | Fails relational test |
| **E. Cooperative/Shapley** | Subsets | $C_V$ | Features | Coalition semantics | Low (illegal states) | Reduced | Estimator-bound | Low | No | Partial | Axiomatic fairness | Illegal counterfactuals |
| **F. Transition Graph w/ Projection** | $(P,m,n)$ | Graph edge | Projection view | Projection mapping | High | Preserved | Estimator-bound | High(C2)/Low(C4) | Yes | Yes | Sound canonical architecture | Conflates target/estimator |

## 12. Preflight Conclusion

**CANONICAL_CONSEQUENCE_APPEARS_TRANSITION_LEVEL_NOT_SPATIAL**

*Subordinate finding:* SPATIAL_CONSEQUENCE_OBJECT_REQUIRES_EXPLICIT_ATTRIBUTION_AXIOMS

The preflight reveals that chess semantics natively identify consequence at the level of legal transitions and branch alternatives (C1/C2). However, mapping this transition-level consequence into a 64-square spatial field (C4) is not uniquely determined by existing axioms. Multiple spatial attribution operators can satisfy the invariants while distributing mass differently. Therefore, the canonical consequence object appears to be transition-level, not spatial. Spatial consequence is a derived, mathematically distinct measurement layer requiring explicit, declared attribution axioms.

## 13. Synthesis Ontology Note

*Note on EVIDENCE_TREE_SYNTHESIS.md wording:* The governing question remains separated from Shape and Amplitude. In the refined ontology, Shape $S(s|P)$ is the proposed spatial answer dimension, Amplitude $A(P)$ is a separate consequence-magnitude dimension, and Human navigability remains entirely outside objective Heat. We do not edit EVIDENCE_TREE_SYNTHESIS.md here, but note this for future synthesis updates.
