# Prolate item 5 — boundary Maxwell transition

Status: **STAGE 5a CERTIFICATION IN PROGRESS**

Define

\[
D(\lambda)=E_\lambda(1,0)-E_\lambda(0,0).
\]

The target is the unique simple parameter `lambda_cross` at which the
equatorial boundary value and the center value coincide.

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

This lies strictly above the certified boundary-entry bracket
`[2.06538,2.06539]`: the stationary circle first enters through the boundary,
and the boundary/center critical values cross later.

## Why the original bracket was replaced

The original exploratory bracket `[3.43486,3.43488]` has endpoint sign margins
of only about `6e-7` and `8e-7`. Direct Arb integration of the regularized
boundary integral reached a radius near `5.3e-6` at practical settings. Thus
the narrow endpoint signs cannot be certified efficiently by this quadrature
architecture.

The proof is therefore split into two stages.

## Stage 5a — existence, uniqueness, and simplicity

Use the exact rational bracket

\[
I_5=[3.434,3.436]=[1717/500,1718/500].
\]

The Arb certificate must prove

- `D(3.434) > 0`;
- `D(3.436) < 0`;
- `D'([3.434,3.436]) < 0`.

The endpoint margins are approximately `6.25e-5` and `8.14e-5`, about one
order of magnitude larger than the measured boundary-integration radius.
Continuity and strict negativity of `D'` then prove one and only one simple
zero in `I_5`, with transverse boundary/center value crossing.

## Stage 5b — refined enclosure

At the exact midpoint

\[
m=3.435=687/200,
\]

compute

\[
N(m)=m-\frac{D(m)}{D'(I_5)}.
\]

Every zero in `I_5` is contained in `N(m)`. The expected Arb radius of `D(m)`
is about `5e-6`, so the Newton enclosure should have total width on the order
of `1.4e-4`, approximately

\[
\lambda_{\rm cross}\in[3.4348,3.4350].
\]

This refinement is recorded independently from the Stage 5a theorem. Later
runs may sharpen it without changing the existence/uniqueness proof.

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

The `phi` interval is split into four exact bands. Each band is validated
independently and the resulting Acb balls are added.

## Files

- `prolate_maxwell_symbolic_audit.py` — exact lambda-derivative audit.
- `prolate_maxwell_arb_certificate.py` — serial Arb/Acb reference certificate.
- `prolate_maxwell_component.py` — four-band production runner.
- `prolate_maxwell_combine.py` — Stage 5a/5b certificate assembler.
- `.github/workflows/prolate-item5-maxwell.yml` — clean GitHub Actions run.
