# B-LOCAL v2.2 design revision addendum — F-4 correction for L2/L3 F evaluation

**Status: DRAFT FOR CHAT BYTE/CODE/MATH AUDIT. DESIGN ONLY.**

This correction supplements `BLOCAL_BENTRY_DEPENDENCY_DESIGN_V2_2_REVISION_ADDENDUM.md` after its byte-audit was GREEN but content audit found blocker **F-4**. It changes no implementation source, run config, dependency pin, workflow, tag, certificate, frozen RED evidence, or previously audited design bytes.

The previously audited revision addendum remains immutable at its audited bytes. Where that revision says that the **L2/L3 evaluation strategy** is unchanged, this correction supersedes that statement. The mathematical L2/L3 obligations, candidate order, `lambda_plus`, `s_neg`, Stage-1 dependency, canonical adapter semantics, fail-closed semantics, and tag-only authorization remain unchanged unless explicitly stated below.

No implementation, runtime smoke, workflow change, tag creation, calibration start, or production run is authorized by this correction.

## 0. F-4 — pinned F_arb is not an executable L2/L3 proof evaluator

Chat-executed diagnostics established that the problem found in F-3 is not specific to the `dFdr_arb` L1 path.

Under a deliberately loose diagnostic setting with absolute tolerance `1e-8` and depth limit `12`:

- the existing **L2 F evaluation** at the exact face `r = 1 - 2^-8` returned NONFINITE;
- the existing **L3 route A** evaluation at the exact endpoint `r = 1` returned NONFINITE;
- each diagnostic failed on the order of approximately `3` seconds.

These are design/readiness diagnostics only, not certificate evidence.

The conclusion is architectural: the pinned validated two-dimensional integral routine `F_arb` may remain a formula/provenance reference, but it is **not a permitted production proof evaluator for L2 or L3** in B-LOCAL v2.2. Leaving L2/L3 on the old route would make a successful L1 redesign insufficient to complete candidate certification.

No claim is made that the mathematical F formula is false. The rejected premise is only that the current pinned integral representation is executable as a finite interval proof route on the required L2/L3 boxes.

## 1. Normative L2/L3 replacement: one cancellation-free F-route

All B-LOCAL v2.2 proof obligations that require a rigorous enclosure of

`F(r,lambda) = partial_r E_lambda(r)`

for L2 or L3 must use the cancellation-free angular **F-route / rigorous angular ball-sum route** defined here.

The route uses the same exact angular partition, hat variables, child-specific gamma enclosure policy, per-subbox denominator bounds, sequential-division policy, adaptive subdivision policy, helper-lemma validation, symbolic-audit discipline, and fail-closed record/checker architecture already made normative for the revised L1 K-route.

The following are prohibited as L2/L3 certificate evaluators:

- direct calls to pinned `F_arb` for the proof enclosure;
- exception-driven retry from `F_arb` into the finite route;
- silent fallback to any alternative kernel;
- point sampling or floating quadrature as proof evidence.

The pinned clean-room kernel remains the formula provenance source. Exact symbolic audit must establish equality between this cancellation-free F-route and the pinned F integrand wherever the original quotient expression is finite.

## 2. Exact F integrand and normalization

Use the same notation as the revised L1 route:

`c = cos(theta)`,
`U = sin(theta) cos(phi)`,
`W = 1-rU`,
`q = ell - 2rU + r^2`,
`L = lambda/w`,
`A = rho^2 A_hat`,
`B = rho^2 B_hat`,
`N = -rho^2 M`,
`y_h = W/sqrt(q)`,
`z = rho/sqrt(q)`,
`gamma = L y_h`.

The pinned F angular kernel before changing variables is

`sin(theta) * [-U h(gamma) + W h'(gamma) gamma_r]`,

with

`gamma_r = L N / q^(3/2)`.

The already-audited measure identity

`sin(theta) dtheta = -dc`

and exact reversal of the c-limits give the `(c,phi)` bracket

`K_F = -U h(gamma) + W h'(gamma) gamma_r`.

Using

`N = -rho^2 M`,
`y_h = W/sqrt(q)`,
`z^2 = rho^2/q`,

one obtains exactly

`W gamma_r = -L M y_h z^2`,

and therefore the normative cancellation-free F bracket is

`K_F = -U h(gamma) - L h'(gamma) M y_h z^2`.

No new geometric identity is introduced: this is direct substitution into the pinned F formula using identities already required by the revised hat mechanism.

The complete normalized quantity is

`F(r,lambda) = (1/pi) integral_[0,1] integral_[0,pi] K_F(c,phi,r,lambda) dphi dc`.

The factor **`1/pi` is normative**. Every L2/L3 root record must make its placement explicit: it may be applied to every child contribution or once to the outward-rounded root sum, but it may not be dropped, approximated, or left implicit in a quantity presented as an enclosure of `F`.

