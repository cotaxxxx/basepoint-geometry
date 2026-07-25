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

Set \(\mu=1/\lambda\). Derive the \(\mu=0\) limiting kernel and certify a strip \(0\le\mu\le\mu_0\). The remainder is compact.

## Assembly D — dependency DAG

Every leaf must be one of:

- direct \(\Psi>0\);
- center-anchor transfer;
- pole-anchor transfer;
- parameter-direction transfer.

The certificate is accepted only if exact rational coverage has no gap and every transfer leaf is reachable from a direct or boundary anchor.
