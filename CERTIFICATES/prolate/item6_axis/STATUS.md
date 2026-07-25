# Item 6 status

- exact 1D energy reduction: **FROZEN**
- exact axial derivative formula: **FROZEN**
- reflection/evenness audit: **PASSED**
- independent high-precision scout: **POSITIVE ON ALL SAMPLED POINTS**
- moving-layer quadrature split at `c=w`: **IMPLEMENTED / NON-CERTIFIED**
- exact center Hessian kernel: **FROZEN / SYMBOLIC AUDIT PASSED**
- sphere endpoint `Q_parallel(1)=4/3`: **EXACTLY VERIFIED**
- compact center Hessian `Q_parallel(lambda)>0`, `1<=lambda<=10`: **CERTIFIED / ARCHIVED SUBCERTIFICATE**
- extended center Hessian `Q_parallel(lambda)>0`, `1<=lambda<=100`: **CERTIFIED**
- extended center certificate: **2117 LEAVES / 4135 EVALUATIONS / TERMINAL 0 / EXACT COVERAGE**
- finite/tail junction: **FIXED AT `lambda_0=100`, `mu_0=1/100`**
- sampled center Hessian values through `lambda=1e6`: **POSITIVE / NON-CERTIFIED**
- exact finite center-cap second-derivative kernel: **SYMBOLIC AUDIT IMPLEMENTED**
- previous monolithic finite center-cap run: **CANCELLED / NO THEOREM CLAIMED**
- blockwise finite center-cap run on `0<=w<=1/20`, `1<=lambda<=10`: **9 EXACT BLOCKS / RUNNING**
- blockwise assembly: **EXACT ADJACENCY + ZERO-TERMINAL COMBINER IMPLEMENTED**
- tail normalization by the positive factor `mu*w`: **CORRECTED**
- logarithmic coefficient `3*pi*sqrt(1-s)`: **EXACT OUTER/LAURENT AUDIT PASSED**
- seven-point tail regression: **PASSED TO BETTER THAN FIVE SIGNIFICANT DIGITS / NON-CERTIFIED**
- center-cap interval proof: **PARTIAL — HESSIAN `[1,100]` CERTIFIED; FINITE-`w` BLOCK RUN ACTIVE**
- compact interior interval cover: **NOT STARTED**
- pole-cap interval proof: **NOT STARTED**
- uniform lower bound for the tail remainder: **NOT STARTED**
- unbounded aspect-ratio tail: **PARTIAL — LEADING COEFFICIENT ONLY**
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

## Finite center-cap route

The finite center-cap implication is

\[
A_\lambda''(v)>0
\quad(0\le v\le1/20)
\]

which gives

\[
\frac{\Psi_\lambda(w)}{w}
=
\int_0^1 A_\lambda''(tw)\,dt>0
\quad(0<w\le1/20).
\]

The current `[1,10]` certificate is split into nine exact adjacent lambda blocks:

`[1,2]`, `[2,3]`, `[3,4]`, `[4,5]`, `[5,6]`, `[6,7]`, `[7,8]`, `[8,9]`, `[9,10]`.

Each block preserves an exact recursive-bisection partition invariant. The final combiner accepts only if every block is certified, every terminal count is zero, the `v` intervals agree, and the lambda intervals are exactly adjacent.

## Tail interface

The compact Hessian method stops at

\[
\lambda_0=100,
\qquad
\mu_0=1/100.
\]

For `lambda>=100`, the proof is assigned to the normalized tail quantity

\[
H(\mu,s)
=
\frac{\Psi_{1/\mu}(\sqrt{s})}{\mu\sqrt{s}}
=
3\pi\sqrt{1-s}\log(1/\mu)+\widehat B(\mu,s).
\]

Target:

\[
A_\lambda'(w)>0
\qquad(\lambda\ge1,\ 0<w<1).
\]

No tail positivity theorem is claimed until the tail remainder is bounded uniformly and Region T is joined to the pole cap.
