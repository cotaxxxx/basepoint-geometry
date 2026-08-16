# B-LOCAL v2.2 design revision addendum — L3 boundary monotonicity route

**Status: DRAFT FOR CHAT BYTE/CODE/MATH AUDIT. DESIGN ONLY.**

This addendum supplements `BLOCAL_BENTRY_DEPENDENCY_DESIGN_V2_2_REVISION_ADDENDUM.md` and `BLOCAL_BENTRY_DEPENDENCY_DESIGN_V2_2_REVISION_ADDENDUM_F4_CORRECTION.md` after the first authorized production-shaped B-LOCAL v2.2 run exposed L3 as the unique runtime bottleneck.

This file changes no implementation source, run configuration, dependency pin, workflow, tag, certificate, prior run artifact, or frozen incident evidence. It authorizes no production run, calibration run, workflow change, tag creation, or implementation change by itself.

Where the F-4 correction selects the cancellation-free F-route as the primary normative L3 evaluator, **this addendum supersedes that evaluator choice for L3 only**. The mathematical L3 obligation, the L2 evaluator, L1 architecture, Stage-1 dependency identity, candidate order, `lambda_plus`, `s_neg`, first-passing semantics, canonical fail-closed semantics, J_START contract, and all unrelated v2.2 obligations remain unchanged unless explicitly stated below.

## 0. Triggering evidence and scope of the revision

The mathematical L3 obligation remains exactly

`H(0,s) < 0` for every `s in [0,s_start]`,

with

`H(u,s) = F(1-u, lambda_plus+s)`.

Thus at the boundary face `u=0`,

`H(0,s) = F(1,lambda_plus+s)`.

The first authorized production-shaped run reached candidate 0, certified L1 and L2 quickly, entered L3, and remained inside the first L3 proof call until the GitHub Actions wall-time limit cancelled the run. Diagnostic replay then showed that point and positive-width F-route enclosures near `s=0` consume the configured inner budget without separating the required negative sign. This is not a change to the mathematical obligation; it is evidence that the selected L3 evaluator is not operationally suitable near the Stage-1 boundary endpoint.

The correct incident statement is:

> Readiness and ladder diagnostics had certified endpoint or selected-point conditions but had not exercised the complete L3 interval obligation `[0,s_start]`. The production run was the first production-shaped test of that full interval obligation.

No statement of mathematical impossibility is made. The established operational conclusion is narrower:

> The true L3 endpoint margin at `lambda_plus` is of order `10^-6`; under the current F-route enclosure widths and fixed budgets, direct interval certification through the endpoint is not practically closing.

This addendum replaces only the L3 proof architecture.

## 1. Existing exact Stage-1 endpoint dependency

The canonical Stage-1 dependency remains unchanged:

- source head: `b0582728d3f8fd3508ba8574a898017212a28caa`;
- certificate path: `CERTIFICATES/prolate/item2_branch/independent_recheck/certificate_item2_independent.json`;
- certificate SHA-256: `d7a1d0764dd1138a59090e53f1e601c58c703f2d34c0c16eb4b2c4f3f4539188`;
- inner manifest SHA-256: `f15d01b410a53ad14dd86688cb7a8a86bf6ef85b108d1d3822840bb0a97bc069`;
- Stage-1 exact upper endpoint:
  `lambda_plus = 206539/100000`.

The certified Stage-1 statement includes the strict endpoint sign

`B(206539/100000) < 0`.

The certified rigorous enclosure recorded in the Stage-1 certificate is

`B(lambda_plus) in [-1.989245103410365999127431e-6, -1.385410863023463633555844e-6]`.

The same certificate proves `B'(lambda)<0` only on the original Stage-1 bracket `[206538/100000,206539/100000]`. This addendum does **not** reinterpret that old derivative certificate as covering any point to the right of `lambda_plus`.

The Stage-1 endpoint value is inherited evidence. It is not recomputed by the v2.2 L3 runner.

## 2. Boundary identity promoted to normative L3 use

The boundary-entry function is

`B(lambda) = F(1,lambda)`.

This identity already underlies the Stage-1 boundary-entry certificate and the prior B-LOCAL endpoint design. F-4 retained an identity route only as a cross-check unless a later design audit promoted it.

This addendum performs that promotion for L3.

The normative identity lemma ID is

`BLOCAL_L3_BOUNDARY_IDENTITY_B_EQ_F_R1_V1`.

