# Measuring the Shape of a Chess Position

## Research report: Milestones 1–8

> **The mathematics needs to earn the color.**

ChessHeat began with an intuitive visualization question:

> **Which squares matter most to what happens next?**

The first sprint turned that question into a measurement research program. The project did not discover a final universal heat formula. It did something more useful: it separated several mathematical objects that had initially been compressed into the word *heat*, tested them independently, falsified multiple human assumptions and fixture hypotheses, exposed weaknesses in the validation process itself, and identified a more precise set of open research questions.

This document records the actual mathematical evolution, experimental process, findings, failures, current implementation limits, and future research program through Milestone 8.6.3. It is intentionally not a product announcement and not a claim that ChessHeat has solved chess pivotality.

---

## 1. Research question

The central hypothesis is:

> **A chess position contains a useful spatial structure of consequence, leverage, hazard, and pivotality that can be measured from legal state changes, engine evidence, and structural geometry.**

The project explicitly rejects the simpler hypothesis that square importance is equivalent to attack density or piece-value-weighted control.

The governing distinction remains:

> **Control != importance.**

A square may be heavily controlled but strategically unimportant. A square may be evenly contested yet highly consequential. Therefore attack maps may be evidence, but they cannot define ChessHeat.

Stockfish is used as a measurement instrument. ChessHeat owns the transformation from engine observations and legal-state geometry into spatial evidence.

---

## 2. Experimental architecture

The reference pipeline is:

`legal chess position -> Python analysis core -> Stockfish adapter -> typed move evidence -> spatial evidence layers -> diagnostic visualization`

The analysis core is deliberately headless. Measurement semantics must remain testable without a user interface.

The research has preserved three principles throughout:

1. **Raw evidence before visualization.** A color is never sufficient provenance.
2. **Typed quantities remain typed.** Mate values are not converted into fake centipawns.
3. **Association is not causality.** Structural events may correlate with good or bad move outcomes without being isolated causes.

---

## 3. Milestone 1 — Engine evidence and the first mathematical correction

The first headless harness evaluates every legal root move under a declared search budget and records FEN, UCI, SAN, origin, destination, captures, promotions, castling, en passant, score type, score value, perspective, and principal variation evidence.

A critical early correction was recognizing that the baseline engine evaluation is already an optimal-continuation quantity. Therefore:

`evaluation_after_move - baseline_evaluation`

is not a clean measure of the consequence caused by the move.

The first useful derived quantity became **regret** or opportunity cost.

For legal root moves `m in M(P)` and a fixed comparison perspective:

```text
E(m)  = engine outcome after choosing m
E*    = best available root outcome
R(m)  = E* - E(m)
```

For centipawn-comparable outcomes:

`R(m)` measures how much value is surrendered relative to the best available choice.

This is not a causal change score. It is a decision-quality / opportunity-cost quantity.

Mate outcomes remain separate because mate distance is not a linear centipawn scale.

### Result

The project moved from a vague notion of "change caused by a move" to an inspectable root-choice sensitivity model.

---

## 4. Milestone 2 — Direct square attribution

The first geographic surface assigns a move's regret evidence to squares directly implicated by that move.

For an ordinary move, direct implication includes:

- origin square;
- destination square.

Special cases preserve additional squares:

- captured square;
- en-passant capture square;
- king and rook origin/destination squares for castling;
- promotion semantics.

Conceptually, for square `s`:

```text
D(s) = {m : s is directly implicated by m}
```

The project does **not** infer that all strategic consequences occur on those squares.

### Result

Direct attribution performed well when the decisive information really was attached to a move endpoint or capture target. It systematically struggled with:

- geometric enablers;
- overloaded defensive obligations;
- discovered pathways;
- long-range rays;
- structural regions larger than the move's origin/destination pair.

This was a useful failure. It demonstrated why destination heat cannot be equated with strategic importance.

---

## 5. Milestones 3–4 — Diagnostic rendering and state delta

The first viewer was intentionally diagnostic rather than polished. It exposed multiple measurement layers and underlying evidence instead of compressing everything into one unexplained color.

Paired-position analysis then introduced a state-transition primitive:

```text
P[t] --m--> P[t+1]
```

with both positions evaluated from the same comparison perspective.

For a metric `X` on square `s`:

```text
Delta_X(s) = X(s | P[t+1]) - X(s | P[t])
```

Missing evidence is not treated as numeric zero. Transition states distinguish evidence that persisted, appeared, disappeared, or was absent in both states.

