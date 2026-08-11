# B-LOCAL v2.2 design revision addendum — RED step-2 recovery contract

**Status: DRAFT FOR CHAT BYTE/CODE/MATH AUDIT. DESIGN ONLY.**

This file supplements `BLOCAL_BENTRY_DEPENDENCY_DESIGN_V2_2.md` and `BLOCAL_BENTRY_DEPENDENCY_DESIGN_V2_2_ADDENDUM_DUFFY.md` after the step-2 implementation audit returned **RED**. It changes no implementation source, run config, dependency pin, workflow, tag, certificate, or prior incident record. The existing step-2 head `4e435b5562b72201601466c2b8b9066be81600c5` and its eight added files are retained as RED evidence and are not repinned.

Where this revision conflicts with the earlier v2.2 design or Duffy addendum on the L1 evaluation strategy, **this revision controls**. Earlier exact algebraic identities and the corrected Duffy measure/Jacobian identities remain in force unless explicitly superseded below.

No runtime smoke test, workflow change, tag creation, calibration start, or production run is authorized by this document.

## 0. RED disposition and preserved evidence

The step-2 audit is closed RED for three blockers and four must-fix design obligations.

### F-1 — source-byte/pin mismatch

The tree shape from design base `85f453d8b216e98ad9eadea54ab7a7dca1cc31fd` was structurally clean: eight new files and no pre-existing-file modification. The canonical config bytes also matched the previously reported Git blob and canonical SHA. However, four of seven newly pinned source files did not match the source SHA-256 values embedded in config. The observed mismatches were:

- `blocal_v22_checker.py`: observed `ea9245ab...`, pinned `cc4b9da4...`;
- `blocal_v22_checker_test.py`: observed `fb220e35...`, pinned `27fcd143...`;
- `blocal_v22_runner.py`: observed `cd288ad1...`, pinned `01b57f40...`;
- `blocal_v22_symbolic_audit.py`: observed `b3b95000...`, pinned `5825f5de...`.

`blocal_v22_boundary.py`, `blocal_v22_model.py`, and `blocal_v22_static_test.py` matched their reported pins. The static test at the RED head self-rejected on the checker pin. The RED head is preserved; this revision forbids repairing that evidence by silent repin.

### F-2 — current boundary route is not executable as specified

Chat-executed diagnostics established all of the following:

1. Passing the coarse helper-angle enclosure `gamma in [0,1]` to the current angle-data path makes `h''` non-finite. Splitting the gamma interval into at least two proper subintervals produced finite, sign-definite enclosures in the diagnostic probe. Since subdivision only in `(u,s)` does not narrow the coarse global gamma ball, a global `[0,1]` helper enclosure is not an executable contract.
2. On the regular route, forcing a positive floor into a `q` ball and then forming the product `qf * sqrt(qf)` is not interval-safe in Arb midpoint-radius arithmetic. A diagnostic case with positive lower endpoints about `4.98e-5` produced a product ball with lower endpoint about `-0.053`, after which division became non-finite. Computing the negative powers by **sequential division through separately positive denominator enclosures** remained finite in the same diagnostic setting.
3. After finite arithmetic was restored, the singular-patch enclosure radius stalled under uniform grid refinement: angular-grid powers `3/5/7` gave radii about `0.033/0.029/0.028`. The plateau is attributable to global helper bounds (`y`, `v`, `z`, and gamma) that do not contract with the source subbox.
4. Per-subbox denominator information materially changes the enclosure. In a diagnostic source subbox with `c_lo` about `0.5`, the usable `q` lower bound improved from about `5.0e-5` to about `0.82`.

These measurements are design evidence only, not certificate evidence.

### F-3 — the old interior-route premise is rejected

The earlier v2.2 design assumed that the pinned `dFdr_arb` path would be usable on `u >= u_cut`. Chat-executed diagnostics reject that premise.

The pinned `dFdr_arb` returned non-finite results on tested positive-width strips spanning examples from

