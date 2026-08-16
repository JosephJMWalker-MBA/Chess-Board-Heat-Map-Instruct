# T3a-4 Corpus Protocol

## Scientific Question

**Freeze:**
Across a preregistered corpus selected entirely by deterministic rule-exact criteria before engine evaluation, does the occurrence of a producer-realized immediate spatial event $E_i(x; J, \theta)$ associate with higher within-position root regret?

### Subject
$E_i$, not $L_i$.

### Evidence Ceiling
`EvidenceLevel.CONSEQUENCE_ASSOCIATION`.
No intervention, causal, Heat, or prevalence claim.

## Why This Is the Next Design

**Record:**
- T3a-2 supplied one positive single-fixture $E_i \leftrightarrow R_i$ association.
- T3a-3 showed that rule-exact legal opportunity $L_i$ does not guarantee single-PV realization $E_i$.
- Manually selecting more positions for likely realization would risk fixture hunting.
- Therefore the next independent replication must select a suite before engine evaluation using only rule-exact criteria and retain zero-support fixtures rather than replacing them.

## Corpus Size

**Freeze target suite size:**
12 fixtures.

This is a development mechanism-stress corpus, not a population/prevalence sample.
No fixture may be replaced because its eventual $E_i$ support is inconvenient.

## Deterministic Position Stream

Specify a portable deterministic generator rather than human fixture selection.

Start each generated game from the standard initial chess position.

For each game index $g$:
- start from standard initial position;
- generate until the game becomes terminal or reaches $p=80$;
- after scanning the $p=80$ state, stop that generated game regardless of terminality;
- continue with game index $g+1$ from the standard initial position.

Do not continue unscanned games beyond ply 80.

For selection of move $p+1$, use the exact UTF-8 byte string:
`T3A4_V1:<g>:<p>`
where `<g>` and `<p>` are base-10 integers with no padding, signs, spaces, or additional newline.

Compute SHA-256.
Convert the 64-character hexadecimal digest using:
`int(digest_hex, 16)`

For legal-move ordering, use ordinary Python lexicographic ordering of ASCII UCI strings:
`sorted(move.uci() for move in board.legal_moves)`
The generator must not rely on python-chess iteration order.

Then:
`index = digest_integer % len(sorted_legal_ucis)`
and play the legal move whose UCI is at that zero-based index.

This produces a deterministic pseudo-random legal move without Python RNG/version/byte-order dependence.

Scan generated positions only when $12 \le p \le 80$.
Define $p$ explicitly as the number of half-moves already played from the standard initial position.
Therefore:
- initial position has $p=0$;
- after White's first move $p=1$;
- after Black's first move $p=2$.

Evaluate fixture eligibility on the board after exactly $p$ half-moves have been played, before choosing move $p+1$.
Only states with $12 \le p \le 80$ are scanned.
Because fixtures require White to move, only qualifying even-$p$ states can ultimately be accepted.

**Do not inspect Stockfish while designing or running this generator.**

## Rule-Only Fixture Acceptance

A position may enter the corpus only if all of the following are determinable through python-chess without engine evaluation:
- valid standard-chess position;
- White to move;
- nonterminal under the FEN-defined state;
- White is not currently in check;
- every legal White root results in a position where Black has at least one legal reply;
A candidate target square $s$ is eligible iff:
- at the scanned root state, $s$ contains a non-king White piece;
- enumerate all legal White root moves;
- for at least two resulting positions, Black has at least one legal move whose destination is $s$ and which captures the original target piece still occupying $s$;
- for at least two resulting positions, no such capture of the original target piece on $s$ is legal;
- roots on which the original target moved from $s$ therefore belong to the opportunity-absent class;
- if another White piece moves onto $s$, that root cannot count as preservation of the original-target opportunity and must not make the event identity ambiguous.

The exact target/event can therefore be represented unambiguously as: $x_f = (s_f, \text{capture}, \text{ply}=2)$.

These are $L_{fi}$-based fixture metadata only.
They must not be interpreted as observed $E_i$ membership.

If more than one target square satisfies every rule-only acceptance condition, choose exactly:
`min(eligible_target_squares)`
over algebraic square names in ordinary ASCII lexicographic order.
No piece-value or mechanism tie-break. Do not choose based on chess attractiveness or likely engine behavior.

## Corpus Selection

Define fixture uniqueness by the exact six-field FEN string:
`piece-placement side-to-move castling en-passant halfmove fullmove`

A scanned state whose exact six-field FEN was already accepted is skipped and generation continues.
Do not normalize halfmove/fullmove fields for uniqueness.

Accept the first 12 unique qualifying FENs produced by the frozen deterministic stream.

- No manual substitutions.
- No rejection because:
  - the position looks ugly;
  - the expected effect seems small;
  - a target piece has low value;
  - the eventual engine may not choose the capture;
  - the mechanism resembles or differs from T3a-2/T3a-3.

T3a-2 and T3a-3 exact six-field FENs are excluded if encountered.

## Position Semantics

The deterministic generated move sequence is selection provenance, not retained experiment history.
The accepted six-field FEN is treated as the authoritative experimental start state.

