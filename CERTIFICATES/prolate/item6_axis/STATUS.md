# Item 6 status

## Final target

\[
\Psi_\lambda(w)=A_\lambda'(w)>0
\qquad(\lambda\ge1,\ 0<w<1).
\]

Item 6 as a whole remains **NOT CERTIFIED**.

## Exact formulas and audits

- exact 1D energy reduction: **FROZEN**
- exact axial derivative formula: **FROZEN**
- reflection/evenness audit: **PASSED**
- moving-layer charts at `c=w`: **EXACTLY AUDITED**
- center Hessian and finite center-cap kernels: **EXACTLY AUDITED**
- pole-boundary reduction: **EXACTLY AUDITED**
- pole second-boundary reduction with `d=2t^2`: **FORMULA FIXED / LATEST CI PENDING**
- tail normalization by `mu*w`: **CORRECTED**
- logarithmic coefficient `3*pi*sqrt(1-s)`: **EXACT OUTER/LAURENT AUDIT PASSED**
- cancellation-regularized tail kernel: **EXACTLY AUDITED**
- tail log derivative `M=-mu*partial_mu H`: **FACTORED EXACT AUDIT IMPLEMENTED / LATEST CI PENDING**
- all current Arb drivers and combiners: **IN AUDIT COMPILE SET**

## Certified nodes

### `C-HESSIAN`

\[
Q_\parallel(\lambda)>0
\qquad(1\le\lambda\le100).
\]

- 4135 evaluations
- 2117 exact-rational leaves
- terminal 0
- exact coverage
- worst rigorous lower endpoint:
  `0.00020046868958001537682007201789783354707398439156606`

Records: `CENTER_EXTENDED_CERTIFICATE.md`, `prolate_axis_center_extended_arb_summary.json`.

### `C-1`

\[
\Psi_\lambda(w)>0
\qquad
\left(1\le\lambda\le10,\ 0<w\le\frac1{20}\right).
\]

Certified through

\[
A_\lambda''(v)>0
\qquad
\left(0\le v\le\frac1{20},\ 1\le\lambda\le10\right).
\]

- 9 exact adjacent lambda blocks
- 6203 evaluations
- 3106 leaves
- terminal 0
- worst rigorous lower endpoint:
  `0.00012893655173892051421755471961636338423925380545573`

Records: `CENTER_CAP_CERTIFICATE_1_10.md`, `prolate_axis_center_cap_1_10_summary.json`.

### `P-BOUNDARY`

\[
\Phi(\lambda)
=
\lim_{w\to1^-}\Psi_\lambda(w)>0
\qquad(1\le\lambda\le100).
\]

- 16 exact adjacent lambda blocks
- 48 evaluations
- 32 leaves
- terminal 0
- worst rigorous lower endpoint:
  `0.0086853328086197058499308881284935494330221451543475`

Records: `POLE_BOUNDARY_CERTIFICATE_1_100.md`, `prolate_axis_pole_boundary_1_100_summary.json`.

## Active finite-domain proof

The preferred finite decomposition is now

\[
0<w\le\frac12,
\qquad
\frac12\le w\le\frac34,
\qquad
\frac34\le w<1.
\]

### Center half

Target:

\[
A_\lambda''(w)>0
\qquad
\left(0\le w\le\frac12,\ 1\le\lambda\le100\right).
\]

This implies `Psi>0` on `0<w<=1/2`. The 16-block run is active; block `[2,3]` is already certified with terminal 0.

### Middle interior

Target:

\[
\Psi_\lambda(w)>0
\qquad
\left(\frac12\le w\le\frac34,\ 1\le\lambda\le100\right).
\]

The correlation-preserving direct driver and strict generic combiner are implemented. The heavy run is queued/active subject to runner capacity.

The earlier direct tranche

\[
1\le\lambda\le10,
\qquad
\frac1{20}\le w\le\frac34
\]

remains valid supporting work. Block `[1,2]` is certified with 7299 leaves and terminal 0.

### Pole transfer

The boundary anchor is certified. The active transfer target is

\[
A_\lambda''(w)<0
\qquad
\left(\frac34\le w\le\frac{63}{64},\ 1\le\lambda\le100\right).
\]

Together with `P-BOUNDARY`, this gives

\[
\Psi_\lambda(w)\ge\Phi(\lambda)>0.
\]

Block `[2,3]` is already certified with 1479 leaves and terminal 0. The remaining final pole layer is

\[
\frac{63}{64}<w<1.
\]

The boundary second-derivative anchor

\[
\Theta(\lambda)=\lim_{w\to1^-}A_\lambda''(w)<0
\]

has successful Arb blocks through the currently completed parameter ranges, but the final archived certificate must be rebound to the corrected positive-branch symbolic audit.

## Tail proof

The exact finite/tail junction is

\[
\lambda_0=100,
\qquad
\mu_0=1/100.
\]

Define

\[
H(\mu,w)=\frac{\Psi_{1/\mu}(w)}{\mu w}.
\]

### Positive interface slab

The first direct target is

\[
H(\mu,w)>0
\qquad
\left(
\frac1{200}\le\mu\le\frac1{100},
\frac1{20}\le w\le\frac34
\right).
\]

Both the original moving split and the faster three-chart split

\[
[-1,w-4\mu],
\quad[w-4\mu,w+4\mu],
\quad[w+4\mu,1]
\]

are implemented. The direct Arb runs are active.

### Log-parameter transfer

Define

\[
M(\mu,w)=-\mu\,\partial_\mu H(\mu,w).
\]

If `M>0`, then `H` increases when `mu` decreases. A first three-block certificate has been started on

\[
\frac1{400}\le\mu\le\frac1{200},
\qquad
\frac1{20}\le w\le\frac34.
\]

The intended unbounded-tail edge is

\[
H(\mu,w)\ge H(1/200,w)>0
\qquad(0<\mu\le1/200).
\]

A final blow-up estimate is still required to include `mu=0` and to certify the center and pole overlaps.

## Exact assembly

`DEPENDENCY_DAG.md` now records every proof node, transfer edge, exact interface, and acceptance condition. The full theorem may be marked `CERTIFIED` only after:

1. all finite center, middle, and pole nodes are certified;
2. the final thin pole layer is closed;
3. the positive tail interface and log-parameter transfer are certified;
4. center and pole tail overlaps are certified;
5. all strict combiners report requested endpoints, exact adjacency, non-overlap, exact coverage, and terminal 0.
