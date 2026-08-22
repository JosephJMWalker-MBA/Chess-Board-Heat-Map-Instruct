# CP Downstream Experiment Protocol Freeze V2
**Protocol Identifier:** CP_REPRESENTATION_EFFICIENCY_PROTOCOL_V2
**Canonical JSON Protocol Digest:** ecd9b1286aed3681de2f4042b339ce20112d0e602b4a9b6860f46d58fb45fb37 (SHA256 of `artifacts/research/cp_representation_efficiency_protocol_v2.json`)

## 1. V1 Failure Provenance
The V1 protocol freeze (commit `ba11bde`) failed independent audit (`8ac1317`) for redefining frozen continuous amplitude operators as binary planes, violating information-equalized interfaces, and reversing outcome utility signs. The V2 freeze restores the authoritative pre-freeze reference (`8876f8c`) while resolving genuine blockers in a completely TARGET-blind manner.

## 2. Inherited Frozen Mathematics & Canonical Orientation
- Unordered pairs $u = (P, \{m,n\})$ use the canonical orientation $m_1 < m_2$ based strictly on lexicographic comparison of UCI strings.
- $D$ is the deduplicated set of destination squares for $m_1, m_2$.
- $T$ is the deduplicated set of from/to squares for $m_1, m_2$.
- $a_X = |CP_X(m_1) - CP_X(m_2)|$
- $d_X = Compare(CP_X(m_1), CP_X(m_2))$ (3-way FIRST_BETTER / EQUAL / SECOND_BETTER).
- $M_D(s) = a_X / |D|$ if $s \in D$ else $0$.
- $M_T(s) = a_X / |T|$ if $s \in T$ else $0$.
- $B_{daS}$ uses $M_0$ which is identically $0$ for all squares.

## 3. Split Grouping & Pair-Eligible Counts
- **Grouping:** Roots are grouped by a conservative transposition-equivalent key: `board_arrangement_fen|side_to_move|castling_rights|en_passant_square`.
- **Partition:** Determined by `SHA256("CHESSHEAT_SPLIT_V2|" + group_key) mod 100` (TRAIN 0-69, VALIDATION 70-84, TEST 85-99).
- **Exact Counts (all 33,859 roots):** TRAIN 23,772; VALIDATION 4,979; TEST 5,108.
- **Exact SOURCE-Pair-Eligible Counts:** TRAIN 23,471; VALIDATION 4,922; TEST 5,051. (A root is eligible if it has $\ge 2$ finite-CP alternatives).
- **20k Feasibility:** 20,000 max budget is strictly feasible within the 23,471 eligible TRAIN roots.
- **Zero-Pair SOURCE Semantics:** 415 zero-pair roots exist in the base population but are prospectively excluded from training budgets, validation pools, and test denominators.

## 4. Budget Ordering
- **Target-Blind & Seed-Independent Ordering:** Select nested budgets (250, 500, 1000, 2000, 4000, 8000, 16000, 20000) using the strict ascending sort of `SHA256("CHESSHEAT_BUDGET_ORDER_V2|" + root_identity)`. 
- Learner seed choice explicitly DOES NOT influence this budget order. Every representation and seed receives identical roots at budget $n$.

## 5. Target Attrition Semantics
If TARGET produces non-evaluable pairs (e.g. mate outcomes), those pairs are excluded from pair-level analysis. If a selected nominal training root has 0 TARGET-evaluable pairs, it is retained in the nominal $x$-axis budget but contributes 0 training examples. It is not replaced. The actual effective training-root counts will be recorded at every budget.

## 6. Numeric P Encoding (8x8x18, float32)
Orientation: row 0=rank 8, row 7=rank 1. Col 0=file a, Col 7=file h. 
- 0-5: White P, N, B, R, Q, K (1.0 occupancy).
- 6-11: Black p, n, b, r, q, k (1.0 occupancy).
- 12: Side-to-move (1.0 for White, 0.0 for Black, broadcast).
- 13-16: Castling rights (White K/Q, Black k/q, broadcast 1.0 or 0.0).
- 17: En-passant target square (one-hot 1.0, else 0.0).
Note: `halfmove_clock`, `fullmove_number`, and `history_identity` are not learner features, though retained in full semantics.

