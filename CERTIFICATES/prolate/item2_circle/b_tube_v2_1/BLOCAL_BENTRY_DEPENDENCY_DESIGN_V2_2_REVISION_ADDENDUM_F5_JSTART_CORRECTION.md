# B-LOCAL v2.2 design revision addendum — F-5 correction for J_START

**Status: DRAFT FOR CHAT BYTE/CODE/MATH AUDIT. DESIGN ONLY.**

This correction supplements `BLOCAL_BENTRY_DEPENDENCY_DESIGN_V2_2_REVISION_ADDENDUM.md` and `BLOCAL_BENTRY_DEPENDENCY_DESIGN_V2_2_REVISION_ADDENDUM_F4_CORRECTION.md` after the F-4 correction byte-audit was GREEN and content audit found the remaining blocker **F-5** in `J_START`.

It changes no implementation source, run config, dependency pin, workflow, tag, certificate, frozen RED evidence, or previously audited design bytes. The previously audited revision and F-4 correction remain immutable at their audited bytes.

Where earlier v2.2 documents permit the old `J_START` implementation to call pinned `F_arb` or `dFdr_arb`, **this correction supersedes that evaluator choice**. The mathematical J_START claim, candidate order, first-passing semantics, outer bisection/Newton logic, Stage-1 dependency, canonical fail-closed semantics, and tag-only authorization remain unchanged except where explicitly tightened below.

No implementation, runtime smoke, workflow change, tag creation, calibration start, or production run is authorized by this correction.

## 0. F-5 — the current J_START evaluator consumes both rejected pinned integrators

The current `blocal_phase4_engine.py` implementation of `build_j_start` uses the rejected validated-integral routines in three places:

1. `f_at(r)` calls pinned `F_arb` at exact dyadic point `r` during the initial left-sign check and bisection;
2. after finding a sign bracket `[left,right]`, it calls pinned `dFdr_arb` on the positive-width Arb interval `[left,right]`;
3. it calls pinned `F_arb` again at the exact midpoint for the interval-Newton image.

For the first configured `u_max = 2^-8`, the initial left point is exactly

`r = 1-u_max = 1-2^-8`,

which is the same point at which the F-4 diagnostic observed direct pinned `F_arb` return NONFINITE under loose readiness settings. The derivative interval `[left,right]` lies inside `[1-u_max,1]`, the same endpoint region in which F-3 diagnostics observed direct pinned `dFdr_arb` fail to provide finite interval evaluations.

Therefore the design cannot be considered executable merely by replacing the L1/L2/L3 evaluators. A candidate that passes those nodes would still enter `build_j_start` and consume the two rejected pinned integral representations.

This is an evaluator failure, not a rejection of the mathematical J_START claim or of the pinned formulas themselves.

Within the audited B-LOCAL runtime call graph, L1, L2, L3, and J_START are the four consumers of rigorous `F`/`F_r` evaluation. Stage-1 is a pinned dependency verification and does not require a new production call to either rejected integral routine. This correction closes the remaining J_START consumer.

## 1. Normative J_START replacement

J_START keeps the existing mathematical purpose: after a candidate has satisfied L1/L2/L3, certify a strict interior interval containing a unique nondegenerate root of

`F(r,lambda_start) = 0`

with

`r in (1-u_max,1)`.

The evaluator replacement is:

- every exact-point enclosure of `F(r,lambda_start)` is produced by the **cancellation-free F-route / rigorous angular ball-sum route** made normative by the F-4 correction;
- every interval enclosure of `F_r(r,lambda_start)` on `[left,right]` is produced by the **cancellation-free K-route / rigorous angular ball-sum route** made normative by the main revision, with exact sign conversion from `H_u=-F_r`;
- direct pinned `F_arb` and `dFdr_arb` calls are forbidden as J_START certificate evaluators.

The pinned clean-room kernel remains the formula provenance source. The already-required symbolic audits for F-route and K-route equivalence remain binding.

No exception-driven retry, alternate unpinned kernel, point sampling, floating quadrature, or fallback from a rejected pinned integral call is permitted.

## 2. Exact F-route point evaluation for bisection

For every exact rational/dyadic bisection point `r0`, J_START must call the production F-route with

- exact `r = r0`;
- exact `lambda = lambda_start`;
- the same fixed angular domain `D=[0,1]x[0,pi]`;
- the same exact dyadic singular square `P_eps` and T1/T2 Duffy construction;
- child-specific gamma enclosures;
- child-specific `q_lo` / `Z_DEN_LO` bounds;
- sequential-division policy;
- deterministic adaptive angular subdivision;
- exact `1/pi` normalization;
- the same fail-closed record/checker obligations required for L2/L3 F-route proof roots.

