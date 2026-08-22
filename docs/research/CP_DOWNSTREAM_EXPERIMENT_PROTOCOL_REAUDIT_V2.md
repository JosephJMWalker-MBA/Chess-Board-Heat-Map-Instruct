# CP Downstream Experiment Protocol Re-audit V2

**Audited Full SHA:** c0914d88530810d9e07bc4e951c8721aca1a611d
**Previous Audit SHA:** 8ac1317922f88872cbcdc84a2c21a336b849930b
**Authoritative Pre-Freeze SHA:** 8876f8cf2d6e1da47b2b40b818413b4095786c36
**Protocol ID:** CP_REPRESENTATION_EFFICIENCY_PROTOCOL_V2
**Claimed JSON Digest:** ecd9b1286aed3681de2f4042b339ce20112d0e602b4a9b6860f46d58fb45fb37
**Independently Recomputed JSON Digest:** ecd9b1286aed3681de2f4042b339ce20112d0e602b4a9b6860f46d58fb45fb37

## Changed Files in V2 Commit
- `artifacts/research/cp_representation_efficiency_protocol_v2.json`
- `docs/research/CP_DOWNSTREAM_EXPERIMENT_PROTOCOL_FREEZE_V2.md`
- `docs/research/CP_ONLY_REPRESENTATION_EFFICIENCY_PREREGISTRATION.md`
- `docs/research/NEXT_WORK_MAP.md`
- `docs/research/RESEARCH_CONTINUITY_CHECKPOINT_2026-08-16.md`
- `src/chessheat/protocol_freeze.py`
- `tests/test_protocol_freeze.py`

**SOURCE/TARGET/Model Boundary:** Verified. TARGET not run. Models not trained. SOURCE evidence untouched.

## Finding Matrix

### V1 Blocker Repair
- **M_D/M_T/B_daS**: Repaired (continuous amplitude restored).
- **Information Equalization**: Repaired (identical $S^\star, d_X, a_X$).
- **Seed Aggregation**: Repaired (budgeting independent of seed).
- **Zero-Pair Roots**: Partially repaired (excluded prospectively, but missing tests).
- **AULC Sign**: Repaired (larger U = better).
**Verdict:** PASS on restoring V1 material failures.

### JSON Seal Completeness
- Missing total 270 side-dimension definition ($d_X$ and $a_X$ absent).
- Missing P orientation, EP/Castling rules, omission of S0 learner fields.
- Missing budget ordering tie-break, B_perm algorithm, exact seed averaging order, Target attrition behavior.
- Missing exact learner specs (bias, init, Adam params, patience, best-checkpoint rule).
- Missing AULC fail-closed rules and bootstrap details.
**Verdict:** FAIL. Canonical JSON does not completely freeze the protocol.

### P Tensor Coordinate Parity
- Markdown claims: row 0 = rank 8.
- Code implementation: `get_square_index("a1") == 0`, meaning rank 1 goes to flat offset 0 (row 0 in 8x8 reshape).
**Verdict:** FAIL. Contradiction between specification and implementation.

### Float32 / Shape Reproducibility
- Claimed float32 `18x8x8` and `270` tensors.
- Code returns Python `List[float]`, bypassing memory layout, precise float32 boundaries, and tensor shape.
**Verdict:** FAIL. Numeric reproducibility not guaranteed by python arrays.

### Pair Orientation / $d_X$ Coherence
- Caller passing `(m2, m1, FIRST_BETTER)` silently canonicalizes moves but leaves label inverted.
**Verdict:** FAIL. Prospective label identity compromised.

### Target Attrition
- Markdown excludes "mate outcomes".
- Pre-freeze inherited `CompareTyped` explicitly handles/orders typed mate outcomes.
**Verdict:** FAIL. Contradicts inherited scientific semantics.

### Split & Preregistration Consistency
- Code uses conservative transposition-group split.
- Preregistration still says "We must split by canonical root identity only".
**Verdict:** FAIL. Conflicting documentation.

### Root Batching (Zero-Pair Target Roots)
- Unspecified whether a 0-pair nominal root consumes an active slot in the 64-root minibatch or merely acts as a budget phantom.
**Verdict:** FAIL. Effective training exposure ambiguous.

### Seed Aggregation
- Explicitly stated to average across seeds before roots.
**Verdict:** PASS mathematically, though omitted from JSON.

### AULC Fail-Closed
- Accepts and propagates `NaN`/`Inf`.
**Verdict:** FAIL. Not fail-closed.

### Bootstrap
- Support code only generates indices; does not compute bounds or re-compute AULC/contrasts.
**Verdict:** FAIL. Procedure not computationally frozen.

### Outcome Logic
- Missing `PROTOCOL_INVALID` boundary zero semantics.
**Verdict:** FAIL.

### Tests Adequacy
- 10 focused tests cover basic logic but miss all edge cases, NaN inputs, exact tensor alignments, full bootstrap, and complete classifier paths.
**Verdict:** FAIL.

### Governance / Continuity
- V2 commit wiped hundreds of lines of established scientific mapping from `NEXT_WORK_MAP.md` (558 lines -> 16 lines) and `RESEARCH_CONTINUITY_CHECKPOINT_2026-08-16.md` (795 lines -> 12 lines).
**Verdict:** FAIL. Massive destruction of preserved research continuity.

### PyTorch Runtime Status
- Uninstalled (`No module named 'torch'`).
- Status: `ML_RUNTIME_DEPENDENCY_NOT_YET_SATISFIED`.

## Overall Verdict
**DOWNSTREAM_PROTOCOL_V2_REAUDIT_FAIL**

**Resulting Status:** `DOWNSTREAM_EXPERIMENT_PROTOCOL_V2_REAUDIT_FAILED`
**Next Blocker:** `DOWNSTREAM_EXPERIMENT_PROTOCOL_REPAIR_REQUIRED_V3`
