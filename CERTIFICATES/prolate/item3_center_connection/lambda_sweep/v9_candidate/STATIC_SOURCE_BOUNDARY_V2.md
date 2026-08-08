# Item 3 sweep v9 candidate v2 — static source boundary

**Status:** `STATIC CONTRACT / EXECUTION VALIDATION PENDING`  
**Date:** 2026-08-08

Candidate source:

```text
prolate_F_derivatives_cleanroom_v9_candidate.py
```

Candidate ID:

```text
ITEM3_SWEEP_V9_FIVE_OUTPUT_CANDIDATE_V2
```

## Required public rigorous interfaces

Exactly the following F-level interfaces are intended for adapter use:

```text
F_arb
F_r_arb
F_lambda_arb
F_rr_arb
F_rlambda_arb.
```

No float, finite-difference, automatic-differentiation, network, subprocess, filesystem
read, dynamic import, or runtime package-install interface belongs to the candidate.

## Import allowlist

The candidate source is limited to:

```text
__future__.annotations
typing.Callable
flint.acb
flint.arb.
```

Adding another import requires a new static audit.

## Analytic boundary requirements

The source must contain exactly one nested integration combination equivalent to

```text
analytic_required = analytic_theta or analytic_phi.
```

The conjunction form

```text
analytic_theta and analytic_phi
```

is prohibited.

Both geometry square roots must receive

```text
analytic=analytic.
```

Every rigorous angle call must forward the same combined analytic requirement.

Before the Gauss `2F1` call, analytic-request evaluation must reject a `z` ball capable of
intersecting the principal real cut beginning at `z=1`.

## Parameter-domain boundary

Every public rigorous evaluation must pass through one common validation function that
rejects:

```text
non-finite r or lambda;
r.lower() <= 0;
r.upper() >= 1;
lambda.lower() < 1;
non-positive/non-finite tolerance;
non-positive depth/evaluation limits.
```

No public interface may bypass that validation path.

## Non-finite handling

A non-finite validated integral is never converted to a finite real enclosure. Public
interfaces fail closed if:

```text
value.is_finite() == false
```

or if the returned complex enclosure's imaginary component excludes zero.

A non-finite result may cause deterministic refinement at a higher adapter layer, but the
kernel itself never labels such a result with a mathematical sign.

## Formula mapping

The candidate's geometry and five F-level integrands are required to match
`ANALYTIC_DOMAIN_INTERCHANGE_PROOF.md` term for term. The earlier prototype remains a
comparison artifact only and is not imported by candidate v2.

## Static attack set

The final source-boundary audit must reject at least:

- import of the old prototype module;
- import of runner/checker/adapter code into the kernel;
- any `math`, `numpy`, `mpmath`, or float diagnostic dependency;
- logical AND for nested analytic propagation;
- missing analytic flag on either square root;
- missing `2F1` cut guard;
- a public interface bypassing `_validate_inputs`;
- missing finite check in `_as_real`;
- an unknown public `*_arb` interface;
- any source-level certification declaration.

## Promotion rule

This static boundary is satisfied only after an independent tool parses the exact
candidate bytes and produces a source-pinned PASS record. Text review alone is not source
approval.