A point in `(r,lambda)` is not permission to bypass the per-angular-cell proof mechanism. The returned J_START point enclosure is the outward-rounded normalized root sum of a reconstructible angular proof tree.

The point-sign classification is unchanged:

- `F_lo > 0` certifies POSITIVE;
- `F_hi < 0` certifies NEGATIVE;
- otherwise the sign is UNRESOLVED and J_START fails closed at that bisection state.

A non-finite child, incomplete angular coverage, missing required record, exhausted adaptive budget, or nonseparating final F enclosure makes the point sign UNRESOLVED.

## 3. Bisection logic and outer budget remain unchanged

The outer J_START bracket construction remains:

`left = 1-u_max`, `right = 1`.

First certify `F(left,lambda_start) > 0` by the F-route. Then, for at most the configured J_START bisection limit, set

`midpoint = (left+right)/2`

and certify the F-route sign at that exact midpoint.

- if the midpoint enclosure is strictly negative, set `right = midpoint` and retain that negative enclosure;
- if it is strictly positive, set `left = midpoint` and retain that positive enclosure;
- if its sign is unresolved, fail closed;
- if no strictly negative interior right endpoint is found within the configured bisection limit, fail closed.

The current outer budgets remain the J_START budgets: `max_bisections` and `max_evaluations` retain their existing logical roles. The existing configured values are not enlarged by this correction.

A **completed F-route root enclosure** used by J_START counts as one outer J_START F evaluation, preserving the prior outer counting semantics. A **completed K-route derivative root enclosure** counts as one outer J_START derivative evaluation. The adaptive angular child work inside those root evaluations is governed by deterministic route-policy child/depth/evaluation budgets that must be explicit and config-bound in the reimplementation; it must not be hidden from provenance or silently charged under an unrelated node budget.

If the implementation reuses a common F-route or K-route angular budget policy already defined for another node, the exact shared policy ID and parameters must be recorded. Otherwise J_START-specific angular budgets must be explicit in config before production.

## 4. Normative J_START derivative enclosure via K-route

After bisection has produced

`1-u_max <= left < right < 1`,

J_START must certify a rigorous enclosure of

`F_r(r,lambda_start)` for all `r in [left,right]`.

The K-route is invoked on that exact `r` interval and exact `lambda_start` using the same cancellation-free derivative bracket, exact angular partition, per-box gamma policy, child-specific denominator bounds, sequential division, adaptive subdivision, helper-lemma validation, symbolic audit, and fail-closed proof-tree structure required by revised L1.

If the shared implementation is parameterized in the L1 coordinates

`u = 1-r`, `lambda = lambda_plus+s`,

then J_START must map the bracket exactly to

`u in [1-right, 1-left]`

and the exact parameter

`s = lambda_start-lambda_plus`.

No outward enlargement or coordinate conversion may omit any point of the original `[left,right]` interval.

The K-route naturally encloses

`H_u = -F_r`.

If its normalized canonical enclosure is

`H_u in [h_lo,h_hi]`,

then J_START must obtain the derivative enclosure by exact interval negation

`F_r in [-h_hi,-h_lo]`.

The derivative-negativity prerequisite is

`-h_lo < 0`, equivalently `h_lo > 0`,

and the full derivative enclosure must exclude zero. If strict negativity is unresolved, J_START fails closed.

The exact positive normalization factor `1/pi` used by the derivative route is part of the quantitative enclosure. The J_START F point enclosures and F_r interval enclosure must refer to the same normalized model quantities.

## 5. Interval Newton arithmetic uses route enclosures, not raw kernel values

Once a strict bracket and derivative enclosure are established, the interval-Newton logical criterion is unchanged.

Let

`X = [left,right]`,
`m = (left+right)/2`,
`F_m` = the normalized F-route enclosure at exact `m`,
`D` = the normalized K-route-derived enclosure of `F_r(X,lambda_start)`.

Require `0 notin D`, with the stronger J_START contract `sup(D) < 0`.

The interval-Newton image is

`N(X) = m - F_m / D`.

This arithmetic must be performed from the rigorous route enclosures themselves. It is forbidden to recover a raw pinned `F_arb` midpoint value or raw pinned `dFdr_arb` derivative ball merely for the Newton division.

The reimplementation must choose and config-bind one rigorous interval-arithmetic policy for this scalar step. An acceptable policy is:

1. parse the canonical dyadic/rational endpoints of `F_m` and `D` exactly;
2. compute the mathematical quotient interval `F_m/D` by exact rational endpoint arithmetic using the known strict sign of `D`;
3. subtract that interval from the exact rational midpoint `m`;
4. outward-round the result once to the canonical dyadic interval schema.

