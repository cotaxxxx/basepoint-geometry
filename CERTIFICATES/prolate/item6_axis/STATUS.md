# Item 6 status

## Final target

\[
\Psi_\lambda(w)=A_\lambda'(w)>0
\qquad(\lambda\ge1,\ 0<w<1).
\]

Item 6 as a whole remains **NOT CERTIFIED**.

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

Certified through `A_lambda''(v)>0` on `0<=v<=1/20`.

- 9 exact adjacent lambda blocks
- 6203 evaluations
- 3106 leaves
- terminal 0
- worst rigorous lower endpoint:
  `0.00012893655173892051421755471961636338423925380545573`

Records: `CENTER_CAP_CERTIFICATE_1_10.md`, `prolate_axis_center_cap_1_10_summary.json`.

### `P-BOUNDARY`

\[
\Phi(\lambda)=\lim_{w\to1^-}\Psi_\lambda(w)>0
\qquad(1\le\lambda\le100).
\]

- 16 exact adjacent lambda blocks
- 48 evaluations
- 32 leaves
- terminal 0
- worst rigorous lower endpoint:
  `0.0086853328086197058499308881284935494330221451543475`

Records: `POLE_BOUNDARY_CERTIFICATE_1_100.md`, `prolate_axis_pole_boundary_1_100_summary.json`.

## Exact signed-angle reduction

For `0<=w<1`, `-1<=c<=1`, and `lambda>0`, define

\[
N=1-wc,
\]

\[
X=\sqrt{1-c^2}\left(\lambda w-(\lambda-\lambda^{-1})c\right),
\]

\[
\delta_\lambda(c,w)=\arctan\frac{X}{N}.
\]

Because `N>0`,

\[
\arccos(C_\lambda(c,w))^2=\delta_\lambda(c,w)^2.
\]

The exact derivatives are

\[
\partial_w\delta
=
\frac{\lambda\sqrt{1-c^2}}
{1-c^2+\lambda^2(c-w)^2},
\]

\[
\partial_w^2\delta
=
\frac{2\lambda^3\sqrt{1-c^2}(c-w)}
{\left(1-c^2+\lambda^2(c-w)^2\right)^2}.
\]

Consequently the finite-domain Arb drivers no longer require the hypergeometric angle regularization. Exact identities are audited by `prolate_axis_signed_angle_symbolic_audit.py`.

## Finite domain `1<=lambda<=100`

The exact target decomposition is

\[
0<w\le\frac12,
\qquad
\frac12\le w\le\frac34,
\qquad
\frac34\le w<1.
\]

### Signed finite grid

`prolate_axis_signed_rectangle_arb.py` certifies either `Psi>0` or `A_second>0` on one exact rational rectangle. `prolate_axis_grid_combine.py` verifies:

- requested rectangle endpoints;
- expected block count;
- pairwise non-overlap;
- exact rational area coverage;
- every block status `CERTIFIED`;
- terminal 0.

The active signed finite grid contains:

- center: 24 rectangles, `A_second>0`, `0<=w<=1/2`;
- middle: 24 rectangles, `Psi>0`, `1/2<=w<=3/4`;
- pole: 40 rectangles, direct `Psi>0`, `3/4<=w<=63/64`.

The earlier `A_second<0` pole-transfer path is now supporting evidence only. Its `[4,5]` block ended with 332 `sign_not_certified` terminal boxes, no evaluation errors, and exact partition conservation. Independent point evaluation remains negative; this is interval dependency loss, not a certified counterexample. The formal pole path is therefore direct signed-angle `Psi>0`.

### Final pole layer

The layer

\[
\frac{63}{64}<w<1
\]

is split into:

1. 144 signed-angle dyadic rectangles covering
   `63/64<=w<=1-2^-24`, `1<=lambda<=100`;
2. a uniform modulus theorem on `1-2^-24<w<1`.

The modulus proof uses `u=1-w`, the inner chart `d=u^2 y^2`, the outer chart `d=2t^2`, and the projective corner chart `u=r sqrt(2)t`. The removable `1/N` factors in `C_w` and `C_ww` are cancelled algebraically before interval evaluation. Exact chart identities are audited by `prolate_axis_pole_modulus_symbolic_audit.py`.

## Tail `lambda>=100`

Set

\[
\mu=\lambda^{-1},
\qquad
H(\mu,w)=\frac{\Psi_{1/\mu}(w)}{\mu w}.
\]

The exact junction is

\[
\lambda_0=100,
\qquad
\mu_0=\frac1{100}.
\]

With

\[
P=(c-w)^2+\mu^2(1-c^2),
\qquad
S=1-c^2+\mu^2c^2,
\]

and the signed angle

\[
\delta=\arctan\frac{\sqrt{1-c^2}(w-c+\mu^2c)}{\mu(1-wc)},
\]

one has

\[
\partial_\mu\delta
=
\frac{\sqrt{1-c^2}(1-wc)(c-w+\mu^2c)}{PS}.
\]

After removing the constant angle term using `integral_{-1}^1 c dc=0`, both

\[
H(\mu,w)
\]

and

\[
M(\mu,w)=-\mu\,\partial_\mu H(\mu,w)
\]

have exact signed-atan kernels. These are audited by `prolate_axis_signed_tail_symbolic_audit.py` and evaluated by `prolate_axis_signed_tail_block_arb.py` with the correlated three-chart split

\[
[-1,w-4\mu],
\quad[w-4\mu,w+4\mu],
\quad[w+4\mu,1].
\]

The active signed tail grid targets:

\[
H>0
\quad\text{on}\quad
\frac1{200}\le\mu\le\frac1{100},
\quad
\frac1{20}\le w\le\frac34,
\]

and

\[
M>0
\quad\text{on}\quad
\frac1{400}\le\mu\le\frac1{200},
\quad
\frac1{20}\le w\le\frac34.
\]

The exact endpoint audits also give

\[
\lim_{\mu\to0}\frac{\Phi(1/\mu)}{\mu}=\frac{\pi^2}{2},
\]

and the logarithmic coefficient of `A_second/mu`:

\[
\frac{3\pi(1-2w^2)}{\sqrt{1-w^2}}.
\]

Thus the coefficient is positive on the center tail and negative on the pole tail. A uniform bounded-remainder certificate is still required before either overlap becomes a theorem.

## Active proof runs

The following new proof paths have been launched and are currently subject to GitHub runner capacity:

- signed-angle representative smoke certificates;
- signed finite grid;
- signed dyadic pole grid;
- signed tail `H/M` grid;
- audited pole modulus cover;
- ordinary exact audit workflow.

Heavy proof workflows are manual-only after their first launch. The ordinary audit workflow cancels stale same-PR audits.

## Remaining obligations

1. receive `CERTIFIED` combined outputs for the signed finite grid;
2. receive `CERTIFIED` combined output for the signed dyadic pole layer;
3. certify the uniform final-pole modulus inequality;
4. certify the positive signed-tail `H` interface;
5. certify `M>0` and extend it to `mu=0`;
6. certify center and pole tail overlaps through uniform remainder bounds;
7. assemble the exact dependency DAG with no gaps, no overlaps, exact endpoints, and terminal 0.

The final theorem must remain **NOT CERTIFIED** until every item above is closed.
