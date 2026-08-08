# Item 3 sweep v9 — source/formula map

**Status:** `STATIC MAP COMPLETE / SOURCE APPROVAL PENDING`  
**Date:** 2026-08-08  
**Issue:** #20

This document maps the analytic formulas in
`ANALYTIC_DOMAIN_INTERCHANGE_PROOF.md` to the current prototype source. It does not approve
the prototype for production and does not replace independent source validation.

## 1. Pinned prototype identity

Prototype file:

```text
CERTIFICATES/prolate/item3_center_connection/lambda_sweep/v9_prototype/
prolate_F_derivatives_cleanroom_v9.py
```

The independently recorded prototype SHA-256 is

```text
9a237ef8f3d7f46d661ef68d1edff9f47ee22c3f25ac8b9630e5b3d64b321966
```

and the Git blob identity recorded by the prototype audit is

```text
57a7725c6ff0c4135723536b313e63d609eac4f6
```

Any source approval must rederive both identities from the final candidate bytes. A source
change invalidates this mapping until it is repeated.

## 2. Angle regularization

Source function:

```text
angle_data_3
```

Analytic object:

```text
h(gamma) = arccos(gamma)^2
h'(gamma)
h''(gamma)
h'''(gamma)
```

The source uses

```text
z = (1-gamma)/2
h = 4 z 2F1(1/2,1/2;3/2;z)^2
```

and hypergeometric regularizations for the first three derivatives. The analytic proof
establishes that the target real functions extend regularly to `gamma=1` with

```text
h'(1)=-2,
h''(1)=2/3,
h'''(1)=-8/15.
```

The formal rederivation independently checks these endpoint values. A future interval
validation must still establish that the concrete hypergeometric calls enclose the target
real extensions for every approved point/box input.

## 3. Geometry map

Source function:

```text
_geometry
```

The following source names correspond directly to the analytic proof:

| Source name | Analytic quantity |
|---|---|
| `s` | `sin(theta)` |
| `c` | `cos(theta)` |
| `u` | `s cos(phi)` |
| `ell` | `s^2 + lambda^2 c^2` |
| `w2` | `lambda^2 s^2 + c^2` |
| `w` | `sqrt(w2)` |
| `q` | `ell - 2 r u + r^2` |
| `W` | `1-r u` |
| `B` | `lambda/w` |
| `gamma` | `B W/sqrt(q)` |
| `d` | `r-u` |
| `N` | `u(1-ell)+r(u^2-1)` |
| `N_r` | `u^2-1` |
| `M` | `N_r q - 3 N d` |
| `M_r` | `-N_r d - 3N` |
| `B_log_lambda` | `c^2/(lambda w^2)` |
| `q_lambda` | `2 lambda c^2` |
| `N_lambda` | `-2 lambda u c^2` |
| `M_lambda` | `N_r q_lambda - 3 N_lambda d` |

The six published geometry derivatives map as follows:

```text
gamma_r          <-> Section 5 first-r identity
gamma_rr         <-> Section 5 second-r identity
gamma_rrr        <-> Section 5 third-r identity
gamma_lambda     <-> Section 5 lambda identity
gamma_rlambda    <-> Section 5 mixed identity
gamma_rrlambda   <-> Section 5 second-r/mixed identity
```

The source and analytic proof use the same denominator powers and the same `N`, `M`
organization. The independent rederivation script starts from `gamma` itself and verifies
these candidate identities without importing `_geometry`.

## 4. F integrand

Source function:

```text
_F_kernel
```

Source structure:

```text
s * (-u*h + W*h1*gamma_r)
```

Analytic identity:

```text
Phi_F = s[-u h(gamma) + W h'(gamma) gamma_r].
```

This is exact syntactic/algebraic correspondence.

## 5. F_r integrand

Source function:

```text
_F_r_kernel
```

Source structure:

```text
s * (
  -2*u*h1*gamma_r
  + W*(h2*gamma_r^2 + h1*gamma_rr)
)
```

Analytic identity:

```text
partial_r Phi_F
 = s[-2u h' gamma_r + W(h'' gamma_r^2 + h' gamma_rr)].
```

## 6. F_lambda integrand

Source function:

```text
_F_lambda_kernel
```

Source structure:

```text
s * (
  -u*h1*gamma_lambda
  + W*(h2*gamma_lambda*gamma_r + h1*gamma_rlambda)
)
```

Analytic identity:

```text
partial_lambda Phi_F
 = s[-u h' gamma_lambda
     + W(h'' gamma_lambda gamma_r + h' gamma_rlambda)].
```

## 7. F_rr integrand

Source function:

```text
_F_rr_kernel
```

Both source and analytic proof define

```text
A = h'' gamma_r^2 + h' gamma_rr.
```

The mapped expression is

```text
s * [
  -3u A
  + W(
      h''' gamma_r^3
      + 3h'' gamma_r gamma_rr
      + h' gamma_rrr
    )
].
```

## 8. F_rlambda integrand

Source function:

```text
_F_rlambda_kernel
```

Mapped expression:

```text
s * [
 -2u(h'' gamma_lambda gamma_r + h' gamma_rlambda)
 + W(
     h''' gamma_lambda gamma_r^2
     + 2h'' gamma_r gamma_rlambda
     + h'' gamma_lambda gamma_rr
     + h' gamma_rrlambda
   )
].
```

The independent formal rederivation checks this by differentiating an abstract
`H(gamma(r,lambda))` expression, rather than by importing the source implementation.

## 9. Fixed-domain integration

Source function:

```text
_rigorous_integral_2d
```

The integration bounds are

```text
theta: 0 -> pi/2
phi:   0 -> pi
```

and the final normalization is division by `pi`. This matches

```text
F(r,lambda) = (1/pi) integral_0^(pi/2) integral_0^pi Phi_F dphi dtheta.
```

The analytic proof establishes legitimacy of differentiating this real fixed-domain
integral on every compact parameter rectangle with `0<=r<1`, `lambda>=1` and finite upper
lambda bound.

The remaining machine obligation is different: validate that `acb.integral` returns a
rigorous enclosure of the mapped real integral for every approved point/box call and that
its branch/analytic flags cannot select an incompatible continuation.

## 10. Quotient layer

The prototype derivative kernel publishes only the five `F`-level quantities. The v9
adapter must form

```text
G_r       = F_r/r - F/r^2,
G_rr      = F_rr/r - 2 F_r/r^2 + 2 F/r^3,
G_rlambda = F_rlambda/r - F_lambda/r^2.
```

The analytic identities are proved. The final interval association and `expression_id`
remain open and must be frozen before source approval.

## 11. Audit classification

Current classification:

```text
analytic real-variable formulas: PROVED
prototype source/formula correspondence: STATICALLY MAPPED
independent formal rederivation source: PRESENT
independent rederivation execution artifact: PENDING
interval-library semantics: PENDING
source approval: NOT APPROVED
v9 freeze: NOT AUTHORIZED
```
