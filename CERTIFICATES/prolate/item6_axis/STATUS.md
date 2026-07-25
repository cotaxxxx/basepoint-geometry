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
- sampled center Hessian values through `lambda=1e6`: **POSITIVE / NON-CERTIFIED**
- tail normalization by the positive factor `mu*w`: **CORRECTED**
- logarithmic coefficient `3*pi*sqrt(1-s)`: **EXACT OUTER/LAURENT AUDIT PASSED**
- seven-point tail regression: **PASSED TO BETTER THAN FIVE SIGNIFICANT DIGITS / NON-CERTIFIED**
- center-cap interval proof: **PARTIAL — CENTER HESSIAN CERTIFIED ONLY ON `[1,10]`**
- center Hessian for `lambda>10`: **NOT CERTIFIED**
- finite-`w` center-cap remainder: **NOT STARTED**
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

Target:

\[
A_\lambda'(w)>0
\qquad (\lambda\ge1,\ 0<w<1).
\]

No finite-`w` center-cap theorem is claimed yet. No tail positivity theorem is claimed until the tail remainder is bounded uniformly and Region T is joined to the pole cap.
