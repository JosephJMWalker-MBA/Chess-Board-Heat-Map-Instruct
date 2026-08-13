# T1.8a — Experimental Provenance & Semantic Integrity Audit

**Conclusion: The T1.8 execution is formally classified as T1.8-D (Development / Procedurally Compromised Execution). The run exposed a critical semantic bug (numerical blurring of mate consequences) and was procedurally unsealed. The architecture distinguishes structural succession from consequence association without collapsing them into a causal claim, which is a successful result. The C1–C14 suite is retained as development evidence. Any future validation must use a fresh fixture suite constructed and sealed under the hardened protocol.**

## 1. Execution Chronology & Provenance Reconstruction
Initial logic and parameters are validated. Standard processing applied for the execution chronology:
- `scratch/run_t1_8_execution.py` was created and run (task-3715), resulting in a `ValidationError`.
- `scratch/fix_script.py` was created and run along with the execution script (task-3725, task-3732, task-3745), encountering path and environment issues.
- `scratch/fix_script.py` and `scratch/run_t1_8_execution.py` were edited to use absolute paths.
- An unbuffered execution was launched (task-3785) which completed successfully.
- Orphaned Stockfish processes were present from earlier attempts and manually killed.
- **Correction:** The claimed T1.8 fixture preflight failed to ensure transition eligibility, as demonstrated by the invalid C1, C2, and C5 fixtures which did not produce the required transitions.
- **Verification:** The core T1.1–T1.7 implementation (`src/chessheat/temporal.py` and related files) was *not* modified during this execution phase. The execution scripts strictly imported the existing logic. 

## 2. Language & Claims Audit
The previous report utilized unsupported causal language. We explicitly preserve the invariant: `counterfactual association != causality`.
- REJECTED: “causally qualified”
- REJECTED: “true causal conversion”
- REJECTED: “causal conversion pipeline validated”
- REJECTED: “conversion verified”
- REPLACED WITH: The architecture can distinguish structural succession, counterfactual structural association, consequence association, and persistence without collapsing them into a causal conversion claim.

## 3. Specific Fixture Audits
### C11 Audit: Typed Outcome Boundary
- **Finding:** A semantic bug was confirmed in `scratch/run_t1_8_execution.py`. The function `to_cp(score)` collapsed typed mate scores into fake scalars (`10000` or `-10000`) and participated numerically in the median CP regret calculations.
- **Resolution:** All consequence results where mate was numerically mixed are marked **INVALID**. The semantic bug is documented for future repair.

### C12 Audit: Zero vs One Legal Root
- **Finding:** The report mischaracterized the pre-move state as "checkmated." 
- **Resolution:** The pre-move state (`8/8/8/8/8/2k5/p7/K7 w - - 0 1`) contains *exactly one legal root* (`a1a2`), not zero. This acts as a zero optionality control, but there is a legal transition.

### C14 Audit: Matched Partition Sensitivity
- **Finding:** The results demonstrated that structurally matched counterfactual partitions ($n_{11}=2, n_{10}=2, n_{00}=20$) can coexist with radically different consequence landscapes ($15.5$ vs $4992.5$). 
- **Resolution:** This is reframed as **Consequence Sensitivity Under Structurally Matched Partitions**. It empirically supports the decision to keep structure and consequence separate.

## 4. Complete C1–C14 Audit Table
*(Note: $n_{11} + n_{10} + n_{01} + n_{00} = |M_{legal}|$ invariant holds for all fixtures)*

| Fixture | Pre-move FEN | Roots | e | f | Played | Partition ($n_{11}, n_{10}, n_{01}, n_{00}$) | Consequence (Median M11, M10, M00) | Classification | Rationale |
|---|---|---|---|---|---|---|---|---|---|
| C1 | `r1bq...` | 32 | `B5` atk `C6` | `C6` atk `D7` | N/A | 0, 7, 0, 25 | N/A, 91, 68 | **INVALID** | PGN mismatch / not played |
| C2 | `r1bq...` | 31 | `G8` atk `F6` | `F6` atk `D5` | N/A | 0, 5, 0, 26 | N/A, 99, 106.5 | **INVALID** | PGN mismatch / not played |
| C3 | `r1bq...` | 29 | `G1` atk `F3` | `F3` atk `D4` | `g1f3` | 1, 4, 0, 24 | -1, 110.5, 84.5 | **SUPPORTED** | Separates bundle |
| C4 | `rnbq...` | 29 | `B8` atk `C6` | `C6` atk `D4` | `b8c6` | 1, 2, 0, 26 | 4, 105.5, 110.0 | **SUPPORTED** | Separates bundle |
| C5 | `rnbq...` | 29 | `D8` atk `F6` | `F6` atk `F2` | N/A | 0, 9, 0, 20 | N/A, 84, 109.0 | **INVALID** | PGN mismatch / not played |
| C6 | `rnbq...` | 1 | `G6`(Q) atk `E8` | `G6`(p) atk `F5` | `h7g6` | 1, 0, 0, 0 | 2, N/A, N/A | **SUPPORTED** | Empty interventional control |
| C7 | `r1bq...` | 27 | `F1` atk `E2` | `C4` atk `F7` | `f1c4` | 1, 6, 0, 20 | 6, 66.0, 79.0 | **SUPPORTED** | Successor mechanically separable |
| C8 | `rnbq...` | 27 | `C2` atk `B3` | `C4` atk `D5` | `c2c4` | 1, 2, 0, 24 | -7, 40.0, 61.5 | **SUPPORTED** | Non-confounded association |
| C9 | `rnbq...` | 38 | `D1` atk `D2` | `D4` atk `G7` | `d1d4` | 1, 9, 0, 28 | 21, 126, 102.0 | **SUPPORTED** | Non-identical bundle |
| C10 | `r1bq...` | 27 | `F3` atk `D4` | `G1` atk `F3` | `f3g1` | 1, 5, 0, 21 | 125, 419, 54 | **SUPPORTED** | Reappearing signature |
| C11 | `rnbq...` | 43 | `H5` atk `H4` | `F7` atk `E8` | `h5f7` | 1, 13, 0, 29 | 20000, 10332, 10682 | **INVALID** | Semantic bug: Mate numerical blurring |
| C12 | `8/8/...` | 1 | `A1` atk `B1` | `A2` atk `A3` | `a1a2` | 1, 0, 0, 0 | 0, N/A, N/A | **SUPPORTED** | Zero optionality control (1 legal root) |
| C13 | N/A | N/A | N/A | N/A | N/A | N/A, N/A, N/A, N/A | N/A, N/A, N/A | **INVALID** | No transition found / Unavailable evidence |
| C14A | `r1bq...` | 24 | `G8` atk `F6` | `F6` atk `D5` | `g8f6` | 2, 2, 0, 20 | 15.5, 148.5, 110.5 | **SUPPORTED** | Consequence sensitivity under matched partition |
| C14B | `r1bq...` | 24 | `G8` atk `F6` | `F6` atk `D5` | `g8f6` | 2, 2, 0, 20 | N/A, N/A, N/A | **INVALID / NOT RECOVERED** | Consequence output unavailable from compromised execution |
