# T3a-1 Branch-Conditioned Consequence Association: Preregistration

This document formally preregisters the T3a-1 experiment before any Stockfish engine evaluations are conducted.

## 1. Hypothesis
Tracking a single spatial event exclusively within the future continuation of a branch preserves information about the root consequence of that branch. Conversely, aggregating the exact same evidence into an unconditioned position-level distribution destroys this associative mapping.

## 2. Frozen Fixture Mechanism
We manually constructed a standard chess tactical mechanism where White has a hanging Knight that can be captured by Black pawns if White does not address the threat.

- **FEN**: `4k3/8/8/3p1p2/4N3/8/8/4K3 w - - 0 1`
- **Candidate Policy**: `{}` (Evaluate the complete set of python-chess legal root moves, which include King moves and Knight moves).

## 3. Preregistered Spatial Event
- **Square**: `e4`
- **Role**: `capture`
- **Continuation Horizon (H)**: Plies 2, 3, 4, 5. (Ply 1 is strictly excluded to prevent trivial root-move leakage).

## 4. Expected Consequence Association
- **Expected Regret Direction**: **BAD** (Higher Regret).
- **Rationale**: If White plays a root move that leaves the Knight on `e4` (e.g., a King move), Black will capture it in the immediate continuation, leading to high regret. If White plays a root move that moves the Knight (e.g., `e4d6`), the continuation will not feature a capture on `e4`, leading to low regret. 
- Therefore, the presence of `(e4, capture)` in Plies 2-5 ($X = 1$) is hypothesized to strictly associate with higher (worse) CP regret than its absence ($X = 0$).

## 5. Frozen Engine Configuration
- **Engine**: Stockfish 18 (via `chessheat.engine.StockfishAdapter`)
- **Nodes Budget**: `100000`
- **Threads**: `1`
- **Hash**: `16` MB

## 6. Classification Rules
Let $X_i \in \{0, 1\}$ be the presence of the event in the continuation horizon for root $i$.
Let $R_i$ be the CP regret for root $i$.
- $D = \text{median}(R \mid X=1) - \text{median}(R \mid X=0)$
- $M = \text{min}(R \mid X=1) - \text{max}(R \mid X=0)$

**Classification**:
- **SUPPORTED**: $D > 0$ and $M > 0$.
- **WEAK_SUPPORT**: $D > 0$ and $M \le 0$.
- **FALSIFIED**: $D \le 0$.
- **INCONCLUSIVE**: The partition sizes are less than 2, the regret outcomes contain mate scores, the continuation lines fall short of $H=5$, or the fixture is mechanically invalid.

## 7. Execution Constraint
This document must be committed to the repository history *before* Stockfish is invoked on this fixture. The generated ExperimentResult artifact must cite the Git SHA of this preregistration commit.
