# ChessHeat Decision Log

This file records consequential product, measurement, and architecture decisions so future implementation work does not silently redefine the project.

## D-001 — ChessHeat models consequence structure, not weighted control

**Status:** Accepted

**Decision:**

The primary purpose of ChessHeat is to identify square-level leverage, hazard, and pivotality as board state changes. Attack counts and piece-value-weighted control may be shown as supporting evidence, but they do not define heat.

**Reason:**

The earlier ChessHeat prototype conflated weighted influence with strategic consequence. That approach can label a square neutral or important for the wrong reason and cannot represent indirect positional leverage.

---

## D-002 — Control and importance remain separate data concepts

**Status:** Accepted

**Decision:**

Control geometry must be stored and exposed separately from leverage/consequence evidence.

**Reason:**

A square can be evenly contested yet pivotal, or heavily controlled yet low-impact.

---

## D-003 — Stockfish is an evidence source, not the product model

**Status:** Accepted

**Decision:**

Use Stockfish to provide reproducible evidence about position evaluation and plausible continuations. ChessHeat owns the transformation from that evidence into square-level representations.

**Reason:**

The product's value lies in exposing spatial consequence structure, not in reproducing a standard engine GUI.

---

## D-004 — Preserve raw evidence before composite scoring

**Status:** Accepted

**Decision:**

Move-level engine results, square attribution records, and search metadata must remain inspectable. No final heat color or scalar may be the only stored result.

**Reason:**

The heat model is a research hypothesis. Preserving raw evidence allows formulas to be revised, compared, and falsified without rerunning every conceptual assumption through opaque transformations.

---

## D-005 — No composite pivotality formula in the initial prototype

**Status:** Accepted

**Decision:**

The first prototype will expose separate raw and derived signals instead of combining them into a single pivotality number.

**Reason:**

A visually persuasive composite could hide a bad model. Individual signals should demonstrate value before weighting is introduced.

---

## D-006 — Direct attribution is an explicit approximation

**Status:** Accepted

**Decision:**

Initial consequence evidence may be attributed to squares directly involved in legal moves: origin, destination, captured square, promotion/castling/en-passant related squares where applicable.

The system must label indirect causal attribution as unsupported until a validated method exists.

**Reason:**

Many strong chess moves create their important effect elsewhere on the board. Pretending destination-square attribution fully explains the move would recreate the conceptual error the project is trying to escape.

---

## D-007 — Heat delta is a first-class future primitive

**Status:** Accepted

**Decision:**

The measurement architecture must support comparison between consecutive legal positions rather than treating every heatmap as an isolated snapshot.

**Reason:**

The future teaching experience depends on answering: "What did that move change?"

---

## D-008 — Opening instruction should teach strategic reconstruction, not database conformity

**Status:** Accepted

**Decision:**

Future opening instruction should use board-state changes, heat delta, and curated strategic objectives to teach why moves matter. Leaving theory is not inherently an error if the resulting position preserves sound strategic logic.

**Reason:**

The goal is transferable chess understanding, not rote tree memorization.

---

## D-009 — Generative AI is outside the core measurement pipeline

**Status:** Accepted

**Decision:**

Generative models may eventually explain structured evidence but may not determine engine evaluation, square heat, tactical truth, or causal attribution.

**Reason:**

ChessHeat should remain reproducible and inspectable at the measurement layer.

---

## D-010 — Python analysis core with a versioned evidence boundary

**Status:** Accepted

**Decision:**

ChessHeat will use a Python-first analysis core that communicates with Stockfish through a narrow engine adapter and emits versioned, structured measurement records. The analysis core must be runnable and testable without any web interface.

The web visualization layer will consume those records. It must not own engine execution, score normalization, legal move generation, square attribution, leverage calculation, hazard calculation, or other measurement semantics.

For the initial prototype, Stockfish should run as a native engine process adjacent to the Python analysis core. Browser-side WebAssembly engine execution may be considered later as a deployment optimization, but it is not the reference measurement implementation.

The frontend framework remains intentionally undecided until the measurement pipeline is proven.

**Reference flow:**

`legal chess position -> Python analysis core -> Stockfish adapter -> raw engine evidence -> ChessHeat measurement records -> web visualization`

**Reason:**

The core research claim concerns measurement, not rendering. Separating the analysis instrument from the interface makes the measurement model independently testable, reproducible, inspectable, and replaceable. It also prevents UI convenience from quietly changing chess semantics.

---

## Open decisions

The following remain intentionally unresolved:

### O-002 — Engine budget

Need to define a reproducible comparison budget such as fixed depth, nodes, or another controlled mode.

### O-003 — Score normalization

Need a documented method for comparing centipawn and mate evaluations while preserving perspective.

### O-004 — Direct square aggregation

Need to compare statistics such as maximum consequence, distribution, downside, upside, and frequency before choosing a visualization mapping.

### O-005 — Hazard definition

Need to determine what qualifies a square as "lava" rather than merely unfavorable or contested.

### O-006 — Pivotality evidence

Need to validate which combination, if any, of consequence magnitude, PV recurrence, persistence, structural change, and indirect attribution deserves the term pivotality.

### O-007 — Validation method

Need to define human/chess-expert and fixture-based methods for determining whether ChessHeat surfaces genuinely useful positional structure.

### O-008 — Web visualization stack

Choose the frontend framework, board component strategy, and deployment shape only after the analysis core produces stable versioned measurement records. The UI must remain a consumer of measurement semantics, not their owner.
