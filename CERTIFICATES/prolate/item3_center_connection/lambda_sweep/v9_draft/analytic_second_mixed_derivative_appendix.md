# Analytic Appendix — Second and Mixed Derivatives

**Status:** `DRAFT / SPEC_PENDING`  
**Issue:** #20  
**Purpose:** state the analytic obligations for a new clean-room derivative kernel.
This appendix contains no implemented integrand and proves no property of an
unwritten kernel.

## 1. Abstract integral form

The existing clean-room source ultimately represents a quantity `F(r, λ)` through
rigorous integration. For v9, write the intended fixed-domain representation abstractly
as

```text
F(r, λ) = ∫_D Φ(r, λ; u) du,
```

where `D` may be multidimensional but must be independent of `(r, λ)` after every
approved change of variables.

The clean-room derivation must supply explicit analytic expressions for

```text
Φ
∂_r Φ
∂_λ Φ
∂_rr Φ
∂_rλ Φ
```

and a rigorous justification for

```text
F_r  = ∫_D ∂_r Φ du,
F_λ  = ∫_D ∂_λ Φ du,
F_rr = ∫_D ∂_rr Φ du,
F_rλ = ∫_D ∂_rλ Φ du.
```

The actual integrands, domain decomposition, removable-singularity treatment, branch
choices, and domination bounds are unresolved and must be independently derived before
v9 source work begins.

## 2. Required differentiation-under-integral proof

For every approved `(r, λ)` box, the derivation shall establish:

1. `Φ` and every required derivative are defined almost everywhere on a fixed domain;
2. parameter derivatives exist in the required order;
3. an integrable parameter-uniform majorant or an equivalent rigorous theorem permits
   differentiation under the integral sign;
4. endpoint singularities and branch transitions are either absent, removed
   analytically, or isolated in a certified domain decomposition;
5. mixed differentiation order is justified where `F_rλ` is used;
6. all algebraic denominators are bounded away from zero on the machine domain;
7. the interval implementation encloses the exact analytic integrand, not a rounded
   surrogate formula.

A numerical agreement check cannot replace any item above.

## 3. Quotient derivatives

Let

```text
G(r, λ) = F(r, λ) r^-1,
```

with `r > 0`.

Differentiating with respect to `r` gives

```text
G_r = F_r r^-1 - F r^-2
    = F_r/r - F/r^2.
```

Differentiating again,

```text
G_rr
  = F_rr r^-1 - F_r r^-2
    - F_r r^-2 + 2 F r^-3
  = F_rr/r - 2 F_r/r^2 + 2 F/r^3.
```

Differentiating `G_r` with respect to `λ` while `r` is fixed,

```text
G_rλ
  = F_rλ r^-1 - F_λ r^-2
  = F_rλ/r - F_λ/r^2.
```

Therefore a kernel that exposes only `F`, `F_r`, and `F_rλ` is insufficient for the
mixed mean-value correction. `F_λ` is also required.

These identities are algebraic and exact. Their safe machine use still requires
rigorous interval division by positive `r` intervals and exact source binding.

## 4. Two-variable inclusion theorem

Let

```text
H(r, λ) = G_r(r, λ).
```

Assume `H` is continuously differentiable on the rectangle `I × Λ`, or satisfies a
weaker theorem sufficient for the following integral identities. Let
`(r0, λ0) ∈ I × Λ`.

For any `(r, λ) ∈ I × Λ`, choose the axis path

```text
(r0, λ0) -> (r, λ0) -> (r, λ).
```

Then

```text
H(r, λ) - H(r0, λ0)
  = ∫_(r0)^r H_r(s, λ0) ds
    + ∫_(λ0)^λ H_λ(r, t) dt.
```

If

```text
H_r(I, Λ) ⊇ {H_r(s, t): (s, t) ∈ I × Λ},
H_λ(I, Λ) ⊇ {H_λ(s, t): (s, t) ∈ I × Λ},
```

then interval integration and inclusion isotonicity yield

```text
H(r, λ)
  ∈ H(r0, λ0)
    + H_r(I, Λ) (r-r0)
    + H_λ(I, Λ) (λ-λ0).
```

