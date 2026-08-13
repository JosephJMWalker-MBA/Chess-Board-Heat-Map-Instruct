# M8.6.8 — Candidate-Set Sensitivity Characterization & M8 Freeze

## The Mathematical Result: Recurrence is Conditional on the Future Set

Comparing the all-legal-roots (W-v2) and top-5 (W-v2-R) Recurrence evaluations reveals a fundamental property of spatial chess measurement:

> **Recurrence geography is conditional on the chosen future set, and constraining that future set induces a measurable specificity–coverage tradeoff.**

Formally:

$$
R(s\mid C)=
\frac{|\{c\in C:s\in PV(c)\}|}{|C|}
$$

The choice of $C$ (the candidate universe) is therefore not merely a performance optimization or an implementation detail. **It is an intrinsic part of the measurement definition.** 

$C_{\text{all-legal}}$ and $C_{\text{top-5}}$ answer mathematically distinct questions:
1. $C_{\text{all-legal}}$ maps where geometry arises across the *entire* legal possibility space.
2. $C_{\text{top-5}}$ maps where geometry recurs strictly across a *restricted set of strong futures*.

Neither definition is automatically the "correct" one; they represent different phenomenological lenses.

## Specificity vs. Spatial Coverage Tradeoff

Applying the $C_{\text{top 5}}$ constraint is not a pure noise filter; it alters the sensitivity–specificity balance of the measurement. 

Across the ten valid W-suite fixtures, total selected squares dropped from 201 to 122. Of the 79 eliminated selections:
* **79 = 68** non-target benchmark selections
* **+ 11** expected benchmark-target selections

Roughly 86% of the removed geography was unwanted non-target benchmark geography, while 14% was expected benchmark-target geography. 

### Successes, Blind Spots, and Independence

1. **W3 (Clean Suppression):** False-positive footprint collapsed (17 → 1) while region recall survived intact (0.33 → 0.33) and precision surged (0.06 → 0.50). This exemplifies the intended non-target benchmark geography suppression effect of restricting $C$.
2. **W2 (Exposed Vulnerability):** W2 was designed around leverage supported by few lines. Under top-5, combined with the hard invariant $L(s) \ge 3$, its single surviving focal square vanishes. This demonstrates the preregistered hostile failure mode on that fixture, rather than proving its prevalence generally.
3. **W4 & W12 (Broad Region Masking):** Constraining Recurrence exposed the structural limitations of the Bundle gate (`region_size <= 15`). The previous all-root Recurrence run was partially masking these limitations. For W12, the result was a cold, highly specific map (FP area 13 → 4) that completely failed to identify both preregistered tactical regions (Recall 0). 
4. **W1, W5, W6, W8 (Residual Footprints):** Their false-positive footprints did *not* change. W1 (17 FP squares) retained its footprint largely due to heavy Bundle channel contributions (16 squares). This validates that correcting Recurrence tells us nothing about Bundle correctness; Direct, Recurrence, and Bundle evidence can independently satisfy their predicates, while `apply_shape_selectivity_v1()` remains an ordered first-success selector.

## Final M8 Conclusions and Freeze

We draw no claim that $C_{\text{top 5}}$ is optimal. A fixed boundary of five has no inherent chess meaning. Future work should treat candidate-universe design as a fundamental research question (e.g., boundaries based on regret thresholds, outcome classes, probability, or decision boundaries).

This concludes the first major research phase. We have established several critical mathematical distinctions:

- $\text{control} \neq \text{importance}$
- $\text{regret} \neq \text{causal delta}$
- $\text{association} \neq \text{causality}$
- $\text{shape} \neq \text{amplitude}$
- $\text{severity} \neq \text{decision leverage}$
- **$\text{recurrence is conditional on the future set}$**
- **$\text{specificity and spatial coverage trade against one another}$**

M8 is now frozen. No further thresholds will be tuned against the W-suite, and no ShapeSelectivity-v2 will be derived from it during this phase.