### Result

The project gained a principled basis for asking:

> **What changed, and where?**

This remains foundational for future teaching applications.

---

## 6. Milestone 5 — Falsification fixtures

Eight predeclared fixture categories were tested across multiple node budgets. The original direct-attribution model showed a characteristic pattern:

- strong on tactical destinations and capture targets;
- partial on some pawn breaks and quiet positional moves;
- weak on soft pins, overloaded defenders, discovered attacks, and pathway geometry.

The exact fixture history is preserved in `tests/fixtures/`.

### Important research corrections

#### F4 was not a valid overloaded-defender fixture

The original F4 hypothesis attributed defensive obligations to a knight geometry that did not actually support those obligations. The fixture was retained historically and later replaced conceptually by a valid dual-defense construction.

The correct lesson is not that ChessHeat "failed overload" on F4. The experiment itself was invalid for that claim.

#### Budget stability is robustness, not proof

Spatial patterns were often stable across 50k, 100k, and 250k node budgets even when raw centipawn values changed. This supports robustness of the observed signal under those budgets. It does not prove that the resulting geography is an intrinsic truth of the position.

### Result

Milestone 5 established the central limitation of direct attribution and justified richer spatial evidence.

---

## 7. Milestone 6 — Principal-variation recurrence

The next hypothesis was that strategically important squares may recur across multiple strong plausible futures even when they are not directly implicated by the root move.

For an admitted candidate set `C(P)` and square `s`:

```text
line_fraction(s)
  = distinct admitted candidate PVs containing s
    / admitted candidate PV count
```

The implementation separately preserves:

- total legal root moves;
- candidate policy;
- admitted candidate count;
- admitted root moves;
- candidate scores;
- candidate regrets;
- aggregated PV count;
- distinct line count;
- visit count;
- earliest ply;
- role-specific recurrence.

A key invariant follows directly from the implementation:

```text
distinct_line_count(s) <= admitted_candidate_count
```

Repeated visits to a square within one PV increase `visit_count`; they do not create additional distinct lines.

The recurrence implementation applies candidate policy before aggregation. It may filter by regret and then by `top_n`.

### Result

Recurrence recovered real future-path geography that direct attribution could not see.

It also produced a major negative finding:

> **Frequency in plausible futures is not the same thing as consequential leverage.**

Balanced or low-amplitude positions can still contain heavily recurring squares.

This later became one of the motivations for separating spatial shape from position-level amplitude.

---

## 8. Milestone 7 — Structural geometry delta

Rather than adding motif-specific detectors for pins, forks, and discovered attacks, ChessHeat introduced a general structural geometry representation `G(P)` containing observable relationships such as:

- attacks;
- defenses;
- sliding rays;
- path squares;
- blockers;
- legal / pseudo-legal mobility.

For move `m`:

```text
Delta_G(P, m) = G(P after m) - G(P)
```

This allowed the system to represent structural effects away from move endpoints.

Examples from development fixtures included:

- a queen ray becoming exposed after a knight vacated a line;
- a rook ray appearing after a bishop left a file;
- legal-mobility changes that distinguish pseudo-legal movement from actual legal freedom.

### Result

Structural geometry fixed a representation problem: important pathways could now exist as evidence even when direct attribution could not reach them.

It did **not** establish causality.

---

## 9. Milestones 7.5–7.7 — Association, confounding, and event bundles

For structural event `e`, the research compared move-outcome distributions for moves that produced the event versus moves that did not.

A typical descriptive association quantity was:

```text
Delta_R(e)
  = median R(m | e occurs)
    - median R(m | e does not occur)
```

or the corresponding mean difference.

This produced an important finding: a geometry event can sharply partition outcomes while still being harmful, incidental, or inseparable from other simultaneous structural changes.

In several fixtures, individual geometry events were perfectly confounded with other events generated by the same root-move subset.

The response was not to invent finer causality. The system grouped perfectly co-occurring events into **event bundles**.

For bundle `B`:

```text
B = {e1, e2, ..., ek}
```

where the constituent events share the same producing-move set.

The bundle retains:

- constituent structural events;
- producing and non-producing moves;
- outcome / regret distributions;
- mean and median regret differences;
- implicated squares / paths;
- confounding status.

### Result

The project adopted a methodological rule:

> **Do not claim finer causal resolution than the data supports.**

Event bundles are regional evidence objects, not proof that every constituent event independently caused the associated outcome difference.

---

## 10. Milestone 8 — Ablation and the failure of a universal linear fusion