The sign predicates may be invariant under this positive normalization, but recorded numerical enclosures must correspond to the normalized F quantity required by the model.

## 3. Singular patch: finite Duffy F expression

The exact singular square and Duffy maps remain

`P_eps = [0,eps] x [0,eps]`,

T1: `(c,phi) = (eps*x, eps*x*y_D)`,

T2: `(c,phi) = (eps*x*y_D, eps*x)`,

with

`rho = eps*x*g`, `g^2 = 1+y_D^2`,

and exact Duffy measure

`dc dphi = eps^2*x dx dy_D`.

Define

`J_F = rho * K_F`.

Then exact multiplication by the Duffy measure gives

`eps^2*x*K_F = (eps/g) * J_F`.

The transformed singular-patch contribution must therefore be evaluated through the finite expression

`(eps/g) * J_F`,

not by first constructing a literal corner quotient in `gamma_r` and multiplying by the Duffy Jacobian afterwards.

On children touching `x=0`, the same bounded extensions are permitted:

- `0 <= y_h <= 1`;
- `-1 <= v <= 1` when needed by shared helper logic;
- `0 <= z <= 1/sqrt(Z_DEN_LO)` with strict runtime-validated `Z_DEN_LO > 0`;
- child-specific finite enclosures of `U`, `L`, `A_hat`, `B_hat`, `M`, `h(gamma)`, and `h'(gamma)`.

The T1/T2 substitution discipline remains exact. Bounds from one triangle may not be reused for the other without an independently valid common lemma.

## 4. Regular children: per-subbox q lower bounds and sequential division remain binding

For every regular L2/L3 angular child, the implementation must recompute a strict child-specific

`q_lo(child) > 0`.

It may use the same exact decompositions as the L1 route, including

`q = W^2 + A + r^2 B`,

`q = (r-U)^2 + B + A`,

or a stronger separately audited exact lower-bound formula.

Although `K_F` can be evaluated directly from bounded `y_h` and `z`, any implementation path that reconstructs a negative power of `q` must obey the existing sequential-division rule. Compound midpoint-radius denominator balls such as `q*sqrt(q)` are forbidden before division.

A global root q floor may not replace a stronger child-specific lower bound. If strict positivity or finiteness cannot be established, the child must split under the deterministic adaptive policy or the candidate fails closed at budget exhaustion.

## 5. Per-box gamma and adaptive subdivision apply unchanged to F-route

A global numerical call to angle-data on `gamma in [0,1]` is forbidden for L2/L3 exactly as for L1.

Every F-route child must derive a child-specific gamma enclosure. If `h(gamma)` or `h'(gamma)` is non-finite or too wide, the route must deterministically refine the source/transformed angular child and/or use a recorded exact finite gamma subdivision whose hull encloses the full child range.

Adaptive refinement is part of the proof, not a performance option. Split triggers include at least:

- non-finite `h` or `h'` on the child gamma enclosure;
- failure of required `q_lo` or `Z_DEN_LO` positivity;
- non-finite `K_F`, `J_F`, or contribution enclosure;
- a contribution width that prevents the applicable L2/L3 predicate from being certified;
- persistence of root-global helper ranges on a separated child when tighter child-specific enclosures are needed for convergence.

Axis choice, tie breaking, maximum depth, evaluation/child budgets, child order, and first-failure semantics must be deterministic and config-bound before production.

## 6. L2 and L3 semantics

This correction changes the **evaluator**, not the mathematical predicates.

### 6.1 L2

Where the existing model requires an enclosure of `F(r,lambda)` for an L2 face/box, the exact `r` and `lambda` bounds supplied by that model are passed to the F-route. The checker must reject an L2 record whose proof route is direct pinned `F_arb`.

The F-route must return a finite canonical normalized enclosure sufficient to establish the existing strict L2 sign predicate. Failure to establish that predicate fails the candidate closed.

### 6.2 L3

The primary normative L3 evaluator is the same cancellation-free F-route, including at exact `r=1` when required by the existing L3 obligation.

The prior direct pinned `F_arb` route A is superseded and must not be used as certificate evidence.

An independently pinned identity route based on a boundary function such as `F(1,lambda)=B(lambda)` may be retained or implemented **only as a separately named cross-check** unless a later design audit explicitly promotes it to a coequal proof route. It may not act as an exception-driven fallback from the primary F-route, and its absence or disagreement may not be silently ignored.

This correction deliberately selects the F-route as the single production L3 evaluator so that L2 and L3 share one auditable finite enclosure architecture.

## 7. Symbolic-audit additions for F-route

Release readiness now additionally requires exact audit of:

