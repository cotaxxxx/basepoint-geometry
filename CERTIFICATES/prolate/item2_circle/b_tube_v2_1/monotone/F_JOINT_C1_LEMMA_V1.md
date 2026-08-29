# F_JOINT_C1 — lemma receipt candidate

LEMMA_ID=F_JOINT_C1
TARGET_CONTRACT=MONOTONE_TUBE_V1_1
EVIDENCE_CLASS=HUMAN_AUDIT_REQUIRED
JUDGE_SIGNATURE_STATUS=PENDING
BINDING_USE_AUTHORIZED=FALSE

## Claim

For the prolate fixed-domain stationary kernel used by the pinned production supply, the real-valued function

\[
F(r,\lambda)=\partial_r E_\lambda(r)
\]

is jointly `C^1` in `(r,lambda)` on an open neighborhood of every MONOTONE_TUBE_V1.1 tube rectangle and of the start/end join hulls used by that assembly.

In particular, on those neighborhoods both partial derivatives exist and are continuous, and the implicit-function theorem may be applied at any zero for which `F_r != 0`.

## Pinned mathematical supply

Production kernel:
`CERTIFICATES/prolate/item2_circle/vendor/prolate_circle_F_cleanroom.py`

Pinned production-kernel SHA256:
`77e7a93c594ba66ac7d98df29ec3c03107b0c63962a5aa60f8503559082c10ac`

The kernel uses the fixed angular domain
`theta in [0,pi/2]`, `phi in [0,2*pi]`, with

- `u = sin(theta) cos(phi)`
- `ell = sin(theta)^2 + lambda^2 cos(theta)^2`
- `w^2 = lambda^2 sin(theta)^2 + cos(theta)^2`
- `q = ell - 2 r u + r^2`
- `gamma = lambda (1-r u)/(w sqrt(q))`
- `h(c)=acos(c)^2`, evaluated through the regular hypergeometric representation used by `angle_data`.

## Audit argument

On the relevant real parameter region, `lambda>0` and `r<1`. Hence `w^2>0`. Also

`q = (r-u)^2 + (ell-u^2)`

and `ell-u^2` is nonnegative; on the compact fixed angular domain and on any compact parameter rectangle strictly inside `r<1, lambda>0`, the denominator supply used by the production kernel stays in its regular real branch. The apparent `h(c)` singularity at `c=1` is removed by the kernel's hypergeometric representation. Therefore the fixed-domain integrand defining `F`, together with its first real partial derivatives in `(r,lambda)`, is continuous on a compact angular domain and locally uniformly bounded on an open parameter neighborhood. Differentiation under the integral sign is therefore valid locally, giving joint `C^1` regularity.

This lemma is qualitative only. It supplies no sign, root count, numerical enclosure, or quantitative derivative bound.

## MONOTONE_TUBE interface

When and only when a Judge signature changes the receipt status to approved, MONOTONE_TUBE_V1.1 may consume exactly:

`F_JOINT_C1_PIN_PASS=TRUE`.

It may not infer `F_r<0`; that sign remains supplied by the separately checked `H_U>0` component plus the pinned sign-identification lemma.

## Nonclaims

- no Krawczyk contraction
- no Newton contraction
- no residual bound
- no uniqueness claim by itself
- no numerical H_U claim
- no endpoint-sign transport claim

STATUS=READY_FOR_JUDGE_AUDIT
