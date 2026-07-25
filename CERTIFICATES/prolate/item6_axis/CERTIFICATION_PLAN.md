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

The direct \(\mu=0\) limiting kernel vanishes, so it does not supply a fixed positive margin. Instead separate the logarithmic leading term in the odd-factor quotient:

\[
\widehat\Psi_{1/\mu}(s)
=
\log(1/\mu)\,\widehat A(s)
+
\widehat B(\mu,s),
\qquad
\widehat A(s)=3\pi\sqrt{1-s}.
\]

The certification target is therefore

\[
\log(1/\mu)\,3\pi\sqrt{1-s}
+
\widehat B(\mu,s)>0,
\]

with an analytic derivation of the leading coefficient and a uniform validated lower bound for the remainder \(\widehat B\) on the tail strip. Region T is joined to Region P before \(s=1\), where the leading coefficient vanishes.

At the center-tail corner, however,

\[
\widehat A(0)=3\pi>0,
\]

so the apparent \((w,\mu)\to(0,0)\) corner obstruction disappears after the odd factor \(w\) is removed. The remaining finite-\(\lambda\) domain is compact.

## Assembly D — dependency DAG

Every leaf must be one of:

- direct \(\Psi>0\);
- center-anchor transfer;
- pole-anchor transfer;
- parameter-direction transfer.

The certificate is accepted only if exact rational coverage has no gap and every transfer leaf is reachable from a direct or boundary anchor.
