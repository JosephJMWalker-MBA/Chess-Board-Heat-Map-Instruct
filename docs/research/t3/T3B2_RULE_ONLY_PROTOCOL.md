# T3b-2 Rule-Only Fixture and Statistic Protocol

This document establishes the first T3b experimental protocol and the first of two required pre-engine boundaries.

## 1. Scientific Question

**Freeze:**
Across a deterministic rule-selected corpus, does membership in a preregistered legal immediate destination-square reply class partition intervention consequence estimates more strongly than typical same-cardinality reply classes from the identical post-root state?

**Subject:**
legal reply class membership under ApplyReply

**Evidence Ceiling:**
`EvidenceLevel.INTERVENTION_SENSITIVITY`
No isolated event causality, square causality, producer preference, natural prevalence, or Heat claim.

## 2. Freeze the First Event Type

For the first T3b experiment use:
$$x_u = (s_u, \text{destination}, \text{ply}=1 \text{ relative to } P_i)$$

*(This corresponds to historical T3a branch-relative ply 2).*

A reply realizes $x_u$ iff its exact legal destination square is $s_u$.

**Do not use** engine output, SAN semantics, score, PV, regret, or producer choice to assign event membership.

*Record:* Destination is the first T3b subject because it is rule-exact, directly spatial, and direction-neutral. It is not being declared a privileged Heat primitive.

## 3. Freeze the Class Structure

For fixture $u$, require:
$$|\mathcal{R}_u| \geq 6$$

Select only intervention units for which exactly two legal replies realize the target event:
$$|C_u(x)| = 2$$

and therefore:
$$|N_u(x)| = |\mathcal{R}_u| - 2 \geq 4$$

Require the two C replies to:
- have distinct UCI identities;
- originate on distinct squares;
- not be promotion alternatives of one pawn move.

The purpose is to ensure event membership is instantiated by more than one concrete reply identity, rather than making C synonymous with one move.

## 4. Freeze Deterministic Position Generation

Use a new domain-separated generator:
`T3B2_V1:<g>:<p>`
encoded as UTF-8 with no whitespace/newline.

**Freeze:**
$g = 0, 1, \dots, 9999$

For each game $g$:
1. begin from the standard initial position;
2. $p$ is the number of already-played half-moves;
3. scan only $12 \leq p \leq 80$;
4. stop the game after scanning $p=80$;
5. use `board.is_game_over(claim_draw=False)`;
6. generate moves by ASCII-lexicographically sorting UCI strings;
7. SHA-256 the exact domain string;
8. use `int(digest_hex, 16) % len(sorted_legal_moves)`;
9. serialize scanned states exactly with:
   `board.fen(shredder=False, en_passant="fen")`

Reconstruct each scanned position from that FEN before eligibility testing so generated repetition history cannot silently enter fixture semantics.

## 5. Freeze Root-Position Eligibility

A scanned position $P$ is considered only when:
- valid standard chess;
- White to move;
- nonterminal with `claim_draw=False`;
- White is not currently in check.

Enumerate all legal White roots $m_i$ in ASCII UCI order.

For each root, apply it rule-exactly to obtain $P_i$.

$P_i$ is eligible only when:
- valid and nonterminal;
- Black to move;
- Black is not in check;
- Black has at least six legal replies.

Then enumerate the complete Black legal-reply universe $\mathcal{R}_i$.

## 6. Freeze Target Discovery

For each $P_i$, group Black legal replies by exact destination-square name.

A square $s$ qualifies iff:
- exactly two replies have destination $s$;
- those replies originate on distinct squares;
- neither event-realizing reply is a promotion.

For a scanned root position $P$, construct every qualifying tuple:
`(white_root_uci, target_square)`
and choose exactly the ASCII-lexicographically smallest tuple.

**No chess-quality, piece-value, capture-status, checking-status, tactical, or engine-likelihood tie-break is permitted.**

## 7. Freeze One Fixture per Generated Trajectory

Accept at most one fixture from each game index $g$.