For L3 only, the checker may conclude

`H(0,s) = B(lambda_plus+s)`

provided that all of the following are verified:

1. the exact coordinate identity `H(0,s)=F(1,lambda_plus+s)` is reconstructed from the B-LOCAL model;
2. the Stage-1 boundary function is the pinned `B(lambda)=F(1,lambda)` object from the audited independent re-derivation;
3. the Stage-1 certificate, source head, manifest, and payload pins match the committed dependency descriptor;
4. the exact contact-centred change-of-variables identities used by Stage-1 are replayed from the pinned symbolic audit source or an independently pinned equivalent audit;
5. no alternate boundary implementation, sampled function, floating surrogate, or vendor-only approximation is substituted.

The identity audit is algebraic in `lambda`; it is not licensed merely by the old numerical Stage-1 bracket. Before production, the release audit must verify that every denominator/radical/domain hypothesis needed to use the identity is valid on the actual extended candidate domain required by Section 4.1.

Failure of any identity/provenance prerequisite makes L3 fail closed.

## 3. New normative L3 proof route

The normative L3 route ID is

`BLOCAL_L3_STAGE1_ENDPOINT_PLUS_BPRIME_MONOTONICITY_V1`.

The normative inference ID is

`BLOCAL_L3_MONOTONICITY_FROM_ENDPOINT_V1`.

For one candidate with exact

`lambda_start = lambda_plus + s_start`, `s_start > 0`,

L3 is certified from exactly two mathematical ingredients:

1. the existing Stage-1 endpoint certificate

   `B(lambda_plus) < 0`;

2. a new rigorous derivative enclosure proving

   `B'(lambda) < 0`

   for every

   `lambda in [lambda_plus,lambda_start]`.

By monotonicity,

`B(lambda) <= B(lambda_plus) < 0`

for every `lambda in [lambda_plus,lambda_start]`. Therefore

`H(0,s) = B(lambda_plus+s) < 0`

for every `s in [0,s_start]`, which is exactly the existing closed-domain L3 obligation.

The endpoint `s=0` is not removed, perturbed, opened, or replaced by a positive cutoff. No gap is introduced and no theorem statement is weakened.

## 4. The derivative route is a Stage-1 dependency extension, not a v2.2 native quantity

The v2.2 native boundary engine currently has production quantities `F` and `H_U`. This addendum does **not** add a native `F_LAMBDA`, `BPRIME`, or third chart/jet quantity to that engine.

Instead, the derivative proof is an explicitly separate Stage-1-derived dependency route using the already audited independent file

`CERTIFICATES/prolate/item2_branch/independent_recheck/bprime_independent.py`.

Its canonical payload SHA-256 from `config.blocal-stage1.json` is

`f5f2fe68773423e7ff037e4be9e31094a4ceff5489abd5aff8b14fc1361cd671`.

The file must be imported byte-identically from the pinned Stage-1 dependency material. It may not be copied, rewritten, patched, monkey-patched, or reimplemented inside the v2.2 native boundary module.

The existing implementation differentiates forward in `lambda` with a Dual object over rigorous `acb` balls; finite differences are not used. Its callable

`Bprime(lam_ball, bands, rel_tol, eval_limit, depth_limit)`

accepts a general lambda ball. The old Stage-1 bracket is fixed only by its standalone driver, not by the callable itself.

A production wrapper must set the pinned runtime precision, initialize module constants with `_init_consts()`, construct the exact candidate interval ball, call the unmodified `Bprime`, and pass the rigorous real enclosure to the canonical outward interval-record path.

### 4.1 Mandatory extended-domain validity audit

Reusing an audited function on a wider lambda interval is not justified merely because the callable accepts a wider ball or because a diagnostic run returned a finite answer.

The release prerequisite therefore includes the audit ID

`BLOCAL_L3_BPRIME_EXTENSION_DOMAIN_AUDIT_V1`.

For each maximal lambda domain that will be admitted by a production config, this audit must verify the hypotheses of the pinned contact-centred B/B-prime formulas on

`t in [0,1]`, `psi in [0,pi/2]`, `lambda in [lambda_plus,lambda_max]`.

At minimum it must establish, by exact algebra and/or rigorous Arb enclosure as appropriate:

- `lambda > 1` on the full domain;
- positivity and nonvanishing of every denominator/radical argument used by the contact-centred formula, including the required `A` and `W` factors;
- validity of the real angle-data domain and every analytic branch assumption used to evaluate `h`, `h'`, and `h''`;
- validity of the exact change-of-variables identities connecting the Stage-1 B integrand to `F(1,lambda)`;
- absence of a new singularity or branch crossing on the extended lambda interval.

The existing symbolic `verify_change_of_variables.py` identities are admissible provenance for the algebraic equalities because they are symbolic in positive `lambda`, but their domain hypotheses must still be checked on the newly admitted interval.

A finite diagnostic B-prime result cannot substitute for this domain audit. Failure of the audit prevents the derivative route from being used as certificate evidence.

### 4.2 Inherited Stage-1 float branch guards

The pinned `bprime_independent.py` contains Python `float` conversions in narrow internal control-flow guards used to select between rigorous analytic representations of the angle data and to reject unresolved branch-cut separation. Those bytes are part of the already audited Stage-1 payload and are not modified here.

This addendum admits those **inherited guards only**, under the audit ID

`INHERITED_STAGE1_ANALYTIC_BRANCH_GUARDS_V1`.

They may influence only which rigorous representation is attempted. They may not supply or round:

- lambda interval endpoints;
- B or B-prime enclosure endpoints;
- derivative sign decisions;
- candidate selection;
- coverage decisions;
- canonical record values.

The wrapper and all new v2.2 L3 code are forbidden from introducing any new binary-float numeric path into those proof decisions. The final strict sign is judged only from the rigorous `acb/arb` enclosure converted outward through the canonical interval path.

The release audit must verify from the pinned source bytes that the admitted float use is limited to the inherited representation/branch guards and that no float-derived quantity is used as proof evidence. Any new float path or any use of a float result to assert `B'<0` is rejected.

## 5. Fixed derivative policy and candidate domain

The derivative policy ID is

`BLOCAL_L3_BPRIME_STAGE1_POLICY_V1`.

For the first implementation attempt under this design, the derivative policy is inherited from the certified Stage-1 B-prime run unless a later audited config revision changes it explicitly:

- `python-flint = 0.9.0`;
- `dps = 18`;
- `bands = 4`;
- `rel_tol = 2^-18`;
- `eval_limit = 8000`;
- `depth_limit = 22`.

The exact candidate derivative domain is always reconstructed as

`[lambda_plus, lambda_start]`.

For the current first production candidate,

`lambda_start = lambda_plus + 2^-9 = 3307749/1600000`.

A diagnostic run using the unmodified pinned `bprime_independent.py` on this full interval returned a strictly negative total enclosure with substantial separation from zero. The diagnostic used the same `dps`, band count, tolerance, evaluation limit, and depth limit as the Stage-1 B-prime driver. This diagnostic is **design evidence only** until preserved as one continuous run artifact satisfying Section 6.

If a later candidate is attempted, its L3 derivative domain is its own exact `[lambda_plus,lambda_start]`. Evidence for a smaller candidate interval may not be reused for a larger interval unless the recorded derivative proof domain already contains the larger interval.

Lambda subdivision is permitted only as an explicit deterministic proof partition if one whole-interval call is unresolved. If subdivision is used, the closed union must equal `[lambda_plus,lambda_start]` exactly, with no gap or unauthorized enlargement. A whole-interval proof is preferred and requires only one derivative root record.

## 6. Mandatory one-process readiness evidence before implementation promotion

Before this route may be promoted from design to implementation-ready, one continuous readiness run must execute the pinned derivative module on the first production candidate interval

`[lambda_plus, lambda_plus+2^-9]`

in a **single process**.

The run must:

1. verify the pinned Stage-1 archive/dependency member bytes before import;
2. verify `BLOCAL_L3_BPRIME_EXTENSION_DOMAIN_AUDIT_V1` for the admitted readiness interval;
3. set the required `ctx.dps`;
4. call `_init_consts()` before `Bprime`;
5. construct the exact interval endpoints without binary-float parsing;
6. execute all four psi bands in one process under `BLOCAL_L3_BPRIME_STAGE1_POLICY_V1`;
7. preserve every band enclosure and the final summed enclosure;
8. require the final rigorous upper endpoint to be strictly `< 0`;
9. record wall time and the exact runtime dependency versions;
10. record source SHA-256, Stage-1 descriptor SHA-256, exact lambda domain, policy parameters, and admitted branch-guard audit ID;
11. mark the artifact as readiness/design evidence, not yet as a B-LOCAL production certificate.

