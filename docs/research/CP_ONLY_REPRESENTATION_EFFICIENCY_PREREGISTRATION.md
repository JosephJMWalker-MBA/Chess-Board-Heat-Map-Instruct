# CP-Only Representation Efficiency Preregistration

## 1. Scientific Question

**Primary Question:**
Under one frozen learner/training regime and equalized underlying move information, does destination-only spatial organization $\mu_D$ or transition-touch organization $\mu_T$ yield greater sample efficiency for predicting held-out target-instrument ordering of CP/CP-source legal-alternative pairs?

This is the strictly singular, only primary utility question. We do not add capacity efficiency or robustness as co-primary outcomes.

## 2. Claim Ceiling

**Maximum Positive Claim:**
Under the frozen source instrument, target instrument, data population, information boundary, learner class, training procedure, and root-budget schedule, one spatial encoding permits more sample-efficient prediction of held-out target ordering than the specified comparator.

Any result from this experiment is conditional on the prospectively frozen July 2026 Lichess official-broadcast root population and the frozen source/target instruments. It does not establish universal representation efficiency across all legal chess positions or all distributions of human play.

**Explicit Non-Claims:**
- no objective square ownership
- no objective consequence $V$
- no universal Heat amplitude
- no additional information beyond $X$
- no universal superiority of one representation
- no causal square importance
- no instrument independence
- no human navigability claim

## 3. Prediction Unit and Canonical Serialization

**Frozen Unit:**
$$u = (P, \{m, n\})$$
for distinct legal root alternatives.

**Canonical Serialization:**
$$c(\{m, n\}) = (m_1, m_2)$$
where $UCI(m_1) < UCI(m_2)$ under ordinary bytewise/lexicographic ordering of canonical UCI strings.
Serialization exists only for identity/orientation. It is **not** a scientific reference move.

## 4. Exact Root-Population Contract

**Status:** ROOT_POPULATION_FROZEN_TO_LICHESS_JULY_2026

**Root Source Universe:**
Lichess official broadcast games, calendar month July 2026, PGN monthly export. This is a completed external corpus and must be treated only as the population source, not as engine evidence or target truth. Do not use the Lichess evaluation or puzzle database.

**Root-Construction Contract:**
1. **Standard Chess Only**: Admit only games reconstructable as standard chess under frozen S0 semantics. Exclude variants entirely. Do not silently reinterpret variants as standard chess.
2. **Complete Replay / History**: A candidate game must replay legally from its declared initial state through the candidate root. The resulting root must fully populate `SufficientPosition` semantics (`board_arrangement_fen`, `side_to_move`, `castling_rights`, `en_passant_square`, `halfmove_clock`, `fullmove_number`, `history_available`, `history_identity`, `variant`). Malformed or non-replayable games are excluded prospectively with recorded reason.
3. **One Root Per Source Game**: Use at most one base root from any source game to prevent pseudo-independent roots. The root-selection procedure must be deterministic and independent of engine evaluation, target $Y$, played-move quality, opening identity, tactical motifs, player rating, game result, human annotation, ChessHeat output, or future CP eligibility.
4. **Rule-Only Candidate Plies**: Before source-engine acquisition, eligible candidate roots must be valid standard-chess states, non-terminal, have $\ge 2$ legal root moves, and have sufficient reconstructable history under S0. Do not require CP/CP eligibility at this stage.
5. **Deterministic Within-Game Selection**: Choose exactly one eligible root from each admissible game by hashing the canonical source-game identity to select an index into the ordered rule-eligible ply set.
   Let $E = (e_0, e_1, \dots, e_{N-1})$ be the ascending list of rule-eligible ply indices for the game.
   Let `GameURL` be the canonical source-game identifier for this corpus. If missing during acquisition, exclude the record prospectively as `MISSING_CANONICAL_GAME_ID`.
   Let $h = \text{SHA256}("ChessHeat-root-v1|" \parallel \text{GameURL})$.
   Let $j = \text{integer}(h) \pmod N$.
   Select root $e_j$.
   This is a deterministic sampling mechanism. The hash does not score or rank chess positions, nor does it claim the selected root is representative of some intrinsic chess property. If a game contains zero rule-eligible roots ($N=0$), exclude it with reason.
