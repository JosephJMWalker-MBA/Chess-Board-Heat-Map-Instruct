# Track 1 (T1) — Consequence, Counterfactuals, and Reappearance

This directory contains research on the T1 hypotheses, focused on bounding the temporal scope of causal measurement.

## Status

**The T1.8 and T1.9 executions are retained as development and forensic evidence, not as valid preregistered experiments.**

*   **T1.8-D**: Compromised development evidence. The claimed T1.8 fixture preflight failed to ensure transition eligibility, as demonstrated by invalid C1/C2/C5. The execution was unsealed and scripts were mutated during runs.
*   **T1.8a**: Provenance and semantic audit of T1.8.
*   **T1.8b**: Hardened validation protocol.
*   **T1.9-P**: Provisionally sealed development evidence. The seal was anchored to a stale git tree, breaking provenance. Furthermore, the regret calculation was mathematically flawed (`wrong E* => all derived R(m) are semantically invalid`), producing invalid negative regrets.
*   **T1.9a**: Consequence semantic audit that disqualified T1.9.
*   **T1.10a**: Consequence Semantics Unification & Harness Qualification. Established the authoritative typed consequence primitive `compute_regrets` and rigorous engine-free preflight checks.

Any future validation must use a fresh fixture suite constructed and sealed under the hardened protocol established in T1.8b and enforced by the code in T1.10a.
