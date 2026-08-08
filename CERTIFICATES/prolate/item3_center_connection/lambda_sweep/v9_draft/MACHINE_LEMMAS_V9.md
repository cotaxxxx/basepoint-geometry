# Item 3 sweep v9 — machine logical lemmas

**Status:** `DEPENDENCY PACKAGE CANDIDATE / MATHEMATICAL CONTENT FOR FINAL AUDIT`  
**Date:** 2026-08-08

This document states the logical lemmas consumed by the v9 machine conclusion.  It does not
approve any source bytes or run.  Source realization is separately hash-bound and audited.

The fixed variables are

```text
0 < r < 1,
lambda >= 1,
theta in [0,pi/2],
phi in [0,pi].
```

The exact F-level analytic representation and derivatives are those derived in
`ANALYTIC_DOMAIN_INTERCHANGE_PROOF.md` and mapped in the final source/formula map.

---

## L-CONT — continuity

**Statement.**  `G(r,lambda)=F(r,lambda)/r` is continuous on every compact machine
rectangle contained in `0<r<1`, `lambda>=1`.

**Proof.**  On such a rectangle, the analytic domain proof gives uniform positivity of all
algebraic denominators, in particular

```text
q >= (1-r_max)^2 > 0,
w^2 >= 1,
W >= 1-r_max > 0.
```

The exact square-sum identity gives `0<gamma<=1`; the removable endpoint representation of
`h(gamma)=acos(gamma)^2` is continuous at `gamma=1`.  Hence the fixed-domain F integrand is
continuous jointly in parameters and integration variables on a compact set and therefore
bounded.  Parameter continuity passes through the finite fixed-domain integral.  Division
by positive r preserves continuity.

---

## L-DERIV — first r derivative of G

**Statement.**  On the machine domain,

```text
G_r = F_r/r - F/r^2.
```

**Proof.**  The analytic package proves differentiation of F under the fixed-domain
integral.  Since `r>0`, ordinary differentiation of `G=F r^-1` gives the displayed
identity.  The final adapter evaluates this exact identity through its frozen dual
association rule.

---

## L-ENCL — rigorous enclosure implication

**Statement.**  If the validated F-level kernel encloses each exact analytic integral and
the validated adapter converts all parameter boxes by outward-containing Arb balls and
returns exact binary-rational lower/upper endpoints of the resulting Arb enclosure, then
the adapter's final canonical interval contains the exact target quantity.

When two algebraically identical finite quotient associations are intersected, the exact
target belongs to both and therefore belongs to their intersection.  If only one is
finite, that finite enclosure remains valid.  Two finite disjoint associations signal an
implementation inconsistency and cannot be used as proof.

**Proof.**  This is inclusion transitivity plus the elementary set identity
`x in A and x in B => x in A intersect B`.  The required python-flint/adapter semantics are
source/runtime validation obligations, not assumptions that may be inferred from numeric
agreement.

---

## L-IVT — existence and uniqueness

**Statement.**  Let `W=[a,b]` and fix lambda.  If G is continuous on W,

```text
G(a)>0,
G(b)<0,
G_r<0 throughout W,
```

then G has exactly one zero in `(a,b)`.

**Proof.**  Existence follows from the intermediate value theorem.  Strict negativity of
`G_r` implies strict decrease, hence at most one zero.

The box version follows pointwise for every lambda in a closed lambda shard when all three
inequalities are certified uniformly on that shard.

---

## L-SIGN — strict interval sign

**Statement.**  If a rigorous real enclosure `[L,U]` contains x, then

```text
L>0 => x>0,
U<0 => x<0.
```

An enclosure touching zero or a nonfinite enclosure implies no strict sign.

**Proof.**  Immediate from set containment and the order on the real line.

---

## L-SECOND-DERIV — second derivative needed by v9

**Statement.**  On every compact machine rectangle,

```text
F_rr = integral_D Phi_F_rr,
G_rr = F_rr/r - 2 F_r/r^2 + 2 F/r^3,
```

with the exact `Phi_F_rr` formula in the analytic derivation.  These derivatives are
continuous on the compact rectangle.

**Proof.**  The domain proof establishes denominator separation and removable angle
regularity through the third derivative.  The exact differentiated integrand is therefore
continuous on the compact parameter/integration product and has a parameter-uniform
integrable majorant.  Differentiation under the integral is valid.  The G identity follows
by a second ordinary derivative of `F/r`.

---

## L-MIXED-DERIV — mixed derivative needed by v9

**Statement.**  On every compact machine rectangle,

```text
F_lambda   = integral_D Phi_F_lambda,
F_rlambda  = integral_D Phi_F_rlambda,
G_rlambda  = F_rlambda/r - F_lambda/r^2.
```

The required mixed differentiation orders commute.

**Proof.**  The same compact-domain argument applies to the mixed analytic integrand.  Its
continuity supplies a common local majorant and justifies parameter differentiation under
the fixed-domain integral.  Continuity of the relevant mixed derivative permits equality
of the mixed orders.  Ordinary differentiation of `G_r` with respect to lambda gives the
G identity.

---

## L-MEAN-VALUE-ENCL — two-variable inclusion and deterministic refinement

**Statement.**  Put `H=G_r` and let

```text
I      = [r_lo,r_hi],
Lambda = [lambda_lo,lambda_hi],
r0      = (r_lo+r_hi)/2,
lambda0 = (lambda_lo+lambda_hi)/2.
```

Then

```text
H(I,Lambda)
 subset
 H(r0,lambda0)
 + G_rr(I,Lambda)*(I-r0)
 + G_rlambda(I,Lambda)*(Lambda-lambda0).
```

Consequently, if rigorous enclosures of the three right-hand quantities produce a finite
mean-value enclosure with strict negative upper endpoint, then

```text
G_r<0 throughout I x Lambda.
```

If strict negativity fails, the machine may only refine according to the frozen exact
score/order policy or stop `INCOMPLETE`; it may not infer a positive derivative.

**Proof.**  For any `(r,lambda)` in the rectangle choose the axis path

```text
(r0,lambda0) -> (r,lambda0) -> (r,lambda).
```

The one-variable fundamental theorem of calculus on the two path segments gives

```text
H(r,lambda)-H(r0,lambda0)
 = integral_(r0)^r G_rr(s,lambda0) ds
 + integral_(lambda0)^lambda G_rlambda(r,t) dt.
```

Both derivative values lie in the whole-rectangle derivative ranges, yielding the stated
set inclusion.  Applying L-ENCL and L-SIGN to the implemented enclosures gives the strict
negative conclusion.

The exact split scores

```text
S_r      = radius(I)*absmax(G_rr enclosure),
S_lambda = radius(Lambda)*absmax(G_rlambda enclosure)
```

and the total axis order are deterministic execution controls, not additional analytic
assumptions.

---

## Multi-run connection corollary

This corollary is consumed by the aggregate verifier rather than by a per-shard runner.
Let two successful adjacent closed lambda shards meet at `lambda_*` and let their certified
root windows have positive-width overlap.  At `lambda_*`, each shard supplies L-IVT with
strict decrease on its own window.  The overlapping windows have connected union, and G is
strictly decreasing throughout that union.  Hence the two unique zeros at the shared
lambda are the same zero.

No numerical root equality test is required.

---

## Nonclaims

These lemmas do not establish the paper's comparison with `a_c`, the local normal-form
connection, analyticity of the stationary branch, or completion of the frozen 16-stage
dependency graph.  They support only the stated v9 machine range conclusion.
