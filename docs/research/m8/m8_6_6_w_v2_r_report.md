# M8.6.6 — W-v2-R Corrected Development Experiment Report

This is a retrospective development experiment executing W-v2 with the corrected `candidate_policy={"top_n": 5}`. It isolates the artifacts caused by candidate-policy omission in the original M8.6.2 run.

## Summary of Findings
**Aggregate False-Positive Area:** 99 squares across 10 valid fixtures.
**Aggregate Selected Area:** 122 squares.

### Comparative Analysis (W-v2 vs W-v2-R)
The previous report contained an arithmetic/provenance error stating the W-v2 false-positive footprint was 427 squares. (That figure actually belonged to the M8.5 F-suite audit). The true aggregate false-positive area for the ten valid W-v2 fixtures was 167 squares.

Under the corrected W-v2-R execution which enforces the frozen `{"top_n": 5}` policy, the false-positive area was reduced from 167 to 99 squares—a reduction of 40.7%. 

This supports the conclusion that a substantial portion of the observed W-v2 diffuseness was caused by the omitted recurrence candidate policy. However, 99 false-positive squares remains a nontrivial footprint. Correcting Recurrence also does not establish the correctness of Bundle semantics; Bundle must be evaluated independently for fixtures like W3, W4, and W12.

### W1_Deep_PV
#### Provenance
- **Total Legal Root Moves:** 14
- **Admitted Candidate Count:** 5
- **Candidate Policy:** `{"top_n": 5}`

#### Metrics
- **A_cp:** 0
- **A_mate:** True
- **Zero Optionality:** False
- **Expected Region Recall:** {'deep_mate_square': 1.0}
- **Selected-Region Precision:** 0.150
- **False-Positive Area:** 17 squares
- **Selected Square Count:** 20

#### Selection Channels
- **Direct Contribution:** 2 squares
- **Recurrence Contribution:** 2 squares
- **Bundle Contribution:** 16 squares
- **Observed-but-Rejected Count:** 41 squares

### W2_Two_Line_Recurrence
#### Provenance
- **Total Legal Root Moves:** 16
- **Admitted Candidate Count:** 5
- **Candidate Policy:** `{"top_n": 5}`

#### Metrics
- **A_cp:** 479
- **A_mate:** False
- **Zero Optionality:** False
- **Expected Region Recall:** {'critical_fork': 0.0}
- **Selected-Region Precision:** 0.000
- **False-Positive Area:** 18 squares
- **Selected Square Count:** 18

#### Selection Channels
- **Direct Contribution:** 1 squares
- **Recurrence Contribution:** 11 squares
- **Bundle Contribution:** 6 squares
- **Observed-but-Rejected Count:** 33 squares

### W3_Single_Consequential_Move
#### Provenance
- **Total Legal Root Moves:** 20
- **Admitted Candidate Count:** 5
- **Candidate Policy:** `{"top_n": 5}`

#### Metrics
- **A_cp:** 630
- **A_mate:** False
- **Zero Optionality:** False
- **Expected Region Recall:** {'back_rank_corridor': 0.3333333333333333}
- **Selected-Region Precision:** 0.500
- **False-Positive Area:** 1 squares
- **Selected Square Count:** 2

#### Selection Channels
- **Direct Contribution:** 1 squares
- **Recurrence Contribution:** 1 squares
- **Bundle Contribution:** 0 squares
- **Observed-but-Rejected Count:** 62 squares

### W4_Legitimate_Broad_Bundle
#### Provenance
- **Total Legal Root Moves:** 34
- **Admitted Candidate Count:** 5
- **Candidate Policy:** `{"top_n": 5}`

#### Metrics
- **A_cp:** 1237
- **A_mate:** True
- **Zero Optionality:** False
- **Expected Region Recall:** {'queen_radiance': 0.2222222222222222}
- **Selected-Region Precision:** 0.174
- **False-Positive Area:** 19 squares
- **Selected Square Count:** 23

#### Selection Channels
- **Direct Contribution:** 1 squares
- **Recurrence Contribution:** 4 squares
- **Bundle Contribution:** 18 squares
- **Observed-but-Rejected Count:** 41 squares

### W5_Quiet_Positional
#### Provenance
- **Total Legal Root Moves:** 8
- **Admitted Candidate Count:** 5
- **Candidate Policy:** `{"top_n": 5}`

