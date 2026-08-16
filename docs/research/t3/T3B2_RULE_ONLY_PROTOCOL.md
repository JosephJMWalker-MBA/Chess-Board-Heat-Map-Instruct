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

At each generated game state:
1. the initial position is $p=0$;
2. after exactly $p$ half-moves, inspect the current board;
3. if $12 \leq p \leq 80$, test that current board for fixture eligibility before selecting move $p+1$;
4. if $p=80$, stop the game after that scan;
5. otherwise, if the game is nonterminal, the hash string `T3B2_V1:<g>:<p>` selects move $p+1$.

Freeze legal move construction exactly as:
`sorted(move.uci() for move in board.legal_moves)`

SHA-256 the exact domain string.
use `int(digest_hex, 16) % len(sorted_legal_moves)`.

Require the fixture-generation environment to use:
`chess.__version__ == "1.11.2"`

If not, stop before manifest generation rather than silently changing generator semantics.
Record Python version as provenance but do not use it as a selection variable.

Root $P$, selected post-root $P_i$, and every derived child $P_{i,r}$ used for identity must be serialized with:
`board.fen(shredder=False, en_passant="fen")`

Reconstruct each scanned position from that FEN before eligibility testing so generated repetition history cannot silently enter fixture semantics.
No implicit/default `board.fen()` calls may define experimental identity.

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

Accepted fixtures must have unique exact six-field:
- root $P$ FENs; and
- selected intervention-state $P_i$ FENs.

If a candidate at some $p$ duplicates either an already accepted root FEN or intervention-state FEN, it is not accepted; continue scanning later $p$ in the same game $g$.

The phrase "first qualifying fixture in game $g$" therefore means the first candidate satisfying all rule-only eligibility, prior-exposure, and uniqueness gates.
Do not abandon a game merely because an earlier otherwise-qualified candidate was duplicate/exposure-excluded.

Within game $g$, accept the first scanned $p$ satisfying all gates, using the tuple tie-break above, then stop scanning that game and continue to $g+1$.

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

Enumerate in this protocol the literal committed paths and SHA-256 digests of every historical T3 raw engine-observation artifact used to construct the exposure set.
Include all applicable T3a-1, T3a-2, T3a-3, and twelve T3a-4 raw observations.

- `tests/fixtures/t3a1_fixture.json` (151a5ad4414ef6caadf4251441b72dfbe934fa0d05bb57aa4dd03c6107f61bf5)
- `tests/fixtures/t3a2_fixture.json` (ec55f31c873292aaefe2229a8b197458b678e6bb3617d6094b22068b8240a1b1)
- `tests/fixtures/t3a3_fixture.json` (8a0f700123697df9892914a7f38f56efbfe09945f2d7752479895a57a70cdf5a)
- `tests/fixtures/t3a4/raw/t3a4_f00.json` (dd102d9b7826dededa21ff54c72e9d92a7350f94a4bce82fff517b5b52cd685d)
- `tests/fixtures/t3a4/raw/t3a4_f01.json` (9601744071efd9b6d39ff94110f8f22b369ad35afc6e8db7f1278a70ed64e4eb)
- `tests/fixtures/t3a4/raw/t3a4_f02.json` (cfa55403c8053e2f2b84bcccec745e150cc261ff1566c6ae87b49dd6ee66d855)
- `tests/fixtures/t3a4/raw/t3a4_f03.json` (71a5927f427f072a65c767a7a75dbedff9b874b3b2a79a324976bf554d6a5e98)
- `tests/fixtures/t3a4/raw/t3a4_f04.json` (f7478bde4c1cd624c4a01c9b2ed1b0601defef0f0888fff91eff1359077cc748)
- `tests/fixtures/t3a4/raw/t3a4_f05.json` (2d0b40d8ca65de1447619c7beee8ba33d0ffb9165eb4012ae8f30df79c2dfd82)
- `tests/fixtures/t3a4/raw/t3a4_f06.json` (2f70e07e98d1a72611f932d815e8339f0bbd1a821ff89cd181f9335f3fe633a0)
- `tests/fixtures/t3a4/raw/t3a4_f07.json` (9d63d91803f9b769ecc3caf8ced4868c7951f461ad326010e85ece0944e7b976)
- `tests/fixtures/t3a4/raw/t3a4_f08.json` (c71be07ec2299159bf86bc2a1454af16513a12261d2b7b46e17f650a40b63031)
- `tests/fixtures/t3a4/raw/t3a4_f09.json` (f3c284a6dfc3f6260aa2fa84a0b26c4046b9a465c52218ce3c14174d24691070)
- `tests/fixtures/t3a4/raw/t3a4_f10.json` (ffa4fa05fc6e251f2e8d3d7a0f536e548717d503d27801b7b08646420fd9bfd7)
- `tests/fixtures/t3a4/raw/t3a4_f11.json` (37cfc3b58962aeeeecc4723d58ef63b5c9ec00e6f588d9c37c53ba9e41368641)

