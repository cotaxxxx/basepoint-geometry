# Prolate item 5 — boundary Maxwell transition

Status: **CERTIFIED**

Define

\[
D(\lambda)=E_\lambda(1,0)-E_\lambda(0,0).
\]

## Certified theorem

On the exact rational interval

\[
I_5=[3.434,3.436]=[1717/500,1718/500],
\]

the validated Arb computation proves

\[
D(1717/500)>0,
\qquad
D(1718/500)<0,
\qquad
D'(I_5)<0.
\]

Therefore `D` has exactly one zero `lambda_cross` in `I_5`. Since the derivative is strictly negative throughout the interval, the zero is simple and the boundary Maxwell transition is transverse: the equatorial boundary value and center value exchange order across the root.

## Certified enclosures

| Condition | Rigorous enclosure | Result |
|---|---|---|
| `D(3.434)>0` | `[5.4940791170e-5, 7.0079587656e-5]` | certified |
| `D(3.436)<0` | `[-8.8965765817e-5, -7.3829624018e-5]` | certified |
| `D'(I5)<0` | `[-0.07314855250, -0.07076008154]` | certified |
| interval Newton | `N(3.435) subset I5` | certified |

One interval-Newton step gives

\[
\boxed{
\lambda_{\rm cross}
\in
[3.4347589497567105,\;3.4349743513998283]
}.
\]

The enclosure has width approximately `2.1540164e-4` and contains the non-certified reference value

\[
3.434868442866843.
\]

## Why the bracket was widened

The original exploratory bracket `[3.43486,3.43488]` had endpoint margins below `1e-6`, while the practical radius of the regularized boundary integral was about `5e-6`. It was therefore narrower than the validated quadrature resolution. The new bracket has endpoint margins of order `1e-5`, allowing all four required quantities to finish with `dps=30`, `tol=1e-6`, and depth `12`.

The four validated quantities completed in approximately 349 seconds total.

## Long-spheroid transition order

The three distinguished parameters are now certified and strictly ordered:

\[
\lambda_\partial\in[2.06538,2.06539]
<
\lambda_{\rm cross}\in[3.4347589497,3.4349743514]
<
\lambda_*\in[4.72438,4.72439].
\]

Thus the certified order is:

1. stationary-circle boundary entry;
2. boundary Maxwell crossing of the center and equatorial-boundary values;
3. loss of center stability.

## Archived evidence

- `certificate_item5_combined.json` — combined Stage 5a/5b certificate.
- `stage5a_state.json` — full endpoint, derivative, midpoint, timing, and settings records.
- `prolate_maxwell_reference.json` — non-certified high-precision reference.
- `prolate_maxwell_symbolic_audit.json` — symbolic derivative audit result.
- `certified_delivery/` — delivered driver/module copies, isolated from the PR's maintained production implementation.
- `DELIVERY_AUDIT.md` — member SHA-256 values, ingestion checks, ZIP hash record, and provenance note.

The actual uploaded delivery ZIP has SHA-256

`832c61f659998188cd231032e6cbb0c7f9be7cf63fb7403a156fb78b99a9957f`.

The different ZIP hash embedded inside the combined JSON is preserved as historical machine output and is explained in `DELIVERY_AUDIT.md`.