Within game $g$, accept the first scanned $p$ containing at least one qualifying tuple, using the tuple tie-break above, then stop scanning that game and continue to $g+1$.

**Freeze suite size:**
`12 fixtures`

Accept the first 12 game indices containing a qualifying fixture.
This intentionally avoids the T3a-4 pattern of collecting many serial snapshots from one generated trajectory.
Do not describe the resulting fixtures as statistically independent random samples. They are deterministic fixtures from 12 distinct generated trajectories.

If $g=9999$ is exhausted before 12 fixtures exist:
`INSUFFICIENT_QUALIFYING_RULE_ONLY_FIXTURES`
and do not invoke an engine.

## 8. Prior-Exposure Exclusion

A candidate root-state FEN or selected post-root $P_i$ FEN that exactly equals a previously engine-observed T3 fixture/state must be rejected based on identity alone.

This exclusion is about prior experimental exposure, not prior result direction.
Bind the exact prior-artifact sources used to construct this exclusion set in the eventual manifest generator.
Do not inspect prior scores/results during generation.

## 9. Freeze History Semantics

Generated move history is selection provenance only.
The exact six-field root FEN and exact post-root FEN are authoritative experimental states.

For S0/S1:
- `history_available = false`
- `history_identity = null`
- `variant = standard`

No repetition claim requiring unavailable history.
Preserve castling, en-passant, halfmove, and fullmove fields exactly.

## 10. Freeze the Consequence Observation

For each legal Black reply $r \in \mathcal{R}_u$:
$$\text{ApplyReply}(P_i, r) = P_{i,r}$$

Future execution evaluates every resulting child state $P_{i,r}$.

Define:
$$Y_{u,r}(\mathcal{J}, \theta)$$
as the typed engine estimate of the resulting child state from frozen White perspective.

**Do not use a naturally selected PV to choose replies.**
Every legal reply belongs to the acquisition universe before engine observation.

## 11. Freeze Instrument Identity Prospectively

Future execution must use:
- Stockfish 18
- Threads = 1
- Hash = 16 MB
- nodes = 100000 per child state
- comparison perspective = white

Producer identity must be persisted from the actual UCI engine identity, not hardcoded into raw data.

Future acquisition must record:
- actual UCI producer name;
- engine binary SHA-256;
- exact options;
- exact node budget;
- exact child-evaluation order;
- instrument-state policy.

**Freeze the acquisition order:**
fixture index ascending
then Black reply UCI ASCII-lexicographic

**Freeze the engine-state policy:**
- one uninterrupted engine process;
- no resume;
- no replacement of completed observations;
- no deliberate hash reset between child evaluations.

If an execution cannot complete in that process, stop as infrastructure/provenance failure rather than resuming into the same experiment.
Actual execution output paths must be absent before acquisition starts.

## 12. Freeze CP Comparability

The first T3b statistic operates only on fixtures for which every $Y_{u,r}$ is CP-typed from the frozen perspective.
If any child consequence is mate-typed, keep the fixture permanently in the suite but mark it non-evaluable for the directional-free class statistic.
No mate-to-CP conversion.

## 13. Freeze a Direction-Free Fixture Statistic

**Do not preregister BAD/HIGHER_REGRET or GOOD/LOWER_REGRET.**

For evaluable fixture $u$, define the event class $C_u$ and complement $N_u$.

Define pairwise ordering:
$$A_u = \frac{1}{|C_u| |N_u|} \sum_{c \in C_u, n \in N_u} \left[ \mathbf{1}(Y_c > Y_n) + \frac{1}{2} \mathbf{1}(Y_c = Y_n) \right]$$

Then define the unsigned rank-separation magnitude:
$$S_u = 2 \left| A_u - \frac{1}{2} \right|$$

Thus:
$$0 \leq S_u \leq 1$$

- $S_u = 0$ means no pairwise ordering tendency between event and non-event replies.
- $S_u = 1$ means complete ordinal separation.

