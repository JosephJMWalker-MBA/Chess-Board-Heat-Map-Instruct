# T3b-5 Strict Matchability Coverage Protocol

## 1. The Feasibility Question

Does the already-frozen $B_{strict}$ basis occur often enough on positions selected independently of matchability to justify designing a future matched-control intervention experiment without relaxing the matcher?

This is a representation/availability feasibility audit, not an intervention-outcome experiment.

- No engine.
- No consequence values.
- No causal claim.
- No Heat claim.

## 2. Bind the Matcher Exactly

**Reference T3b-4 commit:**
`23281ca6d75a239de6f63a6ff542597c1cfc0fc2`

**Freeze without modification:**
$$B_{strict}(r \mid P_i) = (o_r, t_r, c_r, k_r, p_r, g_r)$$

No field may be dropped, added, weighted, or relaxed during this audit.

**Redundant Semantic Consistency Requirements:**
Implementations must verify:
- piece at origin has type $t_r$;
- quiet move implies captured type null;
- ordinary/en-passant capture has a rule-exact captured type;
- en passant captures a pawn;
- nonpromotion implies promotion type null;
- castling flag agrees with python-chess rule semantics.

These are consistency checks, not new matching dimensions.

## 3. Define the Coverage Object Directly on Intervention States

The sampled object is the Black-to-move intervention state:
$P_i$

No preceding White root is needed for the feasibility audit.

For every legal reply $r \in R_i$, compute $B_{strict}(r \mid P_i)$.

Partition the entire legal-reply universe into exact signature strata:
$$S_i(b) = \{ r \in R_i : B_{strict}(r \mid P_i) = b \}$$

**Define:**
$S_i(b) \text{ is matchable} \iff |S_i(b)| \ge 2$.

Any reply in such a stratum has at least one legal same-origin, same-form reply to a different destination.

**Destinations:**
Require distinct destinations mechanically.
Do not choose a target square or event reply during coverage auditing.

## 4. Sample Positions Independently of Matchability

**Freeze exactly:**
game_index $g = 0..255$

One predetermined candidate intervention state per generated trajectory.

**Domain-separated deterministic move stream:**
`T3B5_COVERAGE_MOVE_V1:<g>:<p>`

**Mechanical move-selection rule:**
```python
legal = sorted(move.uci() for move in board.legal_moves)
payload = f"T3B5_COVERAGE_MOVE_V1:{g}:{p}".encode("utf-8")
idx = int(hashlib.sha256(payload).hexdigest(), 16) % len(legal)
```
where $p$ is the number of half-moves already played.

## 5. Predetermine the Sampled Ply Before Playing the Game

Use:
`T3B5_COVERAGE_PLY_V1:<g>`

and:
```python
h = int(
    hashlib.sha256(
        f"T3B5_COVERAGE_PLY_V1:{g}".encode("utf-8")
    ).hexdigest(),
    16,
)
sample_p = 13 + 2 * (h % 34)
```

Therefore:
$sample\_p \in \{13, 15, 17, \dots, 79\}$

and the sampled state is always nominally Black to move.

$sample\_p$ must be determined before any board-state or matchability inspection.
Do not shift it earlier/later because the sampled state is inconvenient.

## 6. Freeze Trajectory/Sample Handling

Begin from the standard initial position.
Generate moves until exactly $sample\_p$ half-moves have been played.

If the game ends before that state:
`TERMINATED_BEFORE_SAMPLE`
Record the trajectory and do not replace it.

At exactly $sample\_p$:
```python
sampled_fen = board.fen(
    shredder=False,
    en_passant="fen",
)
```

reconstruct:
`P_i = chess.Board(sampled_fen)`
so generated repetition history is unavailable to eligibility semantics.

**Require:**
`chess.__version__ == "1.11.2"`

## 7. Freeze Base Eligibility

A sampled state is coverage-eligible iff:
- valid standard chess
- Black to move
- nonterminal under claim_draw=False
- not currently in check

If not eligible, record the exact rule-only reason:
`TERMINATED`, `IN_CHECK`, `INVALID`, `WRONG_SIDE_TO_MOVE`

No resampling and no replacement.
Do not require any minimum global legal-reply count beyond legality itself.

## 8. Freeze Coverage Measurements

For every eligible $P_i$, record only rule-exact quantities:
- canonical six-field FEN
- complete sorted legal reply UCI universe
- reply count
- exact $B_{strict}$ for every reply
- all exact signature strata
- stratum cardinalities
- number of matchable strata
- number of replies belonging to matchable strata
- maximum strict-stratum cardinality
- whether the state has $\ge 1$ matchable stratum

**Optionally record descriptive counts by:**
- moving piece type
- capture mode
- stratum cardinality

but these may not alter eligibility or feasibility classification.

**Do not record:**
- SAN
- engine score
- PV
- check delivered by reply
- mobility after reply
- attack maps
- SEE
- material values
- tactical labels
- T3b-3 statistics

## 9. Freeze the Operational Feasibility Criterion Before Generation

Let:
$M = \# \{ g : \text{the predetermined sampled state is eligible and contains at least one matchable strict stratum} \}$

**Freeze:**
`FEASIBLE_FOR_MATCHED_PROTOCOL_DESIGN` iff $M \ge 12$
`NOT_FEASIBLE_UNDER_FROZEN_COVERAGE_BUDGET` iff $M < 12$

The number 12 is an operational development-feasibility threshold only. It is not a population significance threshold, estimated prevalence requirement, or preregistration of the eventual experiment's sample size.

It asks only whether a bounded 256-trajectory rule-only sample demonstrates at least twelve distinct trajectory-level opportunities for exact matching without relaxing $B_{strict}$.

## 10. Report Coverage Descriptively

Future coverage output must report:
$256, N_{eligible}, M$

and:
$M / 256$
only as a deterministic development-corpus fraction.

Also report the distribution of:
- matchable strata per eligible state
- matchable replies per eligible state
- strict-stratum cardinalities

Do not attach confidence intervals, p-values, population prevalence language, or independence claims.
The 256 trajectories are distinct deterministic trajectories, not a random population sample.

## 11. Freeze Separation from the Later Experiment

The T3b-5 coverage corpus is design data only.

Any later Design-B outcome experiment must use:
- a new domain-separated generator;
- different exact FEN identities;
- a new preregistered fixture-selection protocol;
- no T3b-5 sampled position as an experimental fixture.

No Stockfish observation may ever be added to the T3b-5 coverage artifact.

## 12. Freeze No-Rescue Behavior

If:
$M < 12$
then:
Abandon $B_{strict}$ as operationally too sparse under the frozen audit. Do not remove fields, introduce a distance function, alter sampled plies, scan later positions, increase the 256-game budget, or use T3b-3 results to construct a replacement matcher.

The next scientific step becomes Representation Audit unless a genuinely independent matching basis is justified without reference to outcome data.

If:
$M \ge 12$
then only this is earned:
$B_{strict}$ has sufficient rule-only availability to justify designing a separate matched-control intervention protocol.

This does not authorize an engine run by itself.

## 13. Two-Boundary Process

**Require:**
coverage protocol commit $\rightarrow$ rule-only coverage artifact + independent reconstruction commit.

No engine boundary exists because T3b-5 is permanently engine-free.

After the protocol commit, the next task will mechanically generate the 256 predetermined samples and independently reconstruct the coverage result.

Do not generate them in this task.
