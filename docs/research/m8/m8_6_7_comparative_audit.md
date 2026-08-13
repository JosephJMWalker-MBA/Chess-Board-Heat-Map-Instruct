# M8.6.7 — W-v2-R Comparative Metric Integrity Audit

## Resolving the '427' Claim
The previous report erroneously cited '427 false-positive squares' as the baseline for W-v2.
This number (427) was actually the FP area from the M8.5 spatial selectivity audit on the F-suite fixtures (1,378 -> 427), not W-v2.

The true W-v2 FP footprint across the 10 valid fixtures was 167.
The W-v2-R FP footprint is 99.
Reduction: 167 -> 99 (40.7% reduction)

## FP Area Comparison
| Fixture | W-v2 FP area | W-v2-R FP area | Delta |
|---|---|---|---|
| W1_Deep_PV | 17 | 17 | 0 |
| W2_Two_Line_Recurrence | 25 | 18 | -7 |
| W3_Single_Consequential_Move | 17 | 1 | -16 |
| W4_Legitimate_Broad_Bundle | 26 | 19 | -7 |
| W5_Quiet_Positional | 14 | 14 | 0 |
| W6_Recurring_Negligible_Consequence | 8 | 8 | 0 |
| W7_Balanced_Negative_Control | 39 | 10 | -29 |
| W8_Mate_Sensitive | 8 | 8 | 0 |
| W9_Zero_Optionality_Severe | 0 | 0 | 0 |
| W12_Disjoint_Regions | 13 | 4 | -9 |

## Detailed Fixture-by-Fixture Comparison
### W1_Deep_PV
- **Selected square count:** 20 -> 20
- **Region recall:** {'deep_mate_square': 1.0} -> {'deep_mate_square': 1.0}
- **Precision:** 0.150 -> 0.150
- **Direct selected count:** 2 -> 2
- **Recurrence selected count:** 4 -> 2
- **Bundle selected count:** 14 -> 16

**Recurrence Specifics:**
- Total legal roots: 14
- W-v2 admitted roots: 14 (omitted policy allowed all roots)
- W-v2-R admitted roots: 5
- W-v2-R admitted move list: ['b2h2', 'b2g2', 'b2f2', 'b2e2', 'b2d2']

**Effect Classification:** substantially reduced

---

### W2_Two_Line_Recurrence
- **Selected square count:** 26 -> 18
- **Region recall:** {'critical_fork': 0.3333333333333333} -> {'critical_fork': 0.0}
- **Precision:** 0.038 -> 0.000
- **Direct selected count:** 1 -> 1
- **Recurrence selected count:** 21 -> 11
- **Bundle selected count:** 4 -> 6

**Recurrence Specifics:**
- Total legal roots: 16
- W-v2 admitted roots: 16 (omitted policy allowed all roots)
- W-v2-R admitted roots: 5
- W-v2-R admitted move list: ['f2f3', 'g1f1', 'g2g4', 'd4c6', 'f2f4']

**Effect Classification:** modestly reduced

---

### W3_Single_Consequential_Move
- **Selected square count:** 18 -> 2
- **Region recall:** {'back_rank_corridor': 0.3333333333333333} -> {'back_rank_corridor': 0.3333333333333333}
- **Precision:** 0.056 -> 0.500
- **Direct selected count:** 1 -> 1
- **Recurrence selected count:** 17 -> 1
- **Bundle selected count:** 0 -> 0

**Recurrence Specifics:**
- Total legal roots: 20
- W-v2 admitted roots: 20 (omitted policy allowed all roots)
- W-v2-R admitted roots: 5
- W-v2-R admitted move list: ['g1h1', 'e1e2', 'g1f1', 'e1c1', 'g2g3']

**Effect Classification:** substantially reduced

---

### W4_Legitimate_Broad_Bundle
- **Selected square count:** 36 -> 23
- **Region recall:** {'queen_radiance': 0.5555555555555556} -> {'queen_radiance': 0.2222222222222222}
- **Precision:** 0.278 -> 0.174
- **Direct selected count:** 1 -> 1
- **Recurrence selected count:** 26 -> 4
- **Bundle selected count:** 9 -> 18

**Recurrence Specifics:**
- Total legal roots: 34
- W-v2 admitted roots: 34 (omitted policy allowed all roots)
- W-v2-R admitted roots: 5
- W-v2-R admitted move list: ['c4f4', 'c4f1', 'c4e2', 'c4d3', 'c4b5']

