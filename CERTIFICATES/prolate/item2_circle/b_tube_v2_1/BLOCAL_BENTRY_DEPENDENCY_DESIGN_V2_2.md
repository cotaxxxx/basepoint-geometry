# B-LOCAL v2.2 — explicit boundary-strip regularization for L1

**Status: DRAFT FOR CHAT AUDIT.** This document is design-only. It changes no implementation source, run configuration, dependency pin, workflow, tag, certificate, or prior incident record. v2.1 remains immutable incident history. A v2.2 mathematical run remains unauthorized until a later explicit tag approval.

## 0. Framing and preserved incident evidence

The v2.1 design requires L1 on the closed domain `0 <= u <= u_max`, with `u = 1-r`, while the pinned production kernel evaluates `dFdr_arb` over Arb boxes that may include `r = 1`. At the angular corner `theta = pi/2`, `phi = 0`, `r = 1`, one has `q = 0` and `N = 0`, so the direct interval representation of `gamma_r = (lambda/w) N/(q sqrt(q))` encounters an indeterminate `0/0` form. The v2.1 Arb-to-dyadic adapter correctly rejects the resulting non-finite Arb ball fail-closed.

This patch is not an adapter relaxation and not a retroactive modification of v2.1. It makes the boundary regularization, already implicit in the closed-domain mathematical statement, explicit in the proof architecture.

The v2.1 run tag, its source commit, and run #1 failure log are retained unchanged as incident evidence. They are never moved, deleted, or reinterpreted as a certificate.

## 1. Established mathematical facts admitted by v2.2

At `r = 1`, with

`W = 1 - r u`,
`q = ell - 2 r u + r^2`,
`N = u(1-ell) + r(u^2-1)`,

v2.2 may use the exact identity

`N = -q + W(ell-u)`.

Near the angular corner, writing `c = cos(theta)` and `rho` for a planar distance equivalent to `(phi^2 + c^2)^(1/2)`, one has

`q = O(rho^2)`,
`W = O(rho^2)`,
`ell-u = O(rho^2)`.

Hence

`N = -q + O(rho^4) = O(rho^2)`,
`gamma_r = O(1/rho)`.

Further, at `r = 1`,

`N_r = u^2 - 1 = O(rho^2)`,
`r-u = O(rho^2)`,

so

`gamma_rr = O(1/rho)`.

The actual L1 integrand in `dFdr_arb` is

`sin(theta) * [-2 u h'(gamma) gamma_r + W(h''(gamma) gamma_r^2 + h'(gamma) gamma_rr)]`.

Consequently

`W gamma_r^2 = O(1)`,
`W gamma_rr = O(rho)`,

and the full L1 integrand is `O(1/rho)`. With two-dimensional angular measure `O(rho d rho)`, the improper integral defining `F_r(1,lambda)` is finite.

A non-rigorous floating finite-difference probe suggesting `-F_r(1,lambda_plus)` is positive with substantial margin is diagnostic only and is forbidden as certificate evidence.

## 2. Closed-domain decomposition of L1

A face-only split is prohibited. A finite proof system based on closed dyadic boxes cannot cover `(0,u_max]` exactly without either reintroducing `u=0` into an interior box or leaving a gap.

Therefore v2.2 introduces one exact positive dyadic cut

`u_cut = 2^(-j)`

with `j` fixed in the v2.2 run configuration before execution.

L1 is certified as the union of exactly two closed regions:

### L1-BOUNDARY-STRIP

`0 <= u <= u_cut`,
`-s_neg <= s <= s_start`.

This region is handled only by the new regularized boundary-strip route.

### L1-INTERIOR

`u_cut <= u <= u_max`,
`-s_neg <= s <= s_start`.

This region uses the existing pinned `dFdr_arb` interior evaluation path and the existing Arb-to-dyadic adapter. The mathematical kernel bytes are unchanged.

The two regions may overlap only on the shared face `u = u_cut`. The checker must reconstruct both regions exactly and verify that their closed union is exactly the original L1 rectangle with no gap or unauthorized enlargement.

## 3. Normative boundary-strip route

The v2.2 boundary-strip lemma ID is

`BLOCAL_R1_BOUNDARY_REGULARIZATION_V1`.

Its evaluation route ID must be distinct from the existing `R1_DIRECT_PINNED_F_ARB_V1` route used for L3.

The normative regularization method is **polar regularization after symbolic cancellation**. Explicit-majorant estimates may be implemented only as a negative-control cross-check and may never be used as a silent fallback.

### 3.1 Angular decomposition

For every proof box in the boundary strip, the angular domain is split into:

1. a singular patch `P_eps` around `theta = pi/2`, `phi = 0`, where `eps` is one exact dyadic value fixed in config; and
2. the regular complement `D \ P_eps`.

On the regular complement, a strict exact lower bound `q_min(eps,u_box,s_box) > 0` must be established before any direct interval evaluation is accepted.

### 3.2 Symbolic regularization requirement

The boundary-strip implementation must work with the **full `dFdr` integrand**, not with `gamma_r` alone.

Inside `P_eps`, it must first introduce a polar-type local coordinate system `(rho, alpha)` for the corner and multiply by the Jacobian factor. The implementation must then algebraically regularize the Jacobian-weighted full integrand so that the expression actually handed to Arb has a finite extension at `rho = 0`.