- `u = [2^-13, 2^-12]`,
- `u = [2^-12, 2^-11]`,
- `u = [2^-9, 2^-8]`,
- through `u = [2^-5, 2^-4]`,

under tests including the configured absolute tolerance `2^-160`, looser tolerance `1e-12`, and depth limits including `16` and `24`. Recorded diagnostic calls were on the order of approximately `38` to `166` seconds. A point call at `r = 1 - 2^-8` also failed to produce a timely finite result in a diagnostic run exceeding about `140` seconds.

Therefore **`u_cut` is not a validity threshold for the pinned interior evaluator**. The previous statement “L1-INTERIOR uses existing pinned `dFdr_arb`” is superseded.

### M-1 through M-4

The RED audit additionally requires this revision to close:

- **M-1:** symbolic-audit obligations 6–9 were not all exact algebra/logical proofs;
- **M-2:** proof records lacked fields needed to reconstruct the actual adaptive enclosure path;
- **M-3:** the four required structural negative controls were not implemented;
- **M-4:** analytic helper inequalities such as `_bhat_lower` were comment-level assertions rather than runtime-verified strict prerequisites.

## 1. Revised L1 architecture: one K-route on the full u domain

The normative L1 obligation remains

`H_u(u,s) = -F_r(1-u, lambda_plus+s) > 0`

on the complete closed candidate rectangle

`0 <= u <= u_max`, `-s_neg <= s <= s_start`.

The L1 evaluator is now a **single cancellation-free K-route / rigorous angular ball-sum route over the full interval `0 <= u <= u_max`**.

The old evaluator split

- boundary strip -> regularized route,
- interior strip -> pinned `dFdr_arb`,

is abolished as an evaluator distinction. No L1 proof box may be certified merely because `u >= u_cut`, and no L1 record may cite the pinned `dFdr_arb` integral call as its proof enclosure.

The exact value `u_cut = 2^-12` may remain in the next config only as a validated dyadic **grid landmark / diagnostic partition coordinate** if useful for deterministic tiling and backward record reconstruction. It does not select a different mathematical evaluator. While the field remains present, `u_cut <= 0` or `u_cut > u_max` is a configuration error.

L2, L3, Stage-1 dependency, candidate order, `lambda_plus`, `s_neg`, pinned clean-room kernel bytes, canonical adapter semantics, fail-closed behavior, and tag-only execution authorization are not changed by this design revision.

## 2. Normative angular ball-sum contract

For each closed proof tile `T_us = U_box x S_box`, the implementation must construct a finite exact partition of the angular domain and certify an enclosure of the K-integral by summing rigorous per-angular-cell contribution enclosures.

After the exact `c = cos(theta)` measure cancellation already established in the Duffy addendum,

`sin(theta) K dtheta dphi = K dc dphi`.

Thus the source angular domain is

`D = [0,1] x [0,pi]` in `(c,phi)`.

The fixed exact singular square remains

`P_eps = [0,eps] x [0,eps]`, `eps = 2^-8`,

with the two Duffy triangles, and the regular complement remains exactly reconstructible from

`R1 = [eps,1] x [0,pi]`,

`R2 = [0,eps] x [eps,pi]`.

The proof contribution for a tile is the outward-rounded sum of all accepted angular child contributions. Acceptance requires a finite final canonical dyadic interval with strict positive lower endpoint for `H_u`; a missing child, non-finite child, budget exhaustion without proof, or nonpositive final lower endpoint fails the candidate closed.

No sampled quadrature value, midpoint estimate, floating summation, or silent fallback can enter proof evidence.

## 3. Per-box gamma contract; global [0,1] calls are forbidden

The exact SOS lemma in Section 8 implies the mathematical range `0 <= gamma <= 1` on the relevant domain, but this global range is **not** a permitted numerical evaluation box for `h'` or `h''`.

For every angular child, the implementation must derive a **child-specific gamma enclosure** from that child's current `(u,s,c,phi)` enclosure, or from the corresponding transformed Duffy child.

