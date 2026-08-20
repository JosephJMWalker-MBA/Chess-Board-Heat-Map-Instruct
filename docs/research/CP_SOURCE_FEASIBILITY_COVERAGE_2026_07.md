# CP Source Feasibility Coverage July 2026

## Authorization
`SOURCE_ONLY_FEASIBILITY_COVERAGE_ACQUISITION` explicitly authorized by user.

## Corpus
- **Filename**: `lichess_db_broadcast_2026-07.pgn.zst`
- **URL**: `https://database.lichess.org/broadcast/lichess_db_broadcast_2026-07.pgn.zst`
- **Published SHA**: `714d0eb99f99fca8d791142038b6c59b5ca6a51b3339bd3891a92f4bdffcbf0c`
- **Local SHA**: `714d0eb99f99fca8d791142038b6c59b5ca6a51b3339bd3891a92f4bdffcbf0c`
- **Game Count**: 40038

## Implementation SHA
`0b847dbe48fadd6a913ab64297d6b780812a0a07`

## Root manifest
- **Schema**: `CP_ROOT_POPULATION_JULY_2026_MANIFEST_V1`
- **Digest**: `940d6a92bff309fda826e1b20ccb388333acac3aaab883eda6a2aee092e5675b`
- **Counts / Exclusions**:
  - `MISSING_CANONICAL_GAME_ID`: 0
  - `VARIANT_EXCLUDED`: 571
  - `MALFORMED_INITIAL_STATE`: 0
  - `MALFORMED_REPLAY`: 0
  - `NO_RULE_ELIGIBLE_ROOT`: 0
  - `DUPLICATE_S0_ROOT`: 5693
  - `PRIOR_DEVELOPMENT_EXACT_OVERLAP`: 0
  - `PRIOR_DEVELOPMENT_TRANSPOSITION_OVERLAP`: 21
  - **Admitted Base Roots**: 33753

## Engine
- **Stockfish UCI name**: `Stockfish 18`
- **Binary SHA**: `ae4c93fa9676ca7750d0714342fd8a5b1d018000fc6e0f6cedf112067b5ef374`
- **SOURCE instrument ID**: `CP_SOURCE_SF18_50K_ISOLATED_V1`
- **Budget**: 50k nodes
- **EvalFile Defaults**: `nn-37f18f62d772.nnue` (default), `nn-0000000000a0.nnue` (small default)
- **Observed options digest**: `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` (empty/default)

## Source results artifact
- **Path**: `artifacts/research/cp_source_feasibility_2026_07/raw/cp_source_root_results.jsonl.zst`
- **SHA-256**: `1a9f5d342c159ea43bc322045c73bb5bd28ab0cf840f3214b62d8544e3f191b7`
- **Record Count**: 33753

## Coverage metrics
- Roots attempted: 33753
- Roots successful: 33753
- Roots failed: 0
- Total legal alternatives: 1181355
- Total successful child observations: 1181355
- CP alternatives: 1175000
- Mate alternatives: 6355
- CP alternative fraction: 0.99462
- Roots with >=2 CP alternatives: 33700
- Roots with <2 CP alternatives: 53
- Roots with zero CP/CP pairs: 53
- Total CP/CP source-evaluable unordered pairs: 19850000

Distributions:
- legal alternatives/root: min: 2, median: 35, p90: 50, p95: 60, max: 100
- CP alternatives/root: min: 0, median: 34, p90: 49, p95: 59, max: 100
- CP/CP pairs/root: min: 0, median: 561, p90: 1176, p95: 1711, max: 4950

## Failures
None. (0 failed)

## Interpretation
This stage confirms descriptive source feasibility only. We established a strong base of CP/CP unordered pairs (nearly 20M) demonstrating the structural viability for a targeted split.

## Explicit non-actions
- No target acquisition or processes.
- No model training or evaluation.
- No target labels generated.
- No representation comparison performed.

## Status Updates
- Resulting status: `SOURCE_ONLY_FEASIBILITY_COVERAGE_ACQUIRED`
- Next blocker: `SPLIT_AND_BUDGET_NOT_YET_FROZEN`
- Target remains UNAUTHORIZED.
- Model training remains UNAUTHORIZED.
