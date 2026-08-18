# B-TUBE v2.1 — boundary-aware adaptive tube design V1

Status: **DESIGN ONLY — NO IMPLEMENTATION, TAG, OR RESULT-BEARING RUN AUTHORIZED**

Base implementation commit: `9fdc08c832dfdaf8aa76fd461f256db2db6c4f6c`

Calibration run used as incident evidence: GitHub Actions run `32137381418`

Calibration artifact outer ZIP SHA-256:
`957321f70a128abd5d2be4dbc7f7afeed6ded19799f95c885077c8da2235d74e`

Pinned B-LOCAL dependency source head:
`a8997d11850dbd5b63e3064560a1c311e5c9c267`

## 1. Decision and scope

This document records the approved design choice:

1. **A — boundary-aware adaptive tube** is the primary route;
2. **C — CORE interval with `boundary_connection: DEFERRED`** is the fallback if a positive start-boundary distance cannot be certified;
3. **B — clipping/intersecting a symmetric tube with `(0,1)`** is rejected because it changes the physical-domain/Krawczyk contract rather than merely changing a calibration parameter.

This commit is design-only. It does not modify the calibration implementation, configuration, checker, workflow, production B-TUBE contract, B-LOCAL artifact, or C-G dependency.

## 2. Coordinate correction required before implementation

The calibration predictor variable `q` is the **production kernel coordinate `r`**, not the auxiliary boundary-distance coordinate `u=1-r`.

Evidence is structural:

- `calibration_candidate.py` passes predictor/tube values directly to `kernel.F_arb(...)` and `kernel.dFdr_arb(...)`;
- the pinned clean-room kernel is explicitly `F(r, lambda)=partial_r E_lambda(r)`;
- the pinned B-LOCAL machine conclusion stores `start_root_interval=[2047/2048,1]` in that same `r` coordinate.

Therefore a recorded calibration failure `tube_interval.lo <= 0` means contact with the **left physical boundary `r=0`**. It must not be reinterpreted as direct evidence that the desired B-LOCAL root lies at `u=0`.

The auxiliary coordinate

`u = 1-r`

is used below only to express the distance of the desired start root from the **right boundary `r=1`**.

## 3. What run 32137381418 actually established

The run was infrastructure-successful and fail-closed:

- byte closure, record chain, B-LOCAL tuple propagation, and recommendation semantics all verified;
- all nine configured candidates failed;
- all 228 cell records reported `physical_tube_outside_open_unit_interval`;
- the first cell of every candidate had `q_left=q_right=0`, so its symmetric fixed-radius tube crossed `r=0` before any kernel evaluation.

This exposes a branch-tracking defect in the current calibration predictor route: reverse continuation from the terminal C-G seed can fall onto the `r=0` stationary branch before reaching `lambda_start`.

Independently, the desired B-LOCAL start root is certified only in

`r_* in [2047/2048,1]`,

so even after branch tracking is corrected, a fixed symmetric radius of `2^-5`, `2^-6`, or `2^-7` cannot be justified at the first cell from the current B-LOCAL information alone. A positive lower bound on

`u_*(lambda_start)=1-r_*(lambda_start)`

is therefore still required for FULL boundary connection.

Plan A must solve **both** problems in this order:

1. anchor continuation to the B-LOCAL start root rather than the `r=0` branch;
2. certify positive distance from `r=1` and use it in an adaptive tube rule.

## 4. Gate A0 — certify positive start-boundary distance

Let

- `lambda_plus = 206539/100000`;
- `lambda_start = 3307749/1600000`.

The exact difference is

`lambda_start - lambda_plus = 2^-9`.

The approved proof route is:

### A0.1 Boundary identity

Use the already established boundary identity

`F(1,lambda) = B(lambda)`.

No new boundary formula may be introduced by calibration code.

### A0.2 Transfer the Stage-1 sign to `lambda_start`

The frozen Stage-1/B-LOCAL evidence supplies:

- an enclosure with `sup B(lambda_plus) < 0`;
- a B-prime enclosure with `sup B'(lambda) < 0` on the exact interval required to move from `lambda_plus` to `lambda_start`.

The certificate must recompute the exact parameter difference `2^-9` and derive an upper bound of the form

`B(lambda_start) <= sup B(lambda_plus) + 2^-9 * sup B' < 0`.

The implementation must read and verify the frozen evidence values; display decimals or copied prose are not proof inputs.

### A0.3 Derivative bound in the root bracket

Produce a rigorous finite bound

`M >= sup |partial_r F(r,lambda_start)|`

for

`r in [2047/2048,1]`.

Preferred source is an already audited finite-route/ladder derivative enclosure if its exact domain contains this slice. Otherwise a new design-audited Arb enclosure may be computed from the same pinned clean-room `dFdr_arb` source. No float path is admissible for the proof decision.

### A0.4 Mean-value lower bound

For the certified desired root `r_*` with `F(r_*,lambda_start)=0`,

`|F(1,lambda_start)-F(r_*,lambda_start)| <= M (1-r_*)`.

Hence, from `F(1,lambda_start)=B(lambda_start)<0`, derive

`delta_start := lower_bound(|B(lambda_start)|) / M > 0`

and certify

`1-r_* >= delta_start`.

The B-LOCAL start bracket is then refined to

`r_* in [2047/2048, 1-delta_start]`.

All arithmetic used for the stored certificate must be exact rational/dyadic arithmetic around outward rigorous enclosures.

### A0 fail-closed condition

If any required identity, frozen provenance pin, sign, derivative bound, or strict positivity of `delta_start` cannot be verified, **Plan A stops**. No adaptive calibration is run. The design then falls back to Plan C.

## 5. Gate A0B — branch identity and predictor direction

The current reverse predictor is not allowed to define branch identity.

The adaptive design shall instead:

1. start at `lambda_start` from the refined B-LOCAL root bracket;
2. construct a first predictor point from that bracket by a deterministic exact rule;
3. continue **forward** in lambda, using the preceding accepted cell/JOIN information as the next seed;
4. retain the C-G root bracket at `118/25` as a terminal identity check, not as the sole branch-defining seed.

The first-cell record must bind to the B-LOCAL start-root certificate. A predictor that lands at or is only justified by the `r=0` branch is rejected before recommendation logic.

Required branch guards include:

- exact `lambda_start` equality;
- exact B-LOCAL dependency tuple equality;
- first predictor/start enclosure consistent with the refined B-LOCAL root bracket;
- no silent substitution of the central `r=0` stationary branch;
- terminal consistency with the pinned C-G match dependency.

The calibration predictor remains engineering guidance; the Krawczyk/JOIN chain remains the rigorous branch certificate.

## 6. Gate A1 — deterministic adaptive radius

For a cell predictor hull

`Q_i = [q_i^lo, q_i^hi] subset (0,1)`,

define exact physical-boundary margins

`d_i^L = q_i^lo`,

`d_i^R = 1-q_i^hi`.

Both must be strictly positive.

Each configured candidate retains a nominal radius cap `rho_cap`. The actual cell radius is derived deterministically from the predictor hull and an exact fixed safety factor `sigma` with `0<sigma<1`, for example a dyadic value fixed by configuration:

`rho_i = exact_dyadic_floor( min(rho_cap, sigma*d_i^L, sigma*d_i^R) )`.

Normative requirements:

- `rho_i > 0`;
- `q_i^lo-rho_i > 0`;
- `q_i^hi+rho_i < 1`;
- no clipping/intersection with `(0,1)` is permitted;
- no radius may be accepted merely because a record claims it — the independent verifier recomputes it from raw predictor/configuration data.

The Krawczyk test then runs on the ordinary symmetric physical tube

`Q_i + [-rho_i,rho_i]`.

Thus Plan A changes the **radius selection rule**, not the physical-domain or Krawczyk definition.

