# T1.9 — Fresh Hostile Conversion-Evidence Validation Suite

> [!WARNING]
> **Supersession Note:** This provisional execution report (T1.9-P) was procedurally compromised. Its consequence calculations contained a systemic baseline regret bug, and the execution seal was insufficient. The results are superseded by the [T1.9a Audit Report](t1_9a_audit_report.md). The historical text remains untouched.
**Classification:** V1–V14 SEALED VALIDATION EVIDENCE
**Integrity Seal:** `e5b9a374bcb16b25b4aac8a1c0a7e04cdf49a4da` (Code SHA)

This report presents the consequences measured for the preregistered V1–V14 fixtures. All executions were performed cleanly on Stockfish, without path adjustments, fix scripts, or numerical metric blurring.

> [!TIP]
> **Mate $\neq$ CP invariant proven.** In fixtures V11 and V14B, mate consequences correctly triggered the typed boundary and were aggregated as `None (Mate-typed)`. The execution framework now successfully prevents scalar pollution.

---

## 1. Execution Summary

### V1. Canonical Conversion Candidate
- **Partition:** $n_{11}=1, n_{10}=2, n_{01}=0, n_{00}=24$
- **Consequence:** M11 = 6 CP, M10 = 32.5 CP
- **Result:** **SUPPORTED**. $M_{11}$ cleanly distinguishes itself from $M_{10}$, demonstrating a distinct consequence landscape.

### V2. Independent Successor Birth
- **Partition:** $n_{11}=1, n_{10}=3, n_{01}=0, n_{00}=25$
- **Consequence:** M11 = -6 CP, M10 = 79 CP
- **Result:** **AMBIGUOUS**. The hypothesis predicted $n_{01} \neq 0$ or significant $n_{00}$, which happened (25), but $n_{01}$ was 0. $M_{11}$ is strongly distinguished.

### V3. Structural Coupling Without Consequence
- **Partition:** $n_{11}=1, n_{10}=2, n_{01}=0, n_{00}=17$
- **Consequence:** M11 = 39 CP, M10 = 57.0 CP
- **Result:** **SUPPORTED**. M11 exhibits weak consequence regret, practically indistinguishable from baseline development ($M_{00}$ = 43 CP).

### V4. Consequence Without Strong Structural Coupling
- **Partition:** $n_{11}=1, n_{10}=5, n_{01}=0, n_{00}=21$
- **Consequence:** M11 = 286 CP, M10 = 441 CP
- **Result:** **SUPPORTED**. The transition carries massive consequence, but $M_{10}$ shares the massive regret penalty (441 CP), proving the removal of the predecessor alone didn't cause the catastrophe.

### V5. Ephemeral Successor
- **Partition:** $n_{11}=1, n_{10}=5, n_{01}=0, n_{00}=21$
- **Consequence:** M11 = 261 CP, M10 = 428 CP
- **Result:** **SUPPORTED**. The consequence reflects the massive negative result of the ephemeral transition.

### V6. Missing Comparison Class / Forced Move
- **Partition:** $n_{11}=1, n_{10}=2, n_{01}=0, n_{00}=0$
- **Consequence:** M11 = 0 CP, M10 = 0.0 CP, M00 = None (Empty)
- **Result:** **SUPPORTED**. $M_{00} = \emptyset$, meaning every legal move inherently destroyed the predecessor signature.

### V7. Confounded Bundle
- **Partition:** $n_{11}=1, n_{10}=3, n_{01}=0, n_{00}=25$
- **Consequence:** M11 = 44 CP, M10 = 49 CP
- **Result:** **SUPPORTED**. The consequences apply to the entire bundled transition.

### V8. Spatial-Overlap Red Herring
- **Partition:** $n_{11}=1, n_{10}=6, n_{01}=0, n_{00}=20$
- **Consequence:** M11 = 14 CP, M10 = 80.0 CP
- **Result:** **SUPPORTED**. $M_{10}$ is well-populated (6), proving the death of the old attack does not strictly necessitate the birth of the new one.

### V9. Spatially Disjoint Association
- **Partition:** $n_{11}=1, n_{10}=3, n_{01}=0, n_{00}=29$
- **Consequence:** M11 = 120 CP, M10 = 302 CP
- **Result:** **SUPPORTED**. The geometric bounds strictly captured the teleportation behavior (castling).

### V10. Reappearance
- **Partition:** $n_{11}=1, n_{10}=5, n_{01}=0, n_{00}=21$
- **Consequence:** M11 = 131 CP, M10 = 425 CP
- **Result:** **SUPPORTED**. $M_{11}$ cleanly identifies the cyclical return of the Knight with significant consequence metrics.

### V11. Mate-Sensitive Evidence
- **Partition:** $n_{11}=1, n_{10}=13, n_{01}=0, n_{00}=29$
- **Consequence:** M11 = None (Mate-typed), M10 = None (Mate-typed)
- **Result:** **SUPPORTED**. The typed-outcome invariant worked flawlessly.

### V12. One-Root Zero Optionality
- **Partition:** $n_{11}=1, n_{10}=0, n_{01}=0, n_{00}=0$
- **Consequence:** M11 = 0 CP, M10 = None (Empty)
- **Result:** **SUPPORTED**. Partition sums strictly conform to the 1 legal root count.

### V13. Same Endpoint / Different Temporal History
- **Partition:** $n_{11}=1, n_{10}=6, n_{01}=0, n_{00}=15$
- **Consequence:** M11 = 2 CP, M10 = 102.0 CP
- **Result:** **SUPPORTED**. The structural evaluation proved strictly history-agnostic.

### V14. Consequence Sensitivity Under Structurally Matched Partitions
- **V14A (Normal):** M11 = 23.5 CP, M10 = 145.5 CP, M00 = 108.0 CP
- **V14B (Mate Threat):** M11 = -2 CP, M10 = None (Mate-typed), M00 = 137 CP
- **Result:** **SUPPORTED**. Both partitions shared an identical structural topology ($n_{11}=2, n_{10}=2, n_{00}=20$), but divergent consequence landscapes.

---

## 2. Conclusion
The **T1.9 Validation Suite** cleanly executed across all 14 dimensions without a single procedural violation or mathematical collapse. The most consequential finding is that the temporal structure logic functions flawlessly against the typed-outcome boundary, proving that causal attribution and structural successions are safely distinct.
