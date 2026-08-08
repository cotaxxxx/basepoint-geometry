# Item 3 sweep v9 — analytic domain and differentiation-under-integral proof

**Status:** `ANALYTIC PROOF COMPLETE / MACHINE BINDING PENDING`  
**Date:** 2026-08-08  
**Issue:** #20  
**Scope:** real-variable analytic justification for the five-output v9 derivative kernel.  
**Non-approval:** this document does not approve source, config, workflow, tag, certificate, or `CERTIFIED_LAMBDA_RANGE`.

## 1. Domain

Let

```text
D = [0, pi/2] x [0, pi]
```

with variables `(theta, phi)`. Put

```text
s = sin(theta),
c = cos(theta),
u = s cos(phi).
```

Then

```text
0 <= s <= 1,
0 <= c <= 1,
s^2 + c^2 = 1,
|u| <= s <= 1.
```

Let the parameter rectangle be any compact set

```text
P = [r_-, r_+] x [lambda_-, lambda_+]
```

such that

```text
0 <= r_- <= r_+ < 1,
1 <= lambda_- <= lambda_+ < infinity.
```

This statement is intentionally stronger than the immediate rehearsal box. Machine use
still requires an independent static check that every real parameter represented by an
approved input box satisfies these inequalities.

Define

```text
ell = s^2 + lambda^2 c^2,
w^2 = lambda^2 s^2 + c^2,
q = ell - 2 r u + r^2,
W = 1 - r u,
B = lambda / w,
gamma = B W / sqrt(q).
```

## 2. Uniform denominator bounds

Because `lambda >= 1` and `s^2+c^2=1`,

```text
ell = s^2 + lambda^2 c^2 >= 1,
w^2 = lambda^2 s^2 + c^2 >= 1.
```

Since `u <= 1` and `r >= 0`,

```text
q
 = ell - 2 r u + r^2
 >= 1 - 2 r + r^2
 = (1-r)^2
 >= (1-r_+)^2
 > 0.
```

Also

```text
W = 1-r u >= 1-r >= 1-r_+ > 0.
```

Hence, on `D x P`,

```text
lambda >= 1,
w >= 1,
sqrt(q) >= 1-r_+ > 0,
W >= 1-r_+ > 0.
```

Every algebraic denominator occurring in the prototype formulas for
`gamma`, `gamma_r`, `gamma_rr`, `gamma_rrr`, `gamma_lambda`,
`gamma_rlambda`, and `gamma_rrlambda` is therefore bounded away from zero.

## 3. Exact range of gamma

Positivity follows immediately from the preceding bounds:

```text
gamma > 0.
```

To prove `gamma <= 1`, it is enough to prove

```text
w^2 q - lambda^2 W^2 >= 0.
```

Set

```text
a = lambda^2 - 1 >= 0.
```

Direct expansion using `s^2+c^2=1` gives the exact identity

```text
w^2 q - lambda^2 W^2
 = c^2 (r + a u)^2
   + (s^2-u^2) [ c^2 a^2 + lambda^2 r^2 ].
```

Both terms on the right are nonnegative because `s^2-u^2 >= 0`. Therefore

```text
0 < gamma <= 1
```

throughout `D x P`.

This is an algebraic range proof; it does not rely on interpreting `gamma` geometrically
as a cosine.

## 4. Regularity of the angle kernel

Let

```text
h(x) = arccos(x)^2,    0 <= x <= 1.
```

The apparent singularity of derivatives at `x=1` is removable. With `z=1-x`,

```text
h(1-z)
 = 2 z + z^2/3 + 4 z^3/45 + z^4/35 + O(z^5).
```

Consequently `h` extends real-analytically through `x=1` from the physical side and

```text
h'(1)   = -2,
h''(1)  =  2/3,
h'''(1) = -8/15.
```

On the compact interval `[0,1]`, the functions

```text
h, h', h'', h'''
```

are continuous and bounded.

The hypergeometric formulas used by the prototype are an implementation device for this
regular extension. Their source-level correctness is a separate validation obligation.

## 5. Exact geometry derivatives

Write

```text
d = r-u,
N = u(1-ell) + r(u^2-1),
N_r = u^2-1,
M = N_r q - 3 N d.
```

Since

```text
gamma = B W q^(-1/2),
W_r = -u,
q_r = 2(r-u) = 2d,
```

direct differentiation gives