T3a-1
source: `tests/fixtures/t3a1_fixture.json`
root engine-observed state: top-level `fen`
post-root engine-observed states: every `observations[*].resulting_fen`

T3a-2
source: `tests/fixtures/t3a2_fixture.json`
root engine-observed state: top-level `fen`
post-root engine-observed states: every `observations[*].resulting_fen`

T3a-3
source: `tests/fixtures/t3a3_fixture.json`
root engine-observed state: top-level `fen`
post-root engine-observed states: every `move_observations[*].resulting_fen`

T3a-4 fixtures f00..f11
source: corresponding `tests/fixtures/t3a4/raw/t3a4_fXX.json`
root engine-observed state: top-level `fen`
post-root engine-observed states: every `move_observations[*].resulting_fen`

The exclusion set must contain, at minimum:
- each historical experiment root FEN directly engine-observed;
- every historical legal-root resulting FEN that was directly passed to the engine for evaluation.

State explicitly:
- `principal_variation`, `parsed_pv`, and positions reached inside a PV are not added to the historical exposure set merely because they appeared in an engine-returned line; they were not separate root states passed to the engine for evaluation by these experiments.
- The top-level root FEN was separately engine-observed because the historical harness performed a baseline evaluation.
- Each stored `resulting_fen` was separately engine-observed because the historical harness evaluated that post-root board.

Canonicalize every historical FEN solely for identity comparison by:
`chess.Board(historical_fen).fen(shredder=False, en_passant="fen")`

Do not use scores, regrets, PVs, classifications, event membership, or result direction.
Define "previously engine-observed state" only through this frozen source/field extraction contract; do not permit future interpretation of that phrase.

Reject a candidate fixture if any of the following canonical FENs belongs to the frozen historical exposure set:
- generated root $P$;
- selected post-root intervention state $P_i$;
- any legal-reply child $P_{i,r}$ that T3b-2 would subsequently evaluate.

This prevents the measured child consequence states themselves from being prior T3 engine exposures.
This exclusion is about prior experimental exposure, not prior result direction.
Bind the exact prior-artifact sources used to construct this exclusion set in the eventual manifest generator.
Do not inspect prior scores/results during generation.

## 9. Freeze History Semantics

Generated move history is selection provenance only.
The exact six-field root FEN and exact post-root FEN are authoritative experimental states.

The experimental intervention subject is $P_i$, not the earlier generated White-to-move state $P$.
Therefore future T3b-2 `ExperimentSpec.sufficient_position` must be reconstructed from the exact post-root $P_i$ FEN:
- `side_to_move = black`
- `history_available = false`
- `history_identity = null`
- `variant = standard`
- `spec_version = 2`
- `comparison_perspective = white`
- `hypothesis_identifier = T3b-2`

Persist root $P$ FEN and `white_root_uci` as immutable selection/context provenance, not as substitutes for the intervention state's `SufficientPosition`.
Persist the complete legal reply universe $\mathcal{R}_u$, $C_u$, and $N_u$ in the future manifest.

No repetition claim requiring unavailable history.
Preserve castling, en-passant, halfmove, and fullmove fields exactly.

The manifest must record for every legal reply whether $P_{i,r}$ is terminal by:
`child.is_game_over(claim_draw=False)`
Do not reject or replace a fixture merely because a legal child is terminal.

At execution, if a legal child cannot yield the required typed CP consequence—including rule-terminal/mate outcomes—the fixture remains frozen but becomes non-evaluable under the existing CP-comparability gate.
No synthetic CP value may be assigned.

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

Before any T3b-2 raw output is created, future execution must:
- resolve the actual engine executable;
- compute SHA-256 over the executable bytes;
- start one engine process;
- read the actual UCI engine identity;
- require the reported producer identity to match the preregistered Stockfish 18 identity;
  - actual UCI engine name must equal the exact string "Stockfish 18"
- persist the actual reported identity and binary digest.

If identity verification fails, terminate before experimental acquisition.
Do not infer engine version from filename/path.