It is not sufficient merely to substitute polar coordinates while retaining a literal `0/0` subexpression at `rho = 0`.

The derivation must explicitly use the identity

`N = -q + W(ell-u)`

or an algebraically equivalent exact form, and must expose enough intermediate expressions for independent symbolic audit.

### 3.3 Pinned-kernel relationship

The existing pinned kernel file remains byte-identical and remains the sole source for the mathematical formula definitions used by v2.2.

The new boundary-strip module may not claim that an independently rewritten formula is the old kernel merely because it is mathematically equivalent. Instead, its provenance record must state exactly which pinned formula expressions are being regularized, and the symbolic audit must verify equality between the regularized expression and the pinned full `dFdr` integrand wherever the original expression is finite.

No alternate boundary kernel, `1-epsilon` substitution, exception-driven retry, decimal-string path, binary float, or unpinned fallback is allowed.

## 4. Required boundary-strip conclusion

Finiteness alone is not a proof obligation.

For every attempted candidate, the boundary-strip route must certify the uniform strict inequality

`H_u(u,s) = -F_r(1-u, lambda_plus+s) > 0`

for **all**

`0 <= u <= u_cut`,
`-s_neg <= s <= s_start`.

The route must produce a canonical finite dyadic enclosure

`[lo, hi]`

for each required proof tile, with exact `lo > 0` after conversion to the existing canonical dyadic interval schema. Point sampling, `lo = 0`, approximate positivity, or a qualitative continuity argument is insufficient.

If any required enclosure is non-finite or fails to separate strictly from zero, L1-BOUNDARY-STRIP is `INDETERMINATE` and the candidate fails closed.

## 5. Checker and record obligations

L1 PASS requires both:

1. a complete L1-INTERIOR closed tiling over `[u_cut,u_max] x [-s_neg,s_start]`; and
2. a complete L1-BOUNDARY-STRIP certificate over `[0,u_cut] x [-s_neg,s_start]`.

The boundary-strip records must include at least:

- lemma ID;
- route ID;
- exact `u_cut`;
- exact `eps`;
- exact global `u` and `s` bounds;
- singular-patch enclosure records;
- regular-region enclosure records;
- the proved positive `q_min` values used on regular regions;
- the combined enclosure for every boundary-strip proof tile;
- the final strict dyadic lower bounds;
- the pinned kernel source SHA-256;
- the boundary-strip source SHA-256;
- the symbolic-audit source SHA-256;
- `certified` state and first fail-closed reason when false.

The checker must independently reconstruct the original L1 rectangle and prove exact closed-union coverage by the two subdomains. Interior tiles alone can never imply L1 PASS.

Mandatory negative controls include:

- interior PASS + boundary-strip record missing => L1 FAIL;
- boundary-strip PASS + interior record missing => L1 FAIL;
- `u_cut <= 0` or `u_cut > u_max` => configuration rejection;
- a gap or overlap other than the exact shared face `u=u_cut` => checker rejection;
- non-finite Arb presented to the canonical adapter => fail closed;
- boundary-strip lower bound `lo <= 0` => candidate not accepted.

## 6. Invariants preserved from v2.1

Unless a later audited implementation step explicitly reports otherwise, the following remain unchanged:

- `ARB_TO_CANONICAL_DYADIC_INTERVAL_V1`;
- pinned clean-room kernel bytes and SHA-256;
- `lambda_plus`;
- `s_neg`;
- lambda candidate order;
- `u_max` candidate order;
- precision policy;
- Stage-1 dependency;
- L2 and L3 mathematical obligations;
- tag-only execution authorization;
- `calibration_auto_start = false`;
- prohibition on silent fallback.

Any proposed budget increase required by the boundary-strip proof must be reported before pinning and is not authorized by this design document alone.

## 7. Runtime smoke-test requirement

The existing calculation-free static test is retained but is no longer sufficient by itself for v2.2 release readiness.

Before any v2.2 mathematical tag is authorized, a runtime smoke test must execute the **production-shaped boundary-strip route** on at least the smallest configured closed strip box containing `u=0`, using the pinned runtime dependency and the same finite-enclosure adapter path intended for production.

The smoke test must fail unless:

- the regularized route reaches `u=0` without a non-finite Arb;
- every enclosure passed to the canonical adapter is finite;
- the symbolic/provenance pins match;
- the returned canonical interval is structurally valid.

A point-only evaluation at `u=0` is insufficient; the smoke test must exercise a positive-width `u` strip.

Smoke-test success is readiness evidence only. It is not mathematical certificate evidence and cannot replace the full candidate run.

## 8. Sequencing and authorization boundary

1. Add this design document only. **STOP for chat byte-audit.**
2. After separate approval, implement the boundary-strip route, symbolic audit, checker changes, and v2.2 config pins. Report all source SHA-256 values and exact config diff. **STOP.**
3. After separate approval, add and execute the runtime smoke test. **STOP.**
4. Only after all audits are GREEN may a new immutable source commit be proposed for a tag of the form `blocal-v2.2-run-<40hex>`.
5. Tag creation requires explicit user approval. No v2.1 tag is moved or reused.
6. No calibration workflow is started automatically.
