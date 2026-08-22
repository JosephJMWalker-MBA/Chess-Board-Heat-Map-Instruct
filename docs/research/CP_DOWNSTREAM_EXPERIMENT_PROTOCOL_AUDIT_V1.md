# CP Downstream Experiment Protocol Audit V1

- **Audited Commit**: ba11bde7af3623b3272900b7da66bc5ec53627de
- **Pre-Freeze Reference Commit**: 8876f8cf2d6e1da47b2b40b818413b4095786c36
- **Protocol Identifier**: CP_REPRESENTATION_EFFICIENCY_PROTOCOL_V1
- **Claimed Digest**: 0496ff3a5d9ef629a5e987774814d7f6f0a0de5c7a1aad52be50f5a34f1f8d1a (This is merely the SHA256 of the Markdown text file, not a canonical machine-readable JSON digest).

## 1. Audit Scope
This independent hostile audit evaluated whether the V1 downstream representation-efficiency protocol freeze (commit `ba11bde7`) successfully resolved the six required governance blockers without silently redefining the already-frozen scientific contract. 

## 2. Finding Matrix & Verdicts

| Domain | Verdict | Notes |
|--------|---------|-------|
| Frozen Contract Inheritance | **MATERIAL FAIL** | The freeze silently replaced the explicitly frozen continuous $M_D$ / $M_T$ amplitude operators with binary planes, dropping the explicitly required $a_X$ term entirely. |
| Information Equalization | **MATERIAL FAIL** | The pre-freeze explicitly required the same $S^\star$, $d_X$, and $a_X$ to be provided to every spatial condition. The V1 freeze entirely omitted these features, violating the equalization guarantee. |
| $B_{daS}$ / Matched Comparator | **MATERIAL FAIL** | The freeze conflated the mandatory non-spatial zero-channel baseline ($M_0$) with the separate matched comparator, incorrectly replacing $B_{daS}$ with a permuted spatial grid. |
| Pair Canonicalization | **PASS** | The preregistration (Section 3) already explicitly froze $m_1 / m_2$ order as the lexicographic sorting of their canonical UCI strings. The protocol inherits this. |
| Split / Budget Exactness | **PASS** | `TRAIN` subset size is exactly 23,689 roots (out of 33,859). The 20,000 max budget is mathematically feasible. |
| Zero-Pair-Root Semantics | **MATERIAL FAIL** | `compute_root_weighted_loss()` silently drops roots with 0 eligible pairs. This silently changes the effective sample budget and evaluation denominator without specifying whether the 20k budget is drawn from all roots or only evaluable roots. |
| $P$ Numeric Encoding | **FAIL** | Failed to specify piece order, side-to-move polarity, castling order, or tensor dtype. Two independent implementers could not produce identical bytes. |
| Learner Completeness | **PARTIAL** | Core architecture specified, but ML framework, initialization, optimizer epsilon, `min_delta` for early stopping, and checkpoint selection (best vs. last) remain critically ambiguous. |
| Seed Aggregation | **MATERIAL FAIL** | The freeze tied the budget root selection to the learner seed, creating 5 varying subsets, but failed to define the aggregation rule across those seeds (e.g., whether AULC is averaged, or predictions pooled), leaving the estimand unresolved. |
| AULC Implementation | **MATERIAL FAIL** | `compute_aulc()` returns `0.0` for mismatched/empty inputs. Since the freeze redefined lower AULC as better, an error silently yields a "perfect" efficiency score. |
| AULC Sign / Outcome Logic | **MATERIAL FAIL** | The freeze reversed the AULC sign (lower loss = better), but retained the previous contrast formula ($\Delta_{DT} = AULC_D - AULC_T$). Thus, if $D$ is better, $\Delta_{DT}$ is negative. However, the legacy outcome rules trigger `SUPPORT_muD` only when $\Delta_{DT} > 0$. The logic is completely backwards. |
| Bootstrap / Confidence | **PARTIAL** | Specifies 10k paired root bootstraps, but fails to clarify whether seed variance is nested inside the bootstrap, and fails to specify multiplicity corrections for the three contrasts. |
| Test Adequacy | **FAIL** | The four tests cover simple determinism but miss critical proofs regarding seed aggregation, exact tensor replication, outcome logic correctness, and zero-pair handling. |
| Governance Consistency | **FAIL** | Simple string replacement left contradictory historical statuses and broken tables (e.g. "SPLIT_AND_BUDGET_FROZEN_V1 remains unresolved"). |

## 3. Exact Material Blockers
The following failures critically block scientific validity:
1. Reversal of the AULC sign convention without updating the decision logic, causing winning representations to be classified as losers.
2. Silent violation of the frozen information-equalization interface (omitting $S^\star, a_X, d_X$).
3. Redefining the frozen continuous spatial operators ($M_D, M_T$) into binary planes.
4. Conflating the explicit zero-channel $B_{daS}$ baseline with the separate spatially permuted matched comparator.
5. Missing seed aggregation rule across different train-root subsets.
6. Ambiguous treatment of zero-pair roots affecting the sample budget and evaluation denominator.

## 4. Final Verdict
**OVERALL VERDICT**: `DOWNSTREAM_PROTOCOL_AUDIT_FAIL`
**RESULTING STATUS**: `DOWNSTREAM_EXPERIMENT_PROTOCOL_AUDIT_FAILED`
**NEXT BLOCKER**: `DOWNSTREAM_EXPERIMENT_PROTOCOL_REPAIR_REQUIRED_V2`

TARGET acquisition remains strictly UNAUTHORIZED. No models may be trained.