Future acquisition must perform:
exactly one 100000-node search for every $P_{i,r}$
in:
fixture index ascending
then Black reply UCI ASCII-lexicographic

There must be:
- no baseline evaluation of $P$;
- no baseline evaluation of $P_i$;
- no preliminary "best move" search;
- no `searchmoves`;
- no MultiPV;
- no extra engine evaluation used for validation;
- no hash reset between children.

Engine initialization/configuration/UCI readiness is not an experimental search.
This is important: do not reuse a harness that performs an unregistered baseline search before evaluating children.

**Freeze the engine-state policy:**
- one uninterrupted engine process;
- no resume;
- no replacement of completed observations;
- no deliberate hash reset between child evaluations.

One process must complete the full frozen acquisition. Failure mid-run is a global acquisition/provenance failure; no resume into the same experiment.
Actual execution output paths must be absent before acquisition starts.

## 12. Freeze CP Comparability

The first T3b statistic operates only on fixtures for which every $Y_{u,r}$ is CP-typed from the frozen perspective.
If any child consequence is mate-typed, keep the fixture permanently in the suite but mark it non-evaluable for the directional-free class statistic.
No mate-to-CP conversion.

## 13. Freeze a Direction-Free Fixture Statistic

**Do not preregister BAD/HIGHER_REGRET or GOOD/LOWER_REGRET.**

For evaluable fixture $u$, define the event class $C_u$ and complement $N_u$.

All classification-relevant arithmetic must use exact rational semantics, not binary floating point.

For a class $C$ and complement $N$, let:
$$P = |C| |N|$$
$$G = \#\{(c,n) : Y_c > Y_n\}$$
$$T = \#\{(c,n) : Y_c = Y_n\}$$

Then calculate $S$ exactly as:
$$S = \frac{|2G + T - P|}{P}$$

*(This is algebraically identical to the already frozen $2|A - \frac{1}{2}|$.)*

Implementations must represent this as an exact reduced rational value—for example `fractions.Fraction` in Python—or perform mathematically equivalent integer cross-multiplication.

Thus:
$$0 \leq S_u \leq 1$$

- $S_u = 0$ means no pairwise ordering tendency between event and non-event replies.
- $S_u = 1$ means complete ordinal separation.

Also record descriptively:
$$\Delta_u = \text{median}(Y \mid C_u) - \text{median}(Y \mid N_u)$$

Define the median of rational values explicitly: odd cardinality = middle sorted value; even cardinality = exact arithmetic mean of the two central values.
Use the same exact-median rule for descriptive $\Delta_u$; CP medians may therefore be half-integers.
Persist human-readable decimal forms only as derived display values. Classification must use the exact values.
Do not use the sign of $\Delta_u$ for classification.

## 14. Freeze Exact Same-Cardinality Combinatorial Calibration

Because $|C_u| = 2$, enumerate every unordered two-reply subset:
$$Z \subset \mathcal{R}_u, |Z| = 2$$

Treat each $Z$ temporarily as a pseudo-event class and its complement as pseudo-N, and compute:
$$S_u(Z)$$
using exactly the same definition. No random permutations and no sampled null distribution.

For combinatorial calibration let:
$$L = \#\{Z : S_u(Z) < S_u(C_u)\}$$
$$E = \#\{Z : S_u(Z) = S_u(C_u)\}$$

and:
$$Q_u = \frac{2L + E}{2 \binom{|\mathcal{R}_u|}{2}}$$

Equality and ordering of $S_u(Z)$ must therefore be exact rational comparisons.

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

Freeze suite thresholds as the exact rationals: $\frac{1}{2}$, $\frac{3}{4}$.

Define:
$$H_{0.75} = \#\left\{u : Q_u \geq \frac{3}{4}\right\}$$

Freeze:
$$H_{0.75} \geq \left\lceil \frac{3}{4} K \right\rceil$$

**Classification:**
- `SUPPORTED` iff $Q_{suite} \geq \frac{3}{4}$ AND $H_{0.75} \geq \lceil \frac{3}{4} K \rceil$
- `WEAK_SUPPORT` iff $Q_{suite} > \frac{1}{2}$ and the `SUPPORTED` criterion is not met
- `FALSIFIED` iff $Q_{suite} \leq \frac{1}{2}$
- `INCONCLUSIVE` iff $K < 8$ or a global provenance/spec/acquisition-validity gate fails

**State explicitly** that $\frac{3}{4}$ is a frozen deterministic development criterion, not a population significance threshold.
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
