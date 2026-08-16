# T3b-7 Rule-Only Matched Intervention Fixture Protocol

## 1. Frozen Bound Identities

- **matcher commit:** `23281ca6d75a239de6f63a6ff542597c1cfc0fc2`
- **T3b-6 initial mathematics commit:** `ad28e5903253b51dc16b2dbdb05085ec63ea4721`
- **T3b-6 corrected/final mathematics commit:** `100e4f20b41b260875fb14901b61bbe51c4fe74e`
- **T3b-5 coverage artifact SHA:** `642006581ce870f0ab0eb4fea6ddeadb07b9796b653bdc7afefa3e09492ecceb`
- **T3b-3 raw execution SHA:** `9333f9d26480f43f4d64846be498f720892d93d73da5127296e067653b476d6b`
- **T3b-2 manifest SHA:** `27321ceb4bf5c48716d836f9d4433c017be3a127e94b6d1508bd8973e0d23bc0`

## 2. Frozen Scientific Question

**Across a deterministic rule-selected corpus, are two-reply destination events unusually consequence-sensitive relative to each event reply's exact same-origin, same-move-form legal alternatives under the frozen T3b-6 matched calibration?**

- **Evidence ceiling:** `INTERVENTION_SENSITIVITY`.
- No isolated destination causality, prevalence, producer-independence, or Heat claim.

## 3. Fixture Generation Domain

Generate future intervention states directly.
The experimental state is $P_i$, a Black-to-move state. Do not introduce a preceding White root merely for historical symmetry with T3b-2.

Use new domain:
`T3B7_MATCHED_V1:<g>:<p>`
with:
$g = 0..9999$

Start every trajectory from standard initial chess.

At each nonterminal state, choose the next move from:
```python
legal = sorted(move.uci() for move in board.legal_moves)
idx = int(
    hashlib.sha256(
        f"T3B7_MATCHED_V1:{g}:{p}".encode("utf-8")
    ).hexdigest(),
    16,
) % len(legal)
```
where $p$ is the number of halfmoves already played.

Scan only:
$p = 13, 15, 17, \ldots, 79$
before selecting move $p+1$.

At each scanned state serialize:
`fen = board.fen(shredder=False, en_passant="fen")`
and reconstruct a fresh `chess.Board(fen)` before any fixture eligibility or matcher computation.

Require:
`chess.__version__ == "1.11.2"`

## 4. Intervention-State Eligibility

$P_i$ must be valid standard chess, Black to move, nonterminal under `claim_draw=False`, and not in check.

No repetition/history claim. Future S1 state uses:
- `history_available = false`
- `history_identity = null`

Enumerate the complete Black legal reply universe $R_i$.

For every represented destination square $s$, define:
$$C_i(s) = \{r \in R_i : \text{destination}(r) = s\}$$

A candidate event qualifies only if:
$|C_i(s)| = 2$
the two event replies have distinct origin squares, and neither event reply is a promotion.

Sort the two event replies by ASCII UCI and call them $c_1, c_2$.

Compute the already-frozen:
$B_{strict}$
and:
$$M_i(c_j; s) = \{n \notin C_i(s) : B_{strict}(n) = B_{strict}(c_j)\}$$

Retain all controls. Do not cap, sample, rank, or choose among them.

Require the T3b-6 calibration-resolution condition prospectively:
$|M_i(c_1; s)| \ge 2 \land |M_i(c_2; s)| \ge 2$

This is fixture eligibility, not a modification of $B_{strict}$.

If multiple destination squares qualify at one scanned $P_i$, choose exactly the ASCII-lexicographically smallest square name.
No engine, tactical, material-value, checking, mobility, SEE, or outcome-based tie-break.

For the selected event define:
$$H_j = \{c_j\} \cup M_i(c_j; s)$$

Require mechanically that $H_1 \cap H_2 = \emptyset$; distinct origins plus origin-bearing $B_{strict}$ should imply this, but verify it rather than assume it.

Future engine observation universe for the fixture is exactly:
$$O_i = H_1 \cup H_2$$

Do not evaluate unrelated replies merely because they belong to $R_i$.

For every $r \in O_i$, materialize and persist exact:
$P_{i,r} = \text{ApplyReply}(P_i, r)$
using six-field canonical FEN.

Retain terminal children; do not replace a fixture because a required child is terminal. Later mate typing makes the fixture non-evaluable under T3b-6, with no mate-to-CP conversion.

## 5. Prior-Data Separation

Prior-data separation must be identity-only.

Reconstruct the frozen historical T3 engine-exposure set defined by the T3b-2 protocol and require its previously frozen 414-state digest:
`a4342f713a22ccc3c4790fcc220136b2f78f16e5f014d7a195f26d6fd8842476`

