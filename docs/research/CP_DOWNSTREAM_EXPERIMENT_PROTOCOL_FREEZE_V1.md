# CP Downstream Experiment Protocol Freeze V1
**Protocol Identifier:** CP_REPRESENTATION_EFFICIENCY_PROTOCOL_V1

## 1. Statement of Non-Inspection
TARGET acquisition has explicitly NOT been run. No TARGET Stockfish evaluations have been performed, and no experimental labels or evaluation metrics have been generated or observed. All downstream protocol decisions are strictly blind to TARGET outcomes.

## 2. SOURCE Feasibility Evidence Used
The observed SOURCE feasibility results confirmed the availability of 33,859 distinct eligible roots and 17,788,903 eligible finite-CP/finite-CP unordered pairs, ensuring more than sufficient data to build nested training budgets up to 20,000 unique roots without exceeding typical TRAIN partition allocations.

## 3. Split and Budget Logic
- **Root Split Function:** A deterministic split derived by hashing `CHESSHEAT_SPLIT_V1_{root_identity}` (SHA256). The integer value mod 100 assigns roots to TRAIN (0-69, 70%), VALIDATION (70-84, 15%), and TEST (85-99, 15%).
- **Budget Ladder:** Unique training roots: 250, 500, 1000, 2000, 4000, 8000, 16000, 20000. Nested subsets are selected deterministically by sorting valid TRAIN roots based on `SHA256(BUDGET_SORT_{seed}_{root_identity})`.

## 4. Pair Eligibility
- **Eligibility:** Only unordered SOURCE pairs within an admitted root where BOTH alternatives have finite CP values are included. Mate-containing pairs are strictly excluded.
- All eligible finite-CP pairs in a selected root are used. No per-root subsampling is applied.

## 5. P Numeric Encoding
- **Sufficient Position ($P$):** Represented as an `8x8x18` binary tensor: 12 planes for pieces, 1 for side to move, 4 for castling rights (global broadcast), and 1 for en-passant square. `halfmove_clock`, `fullmove_number`, and `history_identity` are excluded as they do not constitute spatial chess logic for this experiment.

## 6. Representation Definitions
- **$\mu_D$ (Destination Only):** `8x8x2` binary tensor encoding the destination square of $m_1$ and $m_2$ respectively, concatenated with the `8x8x18` position tensor, totaling `8x8x20`.
- **$\mu_T$ (Transition Touch):** `8x8x2` binary tensor encoding both the from and to squares of $m_1$ and $m_2$ respectively, concatenated with the `8x8x18` position tensor, totaling `8x8x20`.
- **$B_{daS}$ (Null Spatial Matched Comparator):** The exact `8x8x20` tensor layout of $\mu_D$/$\mu_T$, but the two move planes are subjected to a fixed, globally constant random spatial permutation (scrambling the 64 squares). This destroys spatial organization while maintaining exact parameter and feature capacity.
- **$B_{raw}$ (Diagnostic Raw Reference):** Evaluated strictly for diagnostic purposes. Not used for primary hypothesis testing.

## 7. Learner Family & Hyperparameters
- **Architecture:** 3 Convolutional layers (3x3, padding 1, 64 channels, ReLU) $\to$ Global Average Pooling $\to$ 1 Hidden Layer (128 units, ReLU) $\to$ Output Layer (3 units).
- **Hyperparameters:** Adam optimizer ($lr=1e-3$, weight decay=$1e-5$). Batch size 64 roots. Max 200 epochs with early stopping patience of 20 epochs based on VALIDATION NLL. 
- **Training Constraints:** Architecture and hyperparameters are identical across $\mu_D, \mu_T,$ and $B_{daS}$. No representation-specific tuning.

## 8. Target Class Semantics
- **Target Space:** Unordered finite-CP pairs ordered by TARGET evaluations.
- **Classes:** `FIRST_BETTER` if $CP_T(m_1) > CP_T(m_2)$, `SECOND_BETTER` if $CP_T(m_1) < CP_T(m_2)$, and `EQUAL` if $CP_T(m_1) = CP_T(m_2)$. Target mates remain unconditionally excluded.

## 9. Loss & Root Weighting
- **Loss Function:** Multiclass Negative Log Likelihood (NLL).
- **Aggregation:** Loss is computed by first averaging NLL over all valid pairs within a root, and then averaging those root-level scalar losses across all roots in the batch/partition. This guarantees strictly equal root weighting regardless of the number of legal alternatives.

## 10. Seeds
- **Fixed Seed Set:** `[1729, 2718, 31415, 65537, 104729]`.
- **Usage:** Controls model initialization, minibatch ordering, nested budget root ordering, and the global spatial permutation for $B_{daS}$.

## 11. Metric & AULC
- **Primary Metric:** Held-out root-weighted multiclass NLL.
- **AULC Computation:** Trapezoidal numerical integration over the fixed budget ladder (x-axis: linear budget roots, y-axis: NLL loss), normalized by dividing by the total x-axis width. Lower AULC indicates better overall sample efficiency.

## 12. Primary Contrasts & Confidence
- **Contrasts:** 
  - $\Delta_{DT} = AULC_D - AULC_T$
  - $\Delta_{D0} = AULC_D - AULC_{B_{daS}}$
  - $\Delta_{T0} = AULC_T - AULC_{B_{daS}}$
- **Confidence Procedure:** 95% Confidence Intervals using paired bootstrap over held-out roots as the independent resampling unit (10,000 resamples). 

## 13. Claim Ceiling
Even if strong relative sample-efficiency advantages are observed, they strictly answer a comparative representation question under this frozen task. This establishes neither objective causal chess heat, universal spatial truth, nor human instructional navigability.