If evaluation of `h'` or `h''` on that child-specific gamma enclosure is non-finite or too wide to certify the contribution, the implementation must refine by one or both of the following exact operations, under fixed budgets:

1. subdivide the source/transformed angular child so that the induced gamma enclosure contracts;
2. subdivide the gamma enclosure itself into finitely many exact closed subintervals, evaluate the one-variable angle-data functions on every gamma subinterval, and take the rigorous union/hull needed by the parent child enclosure.

A call to angle-data with the coarse global ball `[0,1]` is forbidden in production proof evaluation. Gamma subdivision boundaries and resulting `h'`/`h''` enclosures must be recorded.

The implementation must not infer finiteness from the fact that gamma is mathematically bounded; Arb finiteness is an explicit proof-engine prerequisite.

## 4. Positive denominators: per-subbox lower bounds and sequential division

### 4.1 Per-subbox q lower bound is mandatory

Every regular angular child must establish a child-specific strict positive lower bound

`q_lo(child) > 0`

before evaluating any negative power of `q`.

The lower bound must be recomputed from the current child box. It may use the exact identities

`q = W^2 + A + r^2 B`,

`q = (r-U)^2 + B + A`,

or a stronger exact lower-bound formula independently justified and pinned by the symbolic/runtime audit. A global floor inherited from the root angular domain is insufficient when a stronger child-specific bound is available.

If strict positivity cannot be proved on a regular child, that child must be subdivided. If the budget is exhausted, the candidate fails closed. A regular child may not silently switch to an unrecorded alternate formula.

### 4.2 Product denominators are forbidden

Once a strict positive enclosure for `q` is available, the implementation must **not** form a product denominator such as

`q_ball * sqrt(q_ball)`

and then divide by that product ball. Positive lower endpoints of the individual Arb balls do not guarantee that midpoint-radius multiplication preserves a positive lower endpoint tightly enough for this purpose.

Negative powers must be evaluated by a documented **sequential-division / sequential-reciprocal route** using separately verified positive denominator enclosures. For example, a term algebraically equal to

`N / (q sqrt(q))`

must be enclosed by operations equivalent to

`tmp = N / q_pos`,

`result = tmp / sqrt(q_pos)`,

where `q_pos` is a rigorously constructed enclosure of the same mathematical `q` whose lower endpoint is certified strictly positive. Analogous sequential rules apply to higher negative powers.

No artificial floor may exclude any possible value of the mathematical `q`. The per-subbox proof must establish that the chosen positive lower endpoint is a true lower bound before the denominator enclosure is constructed.

## 5. Adaptive angular subdivision is part of the proof contract

Uniform fixed-power angular gridding is no longer sufficient as the normative L1 algorithm.

Each proof tile must use deterministic, budgeted adaptive subdivision in the angular variables. The decision rule must be fixed before the production run and recorded by policy ID. At minimum, a child must be eligible for subdivision when any of the following holds:

- `h'` or `h''` is non-finite on the induced gamma enclosure;
- `q_lo <= 0` on a regular child;
- the K/J/contribution enclosure is non-finite;
- the contribution width prevents the parent ball-sum from proving strict positivity;
- a helper bound remains at a global fallback range although the child is separated from the singular corner and a tighter direct enclosure is available.

The subdivision policy must specify deterministic axis choice, tie breaking, maximum depth, child/evaluation limits, and first-failure semantics. The same inputs and config must reconstruct the same proof tree.

### 5.1 Singular Duffy children

On Duffy children touching the singular corner, the bounded extensions

- helper `y_h in [0,1]`,
- helper `v in [-1,1]`,
- helper `z in [0,1/sqrt(Z_DEN_LO)]`,

remain legal fail-safe bounds. Here `y_h = W/sqrt(q)`; it is distinct from the second Duffy square coordinate, which records must call `y_D` (or an equivalently unambiguous field name).