## 7. Adaptive JOIN semantics

Adjacent cells may have different radii. Let

`Y_i=[-rho_i,rho_i]`,

`Y_(i+1)=[-rho_(i+1),rho_(i+1)]`.

The existing exact JOIN primitive already has the correct mathematical shape because it accepts separate left and right tube sections:

`J_i = (q_i^R + Y_i) intersection (q_(i+1)^L + Y_(i+1))`.

The adaptive design therefore preserves the existing JOIN contract:

- the intersection must exist;
- it must have strictly positive width;
- production retains the point-parameter Krawczyk check on `J_i` itself;
- empty or zero-width adaptive JOIN is a hard failure, never repaired by widening or clipping after the fact.

Calibration should record both neighboring radii in each JOIN record so the independent verifier can reconstruct the intersection without shared helper trust.

## 8. Candidate semantics

The preferred minimal candidate parameterization is:

- existing ordered candidate lambda widths;
- existing ordered nominal radius caps;
- one exact safety factor `sigma` fixed normatively in configuration.

Candidate order remains lambda-width order then radius-cap order unless a later audited design explicitly changes it.

A candidate passes only if, over the entire exact interval `[lambda_start,118/25]`:

1. the start branch is bound to the B-LOCAL refined root bracket;
2. every predictor hull lies strictly inside `(0,1)`;
3. every derived adaptive radius is positive and passes the exact boundary-margin rule;
4. every cell has strict Krawczyk inclusion;
5. every derivative enclosure has the required strict sign;
6. every adaptive JOIN has positive width and satisfies the applicable JOIN Krawczyk requirement;
7. all budgets are respected;
8. the terminal branch matches the pinned C-G dependency.

The first passing candidate only is the permitted calibration recommendation.

## 9. Independent-verifier requirements

The verifier/checker must independently reconstruct at least:

- the exact `lambda_start-lambda_plus=2^-9` identity;
- the B-LOCAL evidence pins used in the `B(lambda_start)<0` transfer;
- the derivative-bound domain and bound `M`;
- the exact positive `delta_start` calculation;
- the refined start-root bracket;
- the forward branch-anchor semantics;
- the adaptive `rho_i` rule for every cell;
- every physical tube;
- every heterogeneous-radius JOIN;
- first-passing-candidate semantics;
- terminal C-G identity.

No verifier may import a producer result as a trusted derived value when it can recompute it from frozen inputs.

## 10. Required controls

At minimum add fail-closed controls for:

1. treating calibration `q` as `u=1-r` rather than kernel `r`;
2. reverse-predictor capture of the `r=0` branch;
3. changed B-LOCAL start-root interval;
4. changed Stage-1/B-prime provenance;
5. nonnegative or uncertified `B(lambda_start)`;
6. nonfinite/nonpositive derivative bound `M`;
7. zero or nonpositive `delta_start`;
8. tampered refined start bracket;
9. adaptive radius exceeding either physical-boundary margin;
10. zero adaptive radius;
11. hidden clipping to `(0,1)`;
12. adaptive JOIN empty/zero width;
13. JOIN radius-record tampering;
14. branch that does not reach the pinned C-G terminal root.

Positive controls must include an exact synthetic fixture with unequal neighboring radii and a positive-width JOIN.

## 11. Commit and run discipline

This design authorizes no result-bearing run.

The next implementation should be split:

- **A0 implementation commit:** boundary-distance certificate + independent verification + controls only;
- audit A0 bytes and certificate route;
- only if A0 is GREEN, prepare **A1 implementation commit:** forward branch anchor + adaptive radius/JOIN calibration;
- audit A1 statically before any approval tag;
- only then authorize a new calibration run.

No production B-TUBE configuration is rewritten by calibration output.

If A0 cannot certify `delta_start>0`, stop Plan A and use Plan C (`CERTIFIED_CORE_INTERVAL` with `boundary_connection: DEFERRED`) rather than weakening the open-domain or Krawczyk contracts.