## 7. Numeric $S^\star$, $d_X$, $a_X$ (270-vector, float32)
All primary models receive this 270-dim non-spatial side vector identically:
- **$m_1$ (133 dims):** 64-onehot From, 64-onehot To, 5-onehot Promotion (None, Q, R, B, N).
- **$m_2$ (133 dims):** Same layout, offset by 133.
- **$d_X$ (3 dims):** One-hot (FIRST_BETTER, EQUAL, SECOND_BETTER).
- **$a_X$ (1 dim):** Raw scalar finite-CP difference.

## 8. $B_{perm}$ & $B_{raw}$
- **$B_{daS}$:** Explicit zero-spatial baseline using $M_0$.
- **$B_{perm}$:** Separate matched comparator. A strictly fixed global spatial permutation (seed-independent, key: `CHESSHEAT_MATCHED_PERM_V2|<sq>`) applied only to $M_T$. Preserves value multiset and mass, destroys geometry.
- **$B_{raw}$:** Diagnostic only, not part of primary testing.

## 9. Learner Architecture & PyTorch Freeze
- **Status:** `ML_RUNTIME_DEPENDENCY_NOT_YET_SATISFIED`. TARGET execution is blocked until PyTorch versioning is pinned in the environment.
- **Architecture:** `19x8x8` input $\to$ Conv2d(19, 64, k=3, p=1) $\to$ Conv2d(64, 64) $\to$ Conv2d(64, 64) $\to$ GAP $\to$ 64 spatial features.
  Non-spatial `270` input $\to$ Dense(128) $\to$ 128 side features.
  Concat(192) $\to$ Dense(128) $\to$ Dense(3 logits). (All ReLUs, no BN, no Dropout).
- **Optimizer:** Adam ($lr=1e-3, \beta=(0.9, 0.999), \epsilon=1e-8, wd=1e-5$).
- **Init:** Kaiming uniform (linear/conv), uniform (bias).
- **Batching:** 64 roots per batch, sorted by `CHESSHEAT_MINIBATCH_V2|<seed>|<epoch>|<root_identity>`.
- **Early Stopping:** Max 200 epochs. Stop when 20 epochs complete with no strict improvement on validation NLL (min_delta=0.0). Restore best epoch for TEST evaluation.

## 10. Seeds & Aggregation
- **Fixed Seed Set:** `[1729, 2718, 31415, 65537, 104729]`.
- **Aggregation:** Average root-weighted NLL across all 5 seeds *before* computing root inference or AULC.

## 11. Utility & AULC
- **Utility:** $U(n) = - \text{mean\_root\_nll}$. Thus **LARGER utility is BETTER**.
- **AULC:** Normalized trapezoidal integration of $U(n)$ across the strict x-axis (250..20,000 roots). Functions must fail closed (raise) if inputs are empty or misaligned.

## 12. Outcomes & Confidence
- **Contrasts:** 
  - $\Delta_{DT} = AULC_D - AULC_T$
  - $\Delta_{D0} = AULC_D - AULC_{B_{daS}}$
  - $\Delta_{T0} = AULC_T - AULC_{B_{daS}}$
  (*Positive $\Delta_{DT}$ favors $D$*).
- **Bootstrap:** 10,000 paired-root resamples of TEST using strict `CHESSHEAT_BOOTSTRAP_V2|<b>|<j>` drawing. Computes 95% marginal percentile bounds (2.5% - 97.5%).
- **Claim Ceiling & TARGET Non-Inspection:** Claims remain explicitly bounded to representation efficiency comparison under this frozen task. TARGET was completely un-inspected during this repair.
