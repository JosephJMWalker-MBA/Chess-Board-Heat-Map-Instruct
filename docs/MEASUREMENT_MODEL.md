# ChessHeat Measurement Model

## Status

This document describes the current measurement architecture after Milestones 1–8.

It is still provisional. ChessHeat does **not** have an authorized universal pivotality formula.

The governing rule is:

> **The mathematics needs to earn the color.**

See [`RESEARCH_REPORT_M1_M8.md`](RESEARCH_REPORT_M1_M8.md) for the experimental history and falsification record.

---

## 1. Core separation

ChessHeat now treats several quantities as distinct rather than collapsing them into one heat score.

### Control

Geometric attack / defense information.

Control is evidence, not importance.

### Decision consequence

How much value is surrendered by choosing one legal root move instead of a better legal root move.

### Spatial evidence

Where direct moves, future continuations, and structural geometry implicate squares or regions.

### Amplitude

How much decision leverage exists in the position as a whole.

### Shape

Where spatial evidence is concentrated, separately from amplitude.

### Temporal provenance

A proposed future layer describing how the present structure was formed. It is not part of current-state pivotality yet.

---

## 2. Root-move outcome and regret

For legal position `P`, analyze legal root moves under the same declared engine budget and comparison perspective.

For legal move `m`:

```text
E(m) = typed engine outcome after choosing m
```

For centipawn-comparable outcomes:

```text
E*   = best root outcome
R(m) = E* - E(m)
```

`R(m)` is **regret / opportunity cost**, not a causal estimate of how much the move changed the position.

The original provisional model used:

```text
E(P after m) - E(P)
```

as a candidate consequence quantity. That interpretation was rejected because the baseline engine value already assumes optimal continuation.

### Perspective

All compared outcomes must use the same declared comparison perspective.

### Mate semantics

Mate outcomes remain typed. Do not convert mate values into fake centipawn scores.

Mixed CP / mate positions require typed amplitude and outcome records rather than one fabricated scalar.

---

## 3. Direct spatial attribution

For each root move, preserve the squares directly implicated by the move.

Possible roles include:

- origin;
- destination;
- capture square;
- en-passant capture square;
- king origin / destination in castling;
- rook origin / destination in castling;
- promotion-related state.

For square `s`:

```text
D(s) = {m : s is directly implicated by m}
```

Direct attribution is explicitly an approximation. It does not imply that the move's important strategic consequence occurs only on those squares.

Useful direct descriptive statistics may include:

- move count;
- candidate fraction;
- min / max / mean / median CP regret where defined;
- origin / destination / capture role counts;
- full implicated-move provenance.

Do not use direct attribution as a causal explanation for indirect effects.

---

## 4. Principal-variation recurrence

Recurrence describes future-path geography across an admitted candidate set.

Candidate policy is applied before recurrence aggregation. The implementation preserves:

- total legal root moves;
- candidate policy;
- admitted candidate count;
- admitted root moves;
- candidate scores;
- candidate regrets;
- number of admitted PVs with parsed content.

For square `s`:

```text
distinct_line_count(s)
  = number of admitted candidate PVs containing s

line_fraction(s)
  = distinct_line_count(s) / admitted_candidate_count
```

Also preserve:

- `visit_count`;
- `earliest_ply`;
- role-specific recurrence.

Required invariant:

```text
distinct_line_count(s) <= admitted_candidate_count
```

Repeated visits in one candidate PV may increase `visit_count`, but they do not increase `distinct_line_count` beyond one for that candidate line.

### Interpretation

Recurrence proves that a square appears in plausible admitted continuations. It does **not** prove the square is consequentially important.

> **Future frequency != leverage.**

---

## 5. Structural geometry

Define deterministic board geometry `G(P)` from chess rules rather than engine evaluation.

Current structural evidence includes:

- attacks;
- defenses;
- sliding rays;
- path squares;
- blockers;
- legal / pseudo-legal mobility changes.

For legal move `m`:

```text
Delta_G(P, m) = G(P after m) - G(P)
```

This allows ChessHeat to represent structural effects away from the move's origin and destination.

Examples include opened files, exposed rays, lost defenses, and mobility changes.

Geometry delta is descriptive. It does not establish why an engine score changed.

---

## 6. Geometry / outcome association

For structural event `e`, compare root-move outcome or regret distributions between moves that produce the event and moves that do not.

Example descriptive quantity:

```text
Delta_R(e)
  = median R(m | e)
    - median R(m | not e)
```

Positive or negative association does not imply isolated causality.

If multiple geometry events have exactly the same producing-move set, preserve them as an **event bundle** rather than pretending the experiment distinguishes their independent causal effects.

Bundle records should preserve:

- constituent events;
- producing moves;
- non-producing moves;
- implicated squares / paths;
- outcome / regret distributions;
- association statistics;
- confounding status.

---

