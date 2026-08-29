# F_lambda transport lemma receipt v1

Status: `JUDGE_SIGNATURE_EXTERNAL / NOT_BINDING / NOT_PROMOTED`

LEMMA_ID=`F_LAMBDA_IS_LAMBDA_DERIVATIVE_OF_ROUTE_F_V1`  
LEMMA_CLASS=`HUMAN_AUDITED_MATHEMATICAL_PRECONDITION`  
SCOPE=`CURRENT_STRICT_INTERIOR_ENDPOINT_SCOPE`

## Statement

Fix a derived endpoint `r` with `0 < r < 1` and an exact compact lambda parent
`[lambda_L, lambda_R]`. Let `F(r,lambda)` denote the mathematical quantity
represented by the frozen B-LOCAL v2.2 ordinary/Duffy F route with its pinned,
lambda-independent normalization. Under the assumptions and audit obligations
below, `lambda -> F(r,lambda)` is C1 on the parent and

`d/dlambda F(r,lambda) = F_lambda(r,lambda)`

where the right-hand side is the mathematical integral represented by the
B-LOCAL v2.3 native `F_lambda` kernel. Therefore strict `F_lambda < 0` on the
parent transports the correct anchor sign monotonically across that parent.

This lemma is restricted to fixed strict-interior endpoints. The boundary case
`r=1` is outside this receipt and requires a separate lemma if needed.

## Inherited analytic assumption

`ANGLE_KERNEL_H_C2_ON_UNIT_INTERVAL=ASSUMED_INHERITED_FROM_FROZEN_ROUTE`

The angle kernel `h` used by the frozen route is C2 on `[0,1]`; hence `h1` and
`h2` used by the native derivative kernel are legitimate continuous derivatives
on the relevant gamma range. This is not a new v2.3 assumption: the frozen
route's second-order/H_U machinery already relies on the same regularity.

## Human-audit obligations

1. `FIXED_R_ENDPOINT`
   - Independent check: `PASS`.
   - The derived endpoint `r` is fixed before transport and is held constant
     while lambda varies over the reconstructed parent.

2. `FIXED_INTEGRATION_DOMAIN`
   - Independent check: `PASS`.
   - Ordinary chart domains and Duffy source domains are independent of lambda
     on the transport parent.

3. `C1_IN_LAMBDA`
   - Independent check: `PASS_CURRENT_STRICT_INTERIOR_SCOPE`.
   - On the compact parent x chart-domain product, `q >= qfloor > 0`,
     `w2 >= 1`, and `g2 >= 1`.
   - The Duffy corner variable satisfies `z = rho/sqrt(q) <= z_hi`, so the
     regularized integrand stays finite on the audited source domain.
   - Together with the inherited `h in C2([0,1])` assumption, every
     lambda-dependent factor in the regularized F integrand is C1.

4. `DERIVATIVE_IDENTITY`
   - Independent check: `PASS`.
   - Content-level symbolic re-audit confirms that the v2.3 ordinary and Duffy
     kernels are exactly the lambda derivative of the frozen F core.
   - Byte authority for the shared kernel is
     `26d3357132fee064293932df51208acd445e8bd14200d70862a2ee62ba4cc086`.

5. `DIFFERENTIATION_UNDER_INTEGRAL`
   - Independent check: `PASS_CURRENT_STRICT_INTERIOR_SCOPE`.
   - The integrand and its lambda derivative are continuous on a compact
     parameter-domain product and therefore uniformly bounded.
   - Standard differentiation under the integral sign applies.

6. `DUFFY_CHANGE_OF_VARIABLES`
   - Independent check: `PASS_INHERITED_AND_REAUDITED`.
   - The frozen Duffy Jacobian and regularized F-route identities are the same
     mathematical representation being differentiated by the v2.3 kernel.

7. `NORMALIZATION_LAMBDA_INDEPENDENT`
   - Independent check: `PASS`.
   - Mathematical normalization is lambda-independent.
   - The interval proof function `normalize_interval` likewise has no lambda
     input or lambda-dependent state.

8. `ENCLOSURE_MACHINERY_NOT_DIFFERENTIATED`
   - Independent check: `PASS`.
   - Floors, clamps, `z_hi`, subdivision choices, canonicalization and cover
     logic are enclosure machinery and are not mathematical differentiation
     targets.

## Independent audit status

`INDEPENDENT_CHECKER_VERDICT=PASS_CURRENT_STRICT_INTERIOR_SCOPE`  
`INDEPENDENT_CHECKER_ROLE=NOT_JUDGE`

The content-level symbolic audit and the explicit-NEG replay regression remain
separate supporting evidence. The replay established bit-identical enclosure,
evaluation count, cover tree and prior-log reproduction on all eight audited
cells, plus the three expected fail-closed negative-control codes.

## HEAD lineage note

`HEAD_LINEAGE=956ea04ba95b8f9fadfe332d0837c11f32a2d1b2 -> 66a1413259ef681c4af643b1251f1d2e108ff8e8 (explicit-NEG boundary contract hardening) -> 8acafde5515306e3624ad576722be62915045073 (regression replay hardening) -> 1b7ff66e991f31ca10f5b9978adfe12400f6bb81 (non-circular replay pinning) -> 0c066afba48f15913601f57df8a1a6f36fb44c83 (source-manifest repin) -> 70ce6b017c3daad82f68375ac60632e48bdc7d75 (explicit-NEG replay pin file only)`

## Nonclaims

- This receipt does not cover `r=1`.
- It does not prove Krawczyk contraction.
- It does not merge the separate existing `F_r<0` evidence into this lemma.
- It does not authorize binding use or promotion by itself.

## Judge signature

`JUDGE_SCOPE=CURRENT_STRICT_INTERIOR_ENDPOINT_SCOPE`

The human Judge signature is not written into this receipt. It is recorded
externally in `F_LAMBDA_TRANSPORT_LEMMA_V1_JUDGE_SIGNATURE.json` against the
exact SHA-256 of this receipt.

The gate `TRANSPORT_LEMMA_HUMAN_AUDIT=PASS_CURRENT_STRICT_INTERIOR_SCOPE` becomes
true only when the external signature file's `receipt_sha256` exactly matches
the SHA-256 of this receipt and its `judge_verdict` is `PASS`.

`BINDING_USE_AUTHORIZED=NO`