Three principal evidence families were compared:

- **A — Direct attribution**;
- **B — PV recurrence**;
- **C — Event-bundle leverage**.

The research also compared pairwise and three-way fusions plus simpler baselines such as attack density and destination regret.

The current `fusion.py` normalizes channel values into within-position ranks and computes simple equal-weight averages over available normalized channels.

This experiment produced two major findings.

### 10.1 No fixed fusion dominated

Different fixtures favored different evidence families. Direct evidence was strongest in some local tactical cases; recurrence helped in some pathway cases; bundle evidence captured some structural changes; combinations sometimes helped but did not establish a universally superior composite.

Therefore the Milestone 8 exit criterion — a composite that demonstrably beats its strongest individual component — has **not** been satisfied.

### 10.2 Rank normalization manufactures relative hotspots

Within-position percentile normalization always produces a hottest relative square when there is any variation, even if the absolute consequence spread is tiny.

This exposed a fundamental distinction:

> **Where is leverage?** and **How much leverage exists?** are different questions.

The project therefore separated:

```text
S(s | P) = spatial shape / localization evidence
A(P)     = position-level decision-leverage amplitude
```

A conceptual renderer may eventually resemble:

```text
H(s | P) = A(P) * S(s | P)
```

but this is an architectural decomposition, not a validated final heat equation.

---

## 11. Typed amplitude and zero optionality

Development experiments explored centipawn decision-spread statistics while preserving mate outcomes separately.

The current sealed helper formalizes the type separation:

```text
A(P) = {A_cp, A_mate, zero_optionality}
```

The implementation accepts a supplied CP-range statistic, keeps mate presence typed, and returns zero decision-leverage amplitude when there is at most one legal move.

This produced another important distinction:

> **Severity != decision leverage.**

A position may be objectively terrible while offering only one legal move. In that case the player has no meaningful choice sensitivity at the root.

Conversely, an apparently ordinary position may have large decision leverage if some legal alternatives are catastrophic.

This was observed repeatedly in development controls whose human "flat" hypothesis was falsified by root-move spread.

---

## 12. ShapeSelectivity-v1

The development corpus showed that raw recurrence and bundle geography can be extremely diffuse. A first explicit attention policy was therefore frozen as `ShapeSelectivity-v1`.

The predicates are:

```text
Direct:
  candidate_fraction >= 0.15

Recurrence:
  earliest_ply <= 2
  AND distinct_line_count >= 3

Bundle:
  producing_move_count >= 3
  AND implicated_region_size <= 15
```

These thresholds were tuned on development / validation evidence. They are not chess laws and must not be treated as untouched discoveries.

Rejected evidence remains valid raw evidence. Selection is not deletion.

The larger principle is:

> **Geographic evidence != geographic relevance.**

### Current implementation caveat

The current `apply_shape_selectivity_v1()` helper is an **ordered first-pass selector**:

1. Direct is checked first;
2. Recurrence second;
3. Bundle third;
4. the first passing channel is returned as the square's channel source.

If no channel passes, the fallback rejection-reason logic currently prioritizes Bundle when Bundle evidence exists, then Recurrence, then Direct.

Therefore the helper does not yet provide a full independent per-channel state record. This matters because forensic prose can incorrectly sound as though a Bundle rejection suppressed Recurrence, when the implementation may simply be reporting one prioritized reason.

This is a specific target for Milestone 8.6.4 and should be corrected or clarified before further model tuning.

---

## 13. Validation methodology: what failed in the experiment itself

The research process generated several failures that are as important as the model results.

### 13.1 One-square "regions" were not sufficient regional validation

A development benchmark described regional coverage, but its formal denominator effectively contained one expected target square per fixture. That did not genuinely validate multi-square corridors or disjoint regions.

Later hostile fixtures intentionally introduced broader and multi-region expectations.

### 13.2 Earlier "holdouts" were not pristine holdouts

Some files described as holdouts or sealed validation were edited or regenerated after evaluation during development. They remain useful evidence but cannot be represented as untouched final validation.

The repository intentionally preserves those historical artifacts rather than renaming history into a cleaner story.

### 13.3 W-v2 was not a pristine one-shot validation

The W-suite was constructed to challenge known assumptions in `ShapeSelectivity-v1`, including:

- deep leverage;
- exactly two supporting lines;
- singleton leverage;
- broad structural regions;
- quiet multi-square leverage;
- recurring but negligible consequence;
- negative controls;
- mate-sensitive choice;
- zero optionality;
- overloaded-defense geometry;
- long corridors;
- disjoint pivotal regions.