## 7. Evidence families used in M8

The main experimental spatial channels are:

### A — Direct

Square evidence derived from directly implicated root moves.

### B — Recurrence

Square evidence derived from appearance across admitted candidate PVs.

### C — Bundle

Square / region evidence derived from event-bundle implication and associated root-move outcome separation.

Baselines include:

- attack density;
- destination regret.

M8 compared individual channels, pairwise combinations, and all-channel fusion.

No fixed fusion has yet demonstrated universal superiority over its strongest individual component.

---

## 8. Rank normalization warning

The current experimental fusion code converts within-position values into ranks in `[0, 1]` before averaging available channels.

This is useful for ablation because the channels have different native units.

It is **not** sufficient as a final heat magnitude because relative ranking creates a hottest square whenever there is any variation.

Therefore:

> **Where is leverage? != How much leverage exists?**

---

## 9. Shape and amplitude

Current architecture separates:

```text
S(s | P) = spatial shape / localization evidence
A(P)     = position-level decision-leverage amplitude
```

A future visualization may eventually use a composition such as:

```text
H(s | P) = A(P) * S(s | P)
```

but that is a conceptual decomposition, not an authorized final formula.

### Typed amplitude

The sealed helper preserves:

```text
A(P) = {A_cp, A_mate, zero_optionality}
```

If the position has at most one legal move:

```text
zero_optionality = true
A_cp = 0
```

This expresses decision leverage, not objective severity.

> **Severity != decision leverage.**

The final CP spread statistic and detailed mate-sensitive amplitude representation remain open research questions.

---

## 10. ShapeSelectivity-v1

The first frozen development attention policy uses:

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

These thresholds were tuned using development evidence and are not universal chess principles.

Rejected evidence remains preserved as raw evidence.

### Important implementation caveat

The current helper checks channels in order:

```text
Direct -> Recurrence -> Bundle
```

and returns the first passing channel as the selected source.

If nothing passes, its rejection-reason fallback prioritizes Bundle when Bundle evidence exists, then Recurrence, then Direct.

Therefore the current helper does **not** represent a complete independent per-channel selection state.

M8.6.4 must audit and clarify these semantics before further tuning.

---

## 11. Heat delta

For consecutive positions `P_a` and `P_b`, compute comparable evidence from the same perspective and preserve state transitions.

Do not treat missing evidence as numeric zero.

Useful states include:

- persisted;
- appeared;
- disappeared;
- absent in both.

Heat delta remains pedagogically important because it supports the question:

> **What did that move change, and where?**

---

## 12. Regional evidence

M7–M8 showed that some legitimate structure is naturally regional rather than square-local.

Candidate first-class regional objects include:

- files;
- diagonals;
- rays / corridors;
- king zones;
- pawn complexes;
- disjoint simultaneous tactical regions.

Do not assume projection to 64 independent squares preserves all relevant structure.

This is an open research track.

---

## 13. Experimental controls

Each engine-derived experiment should preserve at least:

- exact FEN;
- board legality / `Board.is_valid()` preflight;
- side to move;
- comparison perspective;
- engine executable / version;
- threads;
- hash setting;
- budget type and value;
- candidate policy;
- legal root count;
- admitted candidate count;
- fixture manifest identity / hash where sealed;
- evaluator / implementation identity where sealed;
- typed score evidence;
- raw spatial provenance.

A FEN that parses is not automatically a legal board state, and a legal board state is not automatically a valid experimental fixture for the stated hypothesis.

---

## 14. Validation principles

### Preserve falsification

If a human fixture hypothesis is wrong, mark the hypothesis falsified rather than forcing the model to agree with intuition.

### Preserve invalid experiments

Do not silently repair invalid fixtures or contaminated holdouts after viewing results.

### Avoid one-number accuracy claims on adversarial suites

A hostile suite designed to attack known assumptions should be interpreted by failure mode, not marketed as a representative accuracy percentage.

### Separate failure types

Useful taxonomy:

1. **Representation failure** — expected geography is not observed by any evidence layer.
2. **Selectivity failure** — evidence exists but is rejected by attention policy.
3. **Projection / fusion failure** — selected evidence exists but final ranking / rendering represents it poorly.
4. **Fixture failure** — the chess hypothesis or board state is invalid.
5. **Protocol failure** — the experimental seal or execution procedure does not meet its declared standard.

---

## 15. Current research boundary

Before changing thresholds or proposing a new composite, complete M8.6.4:

- reconstruct channel-by-channel provenance on hostile failures;
- verify recurrence invariants mechanically;
- resolve historical terminology drift around `distinct_line_count` versus `visit_count`;
- make selectivity state semantics explicit;
- add invariant tests;
- do not retune `ShapeSelectivity-v1` during the audit.

Only after semantic integrity is restored should the project study consequence-coupled recurrence, richer regional representation, or a new pivotality model.
