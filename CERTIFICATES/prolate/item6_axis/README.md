# Prolate item 6 — axial profile

Status: **FORMULA FROZEN / CENTER AND TAIL COEFFICIENT AUDITS PASSED / INTERVAL COVER PENDING**

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

## 5. Current audited evidence

### 5.1 General formula audit

- the exact one-dimensional energy and derivative formulas are frozen;
- the reflection laws are verified symbolically;
- direct evaluation of \(\Psi\) agrees with numerical differentiation of \(A\) to 30 digits at independent audit points;
- the reference quadrature is split at the moving layer \(c=w\), which is essential when \(\lambda\) is large.

### 5.2 Center Hessian audit

At \(w=0\), put

\[
L=1+(\lambda^2-1)c^2,
\qquad
W^2=\lambda^2(1-c^2)+c^2,
\qquad
C_0=\frac{\lambda}{\sqrt L\,W}.
\]

The exact derivatives \(C_{w,0}\) and \(C_{ww,0}\), and hence the exact integral kernel for

\[
Q_\parallel(\lambda)=A_\lambda''(0),
\]

are frozen in `FORMULA_AUDIT.md`. For the sphere,

\[
Q_\parallel(1)=\frac43
\]

is verified exactly. Floating-point samples are positive through \(\lambda=10^6\), but no interval theorem for all \(\lambda\) is claimed.

### 5.3 High-precision profile scout

Direct one-dimensional quadrature is positive at

\[
w=0.01,0.1,0.3,0.5,0.7,0.9,0.99
\]

for all tested values

\[
\lambda=1,2,2.0653823,3.4348684,4.7243834,10,100.
\]

These values are reference evidence only, not interval certification.

### 5.4 Exact tail coefficient audit

Set

\[
\mu=\lambda^{-1},
\qquad
s=w^2,
\qquad
H(\mu,s)=\frac{\Psi_{1/\mu}(\sqrt{s})}{\mu\sqrt{s}}.
\]

The unscaled derivative tends to zero; the correct asymptotic scale is \(\mu w\log(1/\mu)\). The formal outer/Laurent audit proves

\[
H(\mu,s)
=
3\pi\sqrt{1-s}\log(1/\mu)
+
\widehat B(\mu,s).
\]

Equivalently,

\[
\Psi_{1/\mu}(w)
=
\mu w\left[
3\pi\sqrt{1-w^2}\log(1/\mu)
+
\widehat B(\mu,w^2)
\right].
\]

The opposite \((c-w)^{-2}\) outer terms cancel, while the two \((c-w)^{-1}\) residues add to

\[
3\pi w\sqrt{1-w^2}.
\]

A seven-point decade-slope regression at \(\lambda=10^5,10^6\) agrees with \(3\pi\sqrt{1-w^2}\) to relative error below \(1.7\times10^{-6}\). The remainder \(\widehat B\) is not yet bounded uniformly.

## 6. Certificate decomposition

### 6.1 Region C — center cap

Use odd analyticity

\[
\Psi_\lambda(w)=w\widehat\Psi_\lambda(w^2)
\]

and certify \(\widehat\Psi_\lambda>0\) on \(0\le w\le w_0\). The exact kernel and sphere anchor are now frozen. The remaining work is:

- certify \(Q_\parallel(\lambda)>0\) for every \(\lambda\ge1\);
- enclose the finite-\(w\) remainder uniformly;
- join the compact and tail parameter regimes.

### 6.2 Region I — compact interior

Use validated one-dimensional integration on rational boxes

\[
w_0\le w\le1-\varepsilon,
\qquad
1\le\lambda\le\Lambda.
\]

Leaves may certify either \(\Psi>0\) directly or a derivative sign that transfers a certified anchor.

### 6.3 Region P — pole cap

At \(w\to1\) and \(c\to1\), use a half-angle or blow-up coordinate and preserve the correlation between

\[
1-wc,
\qquad
R^2_\lambda,
\qquad
1-C_\lambda^2.
\]

The pole-cap kernel must use inf-sup intervals and an algebraic `W`-type form before division.

### 6.4 Region T — unbounded aspect-ratio tail

Compactify by \(\mu=1/\lambda\), but do not use the vanishing unscaled \(\mu=0\) kernel as an anchor. Instead certify the rescaled bracket

\[
3\pi\sqrt{1-s}\log(1/\mu)+\widehat B(\mu,s)>0
\]

on a rational strip \(0<\mu\le\mu_0\). This requires a uniform validated lower bound for \(\widehat B\). Region T must overlap Region P before \(s=1\), where the logarithmic coefficient vanishes. At \(s=0\), the coefficient is \(3\pi>0\), so the center-tail corner is nondegenerate after division by the positive factor \(\mu w\).

### 6.5 Assembly D — mixed-label dependency DAG

Use the general anchored-cover theorem in

`01_GENERAL_THEORY/CERTIFICATION_ARCHITECTURE.md`.

Direct positivity, center-anchor propagation, pole-anchor propagation, and parameter-monotonic leaves may interleave. The final proof requires exact coverage and a dependency DAG with no unresolved component.

## 7. Acceptance conditions

The final item 6 package must contain:

- exact symbolic verification of the one-dimensional reduction and \(\partial_w C_\lambda\);
- a certified center-cap lower bound;
- a certified pole-cap lower bound;
- a certified compact interior cover;
- a certified \(\lambda\to\infty\) tail remainder bound;
- exact rational coverage with zero uncovered cells;
- zero unresolved dependency components;
- zero terminal failures;
- environment and SHA-256 manifests.

Only after all four regions and the dependency audit are joined may item 6 be marked **CERTIFIED**.

## 8. Audit files

- `prolate_axis_symbolic_audit.py` — exact derivative and symmetry audit.
- `prolate_axis_center_symbolic_audit.py` — exact center Hessian kernel and sphere endpoint.
- `prolate_axis_tail_symbolic_audit.py` — exact outer/Laurent logarithmic coefficient.
- `prolate_axis_reference.py` — non-certified full-profile scout.
- `prolate_axis_center_reference.py` — non-certified center Hessian scout.
- `prolate_axis_tail_reference.py` — non-certified seven-point tail regression.
- `CERTIFICATION_PLAN.md` — region interfaces and remaining proof obligations.
- `STATUS.md` — evidence-state ledger.
