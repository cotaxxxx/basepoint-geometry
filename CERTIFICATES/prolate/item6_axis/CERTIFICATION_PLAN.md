# Item 6 certification plan

The proof will be assembled from four analytic regions and one dependency audit.

## Region C — center cap

Use odd analyticity

\[
\Psi_\lambda(w)=w\widehat\Psi_\lambda(w^2)
\]

and certify \(\widehat\Psi_\lambda>0\) near \(w=0\). The first coefficient is the axial Hessian eigenvalue \(Q_\parallel(\lambda)\).

## Region I — compact interior

Validate the one-dimensional integral directly on rational \((w,\lambda)\)-boxes, using regularized angle derivatives and adaptive subdivision.

## Region P — pole cap

Introduce a blow-up coordinate near \((w,c)=(1,1)\). Preserve the algebraic correlation among \(N=1-wc\), \(R^2\), and \(1-C^2\) before any division. Use inf-sup arithmetic for wide positive factors.

## Region T — aspect-ratio tail

Set

\[
\mu=1/\lambda,
\qquad
s=w^2.
\]

The unscaled derivative tends to zero as \(\mu\to0\); its leading size is \(\mu\log(1/\mu)\). Remove both positive factors by defining, for \(0<s<1\),

\[
H(\mu,s)
=
\frac{\Psi_{1/\mu}(\sqrt{s})}{\mu\sqrt{s}},
\]

with the \(s=0\) value supplied by odd analyticity. The correct tail decomposition is

\[
H(\mu,s)
=
\log(1/\mu)\,\widehat A(s)
+
\widehat B(\mu,s),
\qquad
\widehat A(s)=3\pi\sqrt{1-s}.
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

The formal outer/Laurent audit proves the coefficient \(\widehat A\): the opposite \((c-w)^{-2}\) terms cancel in the two-sided matching, while the two \((c-w)^{-1}\) residues add to

\[
3\pi w\sqrt{1-w^2}.
\]

The remaining certification target is therefore

\[
\log(1/\mu)\,3\pi\sqrt{1-s}
+
\widehat B(\mu,s)>0,
\]

using a uniform validated lower bound for \(\widehat B\) on a rational tail strip. Region T must join Region P before \(s=1\), where the leading coefficient vanishes.

At the center-tail corner,

\[
\widehat A(0)=3\pi>0,
\]

so the apparent \((w,\mu)\to(0,0)\) obstruction disappears after division by the positive factor \(\mu w\). The remaining finite-\(\lambda\) domain is compact.

## Assembly D — dependency DAG

Every leaf must be one of:

- direct \(\Psi>0\);
- center-anchor transfer;
- pole-anchor transfer;
- parameter-direction transfer.

The certificate is accepted only if exact rational coverage has no gap and every transfer leaf is reachable from a direct or boundary anchor.
