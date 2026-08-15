# ChessHeat Semantic Contract V1 (S0)

This document establishes the normative semantic boundaries and vocabulary for ChessHeat. It defines what a position, subject, relation, branch, observation, intervention, consequence association, and projection are within the system, and crucially, restricts what claims they are permitted to make.

## 1. Sufficient Position Identity (`P`)

A sufficient legal chess state (`P`) requires more than just the arrangement of pieces on the board. 

To maintain semantic integrity, a position must distinguish:
- Board arrangement
- Side to move
- Castling rights
- En-passant state
- Rule-50 state
- Repetition / history availability
- Variant identity (where relevant)

**Constraint**: ChessHeat must *not* fabricate unavailable history. Measurements may declare weaker history requirements explicitly (e.g., admitting transposition matches), but the underlying representation must preserve the distinction.

## 2. Epistemic Evidence Types

Evidence in ChessHeat originates from distinct epistemic processes. We classify evidence into the following types:
- `RULE_EXACT`: Derived exclusively from the rules of chess (e.g., pseudo-legal mobility).
- `ENGINE_DERIVED`: Sourced from a deterministic evaluation function or engine search without human modification.
- `SEARCH_DERIVED`: Derived from tree search policies and pruning heuristics.
- `EMPIRICAL`: Derived from historical datasets or observed play.
- `HEURISTIC`: Derived from approximate or proxy functions (e.g., simple piece values).

## 3. Evidence-Level Ladder

Lower levels of evidence must not silently inherit the causal claims of higher levels. 
1. **Occurrence**: An event happened in a specific line.
2. **Recurrence**: An event happened across multiple lines.
3. **Branch Discrimination**: The event is preferentially associated with lines possessing certain properties.
4. **Consequence Association**: The presence of the event correlates with a change in typed root regret.
5. **Intervention Sensitivity**: Manipulating the board state alters the event and changes the regret (Causal mechanism).
6. **Causal / Subject Validation**: The intervention sensitivity holds across a statistically valid empirical sample.

## 4. Subject Identity

Subject kinds in ChessHeat must be extensible but explicitly typed. At minimum, these include:
- `SQUARE`: A distinct coordinate on the board.
- `PIECE`: A distinct piece instance.
- `MOVE`: A source-to-destination transition.
- `RELATION`: An edge or higher-order relationship between subjects.
- `PATH`: A sequence of squares or moves.
- `REGION`: A grouping of squares.
- `INTERACTION_COMPONENT`: A functional component of a relation (e.g., blocker).
- `GLOBAL_STATE`: Non-spatial properties (e.g., material imbalance).

## 5. Relation Semantic Container

Relations are not strictly pairwise edges. The semantic container must support:
- **Relation Type**: The functional nature of the relationship (e.g., "attacks", "blocks").
- **Participants**: The entities involved.
- **Participant Roles**: The function of each participant (e.g., "origin", "target", "mediator").
- **Geometry/Path** (Optional): The spatial trajectory.
- **Provenance**: The source of the relation.
- **Relation State**: Relations undergo conceptual transitions (`LATENT` -> `ENABLED` -> `REALIZED`). The system must not assume a binary "exists/does not exist" state without context.

## 6. Branch Identity Invariant

The ordering of evidence generation is strictly:
`root move -> branch-local future evidence -> typed root consequence/regret`

**Constraint**: Branch identity must not be inferred from candidate rank alone and must remain available until *after* consequence comparison. Branch collapse into recurrence frequency is a lossy projection.

## 7. Observation vs. Instrument Semantics

We distinguish between three types of conditioning:
- **Board-State Intervention**: Altering the physical piece arrangement or rules.
- **Candidate Conditioning**: Filtering or restricting the set of legal root moves considered.
- **Instrument/Search Conditioning**: Altering the evaluation parameters (e.g., depth, nodes, engine version).

**Observation Identity**: Any recorded observation must carry its producer (engine), configuration, search epoch/state, candidate scope, budget, line source, and provenance. 
**Experimental Invariant**: Independent observations intended for comparison must originate from equivalent instrument states to prevent instrument contamination.

## 8. Projection Boundary

**Constraint**: `canonical evidence != square projection != visualization`

A square heatmap is a downstream lossy projection of evidence; it is not the canonical evidence itself. Furthermore, visualization cannot create evidence or upgrade its epistemic status.

## 9. Objective / Human / Explanation Boundary

The following domains are strictly distinct and must not pollute one another:
- Objective consequence structure
- Decision leverage / amplitude
- Human navigability / policy
- Natural-language explanation

**Constraint**: Objective measurement code must never import or depend on human-navigation or explanation layers.
