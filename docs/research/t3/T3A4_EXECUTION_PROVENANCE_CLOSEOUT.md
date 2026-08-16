# T3a-4 Execution Provenance Closeout

## Overview
This document records the provenance limitations discovered during the execution of the T3a-4 experiment. While the numerical results were fully preregistered and calculable, the execution artifacts do not mechanically prove the required producer identity and search-state continuity.

## Producer Identity Limitation
The execution code called the real engine through `StockfishAdapter`, whose `AnalysisRecord` contains `adapter.get_name()`. However, the T3a-4 raw writer discarded `record.engine_name` and instead persisted the literal:

```
Stockfish 18
```

Therefore, exact producer identity was asserted by the execution layer rather than mechanically persisted from the UCI engine. We will not attempt to establish historical engine identity by starting a new Stockfish process now.

## Execution Continuity Limitation
The acquisition script was invoked multiple times during execution/development and is resumable through `if not os.path.exists(raw_path)`. Each invocation constructs a fresh `StockfishAdapter`. 

Therefore, the committed artifacts do not establish that all 12 raw fixtures were acquired in one uninterrupted engine process with one continuous engine/search-state history. 

We do not claim that any fixture was deliberately rerun or replaced unless there is evidence for that. The correct status is **continuity unverified**.

## Final Classification
Because the protocol treats producer/instrument provenance as part of observation identity and does not claim evaluation-order/engine-state robustness, we freeze:

- **protocol_validity** = false
- **final_scientific_classification** = INCONCLUSIVE
- **final_failure_reason** = ACQUISITION_PROVENANCE_NOT_CLOSED

While separately preserving the preregistered mathematical calculation over the raw observations:

- **conditional_numeric_classification** = FALSIFIED
- **informative_fixture_count** = 7
- **D_suite** = -88.0
- **M_suite** = -411.0

This closeout **does not reinterpret or soften the observed adverse direction**. Six of seven valid $P_f$ values were negative. The conditional result remains evidence against the preregistered producer-realized BAD/HIGHER_REGRET hypothesis, but cannot be promoted as a fully provenance-closed replication.

## Note on Fixtures 08 and 11
For fixtures 08 and 11, the historical aggregate (`t3a4_corpus_result.json`) records `|E=1|=0`, `|E=0|=0`. This is an encoding artifact of Pass B not executing under `MIXED_MATE_CP`. Their E partition should be interpreted as unassigned/unavailable, not as an observed all-zero realization. The frozen historical result files are strictly preserved and remain unmodified.