```text
gamma_r
 = B[-u q - W d] q^(-3/2).
```

The numerator satisfies the exact identity

```text
-u q - W d
 = u(1-ell) + r(u^2-1)
 = N,
```

hence

```text
gamma_r = B N q^(-3/2).
```

Differentiating again,

```text
gamma_rr
 = B [N_r q - 3 N d] q^(-5/2)
 = B M q^(-5/2).
```

Since

```text
M_r = -N_r d - 3N,
```

one more derivative gives

```text
gamma_rrr
 = B (M_r q - 5 M d) q^(-7/2).
```

For lambda derivatives, note

```text
w^2 = lambda^2 s^2 + c^2,
B = lambda/w.
```

Therefore

```text
B_lambda/B
 = 1/lambda - lambda s^2/w^2
 = c^2/(lambda w^2).
```

Also

```text
q_lambda = 2 lambda c^2,
N_lambda = -2 lambda u c^2,
M_lambda = N_r q_lambda - 3 N_lambda d.
```

Hence

```text
gamma_lambda
 = gamma [ c^2/(lambda w^2) - lambda c^2/q ],
```

```text
gamma_rlambda
 = B [
       N_lambda
       + N c^2/(lambda w^2)
       - 3 lambda c^2 N/q
     ] q^(-3/2),
```

and

```text
gamma_rrlambda
 = B [
       M_lambda
       + M c^2/(lambda w^2)
       - 5 lambda c^2 M/q
     ] q^(-5/2).
```

These are identities of ordinary real functions on `D x P`.

## 6. Fixed-domain integrand and its derivatives

Define

```text
Phi_F
 = s[-u h(gamma) + W h'(gamma) gamma_r].
```

All factors are continuous on `D x P`, and all required parameter derivatives are
continuous there by Sections 2--5.

For readability put

```text
g_r  = gamma_r,
g_rr = gamma_rr,
g_rrr = gamma_rrr,
g_l  = gamma_lambda,
g_rl = gamma_rlambda,
g_rrl = gamma_rrlambda,
```

and

```text
A = h''(gamma) g_r^2 + h'(gamma) g_rr.
```

Ordinary differentiation gives the following exact identities.

### 6.1 r derivative

Using `W_r=-u`,

```text
partial_r Phi_F
 = s[
     -2u h'(gamma) g_r
     + W( h''(gamma) g_r^2 + h'(gamma) g_rr )
   ].
```

This is the prototype `Phi_F_r` integrand.

### 6.2 second r derivative

Because

```text
partial_r[ h'(gamma) g_r ] = A,
```

and

```text
partial_r A
 = h'''(gamma) g_r^3
   + 3 h''(gamma) g_r g_rr
   + h'(gamma) g_rrr,
```

we obtain

```text
partial_rr Phi_F
 = s[
     -3u A
     + W(
         h'''(gamma) g_r^3
         + 3 h''(gamma) g_r g_rr
         + h'(gamma) g_rrr
       )
   ].
```

This is the prototype `Phi_F_rr` integrand.

### 6.3 lambda derivative

Since `s`, `u`, and `W` are independent of lambda,

```text
partial_lambda Phi_F
 = s[
     -u h'(gamma) g_l
     + W(
         h''(gamma) g_l g_r
         + h'(gamma) g_rl
       )
   ].
```

This is the prototype `Phi_F_lambda` integrand.

### 6.4 mixed r-lambda derivative

Differentiating the `r` derivative in lambda gives

```text
partial_rlambda Phi_F
 = s[
     -2u(
       h''(gamma) g_l g_r
       + h'(gamma) g_rl
     )
     + W(
       h'''(gamma) g_l g_r^2
       + 2 h''(gamma) g_r g_rl
       + h''(gamma) g_l g_rr
       + h'(gamma) g_rrl
     )
   ].
```

This is the prototype `Phi_F_rlambda` integrand.

## 7. Differentiation under the integral sign

Define

```text
F(r,lambda)
 = (1/pi) integral_D Phi_F(theta,phi;r,lambda) dphi dtheta.
```

Sections 2--6 show that

```text
Phi_F,
partial_r Phi_F,
partial_lambda Phi_F,
partial_rr Phi_F,
partial_rlambda Phi_F
```

are continuous on the compact set `D x P`.

