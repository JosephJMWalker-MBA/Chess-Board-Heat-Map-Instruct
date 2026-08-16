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

Chess semantics natively identify sufficient states, legal actions, successor states, and legal-alternative identities. Given a separately declared consequence target $V$, consequence contrasts can be keyed canonically to legal alternative pairs. 

For legal alternatives $m, n \in L(P)$, define a generic decision contrast:
$$C_V(P;m,n) = V(\Phi(P,m)) - V(\Phi(P,n))$$

This is a consequence contrast, not yet a spatial attribution. CP, mate, and WDL typing must be treated abstractly; we do not invent a universal scalar conversion.

**Explicitly:**
- $V$ itself is not supplied by chess legality.
- Stockfish is not $V$.
- C2 subject identity can be well-defined before the target $V$ is scientifically earned.

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
- Spatial information remains attached as structured differences between the two legal transitions rather than being collapsed into square weights.

### B. Legal-Intervention Sensitivity Field
- A square/region receives consequence according to value changes under legal interventions involving it.
- **Unresolved choice:** Selection of the intervention set and the weighting distribution.

### C. Branch-Conditioned Consequence Measure
- Preserve branch identities and distribute consequence only after comparing legal branches.
- **Unresolved choice:** The additional rule that turns branch consequence into square mass.

### D. State-Difference Support Weighted by Consequence
- Spatial subjects receive support when compared legal continuations differ there, scaled by the branch consequence contrast.

### E. Cooperative/Shapley-style Attribution
- Analyzes whether coalition semantics require illegal/off-manifold chess states or arbitrary feature grouping. Not recommended merely because Shapley values possess attractive axioms.

### F. Consequence on the Legal-Transition Graph with Later Spatial Projection
- Consequence lives primarily on legal actions/transitions; square Heat is a derived, lossy view.

## 5. Candidate Axioms / Desiderata

We separate three kinds of requirements:

**Upstream consequence-target constraints**
- sufficient-state identity
- explicit legal-alternative/reference identity
- branch identity preserved until consequence comparison
- typed target preservation
- no mate-to-CP coercion
- target $V$ distinguished from estimator $\hat{V}$
- producer/instrument provenance

**C2 $\to$ C4 attribution-operator axioms used in the identifiability theorem**
- deterministic under fixed inputs
- depends only on the declared comparison subject and supplied magnitude $a$
- comparison-order invariance for unsigned spatial mass
- zero: $a=0$ implies zero attribution everywhere
- positive homogeneity in the symbolic amplitude: $\mu(s | x, \lambda a) = \lambda \mu(s | x, a)$ for $\lambda \geq 0$
- visualization independence

*(Optional pending exact formulation)*
- rule-preserving board equivariance: $\mu(\pi(s) | \pi x, a) = \mu(s | x, a)$ for a rule-preserving board relabeling/isomorphism $\pi$. Both $\mu_D$ and $\mu_T$ (defined below) satisfy this because from/to sets commute with $\pi$.

**Downstream measurement/projection safeguards**
- projection provenance
- raw attribution mass vanishes with amplitude
- any normalized spatial shape is conditional on amplitude and may not be interpreted as magnitude or displayed without amplitude-aware semantics
- $A=0 \implies$ shape null/undefined

These downstream safeguards do not select between $\mu_D$ and $\mu_T$.

## 6. Shape Versus Amplitude

Incorporating the M8 result: rank or normalization can manufacture artificial hotspots in low-amplitude positions. 

Therefore, a candidate object should be explicitly represented as a pair:
$$(A(P), S(\cdot|P))$$
rather than a single normalized Heat vector.

**Requirement:** Raw attribution mass vanishes with amplitude. Any normalized spatial shape is conditional on amplitude and may not be interpreted as magnitude or displayed without amplitude-aware semantics. Shape must be undefined/null at zero amplitude rather than uniformly or rank normalized. No arbitrary "negligible" threshold or production amplitude definition is provided here.

## 7. The Identifiability Test

Do the proposed axioms uniquely identify a spatial attribution operator?

The theorem does not require ChessHeat to have already earned a universal scalar amplitude. It is conditional: even granting any scientifically valid supplied positive consequence magnitude $a > 0$, the currently defensible spatial axioms do not uniquely determine where that magnitude should be assigned.

Use one abstract legal-transition comparison:
$$x=(P,m,n,C)$$
with both $m,n$ legal, nonzero abstract consequence amplitude $a>0$, distinct legal move identities, and:
$$D(x) = \{to(m), to(n)\}$$
after deduplication, and:
$$T(x) = \{from(m), to(m), from(n), to(n)\}$$
after deduplication.

Choose $x$ with:
$$D(x) \subsetneq T(x)$$
which is stronger than merely $D(x) \neq T(x)$.

Define:
$$\mu_D(s|x) = \begin{cases} a/|D(x)|, & s \in D(x) \\ 0, & \text{otherwise} \end{cases}$$

and:
$$\mu_T(s|x) = \begin{cases} a/|T(x)|, & s \in T(x) \\ 0, & \text{otherwise} \end{cases}$$

### Axiom Admissibility
Both $\mu_D$ and $\mu_T$ satisfy the attribution-operator axioms:
- **Deterministic under fixed inputs:** Yes, depend only on fixed sets $D(x)$ and $T(x)$ and scalar $a$.
- **Depends only on declared comparison/magnitude:** Yes.
- **Comparison-order invariance:** Yes, $D$ and $T$ sets are symmetric in $m,n$.
- **Zero:** If $a=0$, mass is $0$.
- **Positive homogeneity:** $\mu_D(\cdot | \lambda a) = \lambda \mu_D(\cdot | a)$ and $\mu_T(\cdot | \lambda a) = \lambda \mu_T(\cdot | a)$.
- **Visualization independence:** Yes, purely mathematical sets.
- **Voluntary conservation:** $\sum_s \mu_D(s|x) = \sum_s \mu_T(s|x) = a$. Thus $\|\mu_D\|_1 = \|\mu_T\|_1 = a \to 0$ as $a \to 0$.

