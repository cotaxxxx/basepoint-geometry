# Item 3 Sweep v9 Prototype — Analytic Derivation

**Status:** `PROTOTYPE / NOT AUDITED / NOT APPROVED`  
**Issue:** #23  
**Base design head:** `b82c00f2f154f131e02e122efdb156592fa98070`

This document records the explicit formulas implemented by
`prolate_F_derivatives_cleanroom_v9.py`. It is an implementation derivation, not an
independent validation and not a production authorization.

## 1. Fixed-domain formula

Write

\[
s=\sin\theta,\qquad c=\cos\theta,\qquad
u=s\cos\phi,
\]

\[
\ell=s^2+\lambda^2c^2,\qquad
w^2=\lambda^2s^2+c^2,
\]

\[
q=\ell-2ru+r^2,\qquad W=1-ru,
\]

and

\[
\gamma=\frac{\lambda W}{w\sqrt q}.
\]

Let

\[
h(\gamma)=\arccos(\gamma)^2.
\]

After the symmetry reduction in \(\phi\), the energy derivative used by the Item 3
sweep is

\[
F(r,\lambda)
=\frac1\pi\int_0^{\pi/2}\int_0^\pi
s\left[-u\,h(\gamma)+W h'(\gamma)\gamma_r\right]
\,d\phi\,d\theta.
\]

The integration domain is fixed and independent of \(r,\lambda\).

## 2. Stable angle derivatives

Put

\[
z=\frac{1-\gamma}{2},\qquad
h=4z\,{}_2F_1\!\left(\frac12,\frac12;\frac32;z\right)^2,
\qquad x=-\frac h4,
\]

and

\[
S={}_0F_1\!\left(;\frac32;x\right),\quad
T={}_0F_1\!\left(;\frac52;x\right),\quad
U={}_0F_1\!\left(;\frac72;x\right).
\]

Then

\[
h'=-\frac2S,
\]

\[
h''=\frac23\frac{T}{S^3},
\]

\[
h'''=\frac{2}{15}\frac{U}{S^4}
-\frac23\frac{T^2}{S^5}.
\]

The removable endpoint values at \(\gamma=1\) are

\[
h'(1)=-2,\qquad h''(1)=\frac23,\qquad h'''(1)=-\frac8{15}.
\]

The formula for \(h'''\) follows by differentiating the hypergeometric expression for
\(h''\) with respect to \(h\), then multiplying by \(h'\).

## 3. \(r\)-derivatives of \(\gamma\)

Define

\[
B=\frac{\lambda}{w},\qquad d=r-u,
\]

\[
N=u(1-\ell)+r(u^2-1),\qquad N_r=u^2-1,
\]

\[
M=N_rq-3Nd.
\]

Then

\[
\gamma_r=B\,Nq^{-3/2},
\]

\[
\gamma_{rr}=B\,Mq^{-5/2}.
\]

Since

\[
M_r=-N_r d-3N,
\]

one obtains

\[
\gamma_{rrr}
=
B\left(M_rq-5Md\right)q^{-7/2}.
\]

## 4. \(\lambda\)- and mixed derivatives of \(\gamma\)

The logarithmic derivative of \(B\) is

\[
\frac{B_\lambda}{B}
=
\frac{c^2}{\lambda w^2}.
\]

Define

\[
b_\lambda=\frac{c^2}{\lambda w^2},
\qquad
q_\lambda=2\lambda c^2,
\qquad
N_\lambda=-2\lambda u c^2,
\]

\[
M_\lambda=N_rq_\lambda-3N_\lambda d.
\]

Then

\[
\gamma_\lambda
=
\gamma\left(b_\lambda-\frac{\lambda c^2}{q}\right),
\]

\[
\gamma_{r\lambda}
=
B\left(
N_\lambda+Nb_\lambda-\frac{3\lambda c^2N}{q}
\right)q^{-3/2},
\]

\[
\gamma_{rr\lambda}
=
B\left(
M_\lambda+Mb_\lambda-\frac{5\lambda c^2M}{q}
\right)q^{-5/2}.
\]

The diagnostic symbolic audit verifies these six geometry identities by exact
simplification against direct differentiation of \(\gamma\).

## 5. Five integrands

For readability write

\[
g_r=\gamma_r,\quad g_{rr}=\gamma_{rr},\quad
g_{rrr}=\gamma_{rrr},
\]

\[
g_\lambda=\gamma_\lambda,\quad
g_{r\lambda}=\gamma_{r\lambda},\quad
g_{rr\lambda}=\gamma_{rr\lambda}.
\]

The prototype publishes the following five fixed-domain integrands.

### 5.1 \(F\)

\[
\Phi_F
=
s\left[-u h+W h'g_r\right].
\]

### 5.2 \(F_r\)

\[
\Phi_{F_r}
=
s\left[
-2u h'g_r
+
W\left(h''g_r^2+h'g_{rr}\right)
\right].
\]

### 5.3 \(F_\lambda\)

\[
\Phi_{F_\lambda}
=
s\left[
-u h'g_\lambda
+
W\left(
h''g_\lambda g_r+h'g_{r\lambda}
\right)
\right].
\]

### 5.4 \(F_{rr}\)

Let

\[
A=h''g_r^2+h'g_{rr}.
\]

Then

\[
\Phi_{F_{rr}}
=
s\left[
-3uA
+
W\left(
h'''g_r^3
+3h''g_rg_{rr}
+h'g_{rrr}
\right)
\right].
\]

