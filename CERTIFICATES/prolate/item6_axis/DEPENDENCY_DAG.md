# Item 6 exact dependency DAG

Status: **ASSEMBLY IN PROGRESS / FULL THEOREM NOT CERTIFIED**

## Target

\[
\mathcal D=\{(\lambda,w):\lambda\ge1,\ 0<w<1\},
\qquad
\Psi_\lambda(w)>0.
\]

The finite/tail interface is

\[
\lambda=100
\quad\Longleftrightarrow\quad
\mu=\frac1{100}.
\]

The finite `w` interfaces are

\[
w=\frac12,
\qquad
w=\frac34,
\qquad
w=\frac{63}{64},
\qquad
w=1-2^{-24}.
\]

## Exact representation layer

### `R-SIGNED`

For `0<=w<1`, the signed angle `delta` satisfies

\[
\arccos(C)^2=\delta^2,
\]

\[
\delta_w
=
\frac{\lambda\sqrt{1-c^2}}
{1-c^2+\lambda^2(c-w)^2},
\]

\[
\delta_{ww}
=
\frac{2\lambda^3\sqrt{1-c^2}(c-w)}
{\left(1-c^2+\lambda^2(c-w)^2\right)^2}.
\]

State: **EXACT FORMULAS IMPLEMENTED / CI PENDING**.

### `R-SIGNED-TAIL`

For `mu=1/lambda`, the scaled kernels `H` and `M=-mu*H_mu` have exact signed-atan formulas after the identity

\[
\int_{-1}^{1}c\,dc=0
\]

removes the constant `pi^2/4` angle term.

State: **EXACT FORMULAS IMPLEMENTED / CI PENDING**.

## Node table

| Node | Exact domain / boundary | Direct statement | Current state |
|---|---|---|---|
| `C-HESSIAN` | `1<=lambda<=100`, `w=0` | `Q_parallel>0` | **CERTIFIED** |
| `C-1` | `1<=lambda<=10`, `0<w<=1/20` | `Psi>0` from `A_second>0` | **CERTIFIED** |
| `F-CENTER` | `1<=lambda<=100`, `0<w<=1/2` | signed-angle `A_second>0` grid | **RUN QUEUED/ACTIVE** |
| `F-MIDDLE` | `1<=lambda<=100`, `1/2<=w<=3/4` | signed-angle direct `Psi>0` grid | **RUN QUEUED/ACTIVE** |
| `F-POLE` | `1<=lambda<=100`, `3/4<=w<=63/64` | signed-angle direct `Psi>0` grid | **RUN QUEUED/ACTIVE** |
| `P-BOUNDARY` | `1<=lambda<=100`, `w=1^-` | `Phi(lambda)>0` | **CERTIFIED** |
| `P-DYADIC` | `1<=lambda<=100`, `63/64<=w<=1-2^-24` | signed-angle direct `Psi>0` grid | **RUN QUEUED/ACTIVE** |
| `P-MODULUS` | `1<=lambda<=100`, `1-2^-24<w<1` | boundary floor minus uniform modulus loss | **RUN QUEUED/ACTIVE** |
| `T-INTERFACE` | `1/200<=mu<=1/100`, `1/20<=w<=3/4` | signed-angle `H>0` grid | **RUN QUEUED/ACTIVE** |
| `T-MONO` | `1/400<=mu<=1/200`, `1/20<=w<=3/4` | signed-angle `M>0` grid | **RUN QUEUED/ACTIVE** |
| `T-CENTER` | `0<mu<=1/100`, `0<w<=1/20` | center tail overlap | **NOT CERTIFIED** |
| `T-INTERIOR-0` | `0<mu<=1/200`, `1/20<=w<=3/4` | extend `M>0` to `mu=0` | **NOT CERTIFIED** |
| `T-POLE` | `0<mu<=1/100`, `3/4<w<1` | pole tail overlap | **NOT CERTIFIED** |

## Certified edges

### `C-HESSIAN -> C-1`

Certified by

\[
\frac{\Psi_\lambda(w)}w
=
\int_0^1A_\lambda''(tw)\,dt
\]

and the exact `A_second>0` certificate on

\[
0\le v\le\frac1{20},
\qquad
1\le\lambda\le10.
\]

### `P-BOUNDARY`

Independent direct boundary anchor:

\[
\Phi(\lambda)=\lim_{w\to1^-}\Psi_\lambda(w)>0
\qquad(1\le\lambda\le100).
\]

No finite pole-transfer edge is currently required by the formal path. The former `A_second<0` transfer is supporting work only because its `[4,5]` interval run retained terminal boxes.

## Intended finite assembly

Once the strict combined artifacts are certified,

\[
F\text{-CENTER}\cup F\text{-MIDDLE}\cup F\text{-POLE}
\]

covers

\[
1\le\lambda\le100,
\qquad
0<w\le\frac{63}{64}.
\]

Then

\[
P\text{-DYADIC}\cup P\text{-MODULUS}
\]

covers

\[
1\le\lambda\le100,
\qquad
\frac{63}{64}<w<1.
\]

All combiners must verify exact endpoints, pairwise non-overlap, exact rational area coverage, the expected file count, and terminal 0.

## Tail edges

For

\[
H(\mu,w)=\frac{\Psi_{1/\mu}(w)}{\mu w},
\]

`H>0` is equivalent to `Psi>0` for `mu,w>0`.

The candidate monotone edge is

\[
M(\mu,w)=-\mu\,\partial_\mu H(\mu,w)>0.
\]

If `T-INTERFACE` and `T-INTERIOR-0` are certified, then

\[
H(\mu,w)\ge H(1/200,w)>0
\qquad
\left(0<\mu\le\frac1{200},\ \frac1{20}\le w\le\frac34\right).
\]

The exact endpoint information currently available is

\[
\lim_{\mu\to0}\frac{\Phi(1/\mu)}{\mu}=\frac{\pi^2}{2},
\]

and

\[
\frac{A_{1/\mu}''(w)}\mu
\sim
\frac{3\pi(1-2w^2)}{\sqrt{1-w^2}}\log(1/\mu).
\]

These endpoint and coefficient identities are not by themselves proof nodes; uniform remainder bounds are required for `T-CENTER`, `T-INTERIOR-0`, and `T-POLE`.

## Acceptance rules

The final theorem may be marked `CERTIFIED` only when:

1. every node covering `D` is certified;
2. all exact interfaces are covered with no open gap;
3. every direct grid combiner reports the requested endpoints, exact non-overlapping coverage, expected file count, and terminal 0;
4. every transfer uses a certified anchor and a certified uniform inequality;
5. finite and tail regions meet exactly at `lambda=100`;
6. center and pole tail overlaps are explicit certified nodes;
7. no sampled, reference, running, formula-only, or incomplete result is used as a proof node.