For any:
$$s^\star \in T(x) \setminus D(x)$$
we explicitly derive:
$$\mu_D(s^\star | x) = 0$$
while
$$\mu_T(s^\star | x) = a / |T(x)| > 0$$

Therefore:
$$\mu_D \neq \mu_T$$

**Conditional non-identifiability result.** 
Given a fixed legal-alternative comparison subject and any supplied positive consequence magnitude $a > 0$, the currently adopted attribution-operator axioms—even strengthened by conservation—do not uniquely identify a square attribution. The explicit operators $\mu_D$ and $\mu_T$ satisfy those axioms but differ on the same comparison.

At $a=0$, the zero axiom intentionally collapses both operators to the all-zero attribution, so $\mu_D = \mu_T = 0$ on that boundary. This does not restore operator uniqueness: uniqueness would require the admissible operators to agree on every admissible input, while $\mu_D$ and $\mu_T$ differ for the constructed comparison at every $a>0$.

**SPATIAL_ATTRIBUTION_NOT_IDENTIFIED_BY_CURRENT_AXIOMS**

At least one additional substantive attribution assumption or equivalent selection rule is necessary to distinguish these operators; further assumptions may be required to uniquely identify an operator over the full admissible class. Examples include:
- destination-ownership axiom
- transition-touch ownership axiom
- mechanistic dependency attribution axiom
- intervention-distribution axiom
- coalition-value axiom

These are mutually substantive modeling assumptions, not consequences of chess legality. This preflight does not choose one.

## 8. Test the Notion of "Where Consequence Lives"

We must distinguish at least three meanings:
1. **Where board state changes:** The literal diff between two valid board states.
2. **Where a causal/mechanistic dependency operates:** The relational features (e.g., pins, discovered attacks) driving the evaluation.
3. **Where a chosen explanation/attribution operator assigns responsibility:** The mathematically declared projection.

ChessHeat has historically conflated these. A square may remain unchanged yet participate relationally in why two legal continuations differ. Conversely, a changed destination square need not uniquely own the resulting consequence. T2/T3 constraints demonstrate that isolating a single aspect without the structural context is insufficient or falsified.

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

| Candidate | Canonical Subject | Consequence Target | Spatial Subject | Extra Choices | Legal-State Fidelity | Branch Preservation | Instrument Dependence | Uniqueness Status | S0/S1 | T2/T3 | Strongest Claim | Principal Unresolved Issue / Falsifier |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **A. Pairwise Legal-Transition** | Legal-alternative pair | $C_V$ | None at C2 | Any C2$\to$C4 attribution rule | High | Preserved | Estimator-bound | Subject identity high / spatial attribution N/A | Yes | Yes | Canonical comparison subject | Consequence target V and later spatialization |
| **B. Legal-Intervention Sensitivity** | $P$ | $V$ delta | Intervention locus | Intervention set | Variable | Reduced | Estimator-bound | Low | Yes | Partial | Intervention sensitivity | Arbitrary coalitions |
| **C. Branch-Conditioned** | Branch sets | Branch target | Derived | Attribution operator | High | Preserved | Estimator-bound | Low | Yes | Yes | Validated C2 rep. | Redistributes search |
| **D. State-Difference Support** | Diff subset | $C_V$ | Changed squares | Scaling rule | High | Preserved | Estimator-bound | Low | Yes | Compatibility risk | Spatial mapping heuristic | Unchanged relationally relevant squares |
| **E. Cooperative/Shapley** | Subsets | $C_V$ | Features | Coalition semantics | Low (illegal states) | Reduced | Estimator-bound | Low | Distinguish typing | Partial | Axiomatic fairness | Illegal counterfactuals |
| **F. Transition Graph w/ Projection** | Graph structure | $C_V$ or other typed target | Derived projection | Projection mapping | High | Preserved | Estimator-bound | C2 identity high / C4 uniqueness low | Yes | Yes | Architecture compatible with transition-keyed canonical evidence | Conflates target/estimator |

## 12. Preflight Conclusion

**Primary Conclusion:**
**SPATIAL_CONSEQUENCE_OBJECT_REQUIRES_EXPLICIT_ATTRIBUTION_AXIOMS**

**Subordinate Finding:**
Legal transition and branch-alternative identities are currently the best-founded canonical subjects for consequence evidence. Given a declared target $V$, consequence contrasts are naturally keyed there. Current axioms do not uniquely identify a downstream square attribution.

**Architectural Suggestion:**
The preflight suggests the following architecture: canonical evidence may remain transition keyed, attribution may become an explicit measurement layer, and 64-square Heat may remain a lossy projection. This is the architecture presently suggested by the preflight, not a theorem about objective consequence.

**Shape/Amplitude Requirement:**
$A=0 \implies$ zero spatial attribution mass, normalized shape is undefined/null at $A=0$, and no production amplitude definition is provided here.

## 13. Synthesis Ontology Note

*Note on EVIDENCE_TREE_SYNTHESIS.md wording:* The governing question remains separated from Shape and Amplitude. In the refined ontology, Shape $S(s|P)$ is the proposed spatial answer dimension, Amplitude $A(P)$ is a separate consequence-magnitude dimension, and Human navigability remains entirely outside objective Heat. We do not edit EVIDENCE_TREE_SYNTHESIS.md here, but note this for future synthesis updates.
