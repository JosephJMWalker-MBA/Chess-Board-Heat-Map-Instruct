# T3b-1 Comparator Design and Identifiability

## Scientific Objective

Determine the first legal-reply comparison that can test intervention sensitivity without conditioning intervention selection on downstream engine evaluation and without claiming isolated event causality.

**Evidence ceiling remains:**
`EvidenceLevel.INTERVENTION_SENSITIVITY`

---

## Provisional First Comparator: All-Legal-Reply Class Contrast (Design A)

We freeze the provisional first comparator as **All-Legal-Reply Class Contrast**.

For post-root state $P_i$:
- $\mathcal{R}_i = \text{all legal immediate replies}$
- $C_i(x) = \{r \in \mathcal{R}_i : r \text{ realizes } x\}$
- $N_i(x) = \mathcal{R}_i \setminus C_i(x)$

The intervention acquisition universe is the **entire legal reply set**, not a producer-generated PV and not a chosen matched pair. Every reply required by the frozen rule must be retained.

---

## Why Design A Comes Before Design B

Design A (All-Legal-Reply Class Contrast) is selected before Design B (Deterministically matched legal reply) because:

- A introduces no learned or hand-weighted matching metric.
- A does not select controls using downstream consequence values.
- A is deterministic from rule-exact state + event definition.
- A eliminates the T3a producer-realization bottleneck.
- A does not isolate the event from other move differences.

Therefore, A is deliberately a lower-specificity / lower-selection-bias first intervention test.

Design B remains a later possible refinement if intervention sensitivity exists or if a principled rule-exact matching basis can independently be justified. Design B is not contingent on A being positive; either outcome may motivate methodological refinement.

---

## The Intervention Unit

The intervention is:
$$\text{ApplyReply}(P_i, r) = P_{i,r}$$

*Historical shorthand $do(r)$ may be preserved if desired, but $\text{ApplyReply}$ is preferred in T3b-1 to avoid implying Pearl-style isolated causal identification.*

**Crucial Statement:**
The manipulated variable is **legal immediate reply identity**. Event membership is a property of that reply, not the only chess feature changed by the intervention.

---

## Event Realization Semantics

For an immediate target event:
$$x = (s, \text{role}, \text{ply}=1 \text{ relative to } P_i)$$

*(Equivalently, the historical branch-relative ply 2 after White root $m_i$)*.

Event membership is defined entirely from rule-exact reply semantics:
- exact destination/captured square as applicable;
- exact role;
- exact reply identity.

**No engine output may determine $C_i$ or $N_i$.**

Explicitly mapping coordinate systems:
`T3a branch-relative ply 2 == T3b post-root intervention-relative ply 1`
*(Ensures no future off-by-one ambiguity).*

---

## Eligibility Requirements (Conceptual)

A post-root state $P_i$ can only support class contrast if:
- $C_i(x) \neq \emptyset$
- $N_i(x) \neq \emptyset$

*We do not yet freeze minimum cardinalities, suite size, statistic, effect direction, engine budget, or fixture generator. Those belong to later preregistration after comparator semantics are settled.*

---

## What a Positive Result Could Mean

If a future preregistered class contrast finds systematic differences between:
$$Y_{i,r}, r \in C_i(x)$$
and
$$Y_{i,r}, r \in N_i(x)$$

**Earned language is limited to:**
"Under the frozen intervention instrument, consequence estimates are sensitive to legal immediate reply class membership involving event $x$."

**Not earned:**
- event $x$ alone caused the difference;
- square $s$ caused consequence;
- the producer would naturally choose $x$;
- $x$ is objectively important;
- $x$ belongs in Heat.

---

## Falsifiers

Record prospectively:
- legal class contrast may show no systematic sensitivity;
- direction may vary across positions;
- differences may be dominated by obvious non-target move effects;
- usable C/N states may be too sparse;
- typed consequence comparability may fail;
- instrument/order robustness may become necessary before interpretation.

**All are acceptable.**

---

## Unresolved Next Question

Given the all-legal-reply comparator, what deterministic rule-only fixture-selection protocol and preregistered statistic can test intervention sensitivity without selecting positions based on engine outcomes?