6. **Duplicates**: Canonical root identity is the full `SufficientPosition` identity. Exact duplicate semantic roots must not appear twice in the final population. Freeze deterministic duplicate resolution, retaining provenance for every discarded duplicate source. Do not treat two roots with different S0 history identities as identical.
7. **Transposition / Leakage Group**: For later split construction, use a conservative transposition-equivalence grouping key: `board_arrangement_fen` + `side_to_move` + `castling_rights` + `en_passant_square`. Its purpose is leakage prevention, not redefining canonical S0 identity.
8. **Prior Development Overlap**: Previously inspected ChessHeat development, fixture, hostile-validation, and research positions (e.g., M8 / W-suite / T1 / T2 / T3) must be excluded. Exclude exact `SufficientPosition` overlaps and conservative transposition overlaps.
9. **No Target-Based Replacement**: Once admitted to the base population, do not replace a root due to target attrition (e.g. mate-typed source, target acquisition failure). Population construction must remain independent of target $Y$.
10. **Manifest / Provenance Contract**: Reusing `SuiteManifest` / `ExperimentSpec v2` semantics, preserve: external corpus identity, corpus month/version, upstream artifact filename, upstream published checksum, locally verified checksum, parser/version identity, root-selection algorithm/version, game identity/provenance, selected ply, full `SufficientPosition` identity, conservative transposition-group identity, inclusion/exclusion outcome, exclusion reason, duplicate resolution, prior-development-overlap status, software revision, and manifest digest.
11. **Sample Size**: `SPLIT_AND_BUDGET_NOT_YET_FROZEN` remains unresolved. The population universe and deterministic root-generation procedure are frozen now, while the exact training/tune/test counts remain unfrozen.

## 5. Source and Target Acquisition Instrument Contract

**Status:** INSTRUMENT_CONFIG_FROZEN_SF18_50K_250K_V1
**Implementation Status:** ENGINE_STATE_ISOLATION_AUDITED

**Producer Identity:**
Both source and target must use the exact Stockfish 18 binary.
- Observed UCI name: `Stockfish 18`
- Engine binary SHA-256: `ae4c93fa9676ca7750d0714342fd8a5b1d018000fc6e0f6cedf112067b5ef374`
Future execution must verify BOTH before any search. If the exact binary is unavailable or the SHA differs, acquisition is blocked.

**Source and Target Budgets:**
- Source: `CP_SOURCE_SF18_50K_ISOLATED_V1` (budget_type = nodes, budget_value = 50000)
- Target: `CP_TARGET_SF18_250K_ISOLATED_V1` (budget_type = nodes, budget_value = 250000)
The target uses exactly 5x the source node allowance. 250k nodes is the prospectively frozen deeper target instrument, not "ground truth" or "objective consequence."

**Static UCI Configuration:**
Identical for source and target except for node budget:
`Threads = 1`, `Hash = 16`, `Ponder = false`, `MultiPV = 1`, `Skill Level = 20`, `UCI_LimitStrength = false`, `UCI_Chess960 = false`, `UCI_ShowWDL = false`, `SyzygyProbeLimit = 0`, `SyzygyPath = <empty>`
No external tablebases permitted. Do not override `EvalFile` or `EvalFileSmall` from the binary's defaults. Record their observed default values during preflight. Record the complete observed UCI option surface in provenance. If the engine reports a required option/configuration incompatible with this frozen contract, acquisition is blocked.

**Comparison Perspective:**
For each root $P$, `comparison_perspective = side_to_move(P)`. This perspective is frozen before any root move is pushed. Every child observation must be converted back to the ROOT player's perspective (larger CP = better for the player making the root decision). Preserve mate outcomes as typed mate outcomes. Never convert mate to fake centipawns.

**Acquisition Unit:**
For each admitted root $P$:
1. Enumerate ALL legal root moves.
2. Sort legal alternatives by canonical UCI bytewise/lexicographic order.
3. For each legal move $m$: copy/reconstruct $P$; push exactly $m$; analyze the resulting child position $P_m$; retain the typed result from the root-player comparison perspective.
The acquisition object is $O_X(P, m)$ for each legal root alternative $m$. Do not use top-k filtering, best-move-only acquisition, MultiPV as a substitute for all-legal-move child evaluation, played-game move preference, search-based candidate admission, or target-based replacement. Do not perform a separate root baseline search.

