# T3b-4 Matched-Control Identifiability Feasibility Audit

## The Audit Question

Can legal destination interventions be compared within deterministic rule-exact strata that reduce obvious non-target reply differences without using engine outcomes, target-specific weighting, or post-result tuning?

**Evidence ceiling remains:**
`EvidenceLevel.INTERVENTION_SENSITIVITY`.

A matched design does not automatically earn causal identification.

## Candidate Families Audited

- **Weighted/nearest-neighbor chess distance**: Reject as the first Design-B basis unless independently justified mathematics exists. Hand weights over origin distance, destination distance, piece values, attack counts, etc. create too many researcher degrees of freedom.
- **Same piece type only**: Reject as too loose: two different pieces of the same type can begin from different geometry and perform categorically different actions.
- **Same-origin sibling controls**: Treat as conceptually promising because the event reply and control move the exact same physical chess piece from the exact same starting square.
- **Exact same-origin move-form strata**: Audit as the preferred strict candidate.
- **Post-state/tactical matching (e.g., check status, attack-map similarity, mobility, king safety, SEE, tactical labels, engine-derived concepts)**: Reject for the initial matched design because these are downstream state consequences or consequence proxies and can match away part of the destination effect we are trying to examine.

## Preferred Strict Signature

Define the preferred strict signature for any legal reply $r$ from post-root state $P_i$:

$$B_{strict}(r \mid P_i) = (o_r, t_r, c_r, k_r, p_r, g_r)$$

where:
- $o_r$ = exact origin square
- $t_r$ = moving piece type
- $c_r$ = capture mode: none | ordinary | en_passant
- $k_r$ = captured piece type or null
- $p_r$ = promotion piece type or null
- $g_r$ = is_castling boolean

All fields must be obtained rule-exactly from $P_i$ and reply $r$.

**No numeric piece values.**

**Do not include:**
- destination square
- target square
- destination file/rank
- move distance
- ray length
- SAN
- check/checkmate status
- attack-map changes
- mobility
- material evaluation
- piece-square values
- SEE
- engine score
- PV
- regret
- T3b-3 S/Q/Delta
- tactical labels

### Exact Matched-Control Stratum

For event reply $c \in C_i(x)$, define its exact matched-control stratum:

$$M_i(c) = \{ n \in N_i(x) : B_{strict}(n \mid P_i) = B_{strict}(c \mid P_i) \}$$

- No distance function.
- No weights.
- No "closest" control.
- No engine tie-break.
- No target-square-dependent tie-break.
- All members of $M_i(c)$ are retained.

### Prospective Strict Matchability

Define prospective strict matchability:

$$P_i, x \text{ is strictly matchable} \iff \forall c \in C_i(x), \mid M_i(c) \mid \ge 1$$

Because the existing destination-event construction uses distinct event origins, same-origin strata for its two event replies are naturally distinct. Do not turn that historical fact into a universal chess claim.

### Semantic Rationale for Fields

- **Same origin**: Binds the exact moving piece and starting geometry.
- **Capture mode**: Prevents a quiet move from being treated as comparable to an ordinary capture or en-passant capture.
- **Captured piece type (without numeric value)**: Controls the most obvious categorical material-action difference among captures.
- **Promotion type**: Prevents ordinary and promotion transitions from being conflated.
- **Castling status**: Prevents ordinary king moves and castling transitions from being conflated.

Explicitly acknowledge that captured-piece-type matching narrows the question. A future matched experiment would test destination sensitivity conditional on coarse move/material form, not all ways in which occupying a destination square can matter.

## Bundled Differences Not Isolated

Freeze the residual bundled differences that matching does not isolate:
- destination itself
- traversed/path squares
- blocker changes
- attack/defense geometry
- checking relations
- king exposure
- pawn-structure geometry
- resulting legal affordances
- tactical continuations
- other state differences caused by choosing that destination

Therefore even an exact same-origin match does not justify:
**destination square alone caused the consequence difference.**

The strongest possible future interpretation remains:
**consequence estimates are sensitive to legal destination variation within exact same-origin move-form strata.**

## Admissibility Requirements for Design-B Matching Basis

Freeze these admissibility requirements for any Design-B matching basis:
- **RULE-EXACT**
- **DETERMINISTIC**
- **OUTCOME-BLIND**
- **TARGET-BLIND** except for the already-defined C/N partition
- **WEIGHT-FREE**
- **INTERPRETABLE**
- **COMPUTABLE BEFORE ENGINE OBSERVATION**
- **NO LEARNED PARAMETERS**
- **NO POST-RESULT FEATURE SELECTION**

Explicitly state that equality under $B_{strict}$ is symmetric and deterministic; the procedure forms exact strata rather than optimizing a matching objective.

## No-Rescue Rule

If the strict basis later proves too sparse on an independently generated rule-only feasibility corpus, do not relax fields, introduce weighted nearest-neighbor matching, or select a different signature using T3b-3 results. Design B should be abandoned unless a different basis is independently justified before examining experimental outcomes.

**Additional Freezes:**
- Existing T3b-2/T3b-3 fixtures must not be used to decide whether the strict signature has adequate coverage. Coverage must be tested prospectively on a new domain-separated rule-only feasibility corpus.
- Do not define that corpus yet.
- Do not define S, Q, Δ, a matched statistic, thresholds, sample size, generator domain, or expected effect direction in T3b-4.

## Binary Semantic Decision

**Preferred Design-B candidate**: Exact same-origin move-form strata using $B_{strict}$.

**Status**: Admissible for a prospective rule-only coverage audit, but not yet experimentally validated or demonstrated to have sufficient coverage.

## Unresolved Next Question

Does $B_{strict}$ produce enough strictly matchable destination events on a new deterministic rule-only corpus to make Design B feasible without relaxing the matcher?
