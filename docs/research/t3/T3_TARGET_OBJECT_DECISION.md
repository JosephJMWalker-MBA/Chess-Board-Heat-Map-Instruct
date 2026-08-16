# T3 Target-Object Decision

The purpose of this decision note is to determine whether $L_i$, $E_i$, and future intervention evidence should compete to be the single definition of future consequence, or instead occupy distinct epistemic roles.

## Frozen Definitions

- $L_i(x) = 1\{x \text{ is a rule-exact legal opportunity after root } i\}$
- $E_i(x; I, \theta) = 1\{x \text{ is realized in the continuation produced by instrument } I \text{ under config } \theta\}$
- $I_i(x; M)$ = placeholder (not yet implemented) for evidence obtained through a specified legal matched-intervention protocol $M$.

*Note: Do not call $I_i$ causal effect yet.*

## Evaluating the Three Roles

### $L_i$: Legal Eligibility

**What it earns:**
- event exists in the legal future space;
- rule-exact;
- instrument-independent.

**What it does not earn:**
- plausibility;
- producer preference;
- consequence;
- Heat contribution.

### $E_i$: Producer-Conditioned Observation

**What it earns:**
- event appears in the particular observed continuation/support set;
- branch identity can be preserved;
- can be tested for consequence association.

**What it does not earn:**
- instrument independence;
- legal-opportunity completeness;
- intervention sensitivity;
- causality.

**Empirical reason this distinction is required:**
- **T3a-2:** legal opportunity and realization coincided on exposed branches;
- **T3a-3:** legal opportunity existed on five branches while realization occurred on zero.

### $I_i$: Intervention Evidence

**What it may eventually earn:**
- sensitivity of consequence to a controlled legal manipulation involving the event.

**What it does not automatically earn:**
- natural prevalence;
- producer preference;
- causal validity absent matched controls and intervention certification;
- Heat contribution.

## Decision

Unless contradicted by an existing frozen contract, record the provisional T3 architectural decision:

$L_i$, $E_i$, and $I_i$ are not competing definitions of one quantity. They are distinct epistemic stages.

More compactly:
**$L_i$ = eligibility, $E_i$ = observation, $I_i$ = intervention evidence.**

State explicitly that none is itself Heat.
Heat may only be considered downstream of validated consequence evidence and future fusion work.

## Consequence for Next Experiments

- Do not fixture-hunt to make $E_i$ nonzero.
- Do not substitute $L_i$ for $E_i$ after observing zero support.
- Do not use MultiPV merely to rescue T3a-3.
- Do not advance to T3b solely because T3a-2 was positive.
- A future T3a experiment must explicitly declare whether its subject is $L_i$ or $E_i$ before data acquisition.
- If $E_i$ is used, producer/configuration is part of the variable's identity.
- A future intervention protocol must receive a separate hypothesis identifier and evidence level.

## Next Unresolved Experimental-Design Question

What preregistered design can independently test consequence association without selecting fixtures for likely single-PV realization and without conflating legal availability with producer realization?