The earlier split-process diagnostic is sufficient to motivate this design but is not the production proof artifact.

If the one-process readiness result is non-finite, unresolved, has upper endpoint `>=0`, or fails the extended-domain validity audit, implementation promotion stops and the project returns to design review.

## 7. Production L3 record structure

A successful L3 proof for one candidate must bind both inherited endpoint evidence and new derivative evidence.

The top-level L3 record must include at least:

- `node = "L3"`;
- route ID `BLOCAL_L3_STAGE1_ENDPOINT_PLUS_BPRIME_MONOTONICITY_V1`;
- identity lemma ID `BLOCAL_L3_BOUNDARY_IDENTITY_B_EQ_F_R1_V1`;
- inference ID `BLOCAL_L3_MONOTONICITY_FROM_ENDPOINT_V1`;
- candidate index;
- exact `lambda_plus`;
- exact `s_start`;
- exact `lambda_start`;
- exact reconstructed s-domain `[0,s_start]`;
- Stage-1 dependency descriptor identity;
- Stage-1 certificate SHA-256;
- reference/hash for the inherited `B(lambda_plus)<0` evidence;
- exact certified endpoint enclosure for `B(lambda_plus)`;
- derivative source SHA-256;
- derivative policy ID and exact parameters;
- extended-domain audit ID/result;
- inherited branch-guard audit ID/result;
- exact derivative proof domain `[lambda_plus,lambda_start]`;
- ordered derivative interval proof records, one when no subdivision is used;
- final rigorous derivative enclosure or exact hull of the complete derivative partition;
- explicit predicate `Bprime_upper < 0`;
- final claim `H(0,s)<0 on [0,s_start]`;
- certified state and first fail-closed reason when false.

The monotonicity inference is logical evidence, not a new numerical enclosure of B over the whole interval. The checker must not require the v2.2 F-route to numerically re-enclose `F(1,lambda)` after the endpoint and derivative prerequisites have been certified.

## 8. Derivative child/partition records

If one whole lambda ball certifies `B'<0`, the record must expose that exact whole interval and its rigorous result.

If deterministic lambda subdivision is required, every derivative leaf must include at least:

- exact closed lambda interval;
- interval order/index;
- `Bprime` rigorous enclosure;
- exact upper and lower canonical endpoints;
- strict-negative result;
- policy parameters;
- source/provenance identities;
- previous/record hash fields required by the existing chain architecture.

The checker must reconstruct exact closed-union coverage of `[lambda_plus,lambda_start]`. Shared endpoints are allowed; gaps, inversions, missing leaves, duplicate interiors, or unrecorded enlargement are rejected.

No pointwise derivative samples can replace interval derivative leaves.

## 9. Checker obligations

The independent checker must verify at least all of the following before L3 PASS:

1. the candidate index and exact `lambda_start` agree with the deterministic candidate schedule;
2. `s_start = lambda_start-lambda_plus` exactly;
3. the required L3 domain remains exactly `[0,s_start]`;
4. the Stage-1 dependency has status `STAGE1_CONTENT_AUDITED` and all pinned source/certificate/manifest identities match;
5. the inherited endpoint evidence proves a strict negative upper bound for `B(lambda_plus)`;
6. the boundary identity lemma applies to the exact B-LOCAL and Stage-1 quantities;
7. `BLOCAL_L3_BPRIME_EXTENSION_DOMAIN_AUDIT_V1` covers the full derivative domain;
8. the derivative source is the pinned `bprime_independent.py` dependency member;
9. only the inherited branch guards admitted by `INHERITED_STAGE1_ANALYTIC_BRANCH_GUARDS_V1` are present; no new float proof path exists;
10. the derivative proof domain exactly covers `[lambda_plus,lambda_start]`;
11. every derivative proof enclosure is finite and has strict upper endpoint `<0`;
12. the complete derivative partition, if any, has exact closed-union coverage with no gap;
13. the monotonicity inference is applied in the correct direction: `B' < 0` and `lambda >= lambda_plus` imply `B(lambda) <= B(lambda_plus)`;
14. the final L3 claim is the unchanged `H(0,s)<0` on the complete closed interval `[0,s_start]`;
15. no direct F-route sign result is required or silently substituted for a missing endpoint or derivative prerequisite;
16. no sampled derivative, finite difference, float-derived sign/enclosure endpoint, or manually inserted sign flag is accepted as L3 proof evidence.