Away from the exact corner face, the implementation must use child-specific finite enclosures for these helpers whenever doing so tightens the proof. It may not force every descendant to retain the root global helper bounds, because that defeats convergence under subdivision.

`Z_DEN_LO` must be recomputed on the actual transformed child with the correct T1/T2 substitution. T1 bounds may not be reused for T2 or conversely.

### 5.2 Regular children

Regular children use the cancellation-free K expression and the sequential denominator rules of Section 4. The direct pinned integral routine is not called. The pinned kernel remains the formula provenance source, while exact symbolic audit establishes equivalence of the rewritten K-route to the pinned derivative formula wherever the latter is finite.

## 6. Runtime validation of analytic helper inequalities — closes M-4

Every analytic helper inequality used to manufacture a strict bound must be represented by a named audit/lemma ID and must be verified **before candidate evaluation begins** using exact algebra where possible and rigorous Arb enclosure over its declared parameter domain where an analytic interval inequality is required.

This requirement includes `_bhat_lower` and every analogous lower/upper helper used for `A_hat`, `B_hat`, `Z_DEN_LO`, `q_lo`, or transformed finite extensions.

The run-start validation stage must record, for each helper lemma:

- lemma/audit ID;
- exact declared domain;
- precision;
- rigorous enclosure of the residual or bound quantity;
- required sign relation;
- pass/fail status.

If any required strict inequality cannot be verified, the run terminates before evaluating a candidate. Comment assertions, developer knowledge, floating probes, or tests at sample points are not substitutes.

## 7. Symbolic audit revision — closes M-1

The symbolic audit is a release prerequisite, not a self-reported flag. Items 1–5 of the corrected Duffy addendum remain exact-algebra obligations. Items 6–9 are revised as follows.

### 7.1 Obligation 6 — Duffy Jacobians

For T1 and T2 separately, construct the symbolic Jacobian matrices of

T1: `(c,phi) = (eps*x, eps*x*y_D)`,

T2: `(c,phi) = (eps*x*y_D, eps*x)`,

and prove algebraically that the absolute determinant is `eps^2*x` on `0 <= x <= 1`. Numeric substitution is forbidden. The audit result must be derived from the symbolic determinant expression.

### 7.2 Obligation 7 — measure cancellation is a logical lemma

The statement

`sin(theta) dtheta = -dc`, `c = cos(theta)`, `theta in [0,pi/2]`,

is treated as a separate exact logical/analytic lemma, not as a polynomial “exact-zero” marker. The audit must encode the hypotheses `sin(theta) >= 0` and `sin(theta) = sqrt(1-c^2)` on the declared branch and verify that reversing the exact c-integration limits removes the minus sign. Release readiness fails if this lemma is absent or merely asserted by a Boolean constant.

### 7.3 Obligations 8 and 9 — exact Laurent/radical reduction

For each triangle separately, introduce an auxiliary symbol `g` for the only square-root factor in the Duffy geometry, with the exact relation

`g^2 = 1 + y_D^2`.

Obligation 8 must prove

`rho = eps*x*g`

under the triangle-specific substitution.

Obligation 9 must prove that multiplication of `K` by the exact Duffy measure `eps^2*x` equals

`(eps/g) * J`,

using `J = rho*K` and `rho = eps*x*g`, on the algebraic domain where the original expressions are defined.

The implementation must clear only mathematically nonzero symbolic denominators allowed by the declared domain, reduce the resulting Laurent/rational numerator modulo `g^2-(1+y_D^2)`, and require exact zero. Numerical substitutions are not accepted as proof.

The audit artifact must expose the unreduced expression, denominator-clearing factors, reduced numerator, and exact-zero result for independent inspection.

## 8. New exact SOS lemma for gamma — GREEN result retained

The following identity is a normative symbolic lemma and must be added to the exact audit:

`w^2 q - lambda^2 W^2`

`= (c S (lambda^2-1) + r c cos(phi))^2`

