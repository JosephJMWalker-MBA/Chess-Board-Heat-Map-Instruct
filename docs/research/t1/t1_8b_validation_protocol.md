# T1.8b — Validation Protocol Hardening

## 1. Consequence Layer Invariant: `mate != CP`
To prevent the semantic blurring of consequence metrics, the execution environment MUST enforce that typed mate outcomes are never converted into numerical centipawn values (e.g., `10000`, `20000`, `-10000`). 
- **Requirement:** Median and CP regret calculations must ONLY operate over standard numerical centipawn evaluations. Mate outcomes must remain strongly typed as `MateIn(X)` or `MateScore`, maintaining their qualitative separation from centipawns. Any partition calculation that mixes the two is automatically invalidated.
- **Verification:** The typed consequence invariant is mechanically proven by the `test_mate_not_mixed_with_cp` regression test.

## 2. Validation-Runner Contract
All future executions of consequence-layer validation (such as the pending fresh Hostile Conversion-Evidence Validation Suite) must adhere to the following strict runner contract, completely separate from the experimental fixtures themselves.

Before any future run may be started, the runner MUST satisfy all of the following:

1. **Immutable Fixture Manifest:** The full fixture manifest is sealed and hashed.
2. **Code Freezing:** The runner records the frozen source code SHA to ensure T1.1–T1.7 code hasn't drifted.
3. **Engine Determinism:** The runner hard-codes the exact engine path, version, Threads, Hash, and an exact `Nodes` budget (e.g. 500k).
4. **No Runtime Mutation:** The runner forbids runtime script mutations, ad-hoc edits, or helper/fix scripts from being created/run after the execution seal is laid down.
5. **Fail-Fast Eligibility Preflight:** Before Stockfish ever launches, the runner MUST preflight the entire suite and immediately exit on failure if:
   - `board.is_valid()` fails for any pre-move state.
   - The nominated played move is illegal in the root position.
   - $e \in D_t$ evaluates to False (predecessor signature is missing).
   - $f \in B_t$ evaluates to False (successor signature is missing).
6. **Partition Exhaustiveness:** The script must mechanically assert the invariant $n_{11} + n_{10} + n_{01} + n_{00} = |M_{legal}|$ for every fixture.
7. **Typed CP/Mate Invariant:** A targeted runtime assertion enforcing the `mate != CP` rule during metric aggregation.
8. **Output Determinism:** Exactly one isolated output directory is created *before* execution starts, ensuring no paths are ambiguous during execution.
9. **Engine Lifecycle Cleanup:** The runner MUST own the Stockfish lifecycle through a strict `try/finally` block. Orphan engine processes cannot survive an exception, crash, or cancellation.
