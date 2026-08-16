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

For a sufficient position $P$ and legal White root $m_i$, let $P_i$ be the rule-exact post-root state and $\mathcal{R}_i$ its complete set of legal Black replies. For a target event $x$:

$$C_i(x) = \{r \in \mathcal{R}_i : \text{reply } r \text{ realizes } x\}$$
$$N_i(x) = \mathcal{R}_i \setminus C_i(x)$$

Define:
$$do(r): P_i \to P_{i,r}$$
as the rule-exact intervention selecting one particular legal immediate reply and then evaluating the resulting legal child state.

Define provisionally:
$$Y_{i,r}(\mathcal{J}, \theta)$$
as the typed consequence estimate of $P_{i,r}$ under producer/instrument $\mathcal{J}$, configuration $\theta$, and frozen comparison perspective. $Y$ is an instrument estimate, not objective truth.

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
- **What it could earn**: Consequence estimates are sensitive to legal immediate reply class membership involving the target event $x$.
- **What it cannot earn**: The isolated causal effect of event $x$.
- **Principal confound/dependency**: Reply-class differences bundle other chess effects (the intervention changes more than just the target event).

**B. Deterministically matched legal reply**
Choose a non-event reply through a preregistered rule-exact matching metric.
- **What it could earn**: Tighter control over non-target move differences, earning a more specific causal attribution.
- **What it cannot earn**: Objective causal effect free from metric bias.
- **Principal confound/dependency**: The matching metric itself may inject ontology assumptions and may fail to find valid controls.

**C. Instrument forcing (searchmoves)**
Explicitly classify as an instrument intervention.
- **What it could earn**: Characterization of search behavior under restricted move consideration.
- **What it cannot earn**: Chess-state intervention sensitivity (it does not evaluate a true, freely produced legal chess state).
- **Principal confound/dependency**: Intervenes on the engine's attention mechanism rather than the chess board state itself.

**D. Artificial board perturbation**
Explicitly defer pending a separate legality/semantic-validity contract.
- **What it could earn**: Plausible counterfactual tests for states that cannot be reached legally.
- **What it cannot earn**: Meaningful legal chess consequence (creates invalid or semantically undefined positions).
- **Principal confound/dependency**: Relies on the engine's behavior in non-legal or unreachable game states.

---

## Freeze No-Rescue Intent

T3b is motivated by the observational confound exposed by T3a, not by a requirement to recover the T3a-2 positive direction.

All future intervention outcomes—positive, null, opposite-direction, or inconclusive—must be acceptable.

T3a-4's conditional adverse result must remain untouched and must not be reclassified based on T3b.

---

## Unresolved Design Question

What legal-reply comparator can earn intervention sensitivity to a target event while minimizing non-target move differences without smuggling engine preference into control selection?
