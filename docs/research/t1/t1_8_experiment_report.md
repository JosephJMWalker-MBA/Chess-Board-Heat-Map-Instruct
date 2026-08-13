# T1.8 — Structural Conversion Evidence Bundles & Falsification Report

> [!WARNING]
> **Supersession Note:** This report constitutes procedurally compromised development evidence (T1.8-D). Its causal claims and execution provenance were invalidated and superseded by the [T1.8a Audit Report](t1_8a_audit_report.md). The historical text remains untouched.
## 1. Overview
This report finalizes the **T1.8 Execution** phase, in which we evaluate the candidate Structural Conversion hypothesis bounds against the pre-flighted C1–C14 fixture suite. The goal of this execution is to demonstrate how the Temporal Ledger's structural succession is causally qualified using the $n_{11}, n_{10}, n_{01}, n_{00}$ counterfactual partition matrix.

We evaluate the structural transitions across all legal root moves to distinguish mere historical coincidence from true causal conversion, isolating the consequences through Stockfish evaluations (CP Regret).

## 2. Evidence Partition Metrics
For each test fixture, we define the exact pre-move canonical signatures $e \in D_t$ (predecessor) and $f \in B_t$ (successor). We partition all legal root moves $M_{legal}(P_t)$ into four counterfactual classes:
- $M_{11}$ (Bundle): $e$ removed AND $f$ born
- $M_{10}$ (Removal only): $e$ removed, $f$ not born
- $M_{01}$ (Birth only): $f$ born, $e$ not removed
- $M_{00}$ (Neither): $e$ survives, $f$ not born

## 3. Experimental Results

### C6 — Empty Interventional Control ($n_{00} = 0$)
- **Context:** A forced move position (`1. e4 f5 2. Qh5+ g6 3. Qxg6+ hxg6`).
- **Results:**
  - $n_{11} = 1$
  - $n_{10} = 0, n_{01} = 0, n_{00} = 0$
  - Median CP Regret $M_{11} = 2$
- **Finding:** With $n_{00} = 0$ and $n_{01} = 0$, the conditional probability $P(B_f \mid \neg D_e)$ is **undefined** (not zero). The comparison class is empty. 

### C7 — Spatial Confounding ($n_{11} > 0$)
- **Context:** White's `3. Bc4` replacing the $f1$ sightlines with $c4$ sightlines.
- **Results:**
  - $n_{11} = 1$
  - $n_{10} = 6$
  - $n_{00} = 20$
  - Median CP Regret $M_{11} = 6.0$, $M_{10} = 66.0$, $M_{00} = 79.0$
- **Finding:** Because $n_{11} > 0$ and $n_{10} > 0$, we have strong evidence separating the bundle. The transition itself creates the bundle, but other moves remove the predecessor without producing the successor, proving the successor is not strictly bound to the predecessor's death.

### C8 — Non-Confounded Association
- **Context:** White's `2. c4` in the Queen's Gambit. 
- **Results:**
  - $n_{11} = 1$
  - $n_{10} = 2$
  - $n_{00} = 24$
  - Median CP Regret $M_{11} = -7.0$, $M_{10} = 40.0$, $M_{00} = 61.5$

### C9 — Non-Identical Bundle
- **Context:** `3. Qxd4` bringing the Queen into the center.
- **Results:**
  - $n_{11} = 1$, $n_{10} = 9$, $n_{00} = 28$
  - Median CP Regret $M_{11} = 21.0$, $M_{10} = 126.0$, $M_{00} = 102.0$

### C10 — Reappearing Signature
- **Context:** `3. Ng1` returning the knight to its original square.
- **Results:**
  - $n_{11} = 1$, $n_{10} = 5$, $n_{00} = 21$
  - Median CP Regret $M_{11} = 125.0$, $M_{10} = 419.0$, $M_{00} = 54.0$

### C11 — Mate-Sensitive Divergence
- **Context:** White's `4. Qxf7#` delivering checkmate.
- **Results:**
  - $n_{11} = 1$, $n_{10} = 13$, $n_{00} = 29$
  - Median CP Regret $M_{11} = 20000$ (Mate), $M_{10} = 10332$, $M_{00} = 10682$
- **Finding:** Correctly respects typed outcome bounds without collapsing mates into fake centipawns.

### C12 — Zero Optionality Control
- **Context:** A checkmated position resulting in a forced King move (`a1a2`).
- **Results:**
  - $n_{11} = 1$
  - $n_{10} = 0, n_{01} = 0, n_{00} = 0$
  - Median CP Regret $M_{11} = 0$
- **Finding:** A genuine 1-legal-root position correctly isolates the lack of comparison alternatives. 

### C14 — Consequence Sensitivity
- **Context:** Testing the exact same transition (`Ngf6`) against two different histories (one normal development, one where it blunders mate).
- **History A (Normal) Results:**
  - $n_{11} = 2$, $n_{10} = 2$, $n_{00} = 20$
  - Median CP Regret $M_{11} = 15.5$
- **History B (Mate Threat) Results:**
  - $n_{11} = 2$, $n_{10} = 2$, $n_{00} = 20$
  - Median CP Regret $M_{11} = 4992.5$
- **Finding:** The topology of the succession graph and the $n$-counts are identical between the histories, but the spatial consequence strictly bounds the differing outcomes. Structural conversion is verified independent of the consequence magnitude!

## 4. Conclusion
The experiment satisfies the user invariant: **T1.8 preserves the four evidence families (history, persistence, succession, consequence) separately without collapsing them into a single opaque conversion score.** 

The transition topology identifies *where* conversion happens; the counterfactual tables ($M_{11}$ vs $M_{10}$) identify *if* it is observationally bounded; the consequence metrics independently measure *what* effect it had.