An equivalent Arb implementation is permitted only if it constructs an interval containing the exact canonical operands, verifies that the denominator interval excludes zero before division, and canonicalizes the result outward. No midpoint-only division is permitted.

The strict self-containment criterion remains

`left < N_lo <= N_hi < right`.

Failure of strict self-containment fails J_START closed. Success, together with the derivative exclusion of zero and the existing interval-Newton theorem contract, certifies the same unique nondegenerate J_START root claim as before.

If a Krawczyk variant is retained under an existing method identifier, it must consume only the same rigorous F-route/K-route enclosures and satisfy its separately recorded exact self-containment hypotheses. It may not restore direct pinned integral calls. The production record must identify which actual method was used; an ambiguous method label without reconstructible arithmetic is insufficient.

## 6. J_START records must expose the complete proof path

The existing top-level J_START semantics are preserved, but the record must now bind the route evidence needed to reconstruct every sign and Newton step.

### 6.1 Bisection evaluation record

Every F point used during J_START must record at least:

- J_START candidate index and evaluation sequence number;
- exact `lambda_start`;
- exact point `r`;
- F-route ID and F-route source SHA-256;
- exact angular policy ID and budgets;
- root angular-proof record ID/hash;
- exact normalized F enclosure;
- exact `1/pi` normalization record or referenced identity ID;
- sign classification (`POSITIVE`, `NEGATIVE`, or `UNRESOLVED`);
- whether the evaluation became the retained left endpoint, retained right endpoint, or midpoint-only evidence;
- first fail-closed reason when unresolved.

The referenced F-route angular proof must itself satisfy all F-4 child-record requirements.

### 6.2 Derivative proof record

The J_START derivative record must contain at least:

- exact final `[left,right]`;
- exact mapped `u=[1-right,1-left]` when the shared K-route uses u coordinates;
- exact `lambda_start` and exact `s=lambda_start-lambda_plus` when applicable;
- K-route ID and K-route source SHA-256;
- angular policy ID and budgets;
- root K-route proof record ID/hash;
- normalized `H_u` enclosure;
- exact negation rule ID;
- resulting normalized `F_r` enclosure;
- explicit proof that `sup(F_r)<0`;
- first fail-closed reason when false.

### 6.3 Newton record

The interval-Newton record must contain at least:

- exact bracket `X=[left,right]`;
- exact midpoint `m`;
- reference to the midpoint F-route proof record;
- exact `F_m` enclosure;
- reference to the derivative K-route proof record;
- exact derivative enclosure `D`;
- interval-arithmetic policy ID;
- exact quotient enclosure `F_m/D` before final subtraction;
- exact outward-rounded Newton image;
- strict-self-containment predicate and result;
- method ID actually used;
- `claim = J_START_UNIQUE_NONDEGENERATE_ROOT` only when every prerequisite is certified.

The top-level J_START record must reference the ordered bisection, derivative, and Newton records rather than duplicating unauditable summary values.

## 7. Checker obligations for J_START

The checker must independently verify:

1. the initial exact bracket is `[1-u_max,1]` for the selected candidate;
2. the initial left point has a reconstructible F-route proof with strict positive F enclosure;
3. every bisection midpoint is exact and every endpoint update follows from the recorded strict F-route sign;
4. the final right endpoint is strictly less than `1` and has a reconstructible strict negative F enclosure;
5. the recorded K-route derivative domain exactly covers `[left,right]` after any u-coordinate conversion;
6. `H_u=-F_r` is converted by exact interval negation, not by a sign-only assertion;
7. the normalized F_r enclosure is strictly negative throughout the final bracket;
8. the midpoint F enclosure is produced by the F-route and is the operand used by Newton arithmetic;
9. the scalar interval division/subtraction policy encloses exact mathematical interval arithmetic and the denominator excludes zero;
10. the Newton image satisfies strict self-containment;
11. all F-route/K-route source, symbolic-audit, helper-lemma, config, and policy pins match the final implementation state;
12. all referenced angular proof trees are complete and checker-valid.

A J_START summary with valid-looking endpoint signs but missing reconstructible route evidence must be rejected.

## 8. J_START negative controls are binding

The release test suite must add and demonstrate rejection of at least the following J_START mutations:

