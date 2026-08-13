# T1.9a — Seal & Validation Semantics Audit

**Status:** PROVISIONAL EXECUTION (T1.9-P) PENDING AUDIT RESOLUTION

## 1. Audit of the Code Seal
- **Finding:** The previously reported "Code SHA" (`e5b9a374bcb16b25b4aac8a1c0a7e04cdf49a4da`) only resolves to the base repository commit (which predates T1 development entirely). The `t1_9_2_structural_seal.md` did **not** capture cryptographic hashes for the core working tree files (`src/chessheat/temporal.py`, `src/chessheat/consequence.py`). 
- **Resolution:** The pre-execution code seal is **INSUFFICIENT**. The execution provenance is not formally sealed against the core code logic.

## 2. CP Regret Semantics
- **Finding:** The execution runner (`scratch/t1_9_execution.py`) violated the formal definition of regret $R(m) = E^* - E(m)$. 
  - On line 40, `best_score` was computed by asking Stockfish for its baseline evaluation of the FEN state, rather than calculating $E^* = \max_{m \in M_{legal}} E(m)$ from the evaluations of all legal continuations. 
  - Because chess engines compute a singular evaluation based on depth/alpha-beta cutoffs, the engine's root evaluation `best_score` can occasionally be slightly lower than the evaluation of the actual best move when searched individually. 
  - This resulted in negative "regrets" in V2 (-6) and V14B (-2) because the move evaluation $E(m)$ returned a higher CP than the baseline root evaluation $E_{root}$.
- **Resolution:** The reported numbers are **signed outcome deltas from the root evaluation**, not strictly CP regret as defined by the metric $R(m) \ge 0$.

## 3. Missing Evidence-Family Demonstrations
The summary report lacked the necessary mechanical depth to prove the categories:
- **V5 (Ephemeral):** Failed to capture or report the successor observed duration and right-censoring boundary.
- **V7 (Confounded Bundle):** Did not identify the exact `ConversionEvidenceBundle` ID, the constituent geometric pairs, the bundle size, or mechanically prove identical support partitions for the entire bundle.
- **V8/V9 (Spatial Overlap):** Did not compute or output the specific boolean intersection states for the spatial shapes.
- **V10 (Reappearance):** Did not invoke or evaluate `is_born_reappearance=True` against a prior episode.
- **V11 (Mate-Sensitive):** Failed to output `cp_count` and `mate_count`. An empty CP set resulting in `None` does not prove mate was handled correctly unless the mate count is verified.
- **V13 (Different History):** Did not execute or compare two separate temporal ledgers to prove terminal-state equality and temporal-ledger divergence.
- **V14 (Matched Partitions):** Only reported partition sizes (counts), failing to verify identical move memberships between the two FENs.

## 4. Reclassification Against Sealed Hypotheses
*(Only evaluating fixtures called out in the user audit)*

### V2. Independent Successor Birth
- **Preregistered Hypothesis:** The structural partition will reveal a non-zero $n_{01}$ (birth without death) or significant $n_{00}$, proving the birth is not rigidly locked to the death.
- **Raw Evidence:** $n_{01}=0$, $n_{00}=25$.
- **Result:** **FALSIFIED**. 
- **Rationale:** The hypothesis claimed the successor could arise independently of the predecessor's death. However, $P(B_f \mid \neg D_e) = 0$. Across all 25 roots that preserved the predecessor, the successor was born 0 times. The existence of $n_{00} > 0$ simply means there are moves that do neither; it does not prove independent birth.

### V3. Structural Coupling Without Consequence
- **Preregistered Hypothesis:** $M_{11}$ will exhibit near-zero CP regret relative to $M_{10}$ and $M_{00}$, confirming that structural progression does not automatically confer leverage.
- **Raw Evidence:** M11 = 39, M10 = 57, M00 = 43.
- **Result:** **AMBIGUOUS**.
- **Rationale:** The manifest did not preregister a mathematical threshold for "near-zero" or "practically indistinguishable." 39 CP is nearly a third of a pawn advantage, which is a measurable consequence difference from 57 CP. 

### V4. Consequence Without Strong Structural Coupling
- **Preregistered Hypothesis:** The transition has massive negative consequence (regret), but the structural partition $M_{10}$ shows minimal regret, proving the removal of $e$ didn't cause the catastrophe.
- **Raw Evidence:** M11 = 286, M10 = 441.
- **Result:** **INVALID**.
- **Rationale:** The incorrect computation of $E^*$ (using the engine's root baseline instead of $\max_{m \in M_{legal}} E(m)$) invalidates all T1.9 consequence results labeled CP regret, not only the fixtures where negative values appeared. Because the runner never computed the correctly defined regret $R(m) \ge 0$, any consequence-based preregistered hypothesis cannot be classified as SUPPORTED using these numbers. The structural partition can remain observed development evidence, but the consequence portion is invalid for the preregistered regret hypothesis.

## 5. Final T1.9 Status
**Status:** **PROCEDURALLY COMPROMISED**

**Reasoning:**
1. The pre-execution code seal was insufficient. The core `src/` logic was not hashed.
2. The mathematical implementation of CP regret violated the $R(m) \ge 0$ invariant, producing negative deltas.
3. The execution runner failed to output the necessary mechanical evidence (durations, bundles, overlap booleans, history ledgers) required to actually test the 14 conceptual categories.