`  + r^2 sin(phi)^2 w^2`.

The chat audit independently reduced the two sides to exact equality. On the declared B-LOCAL domain the right-hand side is a sum of squares. Together with the existing sign/domain hypotheses, this establishes the exact gamma bound used by the regularized architecture.

The symbolic audit must prove the identity by exact polynomial/radical elimination against the pinned variable definitions; it may not accept a numerical sample or a pre-set success flag.

**Important:** the lemma establishes the mathematical range of gamma. It does not authorize evaluating `h'` or `h''` on the single global Arb ball `[0,1]`; Section 3 remains normative.

## 9. Required machine-readable records — closes M-2

Every accepted or rejected L1 proof tile must expose enough information for the checker to reconstruct the complete adaptive proof tree and the final ball-sum without rerunning hidden policy decisions.

### 9.1 Root proof-tile fields

Each `(u,s)` root tile record must contain at least:

- schema/version and record type;
- candidate ID and deterministic candidate-order index;
- exact `u` bounds;
- exact `s` bounds;
- exact derived `r=1-u` bounds;
- exact derived `lambda=lambda_plus+s` bounds;
- L1 route ID identifying the full-domain K-route;
- angular-partition policy ID;
- gamma-subdivision policy ID;
- denominator policy ID identifying sequential division;
- configured depth/evaluation/child limits;
- root angular domain and exact singular-square parameters;
- ordered list/hash of child contribution records;
- outward-rounded ball-sum enclosure before canonicalization;
- canonical dyadic final enclosure;
- strict-positivity result;
- first fail-closed reason when false.

### 9.2 Every angular child

Every angular child record must contain at least:

- stable child/path ID and parent ID;
- depth and deterministic split reason;
- source region ID (`P_eps/T1`, `P_eps/T2`, `R1`, or `R2` descendant);
- exact source `(c,phi)` box, or exact transformed `(x,y_D)` box plus reconstruction data;
- exact `u`, `s`, `r`, and `lambda` bounds inherited by the child;
- T1/T2 substitution ID when transformed;
- exact patch/Jacobian/measure factor data where applicable;
- child-specific gamma enclosure;
- gamma subdivision boundaries, if used;
- finite `h'` and `h''` enclosures actually used;
- exact `q` enclosure and named formula used to prove `q_lo`;
- strict `q_lo` value for every regular child;
- denominator-construction policy and intermediate sequential-division enclosure IDs;
- `Z_DEN_LO` and its lemma ID for singular children;
- helper `y_h`, `v`, `z`, `A_hat`, `B_hat`, and `M` enclosures actually used;
- K or J enclosure as applicable;
- exact source measure/Jacobian multiplier;
- final contribution enclosure;
- child status (`ACCEPTED`, `SPLIT`, or `FAILED`);
- ordered child IDs if split;
- first fail-closed reason if failed.

### 9.3 Run/provenance fields

The run record must additionally bind:

- pinned clean-room kernel path and SHA-256;
- every proof-source path and final SHA-256;
- symbolic-audit path and final SHA-256;
- checker path and final SHA-256;
- canonical config SHA-256;
- config Git blob SHA when reported;
- exact helper-lemma validation records from Section 6;
- exact SOS-lemma audit result;
- exact obligations 6–9 audit results;
- adaptive-policy IDs and budgets;
- total accepted/split/failed child counts and maximum reached depth;
- terminal state.

The checker must reject records that omit a field required to reconstruct the accepted enclosure path.

## 10. Mandatory structural negative controls — closes M-3

The implementation/checker test suite must include and demonstrate rejection of these four structural mutations:

1. **gap:** remove or shift a child boundary so the closed angular or L1 domain is not completely covered;
2. **overlap:** enlarge child interiors so they overlap beyond permitted shared faces;
3. **circular/transcendental patch:** replace the exact dyadic square/Duffy patch by a circular or transcendental-boundary patch;
4. **invalid `u_cut`:** while the field remains in config as a grid landmark, set `u_cut <= 0` or `u_cut > u_max`.