**Engine-State Isolation Semantics:**
Source and Target use SEPARATE long-lived Stockfish processes. They must never share one process. For every individual child observation $O_X(P, m)$:
1. Establish a fresh UCI new-game boundary before the child search.
2. This boundary must cause Stockfish 18 search state to be cleared before that observation.
3. Set/send the exact child position.
4. Perform exactly one node-limited analysis.
5. Wait for completion before any next observation.
For python-chess, each child observation must receive a newly distinct `game` token so python-chess emits `ucinewgame`. Stockfish 18 handles `ucinewgame` as `search_clear()`, clearing transposition table state and thread search/history state. This resets the state without relying on legal-move ordering to control contamination.

**Source/Target Independence:**
The source and target processes must be separate OS engine processes using the identical verified Stockfish binary, identical static UCI options, and independent engine state. Target acquisition must not initialize from source TT state, consume source PVs, use source scores as search hints, skip moves based on source ranking, alter budget based on source uncertainty, replace source-non-CP cases, or inspect model predictions.

**Target Acquisition Remains Unauthorized:**
Target acquisition remains blocked until the downstream preregistration dependencies are frozen and explicitly authorized. The next stages are implementation and mechanical testing of the isolated acquisition path without touching the frozen July corpus, followed by an independent protocol-vs-implementation audit, and only then source-only feasibility acquisition.

## 6. Source and Target Evaluability
 
 **Source Pair Eligibility:**
 A pair is source-evaluable only when: both alternatives are legal, have distinct UCI identities, both source observations are valid, both source observations are CP-typed, common frozen perspective is maintained, and provenance is valid. Mate/WDL/non-valid source cases are prospectively non-evaluable and must not be replaced. Mate-typed source alternatives are retained in acquisition/coverage accounting but do not enter CP/CP pair construction.
 
 **Population Maintenance Under Attrition:**
 Do not remove the root from the declared base population merely because some source moves are mate-typed, fewer than two CP moves remain, acquisition fails, the position is expensive, or the source ordering is inconvenient. Report attrition. Do not replace it.
 
 **Target Labels:**
 - `FIRST_BETTER`: $O_Y(m_1) > O_Y(m_2)$ under frozen CompareTyped semantics
 - `EQUAL`: Perfect tie
 - `SECOND_BETTER`: $O_Y(m_1) < O_Y(m_2)$ under frozen CompareTyped semantics
 
 **Non-Evaluable Target Cases (retained in coverage accounting, no replacement):**
 - `UNORDERED`: Target-non-evaluable mixed type (if applicable)
 - `TARGET_ACQUISITION_FAILURE`: Evaluation could not be produced
 
 If target attrition leaves a root with zero evaluable pairs, that root is excluded from the pair-level analysis. Do not backfill another root.

## 7. Spatial Encodings

**Frozen Operations:**
$$D = \{to(m_1), to(m_2)\}$$ (deduplicated)
$$T = \{from(m_1), to(m_1), from(m_2), to(m_2)\}$$ (deduplicated)
$$a_X = |CP_X(m_1) - CP_X(m_2)|$$
$$d_X = \text{Compare}(CP_X(m_1), CP_X(m_2))$$

$$M_D(s) = \begin{cases} a_X / |D| & s \in D \\ 0 & \text{otherwise} \end{cases}$$

$$M_T(s) = \begin{cases} a_X / |T| & s \in T \\ 0 & \text{otherwise} \end{cases}$$
No tuning or normalization beyond these frozen operators.

## 8. Information-Equalized Interface and Controls

**Frozen Side Information:**
$$S^\star = (UCI(m_1), UCI(m_2))$$

Every spatial model receives the identical interface:
$$R(P, S^\star, d_X, a_X, M_\mu) \to Y$$
We explicitly supply $a_X$ to the spatial models so the representation is not rewarded merely for making amplitude easier to recover.

**Mandatory Non-Spatial Baseline ($B_{daS}$):**
$$B_{daS} = R(P, S^\star, d_X, a_X, M_0)$$
where $M_0$ is the exact null/zero spatial channel required to preserve the same learner input schema and parameterization.

**Raw Source Reference ($B_{raw}$):**
Includes $P, m_1/m_2 \text{ identities}, CP_X(m_1), CP_X(m_2), d_X, a_X, \rho$ under the same learner/resource procedure where schema permits. *Raw source is an information-rich diagnostic reference, not a guaranteed empirical-performance upper bound.*

