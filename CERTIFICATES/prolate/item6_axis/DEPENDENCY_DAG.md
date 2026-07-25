# Item 6 exact dependency DAG

Status: **ASSEMBLY IN PROGRESS / FULL THEOREM NOT CERTIFIED**

## Target domain

\[
\mathcal D
=
\{(\lambda,w):\lambda\ge1,\ 0<w<1\}.
\]

The target is

\[
\Psi_\lambda(w)>0
\qquad((\lambda,w)\in\mathcal D).
\]

The assembly uses the exact interfaces

\[
w_0=\frac1{20},
\qquad
w_1=\frac34,
\qquad
w_2=\frac{63}{64},
\]

and

\[
\lambda_1=10,
\qquad
\lambda_2=100,
\qquad
\mu_2=\frac1{100},
\qquad
\mu_3=\frac1{200}.
\]

## Node table

| Node | Exact domain / boundary | Label | Current state |
|---|---|---|---|
| `C-HESSIAN` | `1<=lambda<=100`, `w=0` | direct positive Hessian anchor | **CERTIFIED** |
| `C-1` | `1<=lambda<=10`, `0<w<=1/20` | center transfer by `A''>0` | **CERTIFIED** |
| `C-2` | `10<=lambda<=100`, `0<w<=1/20` | center transfer by `A''>0` | **RUN ACTIVE** |
| `I-1` | `1<=lambda<=10`, `1/20<=w<=3/4` | direct `Psi>0` | **RUN ACTIVE** |
| `I-2` | `10<=lambda<=100`, `1/20<=w<=3/4` | direct or parameter transfer | **NOT STARTED** |
| `P-BOUNDARY` | `1<=lambda<=100`, `w=1^-` | direct positive boundary anchor | **CERTIFIED** |
| `P-SECOND` | `1<=lambda<=100`, `w=1^-` | negative boundary second derivative | **RUN / AUDIT REBINDING** |
| `P-1` | `1<=lambda<=100`, `3/4<=w<=63/64` | transfer from boundary by `A''<0` | **RUN ACTIVE** |
| `P-2` | `1<=lambda<=100`, `63/64<w<1` | blow-up transfer | **NOT CERTIFIED** |
| `T-INTERFACE` | `1/200<=mu<=1/100`, `1/20<=w<=3/4` | direct scaled `H>0` | **RUN ACTIVE** |
| `T-CENTER` | `0<mu<=1/100`, `0<w<=1/20` | tail center overlap | **NOT CERTIFIED** |
| `T-INTERIOR` | `0<mu<=1/200`, `1/20<=w<=3/4` | log-parameter transfer | **FORMULA AUDIT / NOT CERTIFIED** |
| `T-POLE` | `0<mu<=1/100`, `3/4<w<1` | tail pole overlap | **NOT CERTIFIED** |

## Certified edges

### Center anchor to finite center cap

`C-HESSIAN -> C-1` is certified by

\[
\frac{\Psi_\lambda(w)}w
=
\int_0^1A_\lambda''(tw)\,dt
\]

and the certificate

\[
A_\lambda''(v)>0
\quad
(0\le v\le1/20,\ 1\le\lambda\le10).
\]

### Pole boundary definition

`P-BOUNDARY` is an independent direct anchor:

\[
\Phi(\lambda)
=
\lim_{w\to1^-}\Psi_\lambda(w)>0
\quad(1\le\lambda\le100).
\]

The intended transfer edge `P-BOUNDARY -> P-1` is

\[
A_\lambda''(w)<0
\Longrightarrow
\Psi_\lambda(w)\ge\Phi(\lambda)>0.
\]

This edge is not marked certified until the finite pole-transfer artifact is complete.

## Tail edges

For

\[
H(\mu,w)=\frac{\Psi_{1/\mu}(w)}{\mu w},
\]

positivity of `H` is equivalent to positivity of `Psi` for `mu,w>0`.

The interface edge from finite lambda to the tail is fixed exactly at

\[
\lambda=100
\quad\Longleftrightarrow\quad
\mu=1/100.
\]

The candidate unbounded transfer is

\[
M(\mu,w)
=-\mu\,\partial_\mu H(\mu,w)>0.
\]

If `T-INTERFACE` and `M>0` on `0<mu<=1/200` are certified, then

\[
H(\mu,w)
\ge
H(1/200,w)>0
\qquad(0<\mu\le1/200),
\]

closing the unbounded interior tail without a separate numerical truncation.

## Acceptance rules

The full item 6 theorem may be marked `CERTIFIED` only when:

1. every node covering `D` is certified;
2. all exact interfaces are covered from both sides or by a closed endpoint convention;
3. every transfer edge points to a certified direct or boundary anchor;
4. every block combiner reports exact rational adjacency and zero terminal boxes;
5. the union of finite and tail regions has no gap at `lambda=100`;
6. the center and pole tail overlaps are explicitly certified;
7. no statement labelled reference, sampled, running, or formula-only is used as a proof node.