**Effect Classification:** substantially reduced

---

### W5_Quiet_Positional
- **Selected square count:** 18 -> 18
- **Region recall:** {'opposition_squares': 1.0} -> {'opposition_squares': 1.0}
- **Precision:** 0.222 -> 0.222
- **Direct selected count:** 1 -> 1
- **Recurrence selected count:** 13 -> 7
- **Bundle selected count:** 4 -> 10

**Recurrence Specifics:**
- Total legal roots: 8
- W-v2 admitted roots: 8 (omitted policy allowed all roots)
- W-v2-R admitted roots: 5
- W-v2-R admitted move list: ['c3c4', 'c3d4', 'c3b4', 'c3d3', 'c3b3']

**Effect Classification:** modestly reduced

---

### W6_Recurring_Negligible_Consequence
- **Selected square count:** 14 -> 14
- **Region recall:** {'king_oscillation': 1.0} -> {'king_oscillation': 1.0}
- **Precision:** 0.429 -> 0.429
- **Direct selected count:** 6 -> 6
- **Recurrence selected count:** 2 -> 2
- **Bundle selected count:** 6 -> 6

**Recurrence Specifics:**
- Total legal roots: 5
- W-v2 admitted roots: 5 (omitted policy allowed all roots)
- W-v2-R admitted roots: 5
- W-v2-R admitted move list: ['e1f2', 'e1e2', 'e1d2', 'e1f1', 'e1d1']

**Effect Classification:** unchanged

---

### W7_Balanced_Negative_Control
- **Selected square count:** 43 -> 11
- **Region recall:** {'center_control': 1.0} -> {'center_control': 0.25}
- **Precision:** 0.093 -> 0.091
- **Direct selected count:** 1 -> 1
- **Recurrence selected count:** 40 -> 4
- **Bundle selected count:** 2 -> 6

**Recurrence Specifics:**
- Total legal roots: 36
- W-v2 admitted roots: 36 (omitted policy allowed all roots)
- W-v2-R admitted roots: 5
- W-v2-R admitted move list: ['d2d3', 'e1g1', 'a2a4', 'a2a3', 'h2h3']

**Effect Classification:** substantially reduced

---

### W8_Mate_Sensitive
- **Selected square count:** 10 -> 10
- **Region recall:** {'stalemate_trap': 0.5} -> {'stalemate_trap': 0.5}
- **Precision:** 0.200 -> 0.200
- **Direct selected count:** 6 -> 6
- **Recurrence selected count:** 3 -> 3
- **Bundle selected count:** 1 -> 1

**Recurrence Specifics:**
- Total legal roots: 5
- W-v2 admitted roots: 5 (omitted policy allowed all roots)
- W-v2-R admitted roots: 5
- W-v2-R admitted move list: ['b6c6', 'b6a6', 'b6c5', 'b6b5', 'b6a5']

**Effect Classification:** unchanged

---

### W9_Zero_Optionality_Severe
- **Selected square count:** 2 -> 2
- **Region recall:** {'forced_move_squares': 0.6666666666666666} -> {'forced_move_squares': 0.6666666666666666}
- **Precision:** 1.000 -> 1.000
- **Direct selected count:** 2 -> 2
- **Recurrence selected count:** 0 -> 0
- **Bundle selected count:** 0 -> 0

**Recurrence Specifics:**
- Total legal roots: 1
- W-v2 admitted roots: 1 (omitted policy allowed all roots)
- W-v2-R admitted roots: 1
- W-v2-R admitted move list: ['a1a2']

**Effect Classification:** unchanged

---

### W12_Disjoint_Regions
- **Selected square count:** 14 -> 4
- **Region recall:** {'back_rank_mate': 0.0, 'queenside_action': 0.3333333333333333} -> {'back_rank_mate': 0.0, 'queenside_action': 0.0}
- **Precision:** 0.071 -> 0.000
- **Direct selected count:** 1 -> 1
- **Recurrence selected count:** 13 -> 0
- **Bundle selected count:** 0 -> 3

**Recurrence Specifics:**
- Total legal roots: 20
- W-v2 admitted roots: 20 (omitted policy allowed all roots)
- W-v2-R admitted roots: 5
- W-v2-R admitted move list: ['e1b1', 'g2g3', 'f2f3', 'e1f1', 'g2g4']

**Effect Classification:** eliminated

---

