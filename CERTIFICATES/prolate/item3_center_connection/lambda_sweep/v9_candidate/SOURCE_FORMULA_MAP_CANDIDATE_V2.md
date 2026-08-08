# Item 3 sweep v9 candidate v2 — source/formula map

**Status:** `STATIC MAP COMPLETE / INDEPENDENT SOURCE AUDIT PENDING`  
**Date:** 2026-08-08

Candidate:

```text
prolate_F_derivatives_cleanroom_v9_candidate.py
```

Analytic proof:

```text
../v9_draft/ANALYTIC_DOMAIN_INTERCHANGE_PROOF.md
```

## 1. Angle kernel

Candidate `angle_data_3` implements

```text
z=(1-gamma)/2
h=4 z 2F1(1/2,1/2;3/2;z)^2
h'=-2/S
h''=(2/3)T/S^3
h'''=(2/15)U/S^4-(2/3)T^2/S^5
```

with

```text
S=0F1(;3/2;-h/4)
T=0F1(;5/2;-h/4)
U=0F1(;7/2;-h/4).
```

The analytic proof establishes the removable physical endpoint

```text
h'(1)=-2,
h''(1)=2/3,
h'''(1)=-8/15.
```

Candidate v2 additionally enforces the integration-library analytic contract by rejecting
an analytic-request `z` ball that can meet the principal real `2F1` cut beginning at 1.
This guard is implementation validation, not a change to the real formula.

## 2. Geometry

Candidate `_geometry` uses exactly

```text
ell=s^2+lambda^2 c^2
w^2=lambda^2 s^2+c^2
q=ell-2ru+r^2
W=1-ru
B=lambda/w
gamma=B W/sqrt(q).
```

The derivative organization maps term-for-term to the proof variables

```text
d=r-u
N=u(1-ell)+r(u^2-1)
N_r=u^2-1
M=N_r q-3Nd
M_r=-N_r d-3N
B_log_lambda=c^2/(lambda w^2)
q_lambda=2lambda c^2
N_lambda=-2lambda u c^2
M_lambda=N_r q_lambda-3N_lambda d.
```

The returned derivatives are exactly

```text
gamma_r
gamma_rr
gamma_rrr
gamma_lambda
gamma_rlambda
gamma_rrlambda
```

from the proof.

Both `sqrt(w^2)` and `sqrt(q)` receive the combined analytic requirement.

## 3. Five F-level kernels

### `_F_kernel`

Maps to

```text
Phi_F=s[-u h+W h' gamma_r].
```

### `_F_r_kernel`

Maps to

```text
partial_r Phi_F
=s[-2u h' gamma_r+W(h'' gamma_r^2+h' gamma_rr)].
```

### `_F_lambda_kernel`

Maps to

```text
partial_lambda Phi_F
=s[-u h' gamma_lambda
 +W(h'' gamma_lambda gamma_r+h' gamma_rlambda)].
```

### `_F_rr_kernel`

With

```text
A=h'' gamma_r^2+h' gamma_rr,
```

maps to

```text
partial_rr Phi_F
=s[-3uA
 +W(h''' gamma_r^3+3h'' gamma_r gamma_rr+h' gamma_rrr)].
```

### `_F_rlambda_kernel`

Maps to

```text
partial_rlambda Phi_F
=s[-2u(h'' gamma_lambda gamma_r+h' gamma_rlambda)
 +W(h''' gamma_lambda gamma_r^2
    +2h'' gamma_r gamma_rlambda
    +h'' gamma_lambda gamma_rr
    +h' gamma_rrlambda)].
```

Every rigorous kernel forwards its `analytic` argument to both geometry and angle data.

## 4. Fixed-domain integration

Candidate `_rigorous_integral_2d` integrates on

```text
theta in [0,pi/2]
phi in [0,pi]
```

and divides by `pi`, matching the proved normalization.

The nested callback combines requirements by

```text
analytic_required = analytic_theta OR analytic_phi.
```

The old prototype conjunction is not inherited.

## 5. Public domain enforcement

Every public F-level interface routes through `_evaluate`, which routes through
`_validate_inputs` before any validated integral call.

The enforced real parameter domain is

```text
0 < r < 1 on the whole r ball
lambda >= 1 on the whole lambda ball.
```

This implements the hypotheses of `DOMAIN_ENFORCEMENT_LEMMA.md` at the kernel boundary in
addition to the higher-level runner/checker tree controls.

## 6. Non-finite behavior

`_as_real` rejects a non-finite complex integral and rejects an imaginary enclosure that
does not contain zero. No non-finite source result is promoted to a real sign enclosure.

## 7. Quotient boundary

Candidate v2 intentionally publishes only F-level outputs. It does not implement

```text
G_r,
G_rr,
G_rlambda.
```

Those belong to the adapter and are governed by

```text
../v9_draft/QUOTIENT_EXPRESSION_FREEZE_CANDIDATE.md.
```

This preserves source-layer separation between the clean-room integral kernel and the
mean-value/refinement adapter.

## 8. Audit state

```text
real formulas: PROVED
candidate source mapping: COMPLETE BY STATIC REVIEW
static source auditor: PRESENT / EXECUTION RECORD PENDING
python-flint runtime validation: PENDING
post-import source identity: PENDING
candidate source approval: NOT APPROVED
v9 freeze: NOT AUTHORIZED
```