1. claim direct pinned `F_arb` as any J_START point/midpoint proof evaluator;
2. claim direct pinned `dFdr_arb` as the J_START derivative proof evaluator;
3. omit or reverse the exact conversion `F_r=-H_u`;
4. use a derivative enclosure containing zero in Newton arithmetic;
5. alter the exact map `[left,right] -> [1-right,1-left]` so the K-route fails to cover the full derivative domain;
6. use an unnormalized F operand with a normalized derivative operand, or vice versa, while claiming the model Newton image;
7. replace a reconstructible F-route/K-route root with a top-level sampled or manually inserted enclosure;
8. update a bisection endpoint contrary to the sign of the recorded F enclosure;
9. accept `right=1` as the final negative interior endpoint when the existing J_START contract requires `right<1`;
10. perform Newton division when the recorded denominator interval does not exclude zero;
11. claim strict self-containment when the reconstructed Newton image touches or crosses either bracket boundary;
12. omit a referenced angular child/proof-tree record required to reconstruct a J_START F or K evaluation.

These are in addition to every negative control already made binding by the revision and F-4 correction. A mutation test passes only when the checker rejects it for the intended reason.

## 9. Runtime readiness for J_START

After design GREEN and reimplementation, the authorized readiness phase must exercise a production-shaped J_START path using the same F-route and K-route that production will use.

At minimum it must demonstrate, under the final fixed policies and budgets:

- a finite normalized F-route enclosure at the initial `r=1-u_max` point for at least the first configured `u_max` attempted by the deterministic schedule;
- finite sign-separating F-route midpoint evaluations sufficient to exercise both endpoint-update branches where a controlled readiness fixture permits them;
- a finite normalized K-route derivative enclosure on a positive-width bracket inside `[1-u_max,1]`;
- exact `F_r=-H_u` conversion with derivative interval excluding zero;
- finite rigorous interval-Newton arithmetic from route-produced operands.

The fixed `eps=2^-8` readiness rule from the F-4 correction remains binding. If the production-shaped J_START F/K routes cannot make progress with that exact eps and the fixed policy/budgets, the project returns to a separately audited design/config revision. No silent eps or budget change is allowed.

Readiness evidence is not certificate evidence.

## 10. Complete evaluator-consumer closure

With this correction, the intended B-LOCAL v2.2 evaluator map is:

- **L1:** cancellation-free K-route / angular ball-sum for `H_u=-F_r` on the full L1 domain;
- **L2:** cancellation-free F-route / angular ball-sum;
- **L3:** cancellation-free F-route / angular ball-sum; any `F(1,lambda)=B(lambda)` identity route is cross-check-only unless separately promoted by audited design;
- **J_START F point/midpoint evaluations:** cancellation-free F-route / angular ball-sum;
- **J_START derivative interval:** cancellation-free K-route / angular ball-sum followed by exact interval negation to `F_r`.

Direct pinned `F_arb` and `dFdr_arb` remain formula/provenance references and may be used in diagnostics only when explicitly authorized as non-certificate evidence. They are not production certificate evaluators anywhere in B-LOCAL v2.2.

Stage-1 dependency verification remains unchanged and does not reintroduce a runtime integral call.

No claim of design closure is valid unless the reimplementation audit confirms that no production proof path or candidate-acceptance path still calls the rejected pinned integral routines.

## 11. Provenance and sequencing for the F-5 correction

This F-5 correction file is the **only path authorized in its correction commit**. The already-audited revision addendum and F-4 correction bytes must remain unchanged.

After this correction commit: **STOP for chat byte/code/math re-audit.** No implementation is authorized until this correction audit is GREEN.

If design audit is GREEN, the reimplementation sequencing remains exactly the already approved sequence:

1. complete all implementation/checker/tests/symbolic-audit/policy bytes, including the J_START F/K route integration;
2. run only static/runtime-readiness tests authorized for that phase;
3. freeze all final source bytes;
4. independently compute SHA-256 for every final source byte sequence;
5. materialize canonical config **last** from those exact final hashes and final route/budget policy bindings;
6. independently recompute the canonical config SHA-256;
7. create one implementation commit containing the finalized implementation/config set and no unrelated changes;
8. **STOP**;
9. perform chat byte/code/math re-audit from actual committed bytes before any later smoke, workflow, tag, or production authorization.

Any source byte or route-policy byte changed after freeze invalidates the materialized config and requires config rematerialization before the single implementation commit.

Workflow modification, tag creation, calibration, production, and any separately gated runtime smoke remain unauthorized. Tag creation still requires explicit user approval.

## 12. Current stopping point

Upon committing this correction, the project state is:

**B-LOCAL v2.2 F-5 J_START DESIGN CORRECTION COMMITTED — ALL KNOWN F/F_r CONSUMERS ROUTED THROUGH FINITE ARCHITECTURE — IMPLEMENTATION UNAUTHORIZED — STOP FOR CHAT AUDIT.**
