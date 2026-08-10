# B-LOCAL v2.2 addendum — exact Duffy regularization for the L1 boundary strip

**Status: DRAFT FOR CHAT AUDIT.** This file supplements `BLOCAL_BENTRY_DEPENDENCY_DESIGN_V2_2.md` only. It changes no implementation source, config, pin, workflow, tag, certificate, or prior incident record. Mathematical execution remains unauthorized.

## 0. Purpose

The v2.2 base design already requires a positive-width boundary strip

`0 <= u <= u_cut`, `-s_neg <= s <= s_start`,

with a regularized route for the full `dFdr` integrand. This addendum completes the exact domain partition and the cancellation-free formula actually permitted to enter interval arithmetic.

A circular singular patch is not normative. The normative singular patch is an exact dyadic square in `(c,phi)` coordinates, followed by a two-triangle Duffy transform.

## 1. Exact variables and identities

Use

`c = cos(theta)`,
`S = sqrt(1-c^2)`,
`U = S cos(phi)`,
`ell = 1 + (lambda^2-1)c^2`,
`A = (lambda^2-1)c^2`,
`B = 1-U^2`,
`W = 1-r U`,
`q = ell - 2 r U + r^2`,
`N = U(1-ell) + r(U^2-1)`.

The following exact identities are normative and must be verified by the symbolic audit:

`q = W^2 + A + r^2 B`,

`q = (r-U)^2 + B + A`,

`N = -U A - r B`.

On the singular patch, introduce a local radial factor `rho` and bounded angular factors by

`A = rho^2 A_hat`,
`B = rho^2 B_hat`,
`M = U A_hat + r B_hat`.

Then

`N = -rho^2 M`.

Define

`L = lambda / w`,
`z = rho / sqrt(q)`,
`y = W / sqrt(q)`,
`v = (r-U) / sqrt(q)`,
`gamma = L y`.

These are helper variables for the regularized expression. They must not be evaluated by first constructing a literal `0/0` quotient at the singular corner.

## 2. Exact bounds for y and v

The enclosure rules for `y` and `v` are algebraic, not numerical heuristics.

From

`q = W^2 + A + r^2 B`

with `A >= 0`, `B >= 0`, one has

`q >= W^2`.

On the B-LOCAL strip, `W = 1-rU >= 0`, hence

`0 <= y <= 1`.

From

`q = (r-U)^2 + B + A`

one has

`q >= (r-U)^2`, hence

`|v| <= 1`.

These bounds must be encoded directly in the boundary-route enclosure logic and independently checked. No floating-point estimate may replace them.

## 3. Required positive lower bound controlling z

The variable `z` requires a separately certified denominator lower bound.

From

`q = W^2 + rho^2(A_hat + r^2 B_hat)`

one obtains

`q >= rho^2(A_hat + r^2 B_hat)`

and therefore, wherever `rho > 0`,

`z <= 1 / sqrt(A_hat + r^2 B_hat)`.

The implementation must prove on every singular-patch proof box an exact strictly positive lower bound

`Z_DEN_LO <= A_hat + r^2 B_hat`

with `Z_DEN_LO > 0`.

Only after this proof may it use

`0 <= z <= 1/sqrt(Z_DEN_LO)`.

It is insufficient merely to state that `B_hat` is approximately one near the corner. The lower bound must be derived by exact interval inequalities on the actual `(c,phi,r,lambda)` proof box.

Failure to prove `Z_DEN_LO > 0` is `INDETERMINATE` and fails closed.

## 4. Integration variable c = cos(theta) and exact measure cancellation

The normative angular variables for the boundary-strip route are `(c,phi)`, not `(theta,phi)`.

Since

`c = cos(theta)`, `theta in [0,pi/2]`,

one has

`dtheta = -dc / sqrt(1-c^2)`

and

`sin(theta) = sqrt(1-c^2)`.

Therefore the factor `sin(theta)` already present in the pinned full `dFdr` angular integrand cancels the change-of-variable denominator exactly:

`sin(theta) dtheta = -dc`.

After reversing limits,

`sin(theta) K dtheta dphi = K dc dphi`,

where `K` is the full derivative bracket defined in Section 7.

