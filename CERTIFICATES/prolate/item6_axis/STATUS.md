# Item 6 status

- exact 1D energy reduction: **FROZEN**
- exact axial derivative formula: **FROZEN**
- reflection/evenness audit: **PASSED**
- independent high-precision scout: **POSITIVE ON ALL SAMPLED POINTS**
- moving-layer quadrature split at `c=w`: **IMPLEMENTED / SYMBOLIC CHART AUDIT PASSED**
- exact center Hessian kernel: **FROZEN / SYMBOLIC AUDIT PASSED**
- sphere endpoint `Q_parallel(1)=4/3`: **EXACTLY VERIFIED**
- compact center Hessian `Q_parallel(lambda)>0`, `1<=lambda<=10`: **CERTIFIED / ARCHIVED SUBCERTIFICATE**
- extended center Hessian `Q_parallel(lambda)>0`, `1<=lambda<=100`: **CERTIFIED**
- extended center certificate: **2117 LEAVES / 4135 EVALUATIONS / TERMINAL 0 / EXACT COVERAGE**
- finite/tail junction: **FIXED AT `lambda_0=100`, `mu_0=1/100`**
- sampled center Hessian values through `lambda=1e6`: **POSITIVE / NON-CERTIFIED**
- exact finite center-cap second-derivative kernel: **SYMBOLIC AUDIT PASSED**
- finite center cap `Psi_lambda(w)>0`, `1<=lambda<=10`, `0<w<=1/20`: **CERTIFIED**
- finite center-cap certificate: **9 BLOCKS / 6203 EVALUATIONS / 3106 LEAVES / TERMINAL 0 / EXACT ADJACENCY**
- compact interior direct driver: **IMPLEMENTED WITH CORRELATION-PRESERVING MOVING-LAYER CHART**
- compact interior first tranche `1<=lambda<=10`, `1/20<=w<=3/4`: **9-BLOCK ARB RUN ACTIVE**
- pole-cap interval proof: **NOT STARTED**
- tail normalization by the positive factor `mu*w`: **CORRECTED**
- logarithmic coefficient `3*pi*sqrt(1-s)`: **EXACT OUTER/LAURENT AUDIT PASSED**
- cancellation-regularized scaled tail kernel: **EXACT SYMBOLIC AUDIT IMPLEMENTED**
- proposed tail remainder target on `mu<=1/100`, `w<=3/4`: **`Bhat>-7` / NON-CERTIFIED REFERENCE SUPPORT**
- uniform lower bound for the tail remainder: **NOT CERTIFIED**
- unbounded aspect-ratio tail: **PARTIAL — LEADING COEFFICIENT + REGULARIZED KERNEL ONLY**
- dependency-DAG assembly: **NOT STARTED**
- final theorem: **NOT CERTIFIED**

## Certified compact center-Hessian statement

\[
Q_\parallel(\lambda)>0
\qquad(1\le\lambda\le100).
\]

The `[1,100]` certificate has:

- 4135 evaluated boxes;
- 2117 certified exact-rational leaves;
- zero terminal boxes;
- exact contiguous rational coverage.

The worst certified leaf is

\[
\lambda\in[231/4,925/16],
\]

with rigorous lower endpoint

\[
Q_\parallel([231/4,925/16])
>
0.00020046868958001537682007201789783354707398439156606.
\]

Full integrity data are recorded in `CENTER_EXTENDED_CERTIFICATE.md` and `prolate_axis_center_extended_arb_summary.json`. The earlier `[1,10]` certificate remains independently archived in `CENTER_COMPACT_CERTIFICATE.md`.

## Certified finite center cap on `[1,10]`

The validated blockwise computation proves

\[
A_\lambda''(v)>0
\qquad
\left(0\le v\le\frac1{20},\ 1\le\lambda\le10\right).
\]

Therefore

\[
\boxed{
\Psi_\lambda(w)>0
\qquad
\left(1\le\lambda\le10,\ 0<w\le\frac1{20}\right).
}
\]

The certificate consists of nine exact adjacent lambda blocks and has:

- 6203 evaluated boxes;
- 3106 certified leaves;
- zero terminal boxes;
- exact rational coverage on every block;
- exact adjacency from `lambda=1` to `lambda=10`.

The worst certified leaf is

\[
v\in[13/640,7/320],
\qquad
\lambda\in[153/16,77/8],
\]

with rigorous lower endpoint

\[
A_\lambda''(v)
>
0.00012893655173892051421755471961636338423925380545573.
\]

Integrity data are recorded in `CENTER_CAP_CERTIFICATE_1_10.md` and `prolate_axis_center_cap_1_10_summary.json`.

## Compact interior route

The first direct interior tranche is

\[
\Psi_\lambda(w)>0
\qquad
\left(1\le\lambda\le10,\ \frac1{20}\le w\le\frac34\right).
\]

The integral is split at the moving layer `c=w` and mapped to two fixed unit intervals:

\[
c=-1+(1+w)t,
\qquad
c=w+(1-w)t.
\]

This preserves the algebraic correlation among `c-w`, `1-wc`, and `R^2` before interval evaluation. Nine exact lambda-block jobs and an exact-adjacency combiner are implemented.

## Tail interface

The compact Hessian method stops at

\[
\lambda_0=100,
\qquad
\mu_0=1/100.
\]

For `lambda>=100`, the proof is assigned to

\[
H(\mu,s)
=
\frac{\Psi_{1/\mu}(\sqrt{s})}{\mu\sqrt{s}}
=
3\pi\sqrt{1-s}\log(1/\mu)+\widehat B(\mu,s).
\]

Before interval evaluation, the constant angle term `h(0)=pi^2/4` is removed exactly using `integral_{-1}^1 c dc=0`. A non-certified grid indicates that the practical target

\[
\widehat B(\mu,s)>-7
\]

on `0<mu<=1/100`, `0<w<=3/4` would leave a large positive main-term margin. No uniform remainder theorem is claimed yet.

Target:

\[
A_\lambda'(w)>0
\qquad(\lambda\ge1,\ 0<w<1).
\]