Taking the union over the rectangle gives

```text
H(I, Λ)
  ⊆ H(r0, λ0)
    + H_r(I, Λ) (I-r0)
    + H_λ(I, Λ) (Λ-λ0).
```

Substitution of `H_r = G_rr` and `H_λ = G_rλ` gives the v9 enclosure.

### 4.1 Path-choice independence of validity

An alternate path can produce a different interval width because interval arithmetic
retains dependencies differently, but either path is valid if its derivative boxes
cover the whole rectangle. v9 must freeze one formula and one evaluation order so
runner and checker reproduce identical evidence semantics.

### 4.2 Canonical center

The midpoint center is selected for deterministic symmetry and to minimize the maximum
absolute coordinate offsets in each independent coordinate. This does not prove that it
minimizes the final interval width after dependency effects. The center rule remains
exact and fixed unless a later contract amendment proves and freezes another rule.

## 5. λ-width obligation

An r-only mean-value form has the structure

```text
G_r(I, Λ)
  ⊆ G_r(r0, Λ) + G_rr(I, Λ)(I-r0),
```

and therefore retains the full raw λ dependency inside `G_r(r0, Λ)`. The reported
diagnostic coefficient of roughly

```text
enclosure radius contribution ≈ 2048 * width(Λ)
```

would remain. At `width(Λ)=2^-20`, this contribution is about `1.95e-3`; at
`width(Λ)=2^-12`, it is about `0.5`. These figures are diagnostic, not certified, but
they show why a mixed derivative is part of the initial v9 design rather than a later
optimization.

The mixed term makes the λ dependence explicit:

```text
G_rλ(I, Λ)(Λ-λ0).
```

Whether this term is sufficiently sharp for broad sweep boxes is a future certified
performance question. Its inclusion prevents the contract from hiding λ inflation
inside a raw interval point-in-r evaluation.

## 6. Interval evaluation order

The adapter shall freeze an evaluation order for each quotient identity. Candidate
orders must be tested for interval sharpness and replay identity. Algebraically
equivalent reassociation can change interval width; therefore source code, operation
order, and source hash are normative.

At minimum, validation shall compare:

```text
F_rr/r - (2 F_r)/r^2 + (2 F)/r^3
(F_rr*r^2 - 2 F_r*r + 2 F)/r^3
```

and analogous forms for `G_r` and `G_rλ`. A sharper candidate may be selected only
after rigorous containment and independent audit. The contract shall name exactly one
normative expression.

## 7. Clean-room derivation package

Before implementation approval, the derivative package shall contain:

1. the source mathematical expression for `Φ`;
2. a line-by-line derivation of `∂_λ Φ`, `∂_rr Φ`, and `∂_rλ Φ`;
3. simplification rules with domain conditions;
4. a fixed integration-domain decomposition;
5. rigorous endpoint and branch analysis;
6. domination or equivalent interchange proofs;
7. exact mapping from mathematical terms to source functions;
8. an independent rederivation by a separate authoring path;
9. canonical hashes of the frozen derivation and source;
10. an explicit list of all assumptions not checked by the machine.

## 8. Diagnostic checks permitted but non-normative

The following may be used to find transcription errors but cannot certify derivatives:

- centered finite-difference comparisons at high precision;
- automatic-differentiation comparisons;
- symbolic computer-algebra simplification;
- comparisons against point quadrature;
- regression against the old `F` and `F_r` kernel;
- sampled estimates of `|G_rr|` or `|G_rλ|`.

Every such output must contain a field equivalent to

```text
proof_status = "DIAGNOSTIC_ONLY"
```

and must not be imported by the production runner or checker.

## 9. Unresolved analytic work

This appendix cannot be frozen until the following are supplied:

- the actual fixed-domain integrand;
- explicit formulas for all five published outputs;
- rigorous interchange conditions;
- singular and branch decomposition;
- the final interval expression order;
- full machine-domain parameter bounds;
- independent derivation evidence.

Until then, all formulas beyond the quotient identities and the abstract mean-value
inclusion remain design obligations rather than established kernel facts.
