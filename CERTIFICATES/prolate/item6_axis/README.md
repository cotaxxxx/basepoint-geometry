# Prolate item 6 — axial profile

Status: **FORMULA FROZEN / NON-CERTIFIED SCOUT COMPLETED / ARB COVER PENDING**

## 1. Geometry and normalization

Let

\[
K_\lambda=\left\{(x,y,z):x^2+y^2+\frac{z^2}{\lambda^2}\le1\right\},
\qquad \lambda\ge1,
\]

and place the base point on the symmetry axis as

\[
p_{\lambda,w}=(0,0,\lambda w),
\qquad -1<w<1.
\]

Write

\[
A_\lambda(w)=E_{K_\lambda}(p_{\lambda,w}).
\]

The coordinate \(w\) is the normalized axial coordinate; \(w=\pm1\) are the two poles.

## 2. Exact one-dimensional reduction

Parametrize the unit sphere by \(u\in S^2\) and put \(c=u_3\). Under the linear map

\[
A=\operatorname{diag}(1,1,\lambda),
\]

the cone-volume measure based at \(p=A(0,0,w)\) becomes

\[
d\mu_{\lambda,w}(u)=\frac{1-wc}{4\pi}\,d\sigma(u).
\]

Define

\[
R^2_\lambda(c,w)=1-c^2+\lambda^2(c-w)^2,
\]

\[
S^2_\lambda(c)=1-c^2+\frac{c^2}{\lambda^2},
\]

and

\[
C_\lambda(c,w)
=
\frac{1-wc}
{\sqrt{R^2_\lambda(c,w)}\sqrt{S^2_\lambda(c)}}.
\]

Then

\[
\boxed{
A_\lambda(w)
=
\frac12\int_{-1}^{1}
(1-wc)\,h(C_\lambda(c,w))\,dc,
}
\]

where

\[
h(x)=\arccos^2x.
\]

This is a regular one-dimensional representation. The apparent singularities at \(c=\pm1\), where \(C=1\), are removable through the regularized derivatives of \(h\).

## 3. Axial derivative kernel

Differentiation gives

\[
\partial_w C_\lambda
=
C_\lambda
\left[
-\frac{c}{1-wc}
+\frac{\lambda^2(c-w)}{R^2_\lambda}
\right].
\]

Consequently

\[
\boxed{
\Psi_\lambda(w)
:=A_\lambda'(w)
=
\frac12\int_{-1}^{1}
\left\{
-c\,h(C_\lambda)
+(1-wc)h'(C_\lambda)\partial_w C_\lambda
\right\}dc.
}
\]

Reflection symmetry gives

\[
A_\lambda(-w)=A_\lambda(w),
\qquad
\Psi_\lambda(-w)=-\Psi_\lambda(w),
\qquad
\Psi_\lambda(0)=0.
\]

Near the center, the regular quantity is

\[
\widehat\Psi_\lambda(w)=\frac{\Psi_\lambda(w)}{w},
\]

with

\[
\widehat\Psi_\lambda(0)=A_\lambda''(0)=Q_\parallel(\lambda).
\]

## 4. Target theorem

The item 6 target is

\[
\boxed{
\Psi_\lambda(w)>0
\quad
\text{for every }\lambda\ge1,\ 0<w<1.
}
\]

If certified, it implies:

1. the axial profile is strictly increasing from the center to either pole;
2. the center is the unique stationary base point on the symmetry axis;
3. no axial saddle-node, pitchfork, boundary entry, or secondary axial branch occurs anywhere in the prolate family;
4. all noncentral stationary sets relevant to the prolate bifurcation are necessarily off-axis.

This statement is independent of item 5. Item 5 compares two critical values; item 6 excludes additional axial critical points.

## 5. Non-certified high-precision scout

Direct 50-digit one-dimensional quadrature gives the following values of \(\Psi_\lambda(0.1)\):

| \(\lambda\) | \(\Psi_\lambda(0.1)\) |
|---:|---:|
| 1 | 0.1324436038714950... |
| 2 | 0.2115695560407072... |
| 2.0653823 | 0.2133580320194856... |
| 3.4348684 | 0.2205933943123919... |
| 4.7243834 | 0.2093132053515003... |
| 10 | 0.1599849001029766... |
| 100 | 0.0373141897978720... |

Additional samples at

\[
w=0.01,0.1,0.3,0.5,0.7,0.9,0.99
\]

are positive for all tested values

\[
\lambda=1,2,2.0653823,3.4348684,4.7243834,10,100.
\]

These values are reference evidence only, not interval certification.

## 6. Proposed certificate decomposition

### 6.1 Center cap

Prove

\[
\widehat\Psi_\lambda(w)>0
\]

on \(0\le w\le w_0\), using the even analytic expansion and a certified positive lower bound for \(Q_\parallel(\lambda)\), together with a remainder enclosure.

### 6.2 Interior band

Use validated one-dimensional integration on rational boxes

\[
w_0\le w\le1-\varepsilon,
\qquad
1\le\lambda\le\Lambda.
\]

Leaves may certify either \(\Psi>0\) directly or a derivative sign that transfers a certified anchor.

### 6.3 Pole cap

At \(w\to1\) and \(c\to1\), use a half-angle or blow-up coordinate and preserve the correlation between

\[
1-wc,
\qquad
R^2_\lambda,
\qquad
1-C_\lambda^2.
\]

The pole-cap kernel must use inf-sup intervals and an algebraic `W`-type form before division.

### 6.4 Unbounded aspect-ratio tail

Compactify by

\[
\mu=\lambda^{-1}\in[0,1].
\]

Treat \(\mu=0\) as the needle limit, derive its limiting kernel, and certify a tail strip

\[
0\le\mu\le\mu_0.
\]

The remaining compact rectangle is handled by the interior certificate.

### 6.5 Mixed-label assembly

Use the general anchored-cover theorem in

`01_GENERAL_THEORY/CERTIFICATION_ARCHITECTURE.md`.

Direct positivity, center-anchor propagation, pole-anchor propagation, and parameter-monotonic leaves may interleave. The final proof requires exact coverage and a dependency DAG with no unresolved component.

## 7. Acceptance conditions

The final item 6 package must contain:

- exact symbolic verification of the one-dimensional reduction and \(\partial_w C_\lambda\);
- a certified center-cap lower bound;
- a certified pole-cap lower bound;
- a certified compact interior cover;
- a certified \(\lambda\to\infty\) tail;
- exact rational coverage with zero uncovered cells;
- zero unresolved dependency components;
- zero terminal failures;
- environment and SHA-256 manifests.

Only after all five regions are joined may item 6 be marked **CERTIFIED**.
