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

## Summary
Total rejected physical setups / signatures during debugging: **5**.
Corpus status: **FROZEN PENDING T1.11.2 EXECUTION SEAL**.