A valid-looking top-level L3 summary without reconstructible endpoint and derivative evidence is rejected.

## 10. Binding negative controls

The release test suite must demonstrate rejection of at least these mutations:

1. missing Stage-1 `B(lambda_plus)<0` evidence;
2. Stage-1 endpoint enclosure whose upper endpoint is `>=0`;
3. wrong Stage-1 certificate, source head, manifest, or payload pin;
4. missing or wrong `B(lambda)=F(1,lambda)` identity/provenance record;
5. missing or failing extended-domain validity audit;
6. derivative proof domain beginning at a value strictly greater than `lambda_plus`;
7. derivative proof domain ending before the candidate's exact `lambda_start`;
8. derivative interval with upper endpoint `>=0`;
9. one missing derivative subdivision leaf;
10. a gap between derivative subdivision leaves;
11. an unauthorized overlap with inconsistent duplicate interior coverage;
12. reuse of derivative evidence from a smaller candidate for a larger uncovered candidate;
13. candidate index or `lambda_start` mismatch;
14. sampled or finite-difference B-prime evidence;
15. source bytes differing from the pinned `bprime_independent.py` member;
16. omission of required `_init_consts()`/runtime initialization provenance in a production wrapper record;
17. introduction of any new float-valued proof-decision path outside the byte-identical inherited Stage-1 representation/branch guards;
18. use of an inherited float guard value itself as a B-prime sign or enclosure endpoint;
19. monotonicity inference with the inequality direction reversed;
20. replacement of `[0,s_start]` by `[s_min,s_start]` with `s_min>0`;
21. direct insertion of a final L3 PASS flag without complete endpoint/derivative evidence.

A negative-control test passes only when the checker rejects the mutation for the intended reason.

## 11. Relationship to the F-route and other nodes

The cancellation-free F-route remains normative for L2 and for every other obligation that still requires it under the F-4 and F-5 corrections.

For L3, the F-route becomes non-normative diagnostic/cross-check evidence. It may be run for comparison, but:

- its absence does not prevent L3 PASS when the endpoint-plus-monotonicity route is complete;
- its failure or unresolved result does not override a valid endpoint-plus-monotonicity proof;
- disagreement with the boundary route is a hard diagnostic stop requiring investigation before release, not a silent route selection rule.

No exception-driven fallback is permitted in either direction.

The J_START evaluator remains governed by the F-5 correction and is not changed here.

## 12. Candidate and budget semantics

The deterministic candidate order and first-passing semantics remain unchanged.

L1 and L2 are evaluated under their existing policies. L3 is evaluated only when the candidate reaches L3 under the normal runner order. The L3 derivative work must have its own explicit route budget/policy accounting and must not be hidden inside the old F-route outer-cell budget.

A complete `Bprime` root call counts according to the new L3 derivative policy to be fixed in implementation/config. Internal `acb.integral` evaluations remain governed by the fixed Stage-1-derived `eval_limit` and `depth_limit` parameters.

Budget exhaustion or non-finite derivative output fails the candidate closed. Increasing the derivative budget, changing precision, changing band count, or changing tolerance after freeze requires an audited config/design update as applicable.

## 13. Sequencing and authorization boundary

The required sequence is:

1. commit this design addendum only; **STOP for chat byte/code/math audit**;
2. obtain GREEN on this design;
3. execute and preserve the mandatory one-process readiness run from Section 6 under separately authorized diagnostic/readiness mechanics;
4. audit that readiness artifact; if not strictly negative, STOP and return to design;
5. after separate approval, implement only the L3 wrapper/record/checker/config changes required by this addendum, leaving the pinned Stage-1 derivative module byte-identical;
6. add the binding negative controls and run the authorized tests/readiness checks;
7. freeze final source bytes, materialize config pins last, and commit the finalized implementation set;
8. **STOP for chat byte/code/math audit**;
9. only after GREEN may a later production tag/run be proposed.

Workflow creation/change, tag creation, calibration, production execution, Stage-1 source modification, and silent config changes are not authorized by this design commit.

## 14. Current stopping point

Upon committing this file, the intended state is:

**B-LOCAL v2.2 L3 B-PRIME DESIGN ADDENDUM COMMITTED — IMPLEMENTATION UNAUTHORIZED — STOP FOR CHAT AUDIT.**
