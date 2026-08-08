# Item 3 sweep v9 — analytic-flag validation delta

**Status:** `NORMATIVE VALIDATION ADDITION / SOURCE REPAIR PENDING`  
**Date:** 2026-08-08

This delta supplements `cleanroom_independent_validation_plan.md` for the concrete
`python-flint==0.9.0` integration semantics identified in
`ACB_INTEGRAL_ANALYTIC_FLAG_AUDIT.md`.

It authorizes no production source, run, tag, or certificate.

## 1. Callback contract to validate

For every callback passed to `acb.integral`, an `analytic=True` request means that the
callback must either:

1. return a rigorous enclosure of the analytic continuation on the entire supplied
   complex ball; or
2. return a non-finite enclosure so the integration algorithm fails closed/subdivides.

The production source must not silently downgrade an analytic request to an ordinary
point/ball evaluation.

## 2. Nested-integration propagation controls

The v9 kernel is nested in `theta` and `phi`. Validation must cover all four boolean
combinations

```text
(analytic_theta, analytic_phi)
(False, False)
(False, True)
(True, False)
(True, True)
```

and establish that the branch-sensitive kernel receives

```text
analytic_required = analytic_theta OR analytic_phi.
```

Required mutation attacks:

### `M-ANALYTIC-AND`

Replace OR by AND. The static/mutation suite must reject the candidate.

### `M-ANALYTIC-INNER-DROP`

Force `analytic_required=False` when only the inner callback requests analyticity. The
suite must reject.

### `M-ANALYTIC-OUTER-DROP`

Force `analytic_required=False` during ordinary inner evaluations while the outer
callback requests analyticity. The suite must reject.

## 3. `sqrt` controls

Both branch-sensitive square roots

```text
sqrt(w^2)
sqrt(q)
```

must receive the combined `analytic_required` flag.

Mutation attacks must reject:

- omission of the flag on either square root;
- hard-coding `analytic=False`;
- forwarding only the inner flag;
- forwarding only the outer flag.

Positive controls must include a complex ball that touches a square-root cut and must
show fail-closed non-finite behavior when analyticity is requested.

## 4. Gauss `2F1` cut controls

The angle representation uses

```text
z=(1-gamma)/2,
2F1(1/2,1/2;3/2;z).
```

The principal continuation has the real cut beginning at `z=1`. Since the python-flint
method has no `analytic=` parameter, source must explicitly guard the cut during an
analytic callback request.

The frozen sufficient rejection predicate is proposed as

```text
analytic_required
AND (0 in Im(z))
AND (upper(Re(z)) >= 1).
```

If true, angle evaluation returns a non-finite tuple before invoking `hypgeom_2f1`.

The final source freeze may replace this by a provably stronger/sharper predicate, but it
must never weaken analytic safety without a contract amendment.

Required controls:

- `z=0`: finite;
- a compact real ball strictly below `1`: finite when all other operations are finite;
- a ball intersecting the real cut at `1`: non-finite under `analytic=True`;
- a ball crossing the cut above `1`: non-finite under `analytic=True`;
- a complex ball with imaginary interval separated from zero and otherwise finite:
  permitted to evaluate;
- non-finite `gamma`: propagates non-finite without attempting a proof verdict.

Required mutation attack:

### `M-2F1-CUT-GUARD-REMOVED`

Remove or bypass the guard. The suite must reject the source even if all physical real
point tests still pass.

## 5. Endpoint regularization controls

At the physical removable endpoint

```text
gamma=1,
z=0,
```

the repaired source must remain finite and enclose the exact values

```text
h=0,
h'=-2,
h''=2/3,
h'''=-8/15.
```

This control distinguishes a correct branch guard from an overbroad rule that rejects the
physical endpoint itself.

## 6. Integration-level positive controls

After source repair, run at least the following with `python-flint==0.9.0`:

1. one rigorous `F` point evaluation in the rehearsal domain;
2. one rigorous evaluation for each of `F_r`, `F_lambda`, `F_rr`, `F_rlambda`;
3. one narrow r/lambda box evaluation for all five outputs;
4. one full mean-value cell reconstruction using fresh calls;
5. the same accepted cell at checker precision.

Every output must be finite, the imaginary interval must contain zero, and independent
reference values/strict containment controls must be satisfied.

These are source-validation controls, not performance qualification and not a
`CERTIFIED_LAMBDA_RANGE`.

## 7. Static source assertions

The final static audit must establish all of:

```text
"analytic_theta and analytic_phi" absent from the integration callback;
combined OR rule present exactly once in the nested integration path;
all five rigorous angle-data call sites forward analytic_required;
all branch-sensitive sqrt calls forward analytic_required;
2F1 analytic cut guard present before hypgeom_2f1;
no diagnostic float path is imported by a rigorous interface.
```

## 8. Promotion rule

The analytic-flag source defect is closed only when:

1. repaired source bytes are fixed;
2. these controls pass under pinned `python-flint==0.9.0`;
3. an independent static audit rederives the assertions from those exact bytes;
4. source hash and post-import identity are bound to the v9 validation manifest.

Until then:

```text
REAL_ANALYTIC_PROOF = PASS
INTEGRATION_CALLBACK_SOURCE = REPAIR_REQUIRED
AUDITED_SOURCE = NOT_APPROVED
V9_FREEZE = NOT_AUTHORIZED
```