This cancellation is normative and must be recorded by the symbolic audit before interval evaluation. The implementation must **not** separately enclose `1/sqrt(1-c^2)` and must not impose a positive lower-bound obligation on `1-c^2`. In particular, the regular piece `R1` is allowed to contain `c=1`; no artificial singularity may be reintroduced there by separating factors that cancel exactly.

Using `c` as the integration variable is normative because it keeps all patch boundaries exact dyadic rationals and avoids transcendental endpoints such as `arccos(eps)`.

## 5. Exact singular square and complement partition

Fix one exact dyadic

`eps = 2^(-m)`

in the v2.2 run config.

The singular square is

`P_eps = { 0 <= c <= eps, 0 <= phi <= eps }`.

The regular complement of this square inside

`D = [0,1] x [0,pi]`

is represented by exactly two closed pieces whose overlap is only their shared boundary:

`R1 = [eps,1] x [0,pi]`,

`R2 = [0,eps] x [eps,pi]`.

The checker must reconstruct

`D = P_eps union R1 union R2`

exactly, with no gap and no overlap except shared faces.

The implementation may further subdivide `R1` or `R2` into exact closed boxes, but no curved or transcendental boundary is permitted.

## 6. Two-triangle Duffy transform on P_eps

Split `P_eps` into two closed triangles along `c=phi`.

For triangle T1 (`0 <= phi <= c <= eps`), use

`c = eps x`,
`phi = eps x y`,
`0 <= x <= 1`, `0 <= y <= 1`.

For triangle T2 (`0 <= c <= phi <= eps`), use

`phi = eps x`,
`c = eps x y`,
`0 <= x <= 1`, `0 <= y <= 1`.

The absolute Jacobian is

`eps^2 x`

for both triangles.

The local radial factor is triangle-specific and must be recorded explicitly:

- on T1, `rho_T1 = eps x sqrt(1+y^2)` because `(c,phi) = (eps x, eps x y)`;
- on T2, `rho_T2 = eps x sqrt(1+y^2)` because `(c,phi) = (eps x y, eps x)`.

Although the same scalar expression occurs in both triangles, the assignments of `c` and `phi` are exchanged. Consequently `A_hat`, `B_hat`, `M`, and the proof of `Z_DEN_LO` must be evaluated using the correct triangle-specific substitution; values or bounds from T1 may not be silently reused for T2.

The transformed integrand must be algebraically rewritten before Arb evaluation so that the factor `x` supplied by the Jacobian cancels the corner growth. A literal singular quotient evaluated first and multiplied by `x` afterwards is forbidden.

The shared diagonal and the coordinate axes may be covered by both transformed triangles only as shared measure-zero faces. The checker must verify the exact square reconstruction.

## 7. Normative cancellation-free full dFdr expression

Define the full derivative bracket **without** the outer `sin(theta)` factor by

`K = -2 U h'(gamma) gamma_r + W(h''(gamma) gamma_r^2 + h'(gamma) gamma_rr)`.

The pinned full angular integrand is `sin(theta) * K`.

After the exact substitutions above, and after multiplication of `K` by the local radial factor `rho`, the following expression is normative wherever the original formula is finite:

`J = L * [ 2 U h'(gamma) M z^3`

`          + L h''(gamma) M^2 y z^5`

`          + h'(gamma) { -B_hat y rho z^2 + 3 M y v z^3 } ]`.

The symbolic audit must verify exact equality

`J = rho * K`

on the algebraic domain where the original `gamma_r` and `gamma_rr` expressions are defined.

By Section 4, the `sin(theta)` factor and `dtheta/dc` cancel exactly. Thus the `(c,phi)` integrand is simply `K`.

On either Duffy triangle,

`dc dphi = eps^2 x dx dy`

and

`rho = eps x sqrt(1+y^2)`.

Therefore the actual transformed singular-patch integrand is exactly

`(eps / sqrt(1+y^2)) * J`.

This transformed expression, not `J` alone and not a separately evaluated `1/sqrt(1-c^2)` factor, is the normative finite quantity to be enclosed and integrated on the Duffy square.

No implementation may drop, approximate, or absorb without record the factor `eps/sqrt(1+y^2)`.

## 8. Corner enclosure rule

The regularized route must not attempt to evaluate `z`, `y`, or `v` at the singular corner by constructing their defining quotients directly.