### 5.5 \(F_{r\lambda}\)

\[
\begin{aligned}
\Phi_{F_{r\lambda}}
=s\Bigl[
&-2u\left(h''g_\lambda g_r+h'g_{r\lambda}\right)\\
&+W\bigl(
h'''g_\lambda g_r^2
+2h''g_rg_{r\lambda}
+h''g_\lambda g_{rr}
+h'g_{rr\lambda}
\bigr)
\Bigr].
\end{aligned}
\]

Each published quantity is \(1/\pi\) times the integral of its corresponding
integrand over
\([0,\pi/2]\times[0,\pi]\).

## 6. Quotient quantities for the mean-value form

For

\[
G=\frac{F}{r},
\]

the adapter-level formulas remain

\[
G_r=\frac{F_r}{r}-\frac{F}{r^2},
\]

\[
G_{rr}
=
\frac{F_{rr}}{r}
-\frac{2F_r}{r^2}
+\frac{2F}{r^3},
\]

\[
G_{r\lambda}
=
\frac{F_{r\lambda}}{r}
-\frac{F_\lambda}{r^2}.
\]

The prototype mean-value core does not choose a production interval association for
these quotient expressions. That choice remains a design and sharpness obligation.

## 7. Conditions still requiring proof

The formulas above do not by themselves establish a production kernel. A future
independent validation must still prove, on the full machine domain:

1. \(q>0\), \(w>0\), and \(\lambda>0\);
2. the correct branch and range of \(\gamma\);
3. uniform integrable majorants for all five integrands;
4. differentiation under the integral sign through the required orders;
5. validity of mixed differentiation;
6. endpoint and removable-singularity handling for interval boxes;
7. independent formula rederivation;
8. rigorous enclosure behavior of the actual `acb.integral` implementation.

## 8. Diagnostic results

The implementation cycle performed three non-normative checks:

- Python syntax compilation: PASS;
- exact SymPy simplification of all six \(\gamma\)-derivative formulas and the
  \(h'''(1)\) limit: PASS;
- midpoint-grid finite-difference comparison at three representative
  \((r,\lambda)\) points: PASS.

Finite differences and symbolic algebra are explicitly `DIAGNOSTIC_ONLY`. They can
detect transcription errors but cannot approve the kernel.
