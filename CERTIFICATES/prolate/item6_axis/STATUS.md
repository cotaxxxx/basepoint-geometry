# Item 6 status

- exact 1D energy reduction: **FROZEN**
- exact axial derivative formula: **FROZEN**
- reflection/evenness audit: **PASSED**
- independent high-precision scout: **POSITIVE ON ALL SAMPLED POINTS**
- moving-layer quadrature split at `c=w`: **IMPLEMENTED / NON-CERTIFIED**
- exact center Hessian kernel: **FROZEN / SYMBOLIC AUDIT PASSED**
- sphere endpoint `Q_parallel(1)=4/3`: **EXACTLY VERIFIED**
- compact center Hessian `Q_parallel(lambda)>0`, `1<=lambda<=10`: **CERTIFIED**
- compact center certificate: **80 LEAVES / 151 EVALUATIONS / TERMINAL 0 / EXACT COVERAGE**
- center Hessian extension to `lambda=100`: **ARB COVER RUNNING**
- sampled center Hessian values through `lambda=1e6`: **POSITIVE / NON-CERTIFIED**
- exact finite center-cap second-derivative kernel: **SYMBOLIC AUDIT IMPLEMENTED**
- finite center-cap Arb driver on `0<=w<=1/20`, `1<=lambda<=10`: **RUNNING**
- tail normalization by the positive factor `mu*w`: **CORRECTED**
- logarithmic coefficient `3*pi*sqrt(1-s)`: **EXACT OUTER/LAURENT AUDIT PASSED**
- seven-point tail regression: **PASSED TO BETTER THAN FIVE SIGNIFICANT DIGITS / NON-CERTIFIED**
- center-cap interval proof: **PARTIAL — HESSIAN `[1,10]` CERTIFIED; FINITE-`w` COVER RUNNING**
- compact interior interval cover: **NOT STARTED**
- pole-cap interval proof: **NOT STARTED**
- uniform lower bound for the tail remainder: **NOT STARTED**
- unbounded aspect-ratio tail: **PARTIAL — LEADING COEFFICIENT ONLY**
- final theorem: **NOT CERTIFIED**

Certified compact statement:

\[
Q_\parallel(\lambda)>0
\qquad(1\le\lambda\le10).
\]

The worst certified leaf is `[79/8,10]`, with rigorous lower endpoint

\[
Q_\parallel([79/8,10])
>
0.48955236624670122276879181945444644042425864613135.
\]

Full integrity data are recorded in `CENTER_COMPACT_CERTIFICATE.md` and `prolate_axis_center_compact_arb_summary.json`.

The finite center-cap route is

\[
A_\lambda''(v)>0
\quad(0\le v\le1/20,\ 1\le\lambda\le10),
\]

which would imply

\[
\frac{\Psi_\lambda(w)}{w}
=
\int_0^1 A_\lambda''(tw)\,dt>0
\quad(0<w\le1/20).
\]

This derived statement is not marked certified until the two-parameter Arb artifact is reviewed.

Target:

\[
A_\lambda'(w)>0
\qquad (\lambda\ge1,\ 0<w<1).
\]

No tail positivity theorem is claimed until the tail remainder is bounded uniformly and Region T is joined to the pole cap.