**Matched Comparator:**
Currently: **MATCHED_COMPARATOR_NOT_YET_FROZEN**
We require exactly one simple same-pair rule-derived non-spatial representation that answers a distinct control question, receiving the exact same $P, S^\star, d_X, a_X$ and using the same learner/resource budget.

## 9. Representation of P

The semantic identity of $P$ is already frozen by `SufficientPosition` semantics: `board_arrangement_fen`, `side_to_move`, `castling_rights`, `en_passant_square`, `halfmove_clock`, `fullmove_number`, `history_available`, `history_identity`, `variant`. We do not silently drop history/rule-state fields.

Status:
- **P_SEMANTIC_IDENTITY_FROZEN_TO_S0**
- **P_NUMERIC_ENCODING_NOT_YET_FROZEN**

## 10. Learner Family

Currently: **LEARNER_FAMILY_NOT_YET_FROZEN**
We must choose one deliberately modest learner family using identical architecture, parameterization, optimizer, regularization, initialization, batch construction, and stopping rule for $\mu_D, \mu_T, B_{daS}$, and the matched control (masking/zeroing input slots explicitly). No representation-specific tuning.

## 11. Pair Subsampling

We use **all** source-eligible pairs within selected training/evaluation roots. Every selected root contributes all prospectively source-eligible unordered CP/CP pairs. Root weighting handles mobility imbalance; post-hoc pair subsampling is explicitly rejected unless computational necessity is proven before target acquisition.

## 12. Split Construction and Learning Budgets

Currently: **SPLIT_AND_BUDGET_NOT_YET_FROZEN**
We must split by canonical root identity only using a deterministic, target-blind procedure. All pairs from one root remain in one partition. Training-root sample-efficiency subsets must be nested and shared across every representation/baseline. We must freeze a deterministic budget schedule as a function of final training-root count, tuning-root partition, and held-out test-root partition.

## 13. Prediction Loss and Root Aggregation

The learner predicts probabilities over `FIRST_BETTER`, `EQUAL`, `SECOND_BETTER`.
The loss is multiclass negative log likelihood.

For a held-out root $P_i$ with target-evaluable pair set $Q_i$:
$$L_{i,\mu}(n) = \frac{1}{|Q_i|} \sum_{u \in Q_i} - \log p_\mu(Y_u | u, n)$$
where $n$ is the number of unique training roots.

The root-weighted statistic across $N_{test}$ roots is:
$$U_\mu(n) = - \frac{1}{N_{test}} \sum_{i} L_{i,\mu}(n)$$
Thus: larger $U$ = better, every root has equal weight, and pairs are averaged within root.

## 14. Primary Sample-Efficiency Statistic

The primary statistic is the normalized trapezoidal area under the held-out root-weighted learning curve (AULC) across the frozen nested root-budget schedule.
The x-axis is linear $n$ (unique training roots).

The primary operator contrast is:
$$\Delta_{DT} = AULC_D - AULC_T$$

Also computed:
$$\Delta_{D0} = AULC_D - AULC_{B_{daS}}$$
$$\Delta_{T0} = AULC_T - AULC_{B_{daS}}$$

## 15. Randomness and Hyperparameter Policy

Currently: **SEED_SET_NOT_YET_FROZEN**
If stochastic, we must preregister fixed seed sets applied symmetrically across representations. No dropping bad seeds. Training seeds $\neq$ root-split identity. Hyperparameters must be identical across all representations (either fixed or a shared, preregistered tuning budget disjoint from test roots).

## 16. Inference and Outcome Classification

We use a prospectively frozen paired root bootstrap over held-out roots (treating roots, not seeds or pairs, as the sampling unit) to determine reliability.
Currently: **CONFIDENCE_LEVEL_NOT_YET_FROZEN**

Under the frozen uncertainty criterion, define LCB and UCB as the lower and upper confidence bounds.
With zero superiority margin:
- resolved positive: $LCB > 0$
- resolved non-positive: $UCB \le 0$
- unresolved: interval contains $0$

