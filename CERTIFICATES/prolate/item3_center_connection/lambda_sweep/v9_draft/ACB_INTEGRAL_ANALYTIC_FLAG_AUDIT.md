# Item 3 sweep v9 — `acb.integral` analytic-flag audit

**Status:** `SOURCE DEFECTS IDENTIFIED / REPAIR REQUIRED`  
**Date:** 2026-08-08  
**Pinned package:** `python-flint==0.9.0`

This audit concerns rigorous integration semantics only. It does not change the real
analytic formulas proved in `ANALYTIC_DOMAIN_INTERCHANGE_PROOF.md`.

## 1. Pinned external implementation

PyPI records `python-flint 0.9.0` as released on 2026-07-03. The release provenance binds
the published package to the upstream source tag/commit

```text
flintlib/python-flint
refs/tags/0.9.0
572c8a213a88c0f92feb1bdb938ce4622f4517fa
```

and the 0.9.0 source distribution has SHA-256

```text
686b2907eedaf0c0842caefab29a5775d2e633fd5815b81e13b81ca2c6ad0a36.
```

Reference:

```text
https://pypi.org/project/python-flint/0.9.0/
```

The python-flint `acb.integral` documentation states the callback contract:

- callback signature is `(x, analytic)`;
- when `analytic=False`, the callback returns an enclosure of the function value;
- when `analytic=True`, the callback must verify that the function is analytic on the
  supplied complex ball and return a non-finite ball if it is not;
- branch-sensitive operations such as `sqrt` must forward the analytic requirement.

Reference:

```text
https://python-flint.readthedocs.io/en/latest/acb.html
```

The FLINT `acb_hypgeom_2f1` documentation describes Gauss `2F1` as an analytically
continued function with singular points including `z=1`; python-flint exposes no
`analytic=` argument on `hypgeom_2f1` analogous to `sqrt(analytic=...)`.

Reference:

```text
https://flintlib.org/doc/acb_hypgeom.html
```

## 2. Prototype source inspected

Prototype source:

```text
CERTIFICATES/prolate/item3_center_connection/lambda_sweep/v9_prototype/
prolate_F_derivatives_cleanroom_v9.py
```

Audited prototype blob before repair:

```text
57a7725c6ff0c4135723536b313e63d609eac4f6
```

The source correctly forwards its current `analytic` boolean to

```text
w2.sqrt(analytic=analytic)
q.sqrt(analytic=analytic).
```

That part matches the library contract.

Two defects remain.

## 3. Defect A — nested integration uses logical AND

The outer callback is

```text
outer(theta, analytic_theta)
```

and the inner callback is

```text
inner(phi, analytic_phi).
```

The prototype currently calls the kernel with

```text
analytic_theta and analytic_phi.
```

This is not sufficient for nested validated integration.

### Case A1: inner analyticity requested

If

```text
analytic_theta = False,
analytic_phi = True,
```

then the inner integrator is explicitly asking the callback to certify analyticity in its
complex `phi` ball. Logical AND passes `False` to the branch-sensitive kernel and disables
that check.

### Case A2: outer analyticity requested

If

```text
analytic_theta = True,
analytic_phi = False,
```

the outer integrator needs the returned inner integral to be analytic as a function of
the supplied complex `theta` ball. During ordinary inner function evaluations,
`analytic_phi` may be false. Logical AND again disables branch checks even though outer
analyticity is being certified.

### Required rule

A branch-sensitive kernel evaluation must check the combined input ball whenever either
integration layer requests analyticity:

```text
analytic_required = analytic_theta or analytic_phi.
```

This is conservative but valid: if either layer asks for an analytic enclosure, every
branch-sensitive operation is checked on the actual combined complex ball supplied to the
kernel.

**Classification:** `BLOCKER / SOURCE REPAIR REQUIRED`.

## 4. Defect B — `2F1` branch is not guarded

The angle regularization uses

```text
z = (1-gamma)/2
H = 2F1(1/2,1/2;3/2;z).
```

For real physical inputs the analytic proof gives

```text
0 < gamma <= 1,
0 <= z < 1/2,
```

so the real integration path is safely separated from the `2F1` singular point/cut at
`z=1` and beyond.

However, `acb.integral` tests analyticity on **complex balls**, not only on the real path.
The real-domain inequality does not by itself prove that every complex `z` ball generated
by the integration algorithm avoids the principal `2F1` cut.

Unlike `sqrt`, python-flint `hypgeom_2f1` does not expose an `analytic=` flag. The callback
must therefore perform an explicit guard before evaluating it.

A sufficient fail-closed guard for the principal cut `[1,+infinity)` is:

```text
if analytic_required
and 0 in z.imag
and z.real.upper() >= 1:
    return a non-finite ball.
```

If the rectangular `z` ball has imaginary interval excluding zero, it does not intersect
the real cut. If its real upper endpoint is strictly below one, it also cannot intersect
the cut. The guard is intentionally sufficient rather than performance-optimal.

Any already-nonfinite `gamma` must also propagate immediately to a non-finite angle tuple.

**Classification:** `BLOCKER / SOURCE REPAIR REQUIRED`.

## 5. Other branch-sensitive operations

The current geometry has two explicit square roots:

```text
sqrt(w^2)
sqrt(q).
```

After Defect A is repaired, their existing `analytic=...` forwarding satisfies the
python-flint callback rule. All trigonometric functions used to form `s`, `c`, and `u` are
entire.

The `0F1` functions used after `h` are entire in their argument for the fixed non-pole
parameters `3/2`, `5/2`, `7/2`. Ordinary division by their values is meromorphic; a zero
in a denominator is expected to yield a non-finite enclosure and therefore fail closed.

## 6. Required repair controls

Before the five-output source can advance beyond prototype status, validation must show:

1. nested integration uses logical OR, not AND, for analytic requirements;
2. `angle_data_3` receives the analytic requirement;
3. a non-finite `gamma` propagates to non-finite angle data;
4. an analytic `z` ball potentially intersecting `[1,+infinity)` is rejected before
   `hypgeom_2f1` evaluation;
5. ordinary physical point inputs remain finite;
6. the exact endpoint `gamma=1` remains finite and reproduces the removable limits;
7. mutation back to AND is rejected by static/adversarial validation;
8. mutation removing the `2F1` cut guard is rejected;
9. fresh point/box integration tests still rigorously enclose independent reference
   values after the repair.

## 7. Mathematical effect

These defects do **not** invalidate the analytic derivative identities or the
real-variable differentiation-under-integral proof. They concern whether the numerical
integration callback fulfills the external library's rigorous complex-analytic contract.

Accordingly the workstream state is:

```text
real analytic proof: PASS
prototype integration callback semantics: REPAIR REQUIRED
source approval: BLOCKED
v9 freeze: NOT AUTHORIZED
```
