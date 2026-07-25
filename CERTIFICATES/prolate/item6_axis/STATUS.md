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
- finite center cap `Psi_lambda(w)>0`, `1<=lambda<=10`, `0<w<=1/20`: **CERTIFIED**
- finite center-cap certificate: **9 BLOCKS / 6203 EVALUATIONS / 3106 LEAVES / TERMINAL 0 / EXACT ADJACENCY**
- finite center-cap extension `10<=lambda<=100`: **13-BLOCK ARB RUN ACTIVE**
- compact interior direct driver: **IMPLEMENTED WITH CORRELATION-PRESERVING MOVING-LAYER CHART**
- compact interior first tranche `1<=lambda<=10`, `1/20<=w<=3/4`: **9-BLOCK ARB RUN ACTIVE**
- pole-boundary symbolic reduction: **PASSED**
- pole-boundary anchor `Phi(lambda)>0`, `1<=lambda<=100`: **CERTIFIED**
- pole-boundary certificate: **16 BLOCKS / 48 EVALUATIONS / 32 LEAVES / TERMINAL 0 / EXACT ADJACENCY**
- finite pole transfer `A_lambda''(w)<0`, `3/4<=w<=63/64`, `1<=lambda<=100`: **16-BLOCK ARB RUN ACTIVE**
- final thin pole layer `63/64<w<1`: **BLOW-UP PROOF NOT YET CERTIFIED**
- tail normalization by the positive factor `mu*w`: **CORRECTED**
- logarithmic coefficient `3*pi*sqrt(1-s)`: **EXACT OUTER/LAURENT AUDIT PASSED**
- cancellation-regularized scaled tail kernel: **EXACT SYMBOLIC AUDIT PASSED**
- proposed tail remainder target on `mu<=1/100`, `w<=3/4`: **`Bhat>-7` / NON-CERTIFIED REFERENCE SUPPORT**
- first compact tail slab `1/200<=mu<=1/100`, `1/20<=w<=3/4`: **3-BLOCK ARB RUN ACTIVE**
- uniform lower bound for the tail remainder down to `mu=0`: **NOT CERTIFIED**
- dependency-DAG assembly: **NOT STARTED**
- final theorem: **NOT CERTIFIED**

## Certified compact center-Hessian statement

\[
Q_\parallel(\lambda)>0
\qquad(1\le\lambda\le100).
\]

The `[1,100]` certificate has 4135 evaluated boxes, 2117 exact-rational leaves, zero terminal boxes, and exact contiguous coverage. The worst certified leaf is

\[
\lambda\in[231/4,925/16]
\]

with

\[
Q_\parallel([231/4,925/16])
>
0.00020046868958001537682007201789783354707398439156606.
\]

Integrity data are recorded in `CENTER_EXTENDED_CERTIFICATE.md` and `prolate_axis_center_extended_arb_summary.json`.

## Certified finite center cap on `[1,10]`

The validated blockwise computation proves

\[
A_\lambda''(v)>0
\qquad
\left(0\le v\le\frac1{20},\ 1\le\lambda\le10\right),
\]

hence

\[
\boxed{
\Psi_\lambda(w)>0
\qquad
\left(1\le\lambda\le10,\ 0<w\le\frac1{20}\right).
}
\]

The certificate has 6203 evaluated boxes, 3106 leaves, zero terminal boxes, and exact adjacency across nine lambda blocks. The worst lower endpoint is

\[
A_\lambda''(v)
>
0.00012893655173892051421755471961636338423925380545573.
\]

Integrity data are recorded in `CENTER_CAP_CERTIFICATE_1_10.md` and `prolate_axis_center_cap_1_10_summary.json`.

## Certified pole-boundary anchor on `[1,100]`

Define

\[
\Phi(\lambda)=\lim_{w\to1^-}\Psi_\lambda(w).
\]

After factoring `d=1-c` and combining `N C_w` before taking the boundary limit, `Phi` is represented by a regular one-dimensional integral. Arb certification proves

\[
\boxed{
\Phi(\lambda)>0
\qquad(1\le\lambda\le100).
}
\]

The certificate has 16 exact adjacent blocks, 48 interval evaluations, 32 leaves, and zero terminal intervals. The worst lower endpoint occurs on `[1,9/8]` and is

\[
\Phi([1,9/8])
>
0.0086853328086197058499308881284935494330221451543475.
\]

Integrity data are recorded in `POLE_BOUNDARY_CERTIFICATE_1_100.md` and `prolate_axis_pole_boundary_1_100_summary.json`.

## Active finite-domain assembly

The compact interior target is

\[
\Psi_\lambda(w)>0
\qquad
\left(1\le\lambda\le10,\ \frac1{20}\le w\le\frac34\right).
\]

The integral is split at `c=w` and mapped to

\[
c=-1+(1+w)t,
\qquad
c=w+(1-w)t,
\]

preserving the correlation among `c-w`, `1-wc`, and `R^2`.

The pole transfer target is

\[
A_\lambda''(w)<0
\qquad
\left(1\le\lambda\le100,\ \frac34\le w\le\frac{63}{64}\right).
\]

Together with the certified boundary anchor this would imply

\[
\Psi_\lambda(w)\ge\Phi(\lambda)>0
\]

on that strip. The remaining final pole layer is `63/64<w<1`.

## Tail interface

The compact method stops at

\[
\lambda_0=100,
\qquad
\mu_0=1/100.
\]

For `lambda>=100`, use

\[
H(\mu,s)
=
\frac{\Psi_{1/\mu}(\sqrt{s})}{\mu\sqrt{s}}
=
3\pi\sqrt{1-s}\log(1/\mu)+\widehat B(\mu,s).
\]

The constant angle term `h(0)=pi^2/4` is removed exactly using `integral_{-1}^1 c dc=0`. The first compact tail slab currently under Arb evaluation is

\[
\frac1{200}\le\mu\le\frac1{100},
\qquad
\frac1{20}\le w\le\frac34.
\]

No theorem for `mu->0` is claimed until the logarithmic remainder is bounded uniformly.

Target:

\[
A_\lambda'(w)>0
\qquad(\lambda\ge1,\ 0<w<1).
\]
