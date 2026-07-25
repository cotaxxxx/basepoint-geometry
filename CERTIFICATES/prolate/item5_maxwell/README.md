# Prolate item 5 — boundary Maxwell transition

Status: **CERTIFICATION IN PROGRESS**

Define

\[
D(\lambda)=E_\lambda(1,0)-E_\lambda(0,0).
\]

The target is a unique simple zero `lambda_cross` at which the equatorial
boundary value and the center value coincide.

## Non-certified reference

Tensor Gauss–Legendre quadrature gives

\[
\lambda_{\rm cross}\approx3.43486844286684,
\]

\[
E_{\lambda_{\rm cross}}(1,0)
=E_{\lambda_{\rm cross}}(0,0)
\approx0.64287764254486,
\]

\[
D'(\lambda_{\rm cross})\approx-0.07195990796855.
\]

The proposed exact rational certification bracket is

\[
I_{\rm cross}=[3.43486,3.43488].
\]

This lies strictly above the certified boundary-entry bracket
`[2.06538,2.06539]`: the stationary circle first enters through the boundary,
and the boundary/center critical values cross later.

## Integral structure

The center value is one-dimensional:

\[
E_\lambda(0,0)=\int_0^1
\arccos^2\!\left(
\frac{\lambda}{\sqrt{\ell w^2}}
\right)dx,
\]

\[
\ell=1+(\lambda^2-1)x^2,
\qquad
w^2=\lambda^2(1-x^2)+x^2.
\]

The boundary value is a regularized two-dimensional quarter-sphere integral.
Using the boundary-entry half-angle chart,

\[
E_\lambda(1,0)
=\frac8\pi\int_0^{\pi/2}\int_0^1
 t^3\arccos^2(c(t,\phi,\lambda))\,dt\,d\phi.
\]

Thus the earlier description as “two one-dimensional integrals” is corrected:
item 5 uses one validated 1D integral and one validated regular 2D integral,
plus their exact lambda derivatives.

## Acceptance conditions

The Arb certificate must prove

- `D(3.43486) > 0`;
- `D(3.43488) < 0`;
- `D'([3.43486,3.43488]) < 0`;
- the interval-Newton image based at `3.43487` lies strictly inside the bracket.

These conditions imply existence, uniqueness, simplicity, and transverse
boundary/center value crossing.

## Files

- `prolate_maxwell_symbolic_audit.py` — exact lambda-derivative audit.
- `prolate_maxwell_arb_certificate.py` — Arb/Acb certificate target.
- `.github/workflows/prolate-item5-maxwell.yml` — clean GitHub Actions run.
