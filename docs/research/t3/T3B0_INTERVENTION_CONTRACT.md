# T3b-0 Intervention Semantics Contract

## The T3a Boundary

The observational program T3a is officially closed with the following frozen statuses:

- **T3a-1**: INCONCLUSIVE — PV horizon
- **T3a-2**: SUPPORTED — single fixture
- **T3a-3**: INCONCLUSIVE — zero realized support
- **T3a-4**: INCONCLUSIVE — provenance
  - *Conditional numeric result strongly FALSIFIED*

**Rule**: No additional T3a experiment may be introduced merely to obtain a favorable single-PV realization result.

---

## Prospective Intervention Objects

For a sufficient position $P$ and legal White root $m_i$, let $P_i$ be the rule-exact post-root state and $R_i$ its complete set of legal Black replies. For a target event $x$:

$$C_i(x) = \{r \in R_i : \text{reply } r \text{ realizes } x\}$$
$$N_i(x) = R_i \setminus C_i(x)$$

Define:
$$do(r): P_i \to P_{i,r}$$
as the rule-exact intervention selecting one particular legal immediate reply and then evaluating the resulting legal child state.

Define provisionally:
$$Y_{i,r}(J, \theta)$$
as the typed consequence estimate of $P_{i,r}$ under producer/instrument $J$, configuration $\theta$, and frozen comparison perspective. $Y$ is an instrument estimate, not objective truth.

---

## Intervention Definitions and Restrictions

### What Counts as an Intervention
- A legal applied reply $do(r)$ is a chess-state intervention.

### What Does NOT Count as an Intervention
- `searchmoves` or analogous engine restrictions are instrument interventions, not chess-state interventions, and must not silently stand in for $do(r)$.
- Comparing $L_i$ across sibling White roots is observational legal-opportunity analysis, not intervention.
- Observing $E_i$ in a naturally produced PV is producer-conditioned observation, not intervention.
- Deleting, teleporting, or arbitrarily replacing pieces produces board perturbations and requires a separate validity contract; it is not automatically a legal chess intervention.

---

## Initial Evidence Ceiling

The maximum claim level for T3b's first successful experiment is:
**EvidenceLevel.INTERVENTION_SENSITIVITY**

Even a positive result does **not** authorize:
- "square s causes consequence"
- objective causal effect
- natural prevalence
- producer-independent consequence
- Heat contribution

---

## The Core Confound

If an event-realizing reply $c \in C_i$ and non-event reply $n \in N_i$ produce different evaluations, the moves generally differ in more than the target event.

Therefore:
$$Y_{i,n} - Y_{i,c}$$
is **not** automatically the isolated causal effect of event $x$. It may establish sensitivity to legal reply selection involving $x$, but event-specific causal attribution requires a separately certified matched-control argument.

---

## Comparator Requirements

Any future T3b comparator must:
- operate within the same post-root state $P_i$;
- use only legal immediate replies;
- preserve exact reply identity;
- retain all event-realizing and control replies required by the preregistered rule;
- avoid selecting controls using downstream engine evaluation;
- state exactly which non-target differences remain between intervention and control;
- fail rather than claim event-specific causality when those differences cannot be isolated.

*Note: No numeric intervention statistic is frozen in T3b-0.*

---

## Candidate Designs

**A. All-legal-reply class contrast**
Compare consequence distributions for $C_i(x)$ versus $N_i(x)$.
- *Advantage*: No producer-realization dependence.
- *Limitation*: Reply-class differences bundle other chess effects.

**B. Deterministically matched legal reply**
Choose a non-event reply through a preregistered rule-exact matching metric.
- *Advantage*: Tighter control.
- *Limitation*: The matching metric itself may inject ontology assumptions and may fail to find valid controls.

**C. Instrument forcing (searchmoves)**
Explicitly classify as an instrument intervention.
- *Advantage/Limitation*: It may study search behavior but cannot by itself establish chess-state intervention sensitivity.

**D. Artificial board perturbation**
Explicitly defer pending a separate legality/semantic-validity contract.

---

## Freeze No-Rescue Intent

T3b is motivated by the observational confound exposed by T3a, not by a requirement to recover the T3a-2 positive direction.

All future intervention outcomes—positive, null, opposite-direction, or inconclusive—must be acceptable.

T3a-4's conditional adverse result must remain untouched and must not be reclassified based on T3b.

---

## Unresolved Design Question

What legal-reply comparator can earn intervention sensitivity to a target event while minimizing non-target move differences without smuggling engine preference into control selection?
