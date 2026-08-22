# CP Downstream Experiment Protocol Freeze V3
**Protocol Identifier:** CP_REPRESENTATION_EFFICIENCY_PROTOCOL_V3
**Target Execution:** STRICTLY UNAUTHORIZED

## 1. Provenance and Failures
- The **V1 protocol** (commit `ba11bde`) accidentally altered frozen scientific math, reducing continuous amplitude maps to binary planes, violating information equalization.
- The **V2 protocol** (commit `c0914d8`) correctly restored the scientific contracts but failed its independent re-audit due to missing canonical machine-readable protocol completeness, contradicting tensor coordinates, irreproducible tensor storage, failing to handle all fail-closed states (like NaNs in AULC or invalid moves), and improperly overwriting historical continuity logs.
- The **V3 protocol** completes the machine-readable payload, locks down the tensor representations, rigorously implements bounding algorithms, and restores historical documentation, while preserving the mathematical scientific integrity of the experimental design.

## 2. Inherited Science & Orientation
- Canonical ordered pairs $m_1 < m_2$ (by lexicographical UCI).
- $D$ is the deduplicated destination squares of $m_1$ and $m_2$.
- $T$ is the deduplicated FROM/TO squares of $m_1$ and $m_2$.
- $a_X = |CP_X(m_1) - CP_X(m_2)|$.
- $d_X =$ 3-way Compare(CP).
- $M_D = a_X / |D|$ on $s \in D$ else 0.
- $M_T = a_X / |T|$ on $s \in T$ else 0.
- $B_{daS} = M_0 = 0$.
- $B_{perm}$ permutes $M_T$.
- Positive $\Delta_{DT} = AULC_D - AULC_T$ favors $D$.

## 3. Split Grouping
- Split partition assigned by the conservative transposition-equivalence tuple (JSON serialized).
- Exact All-Root Counts (33,859): TRAIN 23,639; VALIDATION 5,148; TEST 5,072.
- Exact SOURCE-Eligible Counts (33,444): TRAIN 23,350; VALIDATION 5,094; TEST 5,000.
- 20k feasibility: YES (23,350 > 20,000).
- 415 SOURCE-zero-pair roots are prospectively excluded from pair learning pools.

## 4. Target Labels & Attrition
- TARGET evaluations use inherited `CompareTyped`. Mate evaluations remain ordered if `CompareTyped` permits.
- **Target Attrition:** Nominal training budgets are assigned prospectively on SOURCE-eligible roots. If TARGET yields 0 evaluable pairs for a root, the root consumes **no slot** in a minibatch, generates 0 loss terms, and is simply not utilized. The nominal x-axis position remains anchored.
- Validation/Test root pools must share an exactly identical TARGET-evaluable root set across all representations.

## 5. Canonical Numeric Tensor
- Custom `CanonicalTensorF32` stores data precisely in IEEE-754 float32 (`float32-le`) without PyTorch dependency.
- **$P$ Orientation:** Spatial mapping where `row 0 = rank 8, col 0 = file a` (i.e. `a8 -> (0,0) -> 0`). $P$ is (18, 8, 8).
- **$S_{side}$ Orientation:** 270 categorical scalar features. It uses UCI categorical mapping where `a1=0, h8=63`.
- **$M$ Orientation:** Spatial mapping, matching $P$.

## 6. Learner, Seeds & Batching
- **Architecture:** Conv3(19->64)->Conv3(64->64)->Conv3(64->64)->GAP(64) concat Dense(270->128) -> Dense(192->128)->Dense(128->3)
- **Seeds:** `[1729, 2718, 31415, 65537, 104729]`.
- **Aggregation:** Average all 5 seeds on the root *before* computing the root inference / U(n) utility.
- **Minibatches:** 64 effective roots, sorted deterministically by epoch/seed.

## 7. AULC & Bootstrapping
- `compute_aulc` fails closed if utility is NaN/inf, if length mismatches, or if budgets are non-monotonic.
- Bootstrap utilizes 10,000 strictly deterministic replicates mapping `CHESSHEAT_BOOTSTRAP_V3|b|j`, outputting percentile bounds. 
- Outcome logic explicitly gates on `protocol_valid`.

## 8. Runtime Dependency Status
**ML_RUNTIME_DEPENDENCY_NOT_YET_SATISFIED** (PyTorch is uninstalled and not pinned in this commit). TARGET evaluation remains strictly unauthorized.