However the W-v2 execution driver was constructed and edited after the experiment seal. Early runs failed before final output was saved, but the strict one-shot standard was still violated.

Therefore W-v2 is classified as:

> **hostile validation / development evidence, not final untouched validation.**

### 13.4 Parseable FEN != legal experimental position

W10 and W11 parsed as FEN strings but represented impossible chess states because the side not to move was already in check.

Future preflight must use actual board-state validity checks such as `Board.is_valid()` rather than string parseability alone.

The resulting methodological distinction is:

```text
parseable FEN
!= legal chess state
!= valid experimental fixture
```

### 13.5 Human negative-control hypotheses can be wrong

W7 had been preregistered as a balanced negative control. Root-move analysis showed large decision spread, including several disastrous legal alternatives.

The correct conclusion was that the fixture hypothesis was falsified, not that the amplitude model must be wrong.

---

## 14. Hostile W-suite findings

The preserved W-v2 results are useful precisely because the suite attacked the assumptions of the frozen selector.

Observed behavior included:

- **rare / singleton leverage weakness**;
- **broad-region weakness**;
- **multi-region weakness**;
- **residual recurrence diffuseness**;
- successful preservation of some low-amplitude shape evidence without requiring high final amplitude;
- useful zero-optionality behavior in a forced-move position.

Across valid hostile fixtures, recurrence supplied the majority of selected geography, confirming that the early-ply plus repeated-line gate did not solve diffuseness.

The proper interpretation is not an aggregate accuracy percentage. The suite was intentionally adversarial to known assumptions.

A more accurate characterization is:

> **ShapeSelectivity-v1 is a near-term, repeated-support, geographically bounded attention policy with known blind spots for rare, deep, broad, and multi-focal leverage.**

---

## 15. Current semantic-integrity audit: M8.6.4

Before new threshold tuning or new composite modeling, the repository needs a narrow semantic audit.

### Required checks

1. Reconstruct W2, W3, W4, and W12 expected-square provenance channel by channel.
2. Distinguish for each channel:
   - not observed;
   - observed but rejected;
   - observed and selected.
3. Verify mechanically:

```text
distinct_line_count <= admitted_candidate_count
```

for every Recurrence observation.
4. Resolve historical prose reporting recurrence counts larger than the frozen admitted candidate set. Determine whether those values were actually `visit_count`, came from a different candidate policy, bypassed candidate admission, or were mislabeled.
5. Explicitly distinguish:
   - legal root moves analyzed;
   - recurrence candidates admitted;
   - PV length in plies;
   - distinct candidate lines containing a square;
   - total visits to a square.
6. Audit `ShapeSelectivity-v1` semantics as implemented. The current helper returns one prioritized source rather than independent channel states, and its fallback rejection reason can mask other channel-specific failures.
7. Add machine-checkable assertions before any retuning.

The purpose of M8.6.4 is semantic integrity, not model improvement.

---

## 16. What has actually been established

The first research sprint supports the following conclusions.

### Supported

- Attack/control density and strategic importance are not equivalent.
- Root-move regret is a useful decision-sensitivity quantity when kept separate from causal claims.
- Direct move attribution captures some tactical endpoint structure but misses important indirect geometry.
- PV recurrence adds a distinct future-path signal.
- Structural geometry delta can represent rays, pathways, blockers, defenses, attacks, and mobility changes away from move endpoints.
- Geometry/outcome association must be interpreted cautiously because events are often confounded.
- Event bundles are a more honest regional unit when structural events are inseparable at the available observational resolution.
- Relative spatial shape and absolute decision-leverage amplitude are distinct quantities.
- Mate-sensitive evidence should remain typed rather than converted into fake CP.
- Zero optionality is meaningfully different from severe evaluation.
- Preserving failed fixtures and failed validation procedures materially improves the research record.

### Not established

- A universal scalar definition of pivotality.
- A fixed fusion that beats the strongest individual evidence channel across positions.
- A final amplitude statistic.
- A final spatial-selectivity rule.
- A proven causal attribution model for indirect geometry.
- A final negative-control benchmark.
- A pristine untouched external holdout.
- Human-expert agreement that ChessHeat's current spatial evidence corresponds to subjective chess pivotality.
- A production-ready instructional model.

---

## 17. Open research questions

### Q1 — What turns geographic evidence into geographic relevance?