#### Metrics
- **A_cp:** 1
- **A_mate:** False
- **Zero Optionality:** False
- **Expected Region Recall:** {'opposition_squares': 1.0}
- **Selected-Region Precision:** 0.222
- **False-Positive Area:** 14 squares
- **Selected Square Count:** 18

#### Selection Channels
- **Direct Contribution:** 1 squares
- **Recurrence Contribution:** 7 squares
- **Bundle Contribution:** 10 squares
- **Observed-but-Rejected Count:** 23 squares

### W6_Recurring_Negligible_Consequence
#### Provenance
- **Total Legal Root Moves:** 5
- **Admitted Candidate Count:** 5
- **Candidate Policy:** `{"top_n": 5}`

#### Metrics
- **A_cp:** 0
- **A_mate:** False
- **Zero Optionality:** False
- **Expected Region Recall:** {'king_oscillation': 1.0}
- **Selected-Region Precision:** 0.429
- **False-Positive Area:** 8 squares
- **Selected Square Count:** 14

#### Selection Channels
- **Direct Contribution:** 6 squares
- **Recurrence Contribution:** 2 squares
- **Bundle Contribution:** 6 squares
- **Observed-but-Rejected Count:** 11 squares

### W7_Balanced_Negative_Control
#### Provenance
- **Total Legal Root Moves:** 36
- **Admitted Candidate Count:** 5
- **Candidate Policy:** `{"top_n": 5}`

#### Metrics
- **A_cp:** 509
- **A_mate:** False
- **Zero Optionality:** False
- **Expected Region Recall:** {'center_control': 0.25}
- **Selected-Region Precision:** 0.091
- **False-Positive Area:** 10 squares
- **Selected Square Count:** 11

#### Selection Channels
- **Direct Contribution:** 1 squares
- **Recurrence Contribution:** 4 squares
- **Bundle Contribution:** 6 squares
- **Observed-but-Rejected Count:** 53 squares

### W8_Mate_Sensitive
#### Provenance
- **Total Legal Root Moves:** 5
- **Admitted Candidate Count:** 5
- **Candidate Policy:** `{"top_n": 5}`

#### Metrics
- **A_cp:** 484
- **A_mate:** True
- **Zero Optionality:** False
- **Expected Region Recall:** {'stalemate_trap': 0.5}
- **Selected-Region Precision:** 0.200
- **False-Positive Area:** 8 squares
- **Selected Square Count:** 10

#### Selection Channels
- **Direct Contribution:** 6 squares
- **Recurrence Contribution:** 3 squares
- **Bundle Contribution:** 1 squares
- **Observed-but-Rejected Count:** 22 squares

### W9_Zero_Optionality_Severe
#### Provenance
- **Total Legal Root Moves:** 1
- **Admitted Candidate Count:** 1
- **Candidate Policy:** `{"top_n": 5}`

#### Metrics
- **A_cp:** 0
- **A_mate:** False
- **Zero Optionality:** True
- **Expected Region Recall:** {'forced_move_squares': 0.6666666666666666}
- **Selected-Region Precision:** 1.000
- **False-Positive Area:** 0 squares
- **Selected Square Count:** 2

#### Selection Channels
- **Direct Contribution:** 2 squares
- **Recurrence Contribution:** 0 squares
- **Bundle Contribution:** 0 squares
- **Observed-but-Rejected Count:** 13 squares

### W10_Genuine_Overloaded_Defender
**STATUS: INVALID** - board.is_valid() failed

### W11_Long_Corridor
**STATUS: INVALID** - board.is_valid() failed

### W12_Disjoint_Regions
#### Provenance
- **Total Legal Root Moves:** 20
- **Admitted Candidate Count:** 5
- **Candidate Policy:** `{"top_n": 5}`

#### Metrics
- **A_cp:** 588
- **A_mate:** True
- **Zero Optionality:** False
- **Expected Region Recall:** {'back_rank_mate': 0.0, 'queenside_action': 0.0}
- **Selected-Region Precision:** 0.000
- **False-Positive Area:** 4 squares
- **Selected Square Count:** 4

#### Selection Channels
- **Direct Contribution:** 1 squares
- **Recurrence Contribution:** 0 squares
- **Bundle Contribution:** 3 squares
- **Observed-but-Rejected Count:** 60 squares