These are in addition to the existing fail-closed tests for non-finite Arb, nonpositive final lower bounds, wrong T1/T2 substitution, missing measure/Jacobian identity, `Z_DEN_LO <= 0`, direct corner `0/0`, and symbolic-audit failure.

A negative-control test passes only when the mutated object is rejected for the intended reason; merely observing an exception elsewhere is insufficient.

## 11. Checker obligations under the revised architecture

The checker must independently reconstruct:

1. the complete closed `(u,s)` coverage of L1;
2. for every root tile, the complete angular domain `D` from its recorded adaptive children;
3. the exact Duffy-square reconstruction from T1/T2 descendants;
4. the absence of gaps and unauthorized interior overlaps;
5. the ordered outward-rounded sum of accepted contribution enclosures;
6. the canonicalization of the root enclosure;
7. strict positive lower bounds for every root tile needed for L1 PASS;
8. all required source/config/audit pins.

There is no longer a semantic requirement for “boundary PASS plus interior PASS”. The revised semantic requirement is **full L1 closed-domain PASS under one K-route**, even if deterministic bookkeeping retains `u_cut` as a tile boundary.

First-passing candidate semantics and candidate order remain unchanged.

## 12. Fail-closed prohibitions

The following are forbidden:

- repinning the frozen RED head as if it were valid evidence;
- using pinned `dFdr_arb` as the L1 integral evaluator;
- evaluating angle-data on the global gamma ball `[0,1]`;
- multiplying positive denominator balls into `q*sqrt(q)` or analogous compound denominator balls before division;
- using a global root `q` floor in place of a child-specific certified lower bound;
- retaining global helper ranges on all descendants when a separated child admits tighter finite bounds needed for convergence;
- exception suppression or exception-driven formula fallback;
- decimal-string or binary-float proof paths;
- `1-epsilon` endpoint substitution;
- changing the pinned clean-room kernel bytes;
- using numerical symbolic-audit substitutions as exact proof;
- proceeding after a missing source SHA, non-finite enclosure, incomplete coverage, or budget exhaustion.

## 13. Provenance and sequencing after this design revision

### 13.1 This design revision

This file is the only file authorized in the design-revision commit. After the commit: **STOP for chat byte/code/math audit.** No implementation work is authorized until that audit is GREEN.

The audit must independently verify:

- exactly one commit from frozen head `4e435b5562b72201601466c2b8b9066be81600c5`;
- this addendum is the only changed path;
- no pre-existing bytes changed;
- the addendum SHA-256 from actual GitHub bytes;
- the normative requirements in Sections 1–12.

### 13.2 Reimplementation only after design GREEN

After separate design-audit GREEN, reimplementation may occur, but the final publishable implementation state must follow this exact order:

1. complete all implementation, checker, test, symbolic-audit, and policy source bytes first;
2. execute the required local/static/runtime-readiness tests allowed for that phase;
3. freeze the final source bytes;
4. independently compute SHA-256 for every final source byte sequence;
5. **materialize the canonical config last**, using those exact final SHA-256 values;
6. independently recompute the canonical config SHA-256 from the materialized bytes;
7. create **one implementation commit** containing the finalized implementation/config set and no unrelated change;
8. **STOP**;
9. perform chat byte/code/math re-audit from the actual committed bytes before any later smoke/production authorization.

If any source byte changes after step 3 or after config materialization, the config is invalid and must be rematerialized from the new final bytes before the single implementation commit is created. A follow-up “pin correction” commit is not an accepted substitute for this sequencing.

Workflow modification, tag creation, and production execution remain separately unauthorized. Tag creation continues to require explicit user approval.

## 14. Current stopping point

Upon committing this addendum, the project state is:

**B-LOCAL v2.2 DESIGN REVISION COMMITTED — IMPLEMENTATION UNAUTHORIZED — STOP FOR CHAT AUDIT.**
