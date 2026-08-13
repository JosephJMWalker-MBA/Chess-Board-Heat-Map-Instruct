# T1.8 — Preregistered Structural Conversion Challenge Suite

This report presents the results of executing the T1.8 preregistered 14-fixture challenge suite (C1–C14) against the frozen Temporal Ledger and Consequence architectures.

## Execution Parameters

- **Engine**: Stockfish 16.1
- **Node Budget**: 500,000 nodes per move
- **Implementation**: Frozen `TemporalLedger` and `Consequence` modules

## Results & Classification

The goal of this experiment is to categorize hypothesis support based on the strictly independent evidence families measured by the system.

### Classification Rules

1. **Supported**: The conversion hypothesis is supported if:
   - $n_{01} = 0$ (The successor strictly requires the predecessor's removal)
   - $n_{10} > n_{11}$ (Independent removal of predecessor is more common than joint conversion)
   - $M_{11}$ has a higher median regret than $M_{10}$ (The conversion is strategically worse when attempted independently)
2. **Falsified**: The conversion hypothesis is falsified if:
   - $n_{01} > 0$ (Independent birth observed)
   - The median regrets of $M_{11}$ and $M_{10}$ are equal (No measurable consequence)
3. **Ambiguous**: Conflicting or insufficient evidence.
4. **Invalid**: The fixture is invalid (e.g. empty comparison class, $n_{00} = 0$).

### Fixture Results

(Execution in progress. Data will be populated here once complete.)

## Integrity Validation

- Did the system maintain separation of the four evidence families?
- Were the results generated without a conversion score or classifier?
- Did the system correctly handle missing comparison classes (None vs 0)?