**Deterministic Outcome Logic:**
- `SUPPORT_muD`: $LCB(\Delta_{DT}) > 0$ AND $LCB(\Delta_{D0}) > 0$
- `SUPPORT_muT`: $UCB(\Delta_{DT}) < 0$ AND $LCB(\Delta_{T0}) > 0$
- `SPATIAL_EFFICIENCY_OPERATOR_UNRESOLVED`: at least one spatial condition earns a resolved improvement over $B_{daS}$ ($LCB(\Delta_{D0}) > 0$ OR $LCB(\Delta_{T0}) > 0$), but the $\mu_D$ vs $\mu_T$ contrast is unresolved.
- `NO_SPATIAL_EFFICIENCY_ADVANTAGE`: $UCB(\Delta_{D0}) \le 0$ AND $UCB(\Delta_{T0}) \le 0$
- `INCONCLUSIVE`: intervals/diagnostics do not support another scientific class (e.g. failing to establish positive advantage for either but not resolving them as non-positive)
- `PROTOCOL_INVALID`: preregistered integrity/leakage/evaluability conditions fail

## 17. Diagnostics, Falsifiers, and Protocol Invalidity

Since normalized AULC is the primary estimand, curve crossings across root budgets are a reported *diagnostic*, not automatically a falsifier unless monotonic dominance is separately hypothesized.
Training-seed sensitivity is a reported stability *diagnostic* until an exact seed-aggregation rule is frozen. Seeds are not independent chess sampling units.

**PROTOCOL_INVALID** if:
- wrong UCI producer name
- engine binary SHA mismatch
- missing required UCI option
- configuration mismatch
- source and target accidentally sharing a process
- missing per-child reset boundary
- uncontrolled TT/search-history carryover
- wrong comparison perspective
- child-position reconstruction mismatch
- legal-move omission
- duplicate move acquisition
- node-budget mismatch
- tablebase access
- custom NNUE override
- malformed typed score
- source-derived target search policy
- post-hoc replacement
- target leakage
- root crosses train/tune/test partitions
- representation-specific tuning/resource differences
- corpus construction inconsistent with frozen rule
- software/provenance digest mismatch

## 18. Provenance and Blocker Audit

Future execution must use existing `SufficientPosition`, `ExperimentSpec v2`, `ExperimentResult`, and `SuiteManifest` semantics rather than parallel experiment infrastructure.

### Audit of Remaining Blockers

| Blocker | Constrained by existing code | Scientific Choice Remaining | Implementation Gap | Dependency |
|---|---|---|---|---|
| ROOT_POPULATION_FROZEN_TO_LICHESS_JULY_2026 | N/A | None (Frozen) | None | None |
| INSTRUMENT_CONFIG_FROZEN_SF18_50K_250K_V1 | supports fixed node/depth/time, per-legal-move eval, perspective, Threads/Hash | None (Frozen) | ENGINE_STATE_ISOLATION_AUDITED | None |
| SPLIT_AND_BUDGET_NOT_YET_FROZEN | N/A | training-root counts, partitions | None | source-only feasibility |
| P_NUMERIC_ENCODING_NOT_YET_FROZEN | P semantic identity frozen by SufficientPosition | Model's numeric encoding schema | None | None |
| LEARNER_FAMILY_NOT_YET_FROZEN | N/A | architecture, parameters, stopping rule | No ML framework dependency exists yet | P_NUMERIC_ENCODING |
| MATCHED_COMPARATOR_NOT_YET_FROZEN | N/A | exact rule-derived null encoding | None | LEARNER_FAMILY |
| SEED_SET_NOT_YET_FROZEN | N/A | seeds, aggregation rule | None | LEARNER_FAMILY |
| CONFIDENCE_LEVEL_NOT_YET_FROZEN | N/A | $\alpha$ level, bootstrap size | None | None |

### Blocker Dependency Order
 
 1. ROOT_POPULATION_FROZEN_TO_LICHESS_JULY_2026
 2. INSTRUMENT_CONFIG_FROZEN_SF18_50K_250K_V1
 3. ENGINE_STATE_ISOLATION_AUDITED
 4. SOURCE_ONLY_FEASIBILITY_COVERAGE_INVALID_REPAIR_REQUIRED
 5. SPLIT_AND_BUDGET_NOT_YET_FROZEN
 6. P_NUMERIC_ENCODING_NOT_YET_FROZEN
 7. LEARNER_FAMILY_NOT_YET_FROZEN
 8. MATCHED_COMPARATOR_NOT_YET_FROZEN
 9. SEED_SET_NOT_YET_FROZEN
 10. CONFIDENCE_LEVEL_NOT_YET_FROZEN

## 19. Status

**PREREGISTRATION_DRAFT_ONLY**
**ENGINE_EXECUTION_NOT_AUTHORIZED**
**MODEL_TRAINING_NOT_AUTHORIZED**
