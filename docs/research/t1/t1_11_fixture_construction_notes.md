# T1.11.1 Fixture Construction Notes

## Overview
This document preserves the rejected candidate positions, assumptions, and iterative debugging steps during the construction of the Q1–Q15 hostile validation corpus for T1.11.1. It summarizes the FEN/signature errors encountered and how they were structurally repaired.

## Rejected Candidates & Iterative Debugging Reasons

During the generation of Q1–Q15, several initial hypotheses and FEN setups were rejected due to structural or legal violations discovered during testing:

1. **Q8 (Spatial Overlap Control) Illegal Move**: 
   *Initial attempt:* The original FEN `rnbqkbnr/ppp1pppp/8/3p4/8/8/PPP1PPPP/RNBQKBNR w KQkq - 0 1` did not allow the move `Qh5` because the e2 pawn blocked the Queen.
   *Resolution:* FEN was repaired to `rnbqkbnr/ppp1pppp/8/3p4/8/8/PPP2PPP/RNBQKBNR w KQkq - 0 1` (removing the e2 pawn, placing 3 pawns, 2 empty, 3 pawns: `PPP2PPP`) so `Qh5` is legal and correctly sets up the spatial overlap.
   *Status:* REJECTED original FEN, REPAIRED.

2. **Q12 (One-Root Zero Optionality) Extraneous Kwargs**:
   *Initial attempt:* The script provided `e_type="mobility"` and `f_type="mobility"` as arguments to `build_fixture`. The builder was refactored earlier to use string matching, rendering these kwargs invalid.
   *Resolution:* Removed `e_type` and `f_type`.
   *Status:* REJECTED constructor arguments, REPAIRED.

3. **Q2, Q4, Q5, Q15 (Played Move M11 Membership Violation)**:
   *Initial attempt:* The validation harness rigidly asserts `played_move_san in m_11`. However, Q2's hypothesis ("Independent successor birth") required `n01 > 0`. The initial implementation used `Nc3` as the played move, but because it didn't remove `e`, it was classified as `m_01`, immediately failing the harness's strict `m_11` constraint.
   *Resolution:* We constructed a scenario where *two* pieces can move to the same destination to birth `f`. FEN was set to `r1bqkbnr/pppppppp/8/8/8/8/PPPPNPPP/RN1QKBNR w KQkq - 0 2`. 
     - `e`: b1 Knight's attack on a3
     - `f`: c3 Knight's attack on d5
     - Played move: `Nbc3` (removes `e` and births `f`, so it's in `m_11`).
     - Alternative move: `Nec3` (does NOT remove `e` but births `f`, so it is in `m_01`).
   This successfully populated `m_11` with the played move and `m_01` with `Nec3`, yielding `n01 > 0` without breaking harness logic.
   *Status:* REJECTED initial physical setups, REPAIRED.

4. **Q12 (One-Root Zero Optionality) Mobility Signature Matching**:
   *Initial attempt:* We tried matching `PieceMobility` string representations for a King move.
   *Resolution:* We opted for `AttackRelationship` representing the King's attack shifting from `g8` (before `Kh7`) to `g6` (after `Kh7`), providing cleaner structural isolation for a 1-root position.
   *Status:* REJECTED mobility signature, REPAIRED with attack signature.

5. **Q15 (Turn-Conditioned Mobility) Mobility Extraction Mismatch**:
   *Initial attempt:* We attempted to track the full `PieceMobility` object (`piece=PieceRef(square='g8'...)`). However, `extract_all_signatures()` only yields specific tuples `(piece, destination)` for *legal* destinations. In the root (White's turn), Black's `g8` knight had no legal destinations, meaning it produced *no* signatures in the root. The harness failed finding `e`.
   *Resolution:* We decoupled `e` and `f`. 
     - `e` was set to White's `e2` pawn's attack on `f3`, which is removed when White plays `e4`.
     - `f` was set to the tuple `(PieceRef(square='g8', symbol='n'), 'f6')`, which is birthed as a result of the turn handoff activating Black's legal mobility.
     - Played move: `e4` (removes `e`, births `f`, making it `m_11`).
     - Alternative move: `d4` (does NOT remove `e` but still births `f`, making it `m_01`).
   *Status:* REJECTED `PieceMobility` string representation, REPAIRED using `AttackRelationship` and `(PieceRef, str)` tuple.

## Pre-Seal Fixture Review Corrections

During the pre-seal review, several fixtures were rejected and required revision due to failing their preregistered prose requirements without Stockfish contamination.

1. **Q6 (Missing-Preserving Comparison) - Rejected at Pre-Seal Review**:
   *Issue:* The mechanical preflight falsified the fixture. Its support condition required `n01 + n00 == 0`, but the root had multiple moves that preserved `e` (e.g., King moves), resulting in `n01 + n00 = 2`. The preflight incorrectly labeled it PASS.
   *Resolution:* Replaced with a fresh position (`4k3/8/8/8/8/8/8/4R3 b - - 0 1`) where the Black King is in check and MUST move. Since `e` is the Black King's attack from its root square, *every* legal move (all King moves) removes `e`, strictly guaranteeing `n01 + n00 == 0` with multiple legal roots.

2. **Q10 (Temporal Ledger Reappearance) - Rejected at Pre-Seal Review**:
   *Issue:* The targeted reappearance event `Nf3->e5` had its target square (`e5`) become occupied by a Black pawn during the first episode. This changed the target-piece identity of the `AttackRelationship`, making it a structurally distinct event rather than a true reappearance.
   *Resolution:* Repaired the history to `Nf3, h6, Nd4, a6, Nf3`. Black plays harmless waiting moves so the target square `e5` remains completely empty, preserving exact `AttackRelationship` identity.

3. **Q13 (Same Endpoint / Different History) - Rejected at Pre-Seal Review**:
   *Issue:* The two histories (`Nf3 Nf6 Ng1 Ng8 Nf3` vs `Nf3`) reached the same piece placement but different complete FENs because the halfmove/fullmove clocks differed (5 plies vs 1 ply).
   *Resolution:* Replaced with two equal-length commuting histories (`d4, d5, Nf3, Nf6` vs `Nf3, Nf6, d4, d5`). Both reach the exact same full FEN (`rnbqkb1r/ppp1pppp/5n2/3p4/3P4/5N2/PPP1PPPP/RNBQKB1R w KQkq - 2 3`) but have different temporal lifecycle timings for the `d4->c5` attack.

4. **Q14 (Matched Structural Partitions) - Rejected at Pre-Seal Review**:
   *Issue:* The fixtures (`e4` vs `d4`) were merely similar, not explicitly matched. The isomorphism criterion was underspecified.
   *Resolution:* Constructed two strictly symmetric fixtures (`a3` vs `h3`). An explicit x-axis reflection bijection guarantees exact partition membership counts. The consequence prediction was formalized to `medianR(M11_a) != medianR(M11_b)`.

5. **Q4/Q14 Underspecification - Repaired at Pre-Seal Review**:
   *Issue:* "Consequence association" and "different consequence landscapes" lacked directional or strictly observable observables.
   *Resolution:* Q4 now requires `medianR(m11) < medianR(m10)` with CP-comparable observations. Q14 now requires `medianR(m11_a) != medianR(m11_b)`.

## Summary
Total rejected physical setups / signatures during debugging: **5**.
Total rejected setups at Pre-Seal Review: **4**.
Corpus status: **FROZEN PENDING T1.11.2 EXECUTION SEAL**.
