# ChessHeat Concept

## Problem statement

Chess engines are excellent at ranking moves but poor at exposing the board as a field of consequence.

A player can be told that a move is best, inaccurate, or losing without being shown which squares make the position sensitive. ChessHeat is intended to expose that hidden structure.

The primary object of interest is **the board itself**.

The central question is:

> **If the board state changes, which squares have the greatest leverage over what follows?**

A related question is:

> **Which squares should feel dangerous enough that a player treats them like lava?**

## What ChessHeat is not

ChessHeat is not:

- a replacement chess engine,
- a simple legal-move highlighter,
- a piece-value-weighted attack map,
- a best-move overlay with prettier colors,
- an opening database that rewards rote sequence matching,
- or an LLM-generated interpretation of a position.

Those may be supporting tools, but they are not the core invention.

## The critical distinction: control != importance

A square can be:

- controlled by both sides and still be highly pivotal,
- controlled by many pieces and still have low leverage,
- lightly controlled and yet determine a tactical sequence,
- dangerous for one side but attractive for the other.

Therefore ChessHeat must not infer square importance directly from attack counts or piece values.

### Example intuition

If White and Black each have three pieces influencing `e5`, a control map may call the square neutral. But if occupying, exchanging on, or losing control of `e5` radically changes king safety, central structure, or a tactical continuation, then `e5` may be one of the hottest squares on the board.

The point is not "who owns e5?"

The point is "how much does e5 matter?"

## Four conceptual layers

### 1. Control

Who attacks or defends a square in the current legal position?

Control is descriptive geometry. It is useful evidence but not a proxy for leverage.

### 2. Leverage

How much can meaningful changes involving a square alter the evaluation or strategic structure of the position?

A high-leverage square acts like a sensitive variable in a model: changing its state can produce a disproportionate downstream effect.

### 3. Hazard

How asymmetric is the downside of interacting with a square for a given side?

Hazard is side-dependent. A square can be attractive for White and dangerous for Black, or vice versa.

"Lava" should eventually represent a form of severe downside or tactical instability, not simply enemy control.

### 4. Pivotality

How central is a square across multiple plausible consequential futures?

A pivotal square may repeatedly appear in strong continuations, mediate tactical lines, anchor structural changes, or remain sensitive across candidate moves.

## Move quality and square heat are different

The strongest move is not necessarily played on the hottest square.

A move on `a3` might transform the strategic importance of `d5`. Therefore ChessHeat must eventually support indirect attribution: a move can create its largest consequence somewhere other than its destination square.

This distinction is essential. Otherwise the system collapses back into a move-destination heatmap.

## Board-state comparison

ChessHeat should treat consecutive positions as first-class objects.

Given positions `P[t]` and `P[t+1]`, the system should be able to show:

- which squares became more or less leveraged,
- which hazards appeared or disappeared,
- which pivotal squares emerged,
- and which strategic relationships changed.

This produces a **heat delta** rather than only a static heatmap.

That capability is central to the later teaching system.

## Opening instruction

The long-term opening teacher should explain openings as evolving consequence structures rather than memorized move trees.

A learner should eventually be able to answer:

- What is this opening trying to accomplish?
- Which squares are becoming strategically important?
- Why did this move change the position?
- If I leave theory, did I preserve the opening's strategic logic?
- Can I reconstruct a sensible move after forgetting the memorized sequence?

Possible teaching progression:

1. **Guided** — heatmap and explanations are visible.
2. **Reduced** — heatmap visible, no move suggestion.
3. **Prediction** — learner predicts which square will become pivotal.
4. **Blind** — learner moves before revealing ChessHeat.
5. **Deviation** — learner deliberately leaves theory and evaluates whether the strategic structure survived.

The success criterion is not database conformity. It is transferable understanding.

## Research posture

The vocabulary in this repository is intentionally ahead of the formulas.

Terms such as leverage, hazard, and pivotality must eventually be operationalized and tested. The implementation should preserve raw evidence so alternative definitions can be compared later.

The project should prefer:

- inspectable measurements over opaque scores,
- deterministic transformations over unexplained AI judgments,
- explicit uncertainty over false precision,
- and falsifiable claims over visual plausibility.
