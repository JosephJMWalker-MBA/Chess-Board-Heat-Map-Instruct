# M8 Research Archive Guide

This directory preserves the M8.6.4–M8.6.8 research sequence as a chronological record. Earlier reports are not rewritten when later audits correct their interpretation.

## Reading order

1. `m8_6_4_semantic_integrity_audit.md` — identifies the Recurrence/selectivity semantic anomaly and reconstructs channel evidence.
2. `m8_6_5_experimental_consequence_reclassification.md` — corrects the M8.6.4 wording around the ordered first-success selector and reclassifies W-v2 after discovering the omitted Recurrence candidate policy.
3. `m8_6_6_w_v2_r_report.md` — records the retrospective corrected development run using `candidate_policy={"top_n": 5}`. This run is development evidence only and does not restore holdout status.
4. `m8_6_7_comparative_audit.md` — corrects the historical false-positive baseline and compares the accidental all-legal-root W-v2 run with W-v2-R under identical geographic metrics.
5. `m8_6_8_candidate_sensitivity_characterization.md` — freezes M8 and states the candidate-set sensitivity result.

## Supersession notes

- M8.6.4 used language suggesting stronger channel independence than `apply_shape_selectivity_v1()` itself exposes. M8.6.5 is authoritative on this point: the helper is an ordered first-success selector (`Direct -> Recurrence -> Bundle`), while the audit's per-channel states are a richer forensic reconstruction.
- Recurrence counts greater than five in the original W-v2 run were genuine counts for the candidate universe actually supplied: all legal root moves. The execution driver omitted the frozen `{"top_n": 5}` policy. They are not evidence that the Recurrence counting invariant failed.
- The original W-v2 run remains preserved as hostile/development evidence and is not pristine one-shot validation.
- W-v2-R is a retrospective corrected development experiment. It cannot restore sealed or holdout status.
- W10 and W11 remain invalid fixtures; they were not repaired in place.
- Benchmark expected regions are preregistered targets, not ontological ground truth. Terms such as `non-target benchmark geography` and `expected benchmark-target geography` are preferred over `noise` and `true signal` when interpreting selection changes.

## Frozen M8 result

The phase establishes that Recurrence must be written conditionally on its candidate universe:

`R(s | C) = |{c in C : s in PV(c)}| / |C|`

The accidental all-legal-root candidate universe and the frozen top-five development universe measure different spatial objects. On the hostile W development corpus, constraining the candidate universe reduced non-target benchmark geography while also removing some expected benchmark-target geography.

This demonstrates candidate-set dependence and a specificity-coverage tradeoff on that corpus. It does **not** establish that `top_n=5` is optimal, that the hostile failure modes are common in chess generally, or that a universal pivotality model has been solved.

No `ShapeSelectivity-v2` should be derived from the W corpus during the frozen M8 phase.
