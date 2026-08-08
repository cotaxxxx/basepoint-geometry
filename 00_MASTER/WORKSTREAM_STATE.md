# Workstream state

Updated: 2026-08-08

This ledger separates current workstream control state from older historical status
paragraphs. It records no new machine certificate by itself.

## Item 6 — axial profile

Branch: `agent/prolate-item6-axis`

Audited repair sequence currently includes source head
`6905a795066f7d475d9caf0013d87b9c97192eb0`.

The interval-constructor audit was strengthened from endpoint overlap to full
endpoint-ball containment. GitHub Actions run `31228823621` passed the strengthened audit.
The interval-constructor blocker is **CLOSED**.

The full axial theorem nevertheless remains **NOT CERTIFIED** because finite-grid and
unbounded-tail dependency-DAG obligations remain open. Diagnostic/smoke success is not a
proof node.

## Item 3 sweep v9 — control branch

Branch: `agent/item3-sweep-v9-kernel-prototype`

Pinned prototype implementation scope:

```text
base = b82c00f2f154f131e02e122efdb156592fa98070
head = bb990b552d47af8788b5622b29af9dbaad4cf2f1
compare = 10 commits / 8 changed files
```

The exact immediate rehearsal range is

```text
[123731943/26214400, 118/25]
width = 2^-20.
```

The later upward objective toward `a_c` remains outside this rehearsal.

Resolved deterministic inputs include canonical exact centers, exact split scores,
`NONFINITE` ordering, exact tie to `r`, dps-50 partition replay, fresh dps-70 accepted-cell
verification, and aggregate-side rather than per-shard predecessor chaining.

## Item 3 sweep v9 — analytic/source branch

Branch: `agent/item3-v9-analytic-proof`

### Real analysis — RESOLVED

The branch proves:

- uniform positivity of all algebraic denominators on compact `0<=r<1`, `lambda>=1`
  machine rectangles;
- the exact square-sum identity giving `0<gamma<=1`;
- removable regularity of `h=acos^2` through the required third derivative;
- the explicit `F_r`, `F_lambda`, `F_rr`, `F_rlambda` integrands;
- differentiation under the fixed-domain integral by compactness/continuous majorants;
- mixed derivative commutation;
- exact quotient identities for `G_r`, `G_rr`, `G_rlambda`;
- the two-variable axis-path mean-value inclusion;
- midpoint-refinement preservation of the rehearsal analytic domain.

Thus the analytic content of `L-SECOND-DERIV` and `L-MIXED-DERIV`, and the analytic theorem
inside `L-MEAN-VALUE-ENCL`, is no longer `SPEC_PENDING`.

### Old prototype — NOT APPROVED

Audit of the old blob `57a7725c6ff0c4135723536b313e63d609eac4f6` against the pinned
`python-flint==0.9.0` integration callback contract found two source defects:

1. nested callback analyticity used logical AND instead of OR;
2. Gauss `2F1` had no explicit analytic cut guard.

The old prototype is retained for provenance/comparison only.

### Guarded clean-room candidate v2 — CREATED / NOT APPROVED

New standalone rigorous-only source:

```text
v9_candidate/prolate_F_derivatives_cleanroom_v9_candidate.py
KERNEL_ID = ITEM3_SWEEP_V9_FIVE_OUTPUT_CANDIDATE_V2.
```

It incorporates OR analytic propagation, guarded square roots, fail-closed `2F1` cut
rejection, common `0<r<1`, `lambda>=1` input validation, non-finite rejection, and only the
five rigorous F-level interfaces.

The branch also contains:

```text
STATIC_SOURCE_BOUNDARY_V2.md
static_audit_candidate_v2.py
SOURCE_FORMULA_MAP_CANDIDATE_V2.md.
```

The static auditor computes the candidate SHA-256 and source-boundary checks without
importing python-flint. Execution/archive of that audit and the pinned runtime validation
remain pending.

### Contract freeze candidates — MATERIALIZED

The following formerly open choices now have explicit freeze candidates:

```text
ORDER_CHECKPOINT_FREEZE_CANDIDATE.md
QUOTIENT_EXPRESSION_FREEZE_CANDIDATE.md
SCHEMA_AGGREGATE_FREEZE_CANDIDATE.md
VALIDATION_CORPUS_FREEZE_CANDIDATE.md
PERFORMANCE_GATE_FREEZE_CANDIDATE.md.
```

They specify, respectively:

- v8.1-compatible r/lambda traversal, record order, atomic checkpoint writes, fsync,
  cancellation-tail recovery, cadence, and <=5% checkpoint overhead;
- dual direct/common-denominator quotient associations with rigorous intersection when
  both are finite;
- final v9 schema IDs, embedded initial partial evidence, 32 MiB checkpoint ceiling,
  fixed-length aggregate chain byte grammar, and dependency-entry hash envelope;
- a >=256 unique-leaf validation corpus with category floors, stronger than the historical
  224-leaf benchmark;
- three full hosted qualification repetitions, each <3h, median <=2h30, maximum <=2h45,
  plus nine component timings per operation/input class.

These are candidates until incorporated in the one-shot final freeze and independently
validated.

### Aggregate exact core — IMPLEMENTED CANDIDATE

Pure-stdlib files now exist:

```text
v9_candidate/aggregate_chain_core_v9.py
v9_candidate/test_aggregate_chain_core_v9.py.
```

The core validates canonical reduced-rational shard endpoints, exact downward union,
canonical shard-plan SHA-256, one selected evidence hash per shard, and the frozen
big-endian/raw32 aggregate chain.

A two-shard split of the exact `2^-20` rehearsal range has the fixed test vector

```text
plan SHA-256
3efa83c7365355d1f16d574a12bf1912ab6b0d7f01cd27bce43532c1f4e60659

selected chain tip
83d5bd03c4410181e57dd375e79cefbbed484a07f7ef6e3a8ca8a659cb7e3ffe.
```

The same core logic was independently reproduced during review, including the one-shard
rerun property. A repository-hosted execution artifact is still required before promotion.

### Independent analytic rederivation

The independent formal rederivation source imports no prototype/candidate kernel, adapter,
runner, or checker. Its pinned repository execution artifact remains pending.

## Remaining v9 freeze blockers

Overall status remains **SPEC_PENDING / FREEZE NOT AUTHORIZED**. The critical remaining
work is now substantially narrower:

1. execute/archive candidate-v2 static audit and pinned `python-flint==0.9.0` runtime
   integration/analytic-flag controls;
2. execute/archive the independent analytic rederivation and aggregate-core tests in a
   pinned repository environment;
3. incorporate the five freeze candidates into one final v9 contract revision and run the
   corresponding independent controls;
4. complete post-import source identity and final runner/checker source-binding audit;
5. create canonical dependency entries/hashes from the final proof/source bytes;
6. implement the full shard evidence/checker/aggregate verifier around the exact core;
7. execute the >=256-leaf validation corpus;
8. run the three-repetition performance qualification;
9. perform the one-shot v9 freeze;
10. only then run the exact `2^-20` production rehearsal.

## Promotion rule

No diagnostic, prototype, formal symbolic check, partial run, or local reproduction alone
promotes a source or mathematical verdict. Failed/incomplete rehearsal evidence remains
fail-closed and cannot be converted into a certified subrange by silently shrinking the
approved target.
