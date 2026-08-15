# S1 Research Note: Reproducible Experiment Spine

This note documents the architecture of the S1 experiment spine. The purpose of this spine is to provide the minimum viable scaffolding needed to make future mechanism tests self-describing and reproducible, specifically preparing for T2 and T3 comparative evaluations.

## What the Spine Guarantees

1. **Deterministic Experiment Identity:** An `ExperimentSpec` deterministically hashes its complete configuration (semantic contract version, fixture identity, sufficient position, candidate policy, producer/instrument config, budget, and line source). Any change to these inputs produces a materially distinct experiment identity.
2. **Result Immutability:** An `ExperimentResult` is completely frozen upon creation. It cannot mutate its configuration or results. It links back to its origin specification via the deterministic `spec_digest`.
3. **Suite Distinction:** The spine explicitly distinguishes between `NATURAL_REPRESENTATIVE` suites (games, puzzles, standard positions) and `MECHANISM_STRESS` suites (adversarial configurations designed to break metrics or evaluate edge-case geometries).
4. **Serialization Safety:** Core semantic signatures and fixture identities survive round-trip JSON serialization flawlessly.

## What the Spine Explicitly Does NOT Guarantee

1. **Execution Orchestration:** The spine contains no job runner, generic plugin framework, or automated task queue. It is purely structural.
2. **Storage:** There is no database layer. Artifacts and manifests are expected to be written as plain JSON/text to the file system.
3. **Causal Validity:** Constructing a `ComparisonResult` connects two experiment outcomes for a given hypothesis, but it performs no statistical or causal validity testing on its own.
4. **T2/T3 Semantics:** The spine defines *how* an experiment's boundaries are preserved, but introduces no new regional geometry, block-ray semantics, consequence discrimination algorithms, or heat formulas. All S0/Issue #4 branch semantics remain untouched.
