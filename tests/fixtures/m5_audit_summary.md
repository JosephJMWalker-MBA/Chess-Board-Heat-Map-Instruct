# Milestone 5.5: Machine-Auditable Validation Summary

## F1_Tactical_Fork
**Target Layer:** destination + min_cp_regret
**Expected Hot:** f6
**Expected Quiet:** h1, a1

### Budget Ranks
- **50000 nodes:**
  - Top 5: d2, c2, e2, d6, e1
  - Expected Hot Ranks: {'f6': -1}
- **100000 nodes:**
  - Top 5: d2, e2, c2, e1
  - Expected Hot Ranks: {'f6': -1}
- **250000 nodes:**
  - Top 5: c2, e2, d2
  - Expected Hot Ranks: {'f6': -1}

### Top-5 Stability (Jaccard Index)
- 50k vs 100k: 0.80
- 100k vs 250k: 0.75

## F2_Poisoned_Destination
**Target Layer:** destination + mean_cp_regret
**Expected Hot:** d5
**Expected Quiet:** e4, d3

### Budget Ranks
- **50000 nodes:**
  - Top 5: a1, d2, f1, g1, e2
  - Expected Hot Ranks: {'d5': 23}
- **100000 nodes:**
  - Top 5: d3, f1, g4, c3, d2
  - Expected Hot Ranks: {'d5': 22}
- **250000 nodes:**
  - Top 5:
  - Expected Hot Ranks: {'d5': -1}

### Top-5 Stability (Jaccard Index)
- 50k vs 100k: 0.25
- 100k vs 250k: 0.00

## F3_Soft_Pin
**Target Layer:** origin + mean_cp_regret
**Expected Hot:** e4
**Expected Quiet:** h8, a8

### Budget Ranks
- **50000 nodes:**
  - Top 5: g1, e1, e4
  - Expected Hot Ranks: {'e4': 3}
- **100000 nodes:**
  - Top 5: g1, e1, e4
  - Expected Hot Ranks: {'e4': 3}
- **250000 nodes:**
  - Top 5: g1, e1, e4
  - Expected Hot Ranks: {'e4': 3}

### Top-5 Stability (Jaccard Index)
- 50k vs 100k: 1.00
- 100k vs 250k: 1.00

## F4_Overloaded_Defender
**Target Layer:** destination + best_cp
**Expected Hot:** d5, b7
**Expected Quiet:** f6

### Budget Ranks
- **50000 nodes:**
  - Top 5:
  - Expected Hot Ranks: {'b7': -1, 'd5': -1}
- **100000 nodes:**
  - Top 5:
  - Expected Hot Ranks: {'b7': -1, 'd5': -1}
- **250000 nodes:**
  - Top 5:
  - Expected Hot Ranks: {'b7': -1, 'd5': -1}

### Top-5 Stability (Jaccard Index)
- 50k vs 100k: 1.00
- 100k vs 250k: 1.00

## F5_Central_Pawn_Break
**Target Layer:** delta outcome
**Expected Hot:** e4, d5, d4
**Expected Quiet:** h2, a7

### Budget Ranks
- **50000 nodes:**
  - Top 5:
  - Expected Hot Ranks: {'e4': -1, 'd4': -1, 'd5': -1}
- **100000 nodes:**
  - Top 5:
  - Expected Hot Ranks: {'e4': -1, 'd4': -1, 'd5': -1}
- **250000 nodes:**
  - Top 5:
  - Expected Hot Ranks: {'e4': -1, 'd4': -1, 'd5': -1}

### Top-5 Stability (Jaccard Index)
- 50k vs 100k: 1.00
- 100k vs 250k: 1.00

## F6_Discovered_Attack
**Target Layer:** None
**Expected Hot:** d1, d5
**Expected Quiet:** h8

### Budget Ranks
- **50000 nodes:**
  - Top 5:
  - Expected Hot Ranks: {'d1': -1, 'd5': -1}
- **100000 nodes:**
  - Top 5:
  - Expected Hot Ranks: {'d1': -1, 'd5': -1}
- **250000 nodes:**
  - Top 5:
  - Expected Hot Ranks: {'d1': -1, 'd5': -1}

### Top-5 Stability (Jaccard Index)
- 50k vs 100k: 1.00
- 100k vs 250k: 1.00

## F7_Quiet_Positional_Move
**Target Layer:** origin + min_cp_regret (should be dispersed)
**Expected Hot:**
**Expected Quiet:** a1, h8

### Budget Ranks
- **50000 nodes:**
  - Top 5:
  - Expected Hot Ranks: {}
- **100000 nodes:**
  - Top 5:
  - Expected Hot Ranks: {}
- **250000 nodes:**
  - Top 5:
  - Expected Hot Ranks: {}

### Top-5 Stability (Jaccard Index)
- 50k vs 100k: 1.00
- 100k vs 250k: 1.00

## F8_Negative_Control
**Target Layer:** all
**Expected Hot:**
**Expected Quiet:** a1, h8

### Budget Ranks
- **50000 nodes:**
  - Top 5: c2, d3, c3, b3, d2
  - Expected Hot Ranks: {}
- **100000 nodes:**
  - Top 5: c2, d3, c3, b3, d2
  - Expected Hot Ranks: {}
- **250000 nodes:**
  - Top 5: c2, d3, c3, b3, d2
  - Expected Hot Ranks: {}

### Top-5 Stability (Jaccard Index)
- 50k vs 100k: 1.00
- 100k vs 250k: 1.00
