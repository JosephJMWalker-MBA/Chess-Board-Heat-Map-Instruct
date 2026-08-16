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

For game index $g = 0, 1, 2, \dots$ and ply $p$:
1. obtain all legal moves;
2. sort their UCI strings lexicographically;
3. compute: `SHA256("T3A4_V1:<game_index>:<ply>")`;
4. interpret the digest as an unsigned integer;
5. choose: `digest_integer % legal_move_count`.

This produces a deterministic pseudo-random legal move without Python RNG/version dependence.
Start a new generated game if terminal.

Scan generated positions only after a preregistered minimum ply, suggested: `ply >= 12` and before: `ply <= 80`.

**Do not inspect Stockfish while designing or running this generator.**

## Rule-Only Fixture Acceptance

A position may enter the corpus only if all of the following are determinable through python-chess without engine evaluation:
- valid standard-chess position;
- White to move;
- nonterminal under the FEN-defined state;
- White is not currently in check;
- every legal White root results in a position where Black has at least one legal reply;
- at least one non-king White piece currently occupies a square $s$ for which Black has a legal capture opportunity;
- considering all legal White roots, at least two roots preserve a legal Black capture onto the original target square $s$;
- at least two roots remove that immediate capture opportunity;
- no different White piece can move onto $s$ under a legal root in a way that makes $(s, \text{capture})$ ambiguous with respect to the preregistered target;
- the exact target/event can therefore be represented unambiguously as: $x_f = (s_f, \text{capture}, \text{ply}=2)$.

These are $L_i$-based fixture eligibility conditions only.
They must not be interpreted as observed $E_i$ membership.

If more than one target square satisfies the criteria in a position, choose one through a deterministic rule fixed in the protocol, such as lexicographically smallest square name. Do not choose based on chess attractiveness or likely engine behavior.

## Corpus Selection

Accept the first 12 unique qualifying FENs produced by the frozen deterministic stream.

- No manual substitutions.
- No rejection because:
  - the position looks ugly;
  - the expected effect seems small;
  - a target piece has low value;
  - the eventual engine may not choose the capture;
  - the mechanism resembles or differs from T3a-2/T3a-3.

Exact T3a-2 and T3a-3 FENs must not be inserted manually and should be excluded if encountered exactly, because they are already observed development fixtures.

## Position Semantics

Every accepted fixture must preserve a real `SufficientPosition`.

Treat the generated FEN as the experiment's authoritative start state and explicitly represent history availability according to the S0 contract.
Do not silently infer repetition history unavailable from FEN.
Keep halfmove/fullmove/castling/en-passant fields exactly.

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

A fixture is realization-informative only if, after complete observation:
$|E=1| \ge 2$ and $|E=0| \ge 2$.

A fixture with all-zero, all-one, or insufficient partition cardinality remains permanently in the suite but contributes no directional association statistic. It must be recorded as uninformative for the corpus association test, not deleted/replaced.

## Corpus-Level Identifiability Gate

**Freeze:**
At least 3 of the 12 fixtures must be realization-informative.

Otherwise the entire T3a-4 association test is:
`INCONCLUSIVE` / `INSUFFICIENT_REALIZED_EVENT_SUPPORT_ACROSS_CORPUS`.

This is an acquisition result, not a failed fixture-selection problem.
Do not expand to MultiPV or replace fixtures afterward.

## Fixture-Level Consequence Statistic

For every informative fixture $f$, compute:
$D_f = \text{median}(R_{fi} \mid E_{fi} = 1) - \text{median}(R_{fi} \mid E_{fi} = 0)$

and:
$M_f = \min(R_{fi} \mid E_{fi} = 1) - \max(R_{fi} \mid E_{fi} = 0)$.

Retain typed CP/mate rules from T3a-2/T3a-3. No mate-to-CP conversion.
A fixture containing incompatible typed consequences is non-evaluable for directional association and remains recorded.

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
