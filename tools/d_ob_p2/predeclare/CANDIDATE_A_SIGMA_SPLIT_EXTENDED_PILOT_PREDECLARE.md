# D-OB P2 candidate (a) sigma-split extended pilot: successor measurement predeclare

Status: DIAGNOSTIC / NOT_EVIDENCE. Draft for freeze. D-P2 remains NOT_CERTIFIED.
This document is not part of canonical `design/d-ob-p2`.

## 0. Relation to the closed A4 pilot

- This is a successor predeclare. It does not modify the closed A4 base predeclare
  (`tools/d_ob_p2/predeclare/CANDIDATE_A_SIGMA_SPLIT_PILOT_PREDECLARE.md`, SHA-256
  `dbef315750f1ccacc037d6962450319a74bdb47578323e995dfc495fbf1c0b08`) or its addendum 1
  (`...PILOT_PREDECLARE_ADDENDUM_1.md`, SHA-256 `31a4ed3438dea84b9d5ebffc26da6c0645ea6f784cb2b86acf79edf512d9c3fc`).
- A4 was completed and adjudicated before this extended pilot was designed.
- A4 output TSV SHA-256: `afed07837353095344befb865c3ee94c9a7020a67b2d4e86f68973dc20635d54`.
- A4 verdict: `RUN VALID`, and `candidate (a) NOT READY at k<=8`.
- A4 counts (margin_k_lower > 0, out of 240): k=1: 0/240; k=2: 23/240; k=4: 61/240; k=8: 120/240.
- A4 fallback was zero for all A4 k values.
- Therefore the k design of this extended pilot is informed by A4. This pilot is preregistered only
  with respect to its own not-yet-generated output. Its k design was not chosen blind to A4.
- The A4 rule forbidding extrapolation or adoption beyond k=8 from the A4 pilot remains intact.
  This run is a new preregistered diagnostic; it is not an extrapolation from A4.

## 1. Pins, identity and sample (unchanged from A4)

| object | value |
|---|---|
| measurement script | `near_sigma_split_measure.py`, SHA-256 `a1dcad04d4cbefea9728ab67530c656f5cff00648d6cf4d1008574b3e0898e8d` |
| producer | SHA-256 `dff79bc40d78d53a1491c3edbe368034b2d28a4894da45ac13b3b04c3ad0f19b` |
| map | SHA-256 `0584110495c9d3b98a96d88e3d9fbe717bde326f2b76dcc465db784ad3bd26f8` |
| A4 bridge TSV | SHA-256 `afed07837353095344befb865c3ee94c9a7020a67b2d4e86f68973dc20635d54` |
| judge | `tools/d_ob_p2/evaluate_sigma_pilot_ext.py`, pinned by its file SHA-256 at freeze |

- Population: map rows with `decision=unresolved` and `column=near`, in file order: 7,662 rows.
- Sample: `stride:32:0`: exactly the same 240 keys as A4, in the same order.
- The fixed baseline partition is unchanged (the measurement script is unchanged).

## 2. k set

The exact run uses `--ks 1,8,16,32,64`.

| k | role |
|---|---|
| 1 | producer / L1 reproduction control |
| 8 | bridge control against the closed A4 run |
| 16, 32, 64 | candidates |

Neither k=1 nor k=8 can be selected as k*.

## 3. Execution identity

Executor, host, interpreter, absolute paths, the output path and the worker count are fixed in a separate
execution addendum, frozen before ignition. The output path is new; the closed A4 output is never
overwritten or appended to. Preferred worker count: `--workers 20`, subject to host-load confirmation.
The worker count is an execution condition, not part of the selection rule. The k sum is
1 + 8 + 16 + 32 + 64 = 121 (A4: 15), so the run is substantially more expensive than A4.

## 4. Run-validity gate

The run is VALID only if all six hold:

1. The execution exit line is `EXIT=0`, and the completion summary
   `rows=240 not_still_unresolved=0 k1_not_reproduced=0` is present in the run log and in the output TSV.
2. Exactly 240 data rows whose keys equal the 240 keys re-derived independently from the pinned map with
   `stride:32:0`, in exactly that order.
3. `L1_reproduces_producer=yes` for every row.
4. `still_unresolved=yes` for every row.
5. `margin_k1_lower <= 0` for every row.
6. Bridge determinism: for each of the 240 rows, in the same order and for the same key, the new run's
   `margin_k8_lower` field equals the A4 TSV's `margin_k8_lower` field as an exact string. The comparison
   does not parse the field as a number and does not normalize it in any way.

If any item fails, the result is `RUN INVALID`. The judge then prints no Section 5 count or selection
result and no Section 6 fallback result.

## 5. Score and selection rule

For every run k:

    p_k = #{ i : margin_k_lower(i) > 0 } / 240

- Strict inequality `> 0`. Rows with fallback remain in the denominator.
- Success threshold: p_k >= 0.90, which is exactly count >= 216 of 240.
- Counts are reported for all run k, including k=1 and k=8 as controls.
- k* is the smallest k in {16, 32, 64} with count >= 216.
- If none of {16, 32, 64} reaches 216, the disposition is:
  `candidate (a) NOT READY at fixed partition, k<=64`.
  The fixed-partition candidate (a) route is then closed for this design stage, and the next design
  decision returns to the audit side: either the v2-degeneration route (option A) or an adaptive
  route (option C).
- No interpolation or extrapolation. No rescue based on slope, trend, saturation, confidence
  intervals, standard errors or extrapolated k. The threshold and the k set are not changed after
  seeing any result.
- The sequence of p_k values may be described only as a descriptive saturation curve. It is not a
  gate, threshold, rescue criterion, extrapolation rule or alternative selection rule. No
  levelling-off threshold is defined.

## 6. Fallback reporting

For every run k: the number of leaves with `fallback_k > 0` and the total number of fallback cells.

## 7. Interruption

No resume. An interrupted run is RUN INVALID. A rerun requires a new execution addendum with a new
output identity; Sections 1, 2, 4 and 5 do not change.

## 8. Freeze and ignition order

1. Draft this successor predeclare.
2. Draft the extended judge.
3. Commit both drafts without running the extended pilot and without creating its output.
4. Report commit IDs, parents, tree changes and full file SHA-256 values.
5. Full byte audit by the auditing side against its requirements R1-R8.
6. Explicit `FREEZE countersign` by the auditing side.
7. Execution addendum frozen; then the A2-equivalent check (pins, environment, output absence).
8. Formal `--check-only`.
9. The A2-equivalent check again immediately before ignition.
10. Ignition.

Ignition before the FREEZE countersign loses the clean preregistered execution status; that case must be
adjudicated separately.

## 9. Reporting after a valid run

Verbatim: the check-only output, the run log, the `EXIT=` line, the output TSV SHA-256, the run log
SHA-256, the judge stdout. Results: count out of 240 for k = 1, 8, 16, 32, 64; k* if it exists, otherwise
the exact disposition of Section 5; for every k, fallback leaf count and total fallback cells.
