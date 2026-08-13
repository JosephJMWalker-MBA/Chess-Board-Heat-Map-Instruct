# Milestone 8.6.5: W-v2 Experimental Consequence Reclassification

The discovery that the execution harness for `W-v2` omitted the frozen `candidate_policy={"top_n": 5}`, thereby defaulting to admitting all legal root moves into Recurrence evaluation, has substantial epistemic consequences for the `W-v2` dataset. This report classifies exactly which prior conclusions remain mathematically sound and which must be discarded regarding the frozen experiment state.

## 1. M8.6.4 Semantic Corrections
* **`apply_shape_selectivity_v1()` Mechanics**: The method is an ordered, first-success selector (`Direct` -> `Recurrence` -> `Bundle`). It allows later channels to evaluate after earlier failures, but it does not intrinsically return independent per-channel selection states. The detailed per-channel breakdowns generated in the M8.6.4 audit were a richer forensic reconstruction.
* **W3 Focal Square Correction**: For the back-rank mate (W3), `f8` *was* Recurrence-selected (earliest ply 2, distinct lines 18). However, `e8` and `g8` failed Recurrence entirely (due to low line counts or deep horizons) *before* Bundle evaluated them. Therefore, the failure of the entire back-rank region cannot be solely attributed to the Bundle logic.

## 2. Classification of W-v2 Conclusions

### UNAFFECTED
The omission of the Recurrence candidate policy strictly impacts the PV structure and line counts processed by `aggregate_square_recurrence`. Anything independent of PV candidate filtering is perfectly intact.
* **Direct-Channel Results**: `UNAFFECTED`. Direct evidence relies purely on root-move candidate fractions out of total legal moves. It does not use the PV-based candidate admission policy.
* **Bundle-Channel Results**: `UNAFFECTED`. Bundle structures rely on spatial deltas and geometric comparisons applied strictly at depth 1 (the immediate root moves).
* **CP Amplitude (`A_cp`)**: `UNAFFECTED`. Amplitude is derived from the root-move evaluation delta independent of candidate line subsets.
* **Mate Amplitude (`A_mate`)**: `UNAFFECTED`. Checked against the presence of mate scores across all generated legal moves.
* **Zero-Optionality Status**: `UNAFFECTED`. Measured solely by the count of legal root moves (`|M_legal| = 1`).
* **W7 Hypothesis Falsification**: `UNAFFECTED`. The raw root-move regret spread (`+24` to `-483`) remains structurally unchanged, confirming W7 is highly consequential regardless of PV filtering.
* **W9 Result**: `UNAFFECTED`. Zero-optionality functions correctly and independently of PV recurrence depth.
* **W10/W11 Fixture Invalidity**: `UNAFFECTED`. These were invalid FEN positions structurally rejected by the chess engine, completely separate from the candidate policy parameters.
* **Rare/Singleton Lever (W3) & Broad-Region (W4) Selectivity Mechanics**: `UNAFFECTED` in principle. The mechanics describing how Bundle fails due to `moves < 3` or `size > 15` operated as written and are fundamentally independent of Recurrence overflow.

### PARTIALLY AFFECTED
* **Multi-Region Failure Claims (W12)**: `PARTIALLY AFFECTED`. The failure of disjoint regions is a true limitation of the current spatial clustering implementation. However, the exact spatial profile of the noise interfering with those regions was heavily magnified by the unfiltered recurrence lines.
* **Total Selected Squares**: `PARTIALLY AFFECTED`. While Direct and Bundle accurately contributed their intended squares, the total aggregate count is heavily bloated by the recurrence overflow.
* **Precision / False-Positive Geography**: `PARTIALLY AFFECTED`. False-positive metrics are technically valid for the unthrottled environment that ran, but they massively underrepresent the precision capabilities of the intended frozen model.

### INVALID FOR THE FROZEN EXPERIMENT
Any metric mathematically dependent on `distinct_line_count` or the boundaries of the top-5 candidate set must be treated as invalid for characterizing the intended experimental model.
* **Recurrence Results**: `INVALID`. The recurrence filter ingested up to 34 distinct lines instead of 5, completely breaking the `distinct_line_count >= 3` threshold intention.
* **Claims about ShapeSelectivity-v1 Recurrence Diffuseness**: `INVALID`. The conclusion that "69% of selected geography came from Recurrence because standard moves saturate early plies" cannot be attributed to the model's design. The diffuseness was mechanically caused by admitting vastly more candidate lines than the filter was designed to suppress.
* **Per-Channel Contribution Counts**: `INVALID`. Recurrence's share (139 out of 201) was artificially inflated relative to Direct and Bundle.
* **Region Recall**: `INVALID`. Recall was artificially boosted because hundreds of unexpected PV variations were permitted to stumble across the focal squares. 

## 3. Specification: Corrected Development Experiment (W-v2-R)
A retrospective corrected development experiment (`W-v2-R`) will be executed using the intended `candidate_policy={"top_n": 5}`.

**Formal Experimental Status**:
1. **Not a Sealed Holdout**: This execution *cannot* restore W-v2's holdout or sealed validation status. It is development evidence only.
2. **Artifact Preservation**: The original `W-v2` dataset and `sealed_validation_w_suite_v2.json` manifest must be strictly preserved without modification.
3. **Identifier**: The execution and results will be strictly labeled `W-v2-R`.
4. **W10/W11 Status**: W10 and W11 must remain `INVALID`. They will not be repaired in-place.

**Execution Requirements**:
1. **Preflight**: Execute `Board.is_valid()` before any engine evaluation, failing structurally if the board is illegal.
2. **Provenance Traceability**: The final report must explicitly record the full Recurrence provenance:
   - Total legal roots analyzed
   - Admitted candidate count
   - List of admitted moves
   - Exact Candidate Policy object
   - Distinct-line counts, visit counts, and earliest plies.
3. **No Tuning**: The `ShapeSelectivity-v1` thresholds must remain exactly as frozen.

**Machine-Checkable Invariants**:
The engine pipeline will actively assert:
```python
assert distinct_line_count <= admitted_candidate_count
if admitted_candidate_count > 0:
    assert line_fraction == distinct_line_count / admitted_candidate_count
```
(No execution has been performed during this milestone.)
