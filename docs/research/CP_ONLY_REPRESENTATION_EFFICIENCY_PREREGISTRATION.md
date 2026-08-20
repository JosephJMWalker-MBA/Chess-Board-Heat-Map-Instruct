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
5. **Deterministic Within-Game Selection**: Choose exactly one eligible root from each admissible game using a cryptographic-hash-derived selection. Hash input must be `SHA-256(game_id + ply)` modulo the number of rule-eligible plies. The procedure must be explicitly specified and versionable. If a game contains zero rule-eligible roots, exclude it with reason.
6. **Duplicates**: Canonical root identity is the full `SufficientPosition` identity. Exact duplicate semantic roots must not appear twice in the final population. Freeze deterministic duplicate resolution, retaining provenance for every discarded duplicate source. Do not treat two roots with different S0 history identities as identical.
7. **Transposition / Leakage Group**: For later split construction, use a conservative transposition-equivalence grouping key: `board_arrangement_fen` + `side_to_move` + `castling_rights` + `en_passant_square`. Its purpose is leakage prevention, not redefining canonical S0 identity.
8. **Prior Development Overlap**: Previously inspected ChessHeat development, fixture, hostile-validation, and research positions (e.g., M8 / W-suite / T1 / T2 / T3) must be excluded. Exclude exact `SufficientPosition` overlaps and conservative transposition overlaps.
9. **No Target-Based Replacement**: Once admitted to the base population, do not replace a root due to target attrition (e.g. mate-typed source, target acquisition failure). Population construction must remain independent of target $Y$.
10. **Manifest / Provenance Contract**: Reusing `SuiteManifest` / `ExperimentSpec v2` semantics, preserve: external corpus identity, corpus month/version, upstream artifact filename, upstream published checksum, locally verified checksum, parser/version identity, root-selection algorithm/version, game identity/provenance, selected ply, full `SufficientPosition` identity, conservative transposition-group identity, inclusion/exclusion outcome, exclusion reason, duplicate resolution, prior-development-overlap status, software revision, and manifest digest.
11. **Sample Size**: `SPLIT_AND_BUDGET_NOT_YET_FROZEN` remains unresolved. The population universe and deterministic root-generation procedure are frozen now, while the exact training/tune/test counts remain unfrozen.

## 5. Source and Target Acquisition Instrument Concept

Currently: **INSTRUMENT_CONFIG_NOT_YET_FROZEN**
This is execution-blocking. We must prospectively specify producer/version identity, comparison perspective, exact deterministic acquisition method for all legal alternatives, source budget type/value, target budget type/value, UCI/config settings, process lifecycle, hash reset semantics, threads, hash size, MultiPV/searchmoves behavior, and any randomness. Top-k acquisition is incompatible. The target must use a strictly greater independently acquired budget. Source and target observations must not inherit uncontrolled TT/search state from one another.

## 6. Source and Target Evaluability

**Source Pair Eligibility:**
A pair is source-evaluable only when: both alternatives are legal, have distinct UCI identities, both source observations are valid, both source observations are CP-typed, common frozen perspective is maintained, and provenance is valid. Mate/WDL/non-valid source cases are prospectively non-evaluable and must not be replaced.

**Target Labels:**
- `FIRST_BETTER`: $O_Y(m_1) > O_Y(m_2)$ under frozen CompareTyped semantics
- `EQUAL`: Perfect tie
- `SECOND_BETTER`: $O_Y(m_1) < O_Y(m_2)$ under frozen CompareTyped semantics

**Non-Evaluable Target Cases (retained in coverage accounting, no replacement):**
- `UNORDERED`: Target-non-evaluable mixed type (if applicable)
- `TARGET_ACQUISITION_FAILURE`: Evaluation could not be produced

If target attrition leaves a root with zero evaluable pairs, that root is excluded. Do not backfill another root.

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
- target leakage
- source/target instrument mismatch from frozen spec
- uncontrolled TT/process-state contamination
- root crosses train/tune/test partitions
- representation-specific tuning/resource differences
- malformed sufficient-position state
- corpus construction inconsistent with frozen rule
- software/provenance digest mismatch
- post-hoc replacement of non-evaluable cases

## 18. Provenance and Blocker Audit

Future execution must use existing `SufficientPosition`, `ExperimentSpec v2`, `ExperimentResult`, and `SuiteManifest` semantics rather than parallel experiment infrastructure.

### Audit of Remaining Blockers

| Blocker | Constrained by existing code | Scientific Choice Remaining | Implementation Gap | Dependency |
|---|---|---|---|---|
| ROOT_POPULATION_FROZEN_TO_LICHESS_JULY_2026 | N/A | None (Frozen) | None | None |
| INSTRUMENT_CONFIG_NOT_YET_FROZEN | supports fixed node/depth/time, per-legal-move eval, perspective, Threads/Hash | specific nodes/depth budgets, engine version | ENGINE_STATE_ISOLATION_NOT_YET_IMPLEMENTED | None |
| SPLIT_AND_BUDGET_NOT_YET_FROZEN | N/A | training-root counts, partitions | None | source-only feasibility |
| P_NUMERIC_ENCODING_NOT_YET_FROZEN | P semantic identity frozen by SufficientPosition | Model's numeric encoding schema | None | None |
| LEARNER_FAMILY_NOT_YET_FROZEN | N/A | architecture, parameters, stopping rule | No ML framework dependency exists yet | P_NUMERIC_ENCODING |
| MATCHED_COMPARATOR_NOT_YET_FROZEN | N/A | exact rule-derived null encoding | None | LEARNER_FAMILY |
| SEED_SET_NOT_YET_FROZEN | N/A | seeds, aggregation rule | None | LEARNER_FAMILY |
| CONFIDENCE_LEVEL_NOT_YET_FROZEN | N/A | $\alpha$ level, bootstrap size | None | None |

### Blocker Dependency Order

1. ROOT_POPULATION_FROZEN_TO_LICHESS_JULY_2026
2. INSTRUMENT_CONFIG_NOT_YET_FROZEN + ENGINE_STATE_ISOLATION_NOT_YET_IMPLEMENTED
3. Source-only feasibility/coverage acquisition (measures CP eligibility, pair counts after root/instrument are frozen. May not inspect held-out target labels)
4. SPLIT_AND_BUDGET_NOT_YET_FROZEN
5. P_NUMERIC_ENCODING_NOT_YET_FROZEN
6. LEARNER_FAMILY_NOT_YET_FROZEN
7. MATCHED_COMPARATOR_NOT_YET_FROZEN
8. SEED_SET_NOT_YET_FROZEN
9. CONFIDENCE_LEVEL_NOT_YET_FROZEN

## 19. Status

**PREREGISTRATION_DRAFT_ONLY**
**ENGINE_EXECUTION_NOT_AUTHORIZED**
**MODEL_TRAINING_NOT_AUTHORIZED**