1. the pinned F bracket after exact c-measure cancellation;
2. `W gamma_r = -L M y_h z^2` from `gamma_r = L N/q^(3/2)`, `N=-rho^2 M`, `y_h=W/sqrt(q)`, and `z^2=rho^2/q`;
3. `K_F = -U h(gamma) - L h'(gamma) M y_h z^2`;
4. for T1 and T2 separately, `J_F = rho*K_F`;
5. under `g^2=1+y_D^2`, exact transformed equality `eps^2*x*K_F = (eps/g)*J_F` after permitted denominator clearing and exact reduction;
6. the normalized root identity with the exact positive factor `1/pi`.

Items involving Duffy radicals must use the same exact Laurent/rational reduction discipline required by the revision addendum. Numerical substitution or self-reported Boolean markers are not accepted.

## 8. Record and checker additions for L2/L3

Every L2/L3 root record must bind at least:

- obligation ID (`L2` or `L3`) and route ID;
- exact model-supplied `r` and `lambda` bounds;
- exact normalized target quantity (`F`);
- angular root domain and exact partition policy ID;
- exact `eps` and Duffy route IDs where applicable;
- ordered child record IDs/hashes;
- outward-rounded unnormalized angular sum;
- exact `1/pi` normalization record;
- final canonical normalized F enclosure;
- exact strict sign predicate and pass/fail result;
- first fail-closed reason when false.

Every L2/L3 angular child must carry the same reconstructive fields required for L1 where applicable, including source/transformed box, gamma enclosure/subdivision, finite angle-data enclosures actually used, `q_lo` or `Z_DEN_LO`, helper enclosures, denominator policy, K_F/J_F enclosure, measure factor, final contribution, split reason, ordered descendants, and status.

The run/provenance record must bind the F-route source SHA-256 and the exact F-route symbolic-audit results in addition to the fields already required by the revision addendum.

The checker must independently reconstruct every accepted L2/L3 angular tree and its outward-rounded normalized F enclosure. A top-level sign field without the reconstructible child proof is insufficient.

## 9. Negative controls are all binding

The wording “existing fail-closed tests” in the revision addendum is hereby made explicit: **all previously enumerated negative controls plus the four new structural controls are required release tests**, not optional inherited examples.

The required set includes at least:

1. non-finite Arb => rejection;
2. nonpositive/nonseparating final strict lower or upper bound, as applicable => candidate rejection;
3. wrong T1/T2 substitution => rejection;
4. missing exact measure/Jacobian identity => rejection;
5. `Z_DEN_LO <= 0` => rejection;
6. direct corner `0/0` evaluation => rejection;
7. symbolic-audit failure => release-readiness rejection;
8. angular/L1 coverage gap => rejection;
9. unauthorized interior overlap beyond shared faces => rejection;
10. circular/transcendental patch replacing the exact dyadic square/Duffy construction => rejection;
11. invalid `u_cut` while that config field remains present => configuration rejection.

For L2/L3 specifically, the suite must also demonstrate that a record claiming direct pinned `F_arb` as its proof evaluator is rejected.

A negative-control test passes only when the mutated object is rejected for the intended reason.

## 10. eps = 2^-8 is a design value subject to readiness validation

The design retains

`eps = 2^-8`

as the intended exact dyadic singular-square size.

Its **mathematical definition is fixed for the next implementation attempt**, but production readiness requires an allowed pre-production runtime-readiness test to demonstrate that the production-shaped adaptive F/K routes can obtain finite enclosures and make progress under the fixed budgets with this exact eps.

If `eps = 2^-8` is not operationally viable, the implementation must not silently change it. That result returns the project to a separately audited design/config revision before production authorization.

Readiness success is not certificate evidence.

## 11. Provenance and sequencing for the F-4 correction

This correction file is the only path authorized in its correction commit. The already-audited revision addendum bytes and SHA-256 are preserved unchanged.

After this correction commit: **STOP for chat byte/code/math re-audit.** No implementation is authorized until the correction audit is GREEN.

After design GREEN, the reimplementation sequencing remains exactly:

1. complete implementation/checker/tests/symbolic-audit/policy bytes;
2. run only the tests/readiness checks authorized for that phase, including production-shaped F-route and K-route readiness at fixed `eps=2^-8`;
3. freeze final source bytes;
4. independently compute SHA-256 for every final source byte sequence;
5. materialize canonical config **last** from those exact final hashes;
6. independently recompute canonical config SHA-256;
7. create one implementation commit with the finalized implementation/config set and no unrelated changes;
8. STOP;
9. chat byte/code/math re-audit from committed bytes before any later smoke, workflow, tag, or production authorization.

Any post-freeze source-byte change invalidates the materialized config and requires rematerialization before the single implementation commit.

Workflow modification, tag creation, calibration, runtime smoke beyond explicitly authorized readiness, and production remain unauthorized. Tag creation still requires explicit user approval.

## 12. Current stopping point

Upon committing this correction, the project state is:

**B-LOCAL v2.2 F-4 DESIGN CORRECTION COMMITTED — IMPLEMENTATION UNAUTHORIZED — STOP FOR CHAT AUDIT.**
