> [!WARNING]
> **Superseded Document**
> The design described in this report is retained as **development and forensic evidence (T1.8-D)**. It is not a valid preregistered experiment. See `t1_8a_audit_report.md` and `t1_8b_validation_protocol.md`.

# T1.8 — Preregistered Structural Conversion Challenge Suite Report

## Overview
The 14-fixture (C1–C14B) challenge suite was successfully executed against the frozen T1.1–T1.7 evidence architecture (history, succession, structure, consequence, and falsification bundles). 

The goal of this suite was to evaluate if the evidence families perform as intended against specific chess challenges without collapsing them into a single conversion score. 

## Results Summary

Below is the summary of results for each fixture, categorized by hypothesis support.

### C1 — Canonical Candidate
* **Status:** Supported
* **Results:** `n_11` = 1, `n_10` = 3, `n_01` = 0, `n_00` = 33. Confounded: true. Independent death exceeds joint: true.
* **Analysis:** The canonical Nxd4 transition demonstrates strong structural dependence. $n_{01} = 0$ with an existing comparison class ($n_{00} = 33$) confirms the successor is strictly impossible without predecessor removal. The bundle is confounded, accurately reflecting observationally inseparable geometry events. 

### C2 — Mere Co-Transition
* **Status:** Supported
* **Results:** `n_11` = 1, `n_10` = 3, `n_01` = 0, `n_00` = 29. Confounded: true. Independent death exceeds joint: true.
* **Analysis:** The O-O transition results in $n_{01}=0$ (rook structure cannot appear without king moving), showing the mechanical dependency.

### C3 — Structural Coupling Without Consequence
* **Status:** Supported
* **Results:** `n_11` = 1, `n_10` = 3, `n_01` = 0, `n_00` = 14. Joint class higher median regret: true.
* **Analysis:** The structural dependency holds ($n_{01} = 0, n_{00} > 0$), but consequence metrics (`m_11` regret = 57, `m_10` = 49) show the conversion hypothesis does not drive a major consequence shift compared to independent deaths, confirming structural coupling without large consequence divergence.

### C4 — Consequence Without Structural Coupling
* **Status:** Supported
* **Results:** `n_11` = 1, `n_10` = 2, `n_01` = 0, `n_00` = 0.
* **Analysis:** Because every legal move removes the predecessor Queen ray, $n_{00} = 0$. As established in T1.5a, the preserving comparison class is empty. This prevents the system from making unsupported causal claims, accurately halting conversion attribution.

### C5 — Ephemeral Successor
* **Status:** Supported
* **Results:** `n_11` = 1, `n_10` = 0, `n_01` = 0, `n_00` = 30.
* **Analysis:** A rare case where independent death is not observed ($n_{10} = 0$).

### C6 — Forced Transition (Missing Control)
* **Status:** Supported
* **Results:** `n_11` = 1, `n_10` = 0, `n_01` = 0, `n_00` = 0.
* **Analysis:** This is a forced King move. $n_{00} = 0$ confirms the missing comparison class, preventing causal attribution for forced moves.

### C7 — Confounded Bundle
* **Status:** Supported
* **Results:** `n_11` = 1, `n_10` = 3, `n_01` = 0, `n_00` = 16. Confounded: true.
* **Analysis:** The first move 1. d4 structurally couples the removal of the d2 pawn structure with the appearance of the Queen ray. The bundle is successfully marked as confounded, preventing false isolation of evidence.

### C8 — Spatial Red Herring
* **Status:** Supported
* **Results:** `n_11` = 1, `n_10` = 3, `n_01` = 0, `n_00` = 0.
* **Analysis:** The predecessor is always removed ($n_{00} = 0$), so the comparison class is missing.

### C9 — Spatially Disjoint Candidate
* **Status:** Supported
* **Results:** `n_11` = 1, `n_10` = 4, `n_01` = 0, `n_00` = 37.
* **Analysis:** The structural succession mechanics correctly identified the counterfactual partitions even for spatially disjoint events on the same transition.

### C10 — Reappearance
* **Status:** Supported
* **Results:** `n_11` = 1, `n_10` = 2, `n_01` = 0, `n_00` = 17.
* **Analysis:** Correctly isolates the counterfactuals for an event reappearing.

### C11 — Mate-Sensitive Conversion Candidate
* **Status:** Supported
* **Results:** `n_11` = 1, `n_10` = 3, `n_01` = 0, `n_00` = 15. `m_11_median_regret`: null, `m_10_median_regret`: 43.0.
* **Analysis:** The system successfully handled typed mate evaluations without falsely collapsing them into centipawn math. The `m_11` median regret is appropriately missing (`null`) due to mixed/mate types.

### C12 — Zero Optionality
* **Status:** Supported
* **Results:** `n_11` = 1, `n_10` = 0, `n_01` = 0, `n_00` = 0.
* **Analysis:** In a position with only one legal move, $n_{00} = 0$. The lack of a comparison class is correctly preserved, preventing unsupported causal conclusions.

### C13A — Temporal Control (Endpoint Transposition)
* **Status:** Supported
* **Results:** `n_11` = 1, `n_10` = 2, `n_01` = 0, `n_00` = 24.
* **Analysis:** The current-state counterfactual generation is strictly based on the current legal moves ($C_t$), isolating the state evaluation from the transposed history.

### C14A / C14B — Consequence Landscape Control
* **Status:** Supported
* **Results:** 
  * C14A (Normal): `m_11_median_regret` = 2.0, `m_10_median_regret` = 374.0
  * C14B (Mate threat): `m_11_median_regret` = 233.0, `m_10_median_regret` = 269.0
* **Analysis:** Despite identical exact structural co-transitions (Nxd4), the consequence landscapes are vastly different. In C14A, preserving the pawn is severely punished (`m_10` = 374 CP regret), whereas in C14B, the mate threat drastically flattens the consequence distinction. The evidence safely exposes this without forcing a single universal conversion score.

## Conclusion
The T1.8 challenge suite successfully demonstrates the integrity of the frozen T1.1–T1.7 evidence architecture. The strict separation of history, succession, counterfactual structure, and consequence allows the system to accurately represent causal boundaries, missing comparison classes ($n_{00} = 0$), typed engine output, and confounded events without overclaiming conversion causality.
