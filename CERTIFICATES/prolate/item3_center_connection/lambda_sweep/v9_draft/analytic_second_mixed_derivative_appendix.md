# Analytic Appendix — Second and Mixed Derivatives

**Status:** `ANALYTIC CORE RESOLVED / MACHINE VALIDATION PENDING`  
**Issue:** #20  
**Revision:** 2026-08-08

This appendix records the v9 analytic state after explicit derivation of the five-output
fixed-domain kernel. It does not approve production source, a config, workflow, tag, or
mathematical certificate.

The full proof is:

```text
ANALYTIC_DOMAIN_INTERCHANGE_PROOF.md
```

The current source mapping is:

```text
SOURCE_FORMULA_MAP_V9.md
```

The separate formal rederivation source is:

```text
independent_analytic_rederivation_v9.py
```

## 1. Fixed-domain formula

For

```text
s = sin(theta),
c = cos(theta),
u = s cos(phi),
```

put

```text
ell = s^2 + lambda^2 c^2,
w^2 = lambda^2 s^2 + c^2,
q = ell - 2 r u + r^2,
W = 1-r u,
gamma = lambda W/(w sqrt(q)).
```

The integration domain is fixed:

```text
D = [0,pi/2] x [0,pi].
```

With

```text
h(gamma)=arccos(gamma)^2,
```

the v9 base quantity is

```text
F(r,lambda)
 = (1/pi) integral_D
   s[-u h(gamma) + W h'(gamma) gamma_r]
   dphi dtheta.
```

The explicit derivative integrands for

```text
F_r,
F_lambda,
F_rr,
F_rlambda
```

are proved in `ANALYTIC_DOMAIN_INTERCHANGE_PROOF.md` and mapped one-to-one to the
prototype functions in `SOURCE_FORMULA_MAP_V9.md`.

## 2. Domain and branch theorem

On every compact parameter rectangle satisfying

```text
0 <= r <= r_+ < 1,
1 <= lambda <= lambda_+ < infinity,
```

the proof establishes

```text
ell >= 1,
w^2 >= 1,
q >= (1-r)^2 >= (1-r_+)^2 > 0,
W >= 1-r_+ > 0.
```

It also establishes the exact square-sum identity

```text
w^2 q - lambda^2 W^2
 = c^2 (r + (lambda^2-1)u)^2
   + (s^2-u^2)
     [c^2(lambda^2-1)^2 + lambda^2 r^2]
 >= 0.
```

Consequently

```text
0 < gamma <= 1.
```

Thus the real square-root branches are fixed by strictly positive radicands, and the
physical angle argument never leaves `[0,1]`.

## 3. Removable angle endpoint

The angle kernel has the expansion

```text
h(1-z)
 = 2z + z^2/3 + 4z^3/45 + z^4/35 + O(z^5),
```

so

```text
h'(1)   = -2,
h''(1)  = 2/3,
h'''(1) = -8/15.
```

Therefore the apparent endpoint singularity at `gamma=1` is removable through the order
required by the five-output kernel.

The concrete hypergeometric source representation still requires interval-library
validation; the analytic regularity itself is no longer open.

## 4. Differentiation under the integral sign

The proof shows that the base integrand and the four required parameter derivatives are
continuous on the compact product of the fixed integration domain and any approved compact
parameter rectangle satisfying the domain theorem.

They are therefore bounded by an integrable constant majorant. Standard parameter
differentiation under the integral sign gives

```text
F_r       = (1/pi) integral_D partial_r Phi_F,
F_lambda  = (1/pi) integral_D partial_lambda Phi_F,
F_rr      = (1/pi) integral_D partial_rr Phi_F,
F_rlambda = (1/pi) integral_D partial_rlambda Phi_F.
```

The relevant mixed derivatives are continuous, so their order commutes in the interior
and extends continuously to the compact rectangle boundary.

This closes the real-analysis interchange obligation. No numerical quadrature or sampled
bound enters the argument.

## 5. Quotient derivatives

For `r>0`,

```text
G = F/r
```

satisfies exactly

```text
G_r
 = F_r/r - F/r^2,
```

```text
G_rr
 = F_rr/r - 2F_r/r^2 + 2F/r^3,
```

```text
G_rlambda
 = F_rlambda/r - F_lambda/r^2.
```

The algebra is resolved. The final interval association and corresponding normative
`expression_id` are still open because algebraically equivalent associations can produce
different enclosure widths.

## 6. Mean-value inclusion

For

```text
H=G_r,
```

the axis-path argument gives, on every approved rectangle `I x Lambda`,

```text
H(I,Lambda)
 subset
 H(r0,lambda0)
 + G_rr(I,Lambda)(I-r0)
 + G_rlambda(I,Lambda)(Lambda-lambda0).
```

The center `(r0,lambda0)` is the already frozen exact canonical midpoint. This establishes
the analytic inclusion theorem required by `L-MEAN-VALUE-ENCL`.

## 7. Immediate rehearsal coverage

The inherited pilot root interval is

```text
1/64 < r < 11/256
```

and the immediate rehearsal lambda range is

```text
123731943/26214400 <= lambda <= 118/25.
```

These lie strictly inside the analytic domain above. Machine authorization still requires
static verification that the final runner cannot construct a cell outside the approved
r/lambda domain.

## 8. Dependency disposition

### `L-SECOND-DERIV`

Real-analysis content is **resolved**:

- explicit `F_rr` integrand;
- denominator positivity;
- `0<gamma<=1`;
- removable angle endpoint through `h'''`;
- second-r differentiation under the integral;
- exact `G_rr` quotient identity.

Machine entry remains pending source binding, interval semantics, expression ordering,
and independent validation.

### `L-MIXED-DERIV`

Real-analysis content is **resolved**:

- explicit `F_lambda` and `F_rlambda` integrands;
- mixed derivative existence/commutation;
- differentiation under the integral;
- exact `G_rlambda` quotient identity.

Machine entry remains pending the same implementation gates.

### `L-MEAN-VALUE-ENCL`

The analytic axis-path inclusion is **resolved**. The complete dependency also includes
canonical centers, exact score/axis-selection rules, fail-closed transitions, and interval
semantics from the v9 contract; those machine-control pieces remain subject to final
freeze and validation.

## 9. Remaining non-analytic blockers

The old list of unresolved integrands, domain bounds, branch analysis, and interchange
proofs is superseded by this revision. Remaining blockers are:

1. execute and archive the independent formal rederivation under a pinned environment;
2. validate the source mapping against final candidate bytes;
3. validate concrete `acb.integral` enclosure semantics and analytic-flag behavior;
4. freeze interval expression association/IDs for `G_r`, `G_rr`, `G_rlambda`;
5. statically prove runtime domain enforcement;
6. build canonical dependency entries and hashes;
7. complete the independent validation corpus and post-import source-identity checks.

Overall v9 remains

```text
SPEC_PENDING / FREEZE NOT AUTHORIZED.
```
