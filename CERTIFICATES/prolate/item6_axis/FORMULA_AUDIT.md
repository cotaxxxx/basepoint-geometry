# Item 6 formula audit

## Exact identities

For

\[
N=1-wc,
\quad
R^2=1-c^2+\lambda^2(c-w)^2,
\quad
S^2=1-c^2+c^2/\lambda^2,
\quad
C=N/(RS),
\]

symbolic differentiation gives

\[
\partial_w C
=C\left(-\frac{c}{N}+\frac{\lambda^2(c-w)}{R^2}\right).
\]

The simultaneous reflection

\[
(c,w)\mapsto(-c,-w)
\]

leaves \(N,R^2,S^2,C\) invariant. After changing the integration variable
\(c\mapsto-c\), this proves

\[
A_\lambda(-w)=A_\lambda(w),
\qquad
\Psi_\lambda(-w)=-\Psi_\lambda(w).
\]

## Independent numerical differentiation

At 30 decimal digits, direct evaluation of the integral formula for
\(\Psi_\lambda(w)\) agrees with numerical differentiation of
\(A_\lambda(w)\) at the following audit points:

| \(\lambda\) | \(w\) | absolute difference |
|---:|---:|---:|
| 2 | 0.4 | 0 at working precision |
| 4.7243834 | 0.6 | 0 at working precision |
| 10 | 0.8 | \(1.87\times10^{-30}\) |

This is an implementation audit only. It does not prove positivity on a box.

## Non-certified tail reference

Exploratory high-aspect-ratio calculations indicate that the leading logarithmic coefficient of the axial derivative is

\[
A(w)=3\pi w\sqrt{1-w^2}.
\]

Equivalently, after writing

\[
\Psi_\lambda(w)=w\widehat\Psi_\lambda(w^2),
\qquad
s=w^2,
\]

the corresponding quotient coefficient is

\[
\widehat A(s)=3\pi\sqrt{1-s}.
\]

The formula agrees with numerical data at seven audit points to approximately five significant digits. It is recorded only as a reference target for the Region T implementation: the analytic derivation and interval certification are still pending.

In particular,

\[
\widehat A(0)=3\pi>0,
\]

which indicates that the center-tail corner remains nondegenerate after removing the odd factor \(w\). No theorem is claimed from this numerical agreement.
