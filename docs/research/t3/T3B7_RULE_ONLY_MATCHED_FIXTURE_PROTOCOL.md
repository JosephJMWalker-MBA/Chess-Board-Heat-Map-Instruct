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

T3b-7 is an independently generated Design-B corpus. Its fixture-generation architecture differs from T3b-2/T3b-3 because it samples intervention states $P_i$ directly rather than deriving them through enumerated White roots.

Therefore freeze:
A future difference between T3b-3 and T3b-7 classifications must not be attributed solely to the comparator change. T3b-7 independently tests the matched Design-B estimand under its own preregistered corpus.

This does not alter either experiment.

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

At every scanned $P_i$, perform these steps in exactly this order:

### A. Rule-only event discovery

Enumerate the complete Black legal reply universe $R_i$.
For every represented destination square $s$, define:
$$C_i(s) = \{r \in R_i : \text{destination}(r) = s\}$$

Construct all destination squares satisfying:
- $|C_i(s)| = 2$
- event replies have distinct origins
- neither event reply is a promotion
- $m_1 \ge 2$
- $m_2 \ge 2$

using the frozen $B_{strict}$.

Do not apply historical exposure, prior-design-state exclusion, or accepted-suite uniqueness while determining this candidate-square set.

### B. Target freeze

If the rule-only candidate set is nonempty:

`target_square = min(candidate_squares)`

using ASCII lexicographic square names.

Once chosen, this target is final for that scanned $P_i$.

Construct its $C, c_1, c_2, M_1, M_2, H_1, H_2, O_i$ and required child FENs.

### C. Identity gates

Only after target selection apply:
- prior engine-exposure exclusion;
- prior-design-state exclusion;
- accepted-suite $P_i$ uniqueness;
- accepted-suite child uniqueness.

If the selected target fails any identity gate:
reject the entire scanned $P_i$ and continue to the next odd $p$ in the same trajectory.

Do not fall back to the second-smallest qualifying destination at that same state.

Prior-data identities may exclude a prospectively selected state, but may not choose among otherwise qualifying event identities within that state.

### D. Distinguish invariant failures from eligibility failures

Under frozen semantics, distinct event origins plus origin-bearing $B_{strict}$ imply $H_1 \cap H_2 = \emptyset$.

Still verify this mechanically.

If it fails:
`MATCHER_DISJOINTNESS_INVARIANT_FAILURE`

Abort manifest generation rather than treating the state as merely ineligible or trying another destination.

Likewise, malformed legal-reply identity, impossible $B_{strict}$ field consistency, `python-chess` version mismatch, or noncanonical child reconstruction is a global generation/integrity failure—not a reason to skip to another event.

For every $r \in O_i$, materialize and persist exact:
$P_{i,r} = \text{ApplyReply}(P_i, r)$
using six-field canonical FEN.

Retain terminal children; do not replace a fixture because a required child is terminal. Later mate typing makes the fixture non-evaluable under T3b-6, with no mate-to-CP conversion.

## 5. Prior-Data Separation

### Exact prior-engine-exposure extraction

Preserve the historical pre-T3b-3 exposure basis exactly as frozen by T3b-2:
- exact 15 T3a source files;
- exact source SHA-256 values;
- exact field extraction rules;
- canonicalization with:
```python
chess.Board(fen).fen(
    shredder=False,
    en_passant="fen",
)
```

Require:
- unique canonical count = 414
- digest = `a4342f713a22ccc3c4790fcc220136b2f78f16e5f014d7a195f26d6fd8842476`

No additional historical source may enter that frozen component.

Augment it from immutable T3b-3 raw execution:
`tests/fixtures/t3b3/t3b3_raw_execution.json`
SHA-256 = `9333f9d26480f43f4d64846be498f720892d93d73da5127296e067653b476d6b`

Extract only:
`fixtures[*].observed_replies[*].child_fen`

Require mechanically:
- actual_search_count = 362
- total extracted observed child records = 362

For each fixture require:
`sorted(observed_replies[*].uci) == sorted(legal_reply_ucis)`

Canonicalize only the extracted `child_fen`.

Do not read or use:
outcome, type, value, score, classification, or S/Q/Delta for fixture selection.

Persist in the future manifest:
- `pre_t3b3_engine_exposure_count`
- `pre_t3b3_engine_exposure_digest`
- `t3b3_observed_child_raw_count`
- `t3b3_observed_child_unique_count`
- `t3b3_observed_child_digest`
- `combined_prior_engine_exposure_unique_count`
- `combined_prior_engine_exposure_digest`

Define each digest as SHA-256 of:
`("\n".join(sorted(canonical_fens)) + "\n").encode("utf-8")`

### Exact prior-design-state extraction

From frozen T3b-2 manifest:
`docs/research/t3/t3b2_fixture_manifest.json`
SHA-256 = `27321ceb4bf5c48716d836f9d4433c017be3a127e94b6d1508bd8973e0d23bc0`

extract only:
`fixtures[*].intervention_fen`

Require exactly 12 records.

From frozen T3b-5 coverage artifact:
`docs/research/t3/t3b5_coverage_artifact.json`
SHA-256 = `642006581ce870f0ab0eb4fea6ddeadb07b9796b653bdc7afefa3e09492ecceb`

extract only:
`trajectory_records[*].sampled_fen`

where the key exists and value is non-null.

Require:
- trajectory_count = 256
- TERMINATED_BEFORE_SAMPLE count = 3
- extracted sampled_fen count = 253

Do not use:
destination_events, replies, signature_strata, strictly_matchable*, M_2, matchability counts, or descriptive distributions in T3b-7 selection.

Canonicalize the extracted FEN strings and persist separate plus combined prior-design-state counts/digests in the future manifest.

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

Do not use Python `assert` for semantic/integrity gates in the future generator; preregister explicit runtime failures with stable failure codes.

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
