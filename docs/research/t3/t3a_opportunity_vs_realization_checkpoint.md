# T3a Opportunity vs. Realization Checkpoint

## Exact Completed State

- **T3a-1:** `INCONCLUSIVE` / `INSUFFICIENT_OBSERVED_PV_LENGTH`.
- **T3a-2:** `SUPPORTED`, realized-event partition 5 vs 14, D=27.0, M=3, A(x)=5.
- **T3a-3:** `INCONCLUSIVE` / `INSUFFICIENT_PARTITION_CARDINALITY`, realized-event partition 0 vs 16, D=null, M=null, A(x)=0.

## Conceptual Distinction

Define three separate objects:

- $L_i(x) = 1$ iff event $x$ is a rule-exact legal immediate opportunity after root $i$.
- $E_i(x) = 1$ iff event $x$ is actually realized in the frozen search-derived continuation after root $i$.
- $R_i$ is typed root consequence/regret.

State explicitly:
**LEGAL OPPORTUNITY != SEARCH REALIZATION != CONSEQUENCE**

### Record
- T3a-2 had $L_i = E_i$ on the five exposed roots, so its positive association cannot identify realization-specific information independently of legal opportunity/root mechanism.
- T3a-3 had five preregistered legal opportunities but zero search realizations, establishing that legal availability does not imply single-PV realization.
- T3a-3 therefore does not falsify the T3a-2 association; the realized-event statistic was not identifiable because one partition was empty.
- Do not retrospectively compute an $L_i \leftrightarrow R_i$ classification on T3a-2 or T3a-3 and present it as confirmatory evidence. Such analysis was not preregistered.

## Acquisition Interpretation

A single PV is a producer-conditioned observation. Therefore $E_i(x)$ is conditional on producer/search configuration and may have zero support even when $L_i(x)$ is nonzero.

Preserve the consequence-association ladder: none of this authorizes intervention sensitivity, causality, Heat contribution, or general prevalence claims.

## Methodological Choices

Without implementing or selecting among them yet, the next methodological choices are:

1. **Continue testing single-PV realization $E_i$, accepting zero-support experiments as legitimate outcomes.**
   - *Scientific question:* Does the single strongest producer-realized continuation containing an event associate with regret?
   - *Confound/dependency:* Highly dependent on narrow engine policy; frequently produces zero-support inconclusive experiments.

2. **Preregister legal opportunity $L_i$ as a distinct consequence-association variable.**
   - *Scientific question:* Does the mere legal availability of a future event correlate with consequence, regardless of evaluation choice?
   - *Confound/dependency:* Abandons actual search evidence in favor of raw rule mechanics, failing to distinguish between strong threats and blunders.

3. **Acquire a preregistered top-k/MultiPV support set.**
   - *Scientific question:* Does the presence of an event across a broader set of plausible continuations associate with root regret?
   - *Confound/dependency:* Support becomes heavily candidate-set and instrument dependent, destroying the simplicity of a single objective continuation.

4. **Move to a legal matched intervention that evaluates an event whether or not the producer naturally realizes it — the T3b direction.**
   - *Scientific question:* What is the isolated consequence effect of forcing the event to occur compared to an equivalent history where it is omitted?
   - *Confound/dependency:* Alters the natural observation, requiring robust baseline matching to isolate the event from the intervention's artificial constraint.

*Do not use fixture hunting (manually searching for a position where the engine naturally selects the event) as a solution to zero event support.*

## Unresolved Decision

Is the object ChessHeat ultimately needs the consequence of a legally available future event, the consequence associated with a producer-realized future event, or an intervention-defined event effect?
