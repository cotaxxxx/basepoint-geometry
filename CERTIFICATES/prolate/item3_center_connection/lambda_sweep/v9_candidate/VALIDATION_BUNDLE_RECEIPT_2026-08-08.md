# Item 3 sweep v9 — candidate-v2 validation bundle receipt

**Date:** 2026-08-08  
**Status:** `VALIDATION_BUNDLE_PASSED / SOURCE CANDIDATE NOT YET PRODUCTION-APPROVED`

This receipt records the repository-hosted validation bundle for the guarded five-output
clean-room candidate v2 and the independent analytic/aggregate support code.  It is not a
production tag, final v9 freeze, workflow authorization, or `CERTIFIED_LAMBDA_RANGE`.

## 1. Final bundle outcome

Tracked record:

```text
validation_bundle_outcome.json
status = PASSED
static    = success
runtime   = success
rederive  = success
aggregate = success.
```

The passing bundle is tied to the environment and source hashes below.

## 2. Pinned environment

```text
Python       = 3.13.14
python-flint = 0.9.0
SymPy        = 1.14.0.
```

## 3. Source identities

```text
prolate_F_derivatives_cleanroom_v9_candidate.py
  abac1ce574097df32491aba187694b9800a3f76de9a85df9be0b7995923dab76

static_audit_candidate_v2.py
  e5f30afa32284727731aa1f2481e1eaf19382da29127a2867174f2fa7c545eb3

runtime_audit_candidate_v2.py
  fc404a2f7e4577849248363f1da9f39a60a349d4d9793702ff686e1a4324327f

aggregate_chain_core_v9.py
  3a80f33ad6a7104883ef824a09275b45af28143e82d307601e8d6042bc9c5cea

test_aggregate_chain_core_v9.py
  e287cf161001dec0578b9cb90141de69161b9ce120458338099e44504f2c995b

independent_analytic_rederivation_v9.py
  aad629252e4f2f8f882a16ab9c1d2c9d2cac9679280582312c4adbb0f7963cbb.
```

The candidate kernel hash is identical before and after runtime import.

## 4. Static source-boundary audit

Final status: `PASSED`.

The static audit confirms, among other checks:

- exact five rigorous public `*_arb` interfaces;
- no prototype/runner/checker/adapter import;
- no float diagnostic dependency in the rigorous candidate;
- nested analytic propagation uses OR and no AND;
- both square roots forward `analytic=`;
- all five rigorous angle calls forward `analytic=`;
- exactly one Gauss `2F1` call;
- explicit cut guard occurs before the executable `2F1` call;
- input-domain guards for `0<r<1`, `lambda>=1`;
- final-integral nonfinite rejection and imaginary-zero containment.

The final executable source positions recorded by the audit are

```text
2F1 cut guard line = 56
2F1 call line      = 59.
```

### Historical false-negative classification

The first bundle attempt reported only

```text
2f1_cut_guard_precedes_call = false
```

while separately reporting that the guard existed and that exactly one `2F1` executable
call existed.  Inspection showed that the auditor used

```text
text.index("hypgeom_2f1")
```

which matched the function docstring before the executable call.  This was an auditor
position-classification defect, not a candidate-kernel defect.

The auditor was repaired to compare the guard source line with the actual AST call node
line.  The candidate kernel bytes were unchanged across this correction.  The rerun then
passed every static predicate.

## 5. Pinned runtime audit

Final status: `PASSED` under `python-flint==0.9.0`.

The runtime audit confirms:

- exact candidate module path after import;
- kernel ID `ITEM3_SWEEP_V9_FIVE_OUTPUT_CANDIDATE_V2`;
- source hash stable across import;
- `gamma=1` endpoint evaluation finite;
- endpoint derivative constants contain `-2`, `2/3`, `-8/15`;
- Gauss-cut attack at the guarded endpoint is rejected fail-closed;
- ordinary physical angle input is finite;
- valid domain input accepted;
- `r=0`, `r=1`, and `lambda<1` rejected;
- all five rigorous F-level outputs finite at the pinned runtime test point.

The runtime test point is

```text
r      = 0.03
lambda = 4.72.
```

The recorded enclosures are diagnostic runtime-validation evidence only; they are not a
stationary-point certificate.

## 6. Independent analytic rederivation

Final status: `PASSED`.

The independent source imports neither the prototype/candidate kernel nor
runner/checker/adapter.  It independently passes the recorded checks for:

- angle endpoint derivatives;
- gamma derivatives and range factorization;
- `Phi_F_r`, `Phi_F_lambda`, `Phi_F_rr`, `Phi_F_rlambda`;
- `G_r`, `G_rr`, and `G_rlambda` quotient identities.

Its role remains `FORMAL_REDERIVATION_SUPPORT_ONLY`; it does not by itself validate
`acb.integral` semantics or production source binding.

## 7. Aggregate exact-core controls

Final status: `PASSED`, exit code zero.

The fixed exact two-shard test vector records

```text
plan_sha256
  3efa83c7365355d1f16d574a12bf1912ab6b0d7f01cd27bce43532c1f4e60659

selected_chain_tip
  83d5bd03c4410181e57dd375e79cefbbed484a07f7ef6e3a8ca8a659cb7e3ffe.
```

The exact core validates canonical rationals, exact shard union, canonical plan hash,
selected-shard ordering, the raw32/big-endian selected chain, stale-plan/tip attacks, and
the one-shard rerun property.

## 8. Promotion effect

This bundle closes the previously pending repository-hosted evidence for:

```text
candidate-v2 static source boundary
candidate-v2 pinned runtime sanity/integration path
independent formal rederivation
aggregate exact-core test vector.
```

The appropriate source state is therefore

```text
VALIDATED_SOURCE_CANDIDATE
```

not `PRODUCTION_APPROVED`.

The full v9 workstream remains

```text
SPEC_PENDING / FREEZE NOT AUTHORIZED
```

until final runner/checker/adapter binding, integrated-contract controls, canonical
logical-dependency hashes, the >=256-leaf independent corpus, three-run performance
qualification, and the one-shot freeze are all closed.
