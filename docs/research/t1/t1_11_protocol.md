# T1.11 Protocol

Preregistered Hostile Corpus Q1-Q15.
## Q1: Canonical structural succession
- **Hypothesis:** Moving the e2 pawn establishes a canonical succession where e2's attack on d3 is removed and e4's attack on d5 is born.
- **Support:** n11 > 0 and (n10 > 0 or n01 > 0)
- **Falsifier:** n11 == 0
- **Ambiguous:** n10 == 0 and n01 == 0 and n00 == 0
- **Invalid:** predecessor does not exist in root

## Q2: Independent successor birth
- **Hypothesis:** Moving the b1 knight to c3 (Nbc3) removes its attack on a3 and births an attack on d5. Moving the e2 knight to c3 (Nec3) also births the attack on d5 but preserves the b1 knight's attack on a3, placing Nec3 in m01.
- **Support:** n01 > 0
- **Falsifier:** n01 == 0
- **Ambiguous:** n01 == 0 and n00 == 0
- **Invalid:** f is not born by played move

## Q3: Structural exclusivity
- **Hypothesis:** The only way to birth c4's attack on b5 is to move the c2 pawn, which removes its attack on b3. Thus n01=0 and n00>0.
- **Support:** n01 == 0 and n00 > 0
- **Falsifier:** n01 > 0
- **Ambiguous:** n00 == 0
- **Invalid:** e is not removed by played move

## Q4: Consequence association without structural exclusivity
- **Hypothesis:** The birth of the c3 Knight's attack on d5 has consequence implications despite not exclusively replacing the b1 knight's attack on a3.
- **Support:** medianR(m11) < medianR(m10) with CP-comparable observations
- **Falsifier:** medianR(m11) >= medianR(m10)
- **Ambiguous:** missing CP comparison class
- **Invalid:** f is not born by played move

## Q5: Ephemeral successor
- **Hypothesis:** The d4 pawn attacks e5 but is immediately captured, giving it an ephemeral duration of 1 ply.
- **Support:** duration == 1 and not right_censored
- **Falsifier:** duration > 1
- **Ambiguous:** right_censored == True
- **Invalid:** episode not found

## Q6: Missing predecessor-preserving comparison class
- **Hypothesis:** The black King is in check and MUST move. Every legal move causes the King to leave e8, thus removing its attack on f7. Therefore, n01 and n00 are both exactly 0, but multiple legal roots exist.
- **Support:** n01 + n00 == 0 and legal_root_count > 1
- **Falsifier:** n01 + n00 > 0
- **Ambiguous:** legal_root_count <= 1
- **Invalid:** e is preserved

## Q7: Confounded conversion bundle
- **Hypothesis:** Moving the bishop from d4 to c5 simultaneously removes its attacks on e5 and c5, and births attacks on d6 and b6, creating two structurally confounded pairs.
- **Support:** bundle constituents >= 2 and exact partition equality
- **Falsifier:** partitions differ
- **Ambiguous:** fewer than 2 constituents
- **Invalid:** invalid geometry

## Q8: Spatial overlap control
- **Hypothesis:** The Queen moves from d1 to h5, removing one attack on d5 and birthing another on d5, creating spatial overlap at d5.
- **Support:** len(shared_squares) > 0
- **Falsifier:** len(shared_squares) == 0
- **Ambiguous:** invalid geometry
- **Invalid:** invalid geometry

## Q9: Spatially disjoint control
- **Hypothesis:** The pawn's attack on d3 is removed and attack on d5 is born. They share no structurally implicated squares.
- **Support:** len(shared_squares) == 0
- **Falsifier:** len(shared_squares) > 0
- **Ambiguous:** invalid geometry
- **Invalid:** invalid geometry

## Q10: Reappearance
- **Hypothesis:** The attack f3-e5 is born, removed by Nd4, and born again by Nf3, demonstrating reappearance without the target e5 ever becoming occupied.
- **Support:** is_born_reappearance == True
- **Falsifier:** is_born_reappearance == False
- **Ambiguous:** episode not found
- **Invalid:** invalid geometry

## Q11: Mate-sensitive consequence boundary
- **Hypothesis:** A mate-in-1 is available in the root, forcing consequence layer to evaluate a mate-typed outcome without converting it to fake CP.
- **Support:** mate_count > 0 in any partition
- **Falsifier:** mate_count == 0
- **Ambiguous:** no consequence evidence
- **Invalid:** invalid geometry

## Q12: One-root zero optionality
- **Hypothesis:** There is exactly one legal move in the root position, so all partitions except m11 (and possibly m10 depending on e and f definitions) are empty.
- **Support:** legal_root_count == 1
- **Falsifier:** legal_root_count > 1
- **Ambiguous:** legal_root_count == 0
- **Invalid:** invalid geometry

## Q13: Same endpoint / different history
- **Hypothesis:** Two equal-length commuting histories arrive at the identical exact FEN but possess different temporal ledgers (the d4 pawn attack on c5 has duration 3 plies in A and 1 ply in B).
- **Support:** fen_a == fen_b and ledger_a != ledger_b
- **Falsifier:** fen_a != fen_b or ledger_a == ledger_b
- **Ambiguous:** invalid geometry
- **Invalid:** invalid geometry

## Q14: Matched structural partitions / different consequence landscapes
- **Hypothesis:** Symmetric pawn moves (a3 and h3) produce structurally identical partitions via explicit x-axis reflection bijection, but have different median regret consequence landscapes.
- **Support:** partitions match explicit bijection and medianR(m11_a) != medianR(m11_b) with CP-comparable observations
- **Falsifier:** partitions do not match or medianR(m11_a) == medianR(m11_b)
- **Ambiguous:** missing CP comparison class
- **Invalid:** invalid geometry

## Q15: Turn-conditioned mobility control
- **Hypothesis:** The frozen legal-mobility representation can produce event births solely because actionability transfers to the opposing side.
- **Support:** same-placement opposite-turn control shows mobility tuple changes without physical piece movement
- **Falsifier:** no mobility events change due to turn change
- **Ambiguous:** invalid geometry
- **Invalid:** invalid geometry