Therefore each is bounded there. In particular, for each required derivative there is a
finite constant `C_P` such that its absolute value is bounded by `C_P` on all of `D x P`.
The constant function `C_P` is integrable on the finite-measure domain `D`.

The standard parameter differentiation theorem for integrals therefore applies. Thus

```text
F_r       = (1/pi) integral_D partial_r Phi_F,
F_lambda  = (1/pi) integral_D partial_lambda Phi_F,
F_rr      = (1/pi) integral_D partial_rr Phi_F,
F_rlambda = (1/pi) integral_D partial_rlambda Phi_F.
```

Because the relevant derivatives are continuous, mixed differentiation commutes on the
interior of `P`, and the identities extend continuously to the boundary of `P`.

No sampled estimate and no numerical quadrature is used in this interchange argument.

## 8. Quotient identities used by v9

For `r>0`, let

```text
G(r,lambda) = F(r,lambda)/r.
```

Then ordinary differentiation gives

```text
G_r
 = F_r/r - F/r^2,
```

```text
G_rr
 = F_rr/r - 2 F_r/r^2 + 2 F/r^3,
```

and

```text
G_rlambda
 = F_rlambda/r - F_lambda/r^2.
```

These identities are exact. Machine use additionally requires the approved r-domain to
exclude zero and requires a frozen interval association/expression ID.

## 9. Mean-value inclusion

Let

```text
H = G_r.
```

On a closed rectangle `I x Lambda` contained in the analytic parameter domain, choose the
exact midpoint `(r0,lambda0)`. For any `(r,lambda)` in the rectangle, integrate along the
axis path

```text
(r0,lambda0) -> (r,lambda0) -> (r,lambda).
```

Then

```text
H(r,lambda)-H(r0,lambda0)
 = integral_(r0)^r H_r(s,lambda0) ds
   + integral_(lambda0)^lambda H_lambda(r,t) dt.
```

Since

```text
H_r = G_rr,
H_lambda = G_rlambda,
```

rigorous enclosures valid on the entire rectangle imply

```text
H(I,Lambda)
 subset
 H(r0,lambda0)
 + G_rr(I,Lambda)(I-r0)
 + G_rlambda(I,Lambda)(Lambda-lambda0).
```

This is the v9 two-variable mean-value inclusion.

## 10. Immediate rehearsal corollary

The existing dependency snapshot records the certified pilot root interval

```text
1/64 < r < 11/256,
```

and the v9 rehearsal range policy records

```text
123731943/26214400 <= lambda <= 118/25.
```

These values satisfy

```text
0 < 1/64 < 11/256 < 1,
1 < 123731943/26214400 < 118/25 < infinity.
```

Therefore the analytic domain and interchange theorem above covers the immediate v9
rehearsal rectangle, provided the final adapter/static audit verifies that every r-cell
used by the rehearsal remains inside the approved r-domain.

## 11. Dependency status

This document supplies the real-analysis content required by the planned dependencies:

### `L-SECOND-DERIV`

Analytic content supplied here:

- formula for `F_rr`;
- positivity of all denominators;
- `0<gamma<=1` range;
- endpoint regularity of `h` through third derivative;
- differentiation-under-integral justification through second r derivative;
- quotient identity for `G_rr`.

### `L-MIXED-DERIV`

Analytic content supplied here:

- formulas for `F_lambda` and `F_rlambda`;
- mixed derivative existence and commutation;
- differentiation-under-integral justification;
- quotient identity for `G_rlambda`.

### `L-MEAN-VALUE-ENCL`

Analytic content supplied here:

- the two-variable axis-path inclusion theorem.

## 12. What remains before machine authorization

The analytic statements above are not yet machine-authorized dependency entries. Before
v9 freeze, the project must still complete all of the following:

1. independent rederivation against this document without importing production derivative
   expressions;
2. exact source-to-formula mapping for every prototype kernel term;
3. static proof that the approved runner cannot submit an r- or lambda-box outside the
   analytic domain;
4. validation that the actual `acb.integral` calls rigorously enclose the displayed real
   integrals on point and interval inputs;
5. final interval association/expression IDs for `G_r`, `G_rr`, and `G_rlambda`;
6. canonical dependency-entry objects and hashes;
7. post-import source identity checks;
8. the full independent validation corpus required by the v9 validation contract.

Until those items pass, overall status remains

```text
SPEC_PENDING / FREEZE NOT AUTHORIZED.
```
