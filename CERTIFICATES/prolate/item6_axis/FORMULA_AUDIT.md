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