Instead, on any transformed box containing `x=0`, it must use certified bounded extensions:

- `0 <= y <= 1` from Section 2;
- `-1 <= v <= 1` from Section 2;
- `0 <= z <= 1/sqrt(Z_DEN_LO)` from Section 3;
- exact interval bounds for `U`, `L`, `A_hat`, `B_hat`, `M`, `h'(gamma)`, and `h''(gamma)` from finite expressions and the bounded `gamma = L y` range.

The product expression in Section 7 is then enclosed as a finite interval directly, including the exact transformed measure factor `eps/sqrt(1+y^2)`.

A direct quotient evaluation that produces non-finite Arb followed by exception handling is forbidden.

## 9. Regular complement route

On `R1` and `R2`, after the exact measure cancellation of Section 4, the route must first certify a strict positive lower bound

`q_min > 0`

for each proof box before using a direct algebraic representation containing negative powers of `q`.

Only then may the direct pinned full `dFdr` bracket `K` be evaluated on that box. The existing canonical Arb-to-dyadic adapter remains unchanged and accepts only finite output.

If a box cannot prove `q_min > 0`, it must be subdivided or fail closed according to the fixed budget. No silent switch to the Duffy route is permitted on a regular-region box.

## 10. Symbolic-audit obligations

The new symbolic audit must independently establish at least:

1. `q = W^2 + A + r^2 B`;
2. `q = (r-U)^2 + B + A`;
3. `N = -U A - r B`;
4. with `A=rho^2 A_hat`, `B=rho^2 B_hat`, `N=-rho^2 M`;
5. the exact algebraic equality `J = rho * K`;
6. the two Duffy Jacobians equal `eps^2 x`;
7. `sin(theta) * dtheta/dc = -1`, with the sign removed only by exact reversal of the `c` integration limits;
8. on each triangle, `rho = eps x sqrt(1+y^2)` with the triangle-specific assignment of `(c,phi)`;
9. the final transformed singular-patch integrand is exactly `(eps/sqrt(1+y^2)) * J`.

The audit is exact algebra only. Numerical agreement is not a substitute.

## 11. Record additions required by this addendum

In addition to the v2.2 base-design fields, each boundary-strip singular-patch record must expose enough machine-readable data to audit:

- patch type `EXACT_DYADIC_SQUARE`;
- `eps`;
- Duffy triangle ID (`T1` or `T2`);
- exact transformed `(x,y)` box;
- exact source `(c,phi)` image bounds or reconstruction data;
- the triangle-specific `rho` definition;
- proved lower bound `Z_DEN_LO`;
- bounds used for `y`, `v`, and `z`;
- the exact measure-cancellation identity ID;
- the finite regularized `J` enclosure;
- the Duffy-Jacobian factor;
- the final `(eps/sqrt(1+y^2))*J` contribution enclosure;
- symbolic-audit source SHA-256;
- boundary-route source SHA-256;
- pinned kernel SHA-256.

Regular-region records must expose their exact `(c,phi)` box, the measure-cancellation identity ID, and proved `q_min > 0` before the direct evaluation enclosure.

## 12. Negative controls

The implementation/checker test suite must include at least:

- fail to prove the exact `sin(theta)` / `dtheta/dc` cancellation => release-readiness rejection;
- separately evaluate `1/sqrt(1-c^2)` after cancellation should have occurred => rejection;
- omit the Duffy Jacobian or the derived `eps/sqrt(1+y^2)` factor => rejection;
- use the T1 substitution or `A_hat/B_hat` bounds silently for a T2 record, or conversely => rejection;
- use a circular patch or transcendental patch boundary => config/checker rejection;
- permit `Z_DEN_LO <= 0` => boundary record not certified;
- directly evaluate `z`, `y`, or `v` as `0/0` at a box containing the corner => fail closed;
- alter the exact complement partition so that a gap exists => checker rejection;
- overlap complement interiors beyond shared faces => checker rejection;
- symbolic audit not exact-zero => implementation not release-ready.

## 13. Sequencing

This addendum is design-only.

1. Add and audit this corrected file only. **STOP for chat byte-audit.**
2. After GREEN, step 2 implementation may begin using this addendum and the base v2.2 design together as the normative design contract.
3. No code/config/pin/workflow/tag change is authorized by this addendum itself.