Then augment prior engine exposure with every child FEN directly evaluated in immutable T3b-3 raw execution:
SHA = `9333f9d26480f43f4d64846be498f720892d93d73da5127296e067653b476d6b`
Do not inspect the corresponding scores while constructing this set.

Separately construct a prior-design-state exclusion set containing:
- every T3b-2 intervention-state $P_i$ from the frozen manifest;
- every non-null sampled FEN from the frozen T3b-5 coverage artifact.

This exclusion is based on identity only.

Reject a candidate if:
- its $P_i$ occurs in either prior-exposure or prior-design-state set; or
- any required future observed child $P_{i,r}, r \in O_i$ occurs in either set.

Thus no T3b-5 sampled FEN becomes either a Design-B fixture or a future engine-observed matched child.

Do not inspect T3b-5 matchability counts, event identities, or FEN contents for any purpose other than exact identity exclusion.

## 6. Suite Construction

Accept at most one fixture per generated trajectory.
Within game $g$, accept the first odd scanned $p$ satisfying every frozen gate. Then stop that trajectory.

Require all accepted $P_i$ FENs unique.

Require all required observed child FENs $P_{i,r}$ unique across the entire accepted suite. If a candidate introduces a duplicate child identity, reject that candidate and continue scanning later odd $p$ in the same trajectory.

Freeze:
`suite_size = 16 fixtures`

Accept the first 16 game indices containing qualifying fixtures.

If $g=9999$ is exhausted first:
`INSUFFICIENT_CALIBRATION_ADMISSIBLE_MATCHED_FIXTURES`
and no engine may be invoked.

Do not enlarge the domain, reduce $m_j$, relax the matcher, permit singleton controls, change target selection, or reuse T3b-5 positions as rescue.

## 7. Freeze Future Evaluability

A fixture is evaluable only if every required observation in:
$H_1 \cup H_2$
is CP-typed from the frozen White perspective.

Any required mate-typed result:
`NON_CP_MATCHED_CHILD_PRESENT`
with that fixture retained but $D, S, Q = \text{null}$.
No replacement after engine observation.

Freeze the future minimum:
`K_min = 12 evaluable fixtures`

**Justification:**
The 16-fixture bounded development suite permits at most four type-ineligible fixtures while requiring at least 75% of the frozen suite to remain evaluable. This is an operational completeness rule, not a statistical power or significance threshold.

If $K < 12$, final suite classification is:
- `INCONCLUSIVE`
- `INSUFFICIENT_TYPED_MATCHED_FIXTURES`

Do not replace mate-containing fixtures.

## 8. Frozen Mathematical Analysis

Freeze the mathematical analysis by reference to T3b-6.

Do not redefine $D_j, S_j, S^{match}_u, \Omega_u, Q_u, Q_{suite}, H_{.75}$, or their thresholds in a different form.
Restate them exactly enough for a self-contained protocol and bind final mathematics to commit:
`100e4f20b41b260875fb14901b61bbe51c4fe74e`

Classification remains:
- **SUPPORTED:** $Q_{suite} \ge 3/4$ AND $H_{.75} \ge \lceil 3K/4 \rceil$
- **WEAK_SUPPORT:** $Q_{suite} > 1/2$ AND SUPPORTED unmet
- **FALSIFIED:** $Q_{suite} \le 1/2$
- **INCONCLUSIVE:** $K < 12$ OR global provenance/spec/acquisition failure

Exact rational arithmetic only.

## 9. Future Instrument

Freeze the future instrument prospectively for comparability with T3b-3:
- producer UCI name = exactly "Stockfish 18"
- Threads = 1
- Hash = 16 MB
- nodes = 100000 per required child
- comparison perspective = white

Actual executable path and binary SHA must be observed and persisted at execution; never inferred from filename.

Future acquisition must use one uninterrupted engine process, no resume, no hash reset, no baseline $P_i$ search, no MultiPV, no searchmoves, no preliminary search, and exactly one search per required child in:
1. fixture index ascending
2. then required reply UCI ascending

Engine execution is not authorized by this protocol commit.

## 10. Two Remaining Boundaries

Freeze:
1. T3b-7 protocol commit
2. -> deterministic rule-only manifest + independent firstness/integrity reconstruction
3. -> separate explicit engine authorization/execution

The next task after this protocol passes review will generate the manifest only.

---
**T3b-7 status:**
PREREGISTERED RULE-ONLY MATCHED FIXTURE PROTOCOL
MANIFEST NOT GENERATED
ENGINE NOT AUTHORIZED