A square appearing in a strong PV proves that it occurs in a plausible continuation. It does not prove that the square deserves visual emphasis.

Can relevance be defined without simply increasing recurrence thresholds and thereby discarding rare, deep, broad, or multi-focal legitimate leverage?

### Q2 — Should recurrence be consequence-coupled?

Instead of asking only:

> Does this square recur?

future research may ask:

> Does passage through this square distinguish materially different decision outcomes?

This would couple future-path evidence to consequence without assuming that frequency alone implies leverage.

### Q3 — Are squares the correct primitive representation?

Files, diagonals, corridors, king zones, pawn complexes, and disjoint tactical regions may need to exist as first-class spatial objects before projection onto 64 squares.

Broad-region and multi-region hostile fixtures are direct motivation for this question.

### Q4 — How should amplitude be defined across mixed CP and mate outcomes?

The current typed architecture is stronger than a fake scalar conversion, but the final mate-sensitive amplitude representation remains unresolved.

Useful quantities may include preserving-mate fraction, forfeiting-mate fraction, allowing-mate-against fraction, and comparable mate-distance changes where semantics permit.

### Q5 — What constitutes a true chess negative control?

Positions that look quiet to humans may still contain catastrophic legal alternatives and therefore high decision leverage.

A future negative-control protocol must define low leverage from the actual root-choice distribution rather than visual calmness alone.

### Q6 — How should spatial evidence be validated?

Future validation should use true multi-square regions, corridors, disjoint zones, explicit object-level provenance, and independently frozen fixtures.

Expert judgment may eventually be useful, but it must not replace mechanical provenance.

---

## 18. Future research track — Temporal Ledger

A new question emerged from considering actual game history rather than only the current snapshot and future search:

> **Can ChessHeat reconstruct how the current spatial structure was formed without contaminating objective current-state measurement?**

The proposed Temporal Ledger remains a separate research layer.

Four descriptive historical dimensions are candidates:

### Investment

Where were tempi and movable resources repeatedly spent?

Repeated movement is not automatically waste. Compensation must remain observable rather than being assumed.

### Optionality

Where did move sequences repeatedly narrow the opponent's viable choice space?

A possible descriptive trajectory is:

```text
31 viable choices -> 9 -> 4 -> 2 -> 1
```

but the definition of "viable" must be preregistered rather than chosen after observing a result.

### Conversion

Where did temporary activity become persistent structure?

Example pattern:

```text
forcing action
-> line opens
-> piece occupies line
-> defender displaced
-> weakness persists
```

Existing `Delta_G` evidence may allow these transitions to be represented without initially claiming causality.

### Persistence

Which structural objects survived through subsequent moves, and which were transient?

Possible descriptive quantities include lifetime, reappearance, reversal, and persistence of geometry objects.

### Critical transposition control

The cleanest first Temporal Ledger experiment is two different histories that arrive at the same complete legal state:

```text
H_A -> P
H_B -> P
```

Current-state ChessHeat should satisfy:

```text
CurrentState(H_A, P) = CurrentState(H_B, P)
```

except where the supposedly identical states actually differ in legal-state information such as castling rights, en-passant state, repetition context, or move counters relevant to the rules.

The historical ledger may legitimately satisfy:

```text
TemporalLedger(H_A) != TemporalLedger(H_B)
```

This creates a falsifiable boundary between:

> **what the board is now**

and

> **how the board became what it is.**

Temporal evidence should not be fused into present pivotality until it demonstrates a distinct measurable quantity.

---

## 19. Research direction after M8

The near-term sequence is:

1. complete M8.6.4 semantic-integrity audit;
2. freeze the corrected interpretation of M8 without retuning `ShapeSelectivity-v1` on hostile evidence;
3. improve fixture legality and experimental sealing protocol;
4. study regional representations and consequence-coupled recurrence;
5. begin Temporal Ledger as a separate descriptive research layer;
6. only then revisit a composite pivotality model;
7. defer opening instruction until the measurement layer has earned enough trust.

---

## 20. Closing result

ChessHeat started with:

> **Which squares are hot?**

The first sprint showed that this question hides several different mathematical objects:

- decision sensitivity;
- direct move implication;
- future-path recurrence;
- structural geometry change;
- regional event association;
- spatial selectivity;
- position-level amplitude;
- and potentially historical trajectory.

The research has not yet earned one final color scale.

That is the point.

The most valuable result so far is a clearer standard for what a meaningful chess heatmap would need to represent before visualization can be trusted:

> **The mathematics needs to earn the color.**