Therefore for the T3a-4 experiment:
`history_available = false`
`history_identity = null`
unless the existing S0 contract mechanically forbids that interpretation.

State explicitly that no repetition claim requiring unavailable pre-FEN history may be made.
Preserve castling, en-passant, halfmove, and fullmove fields exactly from the accepted FEN.

If this interpretation conflicts with an existing frozen S0 requirement, stop and report the conflict instead of generating the corpus.

## Event Variable

For fixture $f$, root $i$:
$E_{fi} = 1$ iff the actual frozen Stockfish continuation contains:
`SpatialEvent(square=s_f, role="capture", ply=2)`.
Otherwise:
$E_{fi} = 0$.

Never derive $E_{fi}$ from $L_{fi}$.
Preserve $L_{fi}$ only as rule-exact descriptive metadata so future work can inspect opportunity/realization divergence without retrospectively changing the hypothesis.

## Instrument

Freeze prospectively for every fixture:
- **Stockfish 18**
- **Threads:** 1
- **Hash:** 16 MB
- **Nodes:** 100000
- **Candidate policy:** `{}`
- **Line source:** `pv`
- **Comparison perspective:** `white`
- **ExperimentSpec.spec_version:** 2

## Fixture-Level Evaluability

Every legal root must expose ply 2.

A fixture with any of the following remains in the 12-fixture manifest but is non-evaluable for directional association:
- at least one root lacks observed ply 2;
- incompatible consequence typing;
- $|E=1| < 2$;
- $|E=0| < 2$.

Such a fixture contributes no $P_f$, but is never replaced.

## Corpus-Level Identifiability Gate

**Freeze:**
The suite is:
`INCONCLUSIVE` / `INSUFFICIENT_REALIZED_EVENT_SUPPORT_ACROSS_CORPUS`
iff fewer than 3 of the 12 fixtures yield valid $P_f$.

This is an acquisition result, not a failed fixture-selection problem.
Do not expand to MultiPV or replace fixtures afterward.
A global provenance/instrument/spec mismatch is separately suite-invalid and must not be treated merely as one non-evaluable fixture.

## Fixture-Level Consequence Statistic

For every informative fixture $f$, compute:
$D_f = \text{median}(R_{fi} \mid E_{fi} = 1) - \text{median}(R_{fi} \mid E_{fi} = 0)$

and:
$M_f = \min(R_{fi} \mid E_{fi} = 1) - \max(R_{fi} \mid E_{fi} = 0)$.

For T3a-4 directional statistics, require all root regrets within an informative fixture to be CP-typed.
If any root regret is mate-typed, that fixture remains recorded but contributes no $P_f$.
No mate-to-CP conversion.

## Corpus-Level Statistic

Do not pool raw roots across positions as though they came from one chess position.

Give each informative fixture one equal-weight directional quantity:
$P_f = \text{median}\{R_{fi} - R_{fj} : E_{fi}=1, E_{fj}=0\}$.
This is the median within-fixture cross-partition regret difference.

Then define:
$D_{suite} = \text{median}_f(P_f)$
and:
$M_{suite} = \min_f(P_f)$.

**Freeze:**
- `SUPPORTED` if $D_{suite} > 0$ and $M_{suite} > 0$;
- `WEAK_SUPPORT` if $D_{suite} > 0$ and $M_{suite} \le 0$;
- `FALSIFIED` if $D_{suite} \le 0$;
- `INCONCLUSIVE` if the corpus-level identifiability/provenance/type/completeness gates fail.

Record every $D_f$, $M_f$, $P_f$, partition size, and zero-support fixture. No fixture may disappear from the report.
Explicitly state that this classification is a deterministic development criterion, not a population-level significance claim.

## Blinding Boundary

**Freeze the order:**
protocol commit $\rightarrow$ deterministic rule-only corpus generation $\rightarrow$ corpus manifest commit $\rightarrow$ engine execution.

There must be two Git boundaries before Stockfish:
1. protocol frozen;
2. exact 12-fixture corpus/event manifest frozen.

Stockfish may not run before both commits are pushed.

## Required Falsifiers

Record explicitly:
- Too few informative fixtures $\rightarrow$ single-PV realization is too sparse under this acquisition design.
- $D_{suite} \le 0 \rightarrow$ the preregistered producer-realized association fails on the corpus.
- Positive median but at least one non-positive $P_f \rightarrow$ only weak support, not robust replication.
- Strong dependence on one mechanism family must be reported and cannot be hidden by pooling.

## Forbidden Rescue Paths

- no hand-picked replacement fixtures;
- no repeated generator seeds until results look better;
- no MultiPV after seeing sparse support;
- no changing target events after engine execution;
- no converting $L_i$ into $E_i$;
- no top-N candidate filtering;
- no changing node budget;
- no Heat claim;
- no T3b causal language.

---

T3a-4 tests whether producer-realized immediate future evidence carries consequence association across a corpus selected without producer knowledge. It does not test legal opportunity as consequence, intervention sensitivity, causal validity, or Heat.
