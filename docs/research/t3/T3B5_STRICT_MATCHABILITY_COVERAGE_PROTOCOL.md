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

For each eligible sampled $P_i$, enumerate the complete legal reply universe:
$R_i$.

For every exact destination square $s$ reached by at least one legal reply, define prospectively:
$x_s = (s, \text{destination}, \text{ply}=1)$

and:
$$C_i(s) = \{ r \in R_i : \text{destination}(r) = s \}$$
$$N_i(s) = R_i \setminus C_i(s)$$

No target is manually chosen.
Every destination represented in the legal reply universe is audited.

For each:
$c \in C_i(s)$,

define:
$$M_i(c;s) = \{ n \in N_i(s) : B_{strict}(n \mid P_i) = B_{strict}(c \mid P_i) \}$$

Note the explicit exclusion:
$n \in N_i(s)$.
A second move with the same destination is not a control for that destination event.

## 4. Freeze strict destination-event matchability

Define:
$s \text{ is strictly matchable in } P_i \iff C_i(s) \neq \emptyset \land \forall c \in C_i(s), |M_i(c;s)| \ge 1$.

This is the direct T3b-4 quantifier.

Do not use:
existence of any $B_{strict}$ stratum with cardinality $\ge 2$
as the primary feasibility object.

That quantity may still be recorded descriptively as sibling-stratum availability, but it cannot contribute to $M$.

## 5. Sample Positions Independently of Matchability

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

## 6. Predetermine the Sampled Ply Before Playing the Game

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

## 7. Freeze Trajectory/Sample Handling

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

## 8. Freeze Base Eligibility

A sampled state is coverage-eligible iff:
- valid standard chess
- Black to move
- nonterminal under claim_draw=False
- not currently in check

If not eligible, record the exact rule-only reason:
`TERMINATED`, `IN_CHECK`, `INVALID`, `WRONG_SIDE_TO_MOVE`

No resampling and no replacement.
Do not require any minimum global legal-reply count beyond legality itself.

## 9. Freeze the Design-B event cardinality question explicitly

Record two separate rule-only coverage counts:

$M_{\ge 1} = \# \{ g : P_i \text{ eligible and contains at least one strictly matchable destination } s \}$
and:
$M_2 = \# \{ g : P_i \text{ eligible and contains at least one strictly matchable destination } s \text{ with } |C_i(s)| = 2 \}$

The second count preserves the cardinality structure used by T3b-2/T3b-3.

Primary feasibility criterion must use $M_2$:
`FEASIBLE_FOR_MATCHED_PROTOCOL_DESIGN` iff $M_2 \ge 12$
`NOT_FEASIBLE_UNDER_FROZEN_COVERAGE_BUDGET` iff $M_2 < 12$

Preserve the already frozen threshold 12.
$M_{\ge 1}$ is descriptive only and cannot rescue failure of $M_2$.

Rationale:
T3b-5 is auditing whether Design B can tighten the already-studied two-reply destination-class intervention without changing the subject merely because matching is sparse.
If future research wants a singleton destination-event Design B, that requires a separate semantic/preregistration decision rather than silently deriving it from this coverage audit.

## 10. Freeze destination-event measurements

For every eligible sampled state record, rule-only:
- every represented destination square
- $C_i(s)$ reply UCIs
- $|C_i(s)|$
- for every $c$ in $C_i(s)$:
    - exact $B_{strict}(c)$
    - complete $M_i(c;s)$ control UCI set
- whether every $c$ has $\ge 1$ control
- destination strictly_matchable boolean

Also retain the existing descriptive whole-position signature-stratum information if desired.

Record per state:
- number of represented destination events
- number of strictly matchable destination events
- number of strictly matchable destination events with $|C|=2$
- has_any_strictly_matchable_destination
- has_any_strictly_matchable_two_reply_destination

No engine quantities or downstream tactical properties.

## 11. Correct the aggregate definition

Replace the old M everywhere with primary:
$M = M_2$.

Future output must report:
$256, N_{eligible}, M_{\ge 1}, M_2$.

Report:
$M_{\ge 1} / 256, M_2 / 256$
only as deterministic development-corpus fractions.

## 12. Freeze Separation from the Later Experiment

The T3b-5 coverage corpus is design data only.

Any later Design-B outcome experiment must use:
- a new domain-separated generator;
- different exact FEN identities;
- a new preregistered fixture-selection protocol;
- no T3b-5 sampled position as an experimental fixture.

No Stockfish observation may ever be added to the T3b-5 coverage artifact.

## 13. Preserve no-rescue behavior

If:
$M_2 < 12$
Design B fails this frozen operational feasibility audit.

Do not rescue it using:
- $M_{\ge 1}$;
- singleton event classes;
- relaxed $B_{strict}$;
- later plies;
- more trajectories;
- weighted matching;
- T3b-3 outcome information.

The next scientific step becomes Representation Audit unless a genuinely independent matching basis is justified without reference to outcome data.

If:
$M_2 \ge 12$
then only this is earned:
$B_{strict}$ has sufficient rule-only availability to justify designing a separate matched-control intervention protocol.

This does not authorize an engine run by itself.

## 14. Two-Boundary Process

**Require:**
coverage protocol commit $\rightarrow$ rule-only coverage artifact + independent reconstruction commit.

No engine boundary exists because T3b-5 is permanently engine-free.

After the protocol commit, the next task will mechanically generate the 256 predetermined samples and independently reconstruct the coverage result.

Do not generate them in this task.
