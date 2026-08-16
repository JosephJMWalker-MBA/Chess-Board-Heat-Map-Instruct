# T3b-6 Matched-Control Estimand & Calibration Preregistration

## 1. Frozen Matcher and Target
Use the frozen T3b-4 strict matcher exactly:

$$B_{strict}(r \mid P_i) = (o_r, t_r, c_r, k_r, p_r, g_r)$$

and

$$M_i(c;s) = \{ n \in N_i(s) : B_{strict}(n \mid P_i) = B_{strict}(c \mid P_i) \}$$

Do not add, remove, relax, weight, or optimize matcher fields.

### Design-B Scientific Subject
Freeze the Design-B scientific subject as:
**For a rule-selected two-reply destination event, are its event-realizing replies unusually consequence-sensitive relative to exact same-origin, same-move-form legal alternatives?**

### Evidence Ceiling
Evidence ceiling remains: `EvidenceLevel.INTERVENTION_SENSITIVITY`.

Explicitly retain the T3b-4 ceiling:
**consequence estimates are sensitive to legal destination variation within exact same-origin move-form strata.**

Do not authorize:
- destination square alone caused the difference;
- objective causal effect;
- natural prevalence;
- producer independence;
- Heat contribution.

## 2. Event Replies and Matchability Requirement
For every future fixture $u$, retain exactly two event replies:
$$C_u(s) = \{c_1, c_2\}$$
with the existing distinct-origin semantics.

Strict matchability requires $m_j \ge 1$.

Define:
$$m_j = |M_u(c_j; s)|$$

A future Design-B outcome fixture must satisfy prospectively and rule-only:
**calibration-admissible fixture** $\iff m_1 \ge 2 \land m_2 \ge 2$.

If $m_j = 1$, then $H_j$ contains exactly two identities. Under the pseudo-label construction:
- unequal CP outcomes give signed contrasts $+1, -1$, hence $S_j = 1$ for both identities;
- tied CP outcomes give $S_j = 0$ for both identities.

Therefore:
$m_j = 1 \implies S_j(z)$ is invariant over $z \in H_j$.

In particular:
$m_1 = m_2 = 1 \implies Q_u = 1/2$
for every possible outcome assignment.

State explicitly:
Such a value would be structurally forced by the calibration universe rather than evidence against destination sensitivity.

Therefore a future Design-B outcome fixture must satisfy prospectively and rule-only:
$m_1 \ge 2, m_2 \ge 2$.

This requirement is a calibration-resolution condition, not an enrichment or relaxation of $B_{strict}$.
It must be checked before engine observation.

Define:
$$G_j = \#\{ n \in M_u(c_j; s) : Y_{c_j} > Y_n \}$$
$$T_j = \#\{ n \in M_u(c_j; s) : Y_{c_j} = Y_n \}$$

The matched statistic requires compatible CP-typed outcomes for every member of:
$H_1 \cup H_2$.

A mate-typed observation in that required matched/calibration universe makes the fixture non-evaluable for $D, S, Q$; no mate-to-CP conversion.
Do not require CP typing for unrelated legal replies outside $H_1 \cup H_2$ merely for this statistic.

## 3. Ordinal Evidence and Unsigned Sensitivity
Freeze the signed within-stratum ordinal contrast:
$$D_j = \frac{2G_j + T_j - m_j}{m_j}$$

Preserve $D_j$ in future evidence artifacts. Do not discard sign before storage.

Define unsigned within-stratum sensitivity:
$$S_j = |D_j|$$

Freeze the primary matched fixture statistic:
$$S_u^{match} = \frac{S_1 + S_2}{2}$$

### Equal Weighting Rationale
State explicitly why event replies are equal-weighted:
Matching-set cardinality is legal opportunity structure, not scientific importance. A control-rich origin must not receive more fixture weight merely because that piece has more same-form sibling destinations.

### Explicitly Rejected Statistics
Explicitly reject as the primary statistic:
$$A_{pooled} = \frac{\sum_{j=1}^2 \sum_{n \in M_j} [1(Y_{c_j} > Y_n) + \frac{1}{2} 1(Y_{c_j} = Y_n)]}{m_1 + m_2}$$

This is rejected as the primary fixture estimator because an event reply contributes once per available control, so control-set cardinality determines scientific weight.