Also record descriptively:
$$\Delta_u = \text{median}(Y \mid C_u) - \text{median}(Y \mid N_u)$$
but do not use the sign of $\Delta_u$ for classification.

## 14. Freeze Exact Same-Cardinality Combinatorial Calibration

Because $|C_u| = 2$, enumerate every unordered two-reply subset:
$$Z \subset \mathcal{R}_u, |Z| = 2$$

Treat each $Z$ temporarily as a pseudo-event class and its complement as pseudo-N, and compute:
$$S_u(Z)$$
using exactly the same definition. No random permutations and no sampled null distribution.

Define the event-class midrank extremeness percentile:
$$Q_u = \frac{1}{\binom{|\mathcal{R}_u|}{2}} \left( \#\{Z : S_u(Z) < S_u(C_u)\} + \frac{1}{2} \#\{Z : S_u(Z) = S_u(C_u)\} \right)$$

This tie convention is mandatory.
If all reply outcomes are tied, $Q_u = 0.5$, not 1.

**State explicitly:**
$Q_u$ is a deterministic finite-set extremeness measure, not a population p-value or significance claim.
It asks whether the rule-defined event pair separates consequence unusually strongly compared with every same-cardinality pair available in the identical legal-reply universe.

## 15. Freeze Suite Evaluability

A fixture contributes $Q_u$ only if:
- the complete legal-reply universe was observed exactly;
- every child has a typed consequence;
- all consequences are CP;
- exact C/N membership still matches the frozen manifest.

Keep every non-evaluable fixture in the 12-fixture result.

Require:
$K \geq 8$ evaluable fixtures.
Otherwise:
`INCONCLUSIVE` / `INSUFFICIENT_TYPED_INTERVENTION_FIXTURES`
No fixture replacement.

## 16. Freeze the Suite Statistic and Classification

For the $K$ evaluable fixtures:
$$Q_{suite} = \text{median}_u(Q_u)$$

Define:
$$H_{0.75} = \#\{u : Q_u \geq 0.75\}$$

**Classification:**
- `SUPPORTED` iff $Q_{suite} \geq 0.75$ AND $H_{0.75} \geq \lceil 0.75 \times K \rceil$
- `WEAK_SUPPORT` iff $Q_{suite} > 0.50$ and the `SUPPORTED` criterion is not met
- `FALSIFIED` iff $Q_{suite} \leq 0.50$
- `INCONCLUSIVE` iff $K < 8$ or a global provenance/spec/acquisition-validity gate fails

**State explicitly** that 0.75 is a frozen deterministic development criterion, not a population significance threshold.
No post-result alternate percentile, effect direction, CP threshold, or statistic.

## 17. Preserve Sign Information Without Making it the Hypothesis

Persist every $\Delta_u$, including sign.
Report whether signs agree or vary.
Opposite-direction fixtures are not discarded and do not independently falsify a direction-free intervention-sensitivity hypothesis.

## 18. Freeze the Two-Boundary Process

Require:
`protocol commit -> rule-only fixture manifest commit -> engine execution`

Stockfish may not evaluate a fixture before both pre-engine commits are pushed.
After this protocol is frozen, the next task will be to generate exactly the deterministic 12-fixture manifest and prove firstness independently.
Do not generate it in this task.

## 19. Forbidden Rescue Paths

- no replacing fixtures because C/N looks tactically strange;
- no selecting positions for expected engine effect;
- no changing destination to capture after results;
- no changing $|C| = 2$;
- no switching to matched-pair Design B after seeing results and calling it the same experiment;
- no MultiPV;
- no engine-informed fixture selection;
- no mate-to-CP conversion;
- no direction rescue;
- no Heat claim;
- no causal-isolation language.

## 20. Exact Claim Boundary

If supported, the strongest permitted statement is:

"Under the frozen intervention instrument, rule-defined destination-square reply classes separated legal-reply consequence estimates more strongly than typical same-cardinality reply classes across the preregistered development corpus."

Also state:

This is intervention sensitivity to legal reply class membership. It does not isolate the destination-square event as the sole causal factor.
