# T1.11 Execution Report & Archive

This report documents the immutable execution of the frozen T1.11 experiment.

## Provenance

- **Execution Commit:** `c840337595580c2c013d58ccc578b3fd4bc12f0a`
- **Seal SHA-256:** `8d1e08267830a5608b8932a22c5484624844f01818baad6827e299a1232c7520`
- **Engine:** Stockfish 18 (`/opt/homebrew/bin/stockfish`)
- **Engine Configuration:** Threads=1, Hash=16 MB
- **Node Budget:** 500,000 nodes/legal root
- **Perspective Policy:** `root_side`
- **Execution UTC Start Time:** 2026-08-14T13:40:37Z
- **Execution UTC End Time:** 2026-08-14T13:41:41Z

## Frozen Classification Results

### Q1–Q15 Classifications

- **Q1:** SUPPORTED
- **Q2:** SUPPORTED
- **Q3:** SUPPORTED
- **Q4:** FALSIFIED
- **Q5:** SUPPORTED
- **Q6:** SUPPORTED
- **Q7:** SUPPORTED
- **Q8:** SUPPORTED
- **Q9:** SUPPORTED
- **Q10:** SUPPORTED
- **Q11:** SUPPORTED
- **Q12:** SUPPORTED
- **Q13:** SUPPORTED
- **Q14:** SUPPORTED
- **Q15:** SUPPORTED

### Selected Deep Dive Details

- **Q4:** M11=50, M10=48 → FALSIFIED
- **Q11:** Qh4# mate typed → SUPPORTED
- **Q14:** primary M11=32, twin M11=58 → SUPPORTED

## Reporting Clarification

`root_side` is the evaluation policy that determines the comparison perspective dynamically. The resolved comparison perspectives based on `board.turn` were:

- **Q4:** White
- **Q11:** Black
- **Q14 primary:** White
- **Q14 twin:** White

The emitted raw JSON output files have been archived byte-for-byte unmodified. Do not edit them to add the resolved perspective.

## Interpretive Limits

1. **Not a Success Percentage:** The result of 14/15 SUPPORTED is not a success percentage or model accuracy metric. These fixtures are not interchangeable trials; they each exercise distinct structural, temporal, confounding, and consequence boundaries.
2. **Association Remains Noncausal:** Observed engine evaluation regrets reflect state associations, not strictly causal attributions of the chosen root move alone.
3. **Falsification Magnitude:** Q4 remains falsified despite the 2 cp magnitude difference. We preregistered literal direction, not a practical-significance threshold after seeing the data. The prediction that the joint remove-and-birth class would exhibit lower median CP regret than the remove-without-birth class was proven false in this specific context.
4. **Fixture-Specific Consequence Difference:** Q14 demonstrates that local structurally matched partitions can yield divergent consequence (32 cp vs 58 cp regret), underscoring that shape does not equal amplitude, and structural equivalence does not imply consequence equivalence. This is a fixture-specific difference under structural matching, not a universal law.
5. **Mate Types:** Mate type is preserved strictly as a discrete outcome type; it is not converted to CP integers.

## New Post-Run Robustness Question

The execution relies on sequential evaluations per root move using a single engine instance and a shared 16 MB transposition table. As later analyses may encounter cached information from earlier evaluations (especially notable in Q14 where primary and twin roots are evaluated sequentially):

**Are CP regret relationships stable to root-evaluation ordering and transposition-table state?**

This is recorded as an explicitly identified future robustness question. It must be separately preregistered and tested, and is not grounds for altering or reinterpreting the sealed T1.11 classifications.