Also explicitly reject:
$\left| \frac{D_1 + D_2}{2} \right|$
as the primary sensitivity statistic because opposite signed departures would cancel even though both event replies may be individually destination-sensitive.

Preserve signed $D_1, D_2$ so direction/coherence remains inspectable descriptively, but no signed direction may alter the preregistered classification.

## 4. Exact Calibration
For each $j$, define:
$$H_j = \{c_j\} \cup M_u(c_j; s)$$

For every pseudo-event identity $z \in H_j$, define its sibling set:
$H_j \setminus \{z\}$
and compute $D_j(z)$ and
$$S_j(z) = |D_j(z)|$$
using the exact same tie-half-credit formula.

Enumerate exhaustively:
$$\Omega_u = H_1 \times H_2$$

For every $\omega = (z_1, z_2)$:
$$S_u(\omega) = \frac{S_1(z_1) + S_2(z_2)}{2}$$

Let:
$$S_u^{obs} = S_u(c_1, c_2)$$
$$L_u = \#\{ \omega : S_u(\omega) < S_u^{obs} \}$$
$$E_u = \#\{ \omega : S_u(\omega) = S_u^{obs} \}$$

Freeze:
$$Q_u = \frac{2L_u + E_u}{2|\Omega_u|}$$

Use exact integer/rational arithmetic for $D$, $S$, $Q$, comparisons, thresholds, and medians. Floating-point renderings may be descriptive only.

### Pseudo-Event Clarification
State explicitly:
The Cartesian pseudo-event assignments are calibration labels only. A pseudo-pair is not required to share a destination square and must not be interpreted as a substitute destination event.

This is necessary because requiring common pseudo-destinations would introduce a new matchability condition not audited by T3b-5.

State explicitly:
$Q_u$ is an exact finite calibration percentile under the frozen within-stratum label universe. It is not a p-value, significance test, confidence level, randomized-treatment inference, or population probability.

## 5. Suite Aggregation
Mechanically inherit the existing T3b suite decision structure rather than choosing new thresholds.

For $K$ evaluable fixtures define:
$Q_{suite} = \text{median}_u(Q_u)$
with the exact conventional median: middle value for odd $K$, arithmetic mean of the two middle exact rationals for even $K$.

Define:
$H_{.75} = \#\{ u : Q_u \ge 3/4 \}$

Freeze:
- **SUPPORTED** iff $Q_{suite} \ge 3/4$ and $H_{.75} \ge \lceil 3K/4 \rceil$.
- **WEAK_SUPPORT** iff $Q_{suite} > 1/2$ but the SUPPORTED criterion is unmet.
- **FALSIFIED** iff $Q_{suite} \le 1/2$.
- **INCONCLUSIVE** iff the eventual protocol's minimum evaluable-fixture requirement is unmet or a global provenance/spec/acquisition/type-validity requirement fails.

Do not choose the future fixture count or generator in T3b-6. Do not silently convert the historical $K \ge 8$ rule into the future Design-B sample-size rule yet. That belongs to the subsequent rule-only fixture protocol.

Explain that the 1/2 and 3/4 calibration thresholds are inherited for continuity with the existing T3b framework, not statistical-significance thresholds.

## 6. Freeze Residual Confounding
Reaffirm that strict matching controls:
- exact origin;
- moving piece type;
- capture mode;
- captured piece type;
- promotion type;
- castling status.

It does not isolate:
- destination itself from path geometry;
- blocker changes;
- attack/defense geometry;
- checking relations;
- king exposure;
- pawn structure;
- resulting legal affordances;
- tactical continuation differences.

Therefore even a future SUPPORTED result earns only matched INTERVENTION_SENSITIVITY.

## 7. Separation from Future Protocol
T3b-6 must define mathematics only.

Do not define:
- a fixture generator;
- corpus domain string;
- fixture count;
- sampled ply range;
- target-selection tie-break;
- engine executable;
- engine search order;
- acquisition script;
- output paths;
- actual experimental FENs.

---
**T3b-6 status:** PREREGISTERED MATHEMATICAL CONTRACT / PENDING INDEPENDENT REVIEW
**Next possible step after review:** T3b-7 rule-only matched intervention fixture protocol.
