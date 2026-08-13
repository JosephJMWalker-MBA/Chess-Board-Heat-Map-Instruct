# Milestone 8.6.4: Recurrence & Selectivity Semantic Integrity Audit

This report executes the semantic integrity audit without altering any thresholds, rules, or core logic.

## 1. Channel Independence Verification
I verified the mechanical independence of the three spatial selection channels (`Direct`, `Recurrence`, `Bundle`). The `apply_shape_selectivity_v1` logic processes each channel's condition sequentially. A failure in one channel explicitly *does not* abort or suppress evidence selected independently by another channel.

Here is the exact square-by-square state for expected squares in the requested fixtures:

### W2 (Two-Line Recurrence)
- **e6**
  - **Direct**: observed-rejected (val: 0.06, predicate: `<0.15`)
  - **Recurrence**: observed-selected (earliest: 1, lines: 8, predicate: `<=2 and >=3`)
  - **Bundle**: observed-rejected (moves: 1, size: 10, predicate: `moves < 3`)
- **d8**, **c7**
  - **Direct** / **Recurrence**: not observed
  - **Bundle**: observed-rejected (moves: 1, size: 10, predicate: `moves < 3`)

### W3 (Single Consequential Move)
- **e8**
  - **Direct**: observed-rejected (val: 0.05, predicate: `<0.15`)
  - **Recurrence**: observed-rejected (earliest: 1, lines: 1, predicate: `distinct_lines < 3`)
  - **Bundle**: observed-rejected (moves: 1, size: 13, predicate: `moves < 3`)
- **f8**
  - **Direct**: not observed
  - **Recurrence**: observed-selected (earliest: 2, lines: 18, predicate: `<=2 and >=3`)
  - **Bundle**: observed-rejected (moves: 1, size: 13, predicate: `moves < 3`)
- **g8**
  - **Direct**: not observed
  - **Recurrence**: observed-rejected (earliest: 6, lines: 5, predicate: `earliest_ply > 2`)
  - **Bundle**: observed-rejected (moves: 20, size: 36, predicate: `size > 15`)

### W4 (Legitimate Broad Bundle)
*(Showing focal squares c4, c8, b5 for brevity)*
- **c4**
  - **Direct**: observed-selected (val: 0.71, predicate: `>=0.15`)
  - **Recurrence**: observed-selected (earliest: 1, lines: 34, predicate: `<=2 and >=3`)
  - **Bundle**: observed-rejected (moves: 1, size: 4, predicate: `moves < 3`)
- **c8**
  - **Direct**: observed-rejected (val: 0.03, predicate: `<0.15`)
  - **Recurrence**: observed-selected (earliest: 1, lines: 34, predicate: `<=2 and >=3`)
  - **Bundle**: observed-rejected (moves: 1, size: 21, predicate: `moves < 3`)
- **b5**
  - **Direct**: observed-rejected (val: 0.03, predicate: `<0.15`)
  - **Recurrence**: observed-selected (earliest: 1, lines: 7, predicate: `<=2 and >=3`)
  - **Bundle**: observed-selected (moves: 31, size: 2, predicate: `moves>=3 and size<=15`)

### W12 (Disjoint Regions)
*(Showing e8, a8 for brevity)*
- **e8**
  - **Direct**: observed-rejected (val: 0.05, predicate: `<0.15`)
  - **Recurrence**: observed-rejected (earliest: 1, lines: 1, predicate: `distinct_lines < 3`)
  - **Bundle**: observed-rejected (moves: 1, size: 15, predicate: `moves < 3`)
- **a8**
  - **Direct**: not observed
  - **Recurrence**: observed-selected (earliest: 2, lines: 10, predicate: `<=2 and >=3`)
  - **Bundle**: observed-rejected (moves: 1, size: 15, predicate: `moves < 3`)

## 2. Recurrence Distinct-Line-Count Audit
You correctly spotted a numerical anomaly: W4 reported `Rec=(lines: 34)`.

I investigated the relationship between total moves, distinct lines, and admitted candidates:
- **Legal root moves analyzed**: Total moves legally available in the FEN. (e.g., 34 in W4)
- **Candidates admitted to Recurrence**: Determined by `record.candidate_policy.get("top_n")`.
- **Distinct candidate lines containing a square**: The number of admitted candidate variations passing through that square.
- **Total square visits**: Sum of all times the square was touched across all lines.

**Resolution:**
The `aggregate_square_recurrence` implementation mathematically bounds `distinct_line_count <= admitted_candidate_count`. That logic is perfectly sound. 
The anomaly occurred because `run_w_v2.py` (the unsealed execution driver) called the engine adapter without explicitly passing the `candidate_policy={"top_n": 5}` argument. As a result, it defaulted to `{}`, which meant `top_n=None`. `recurrence.py` correctly interpreted `None` as "admit all legal root moves." 

Therefore, candidate admission was entirely bypassed in the W-v2 run, admitting all 34 lines into Recurrence evaluation instead of the top 5. The reported values genuinely were the distinct lines, but the candidate policy failed to throttle the input.

## 3. Invariant Tests Added
I wrote `test_semantics_audit.py` to continuously assert these mechanics:
1. `test_channel_independence_no_suppression`: Asserts that an `observed-rejected` state in Bundle/Recurrence cannot override an `observed-selected` state in Direct, mathematically locking in channel independence.
2. `test_recurrence_distinct_line_count_invariant`: Injects a strict `top_n=2` policy and asserts that `admitted_candidate_count == 2` and `distinct_line_count <= admitted_candidate_count`, verifying the recurrence mathematics independently.

The tests passed successfully.
