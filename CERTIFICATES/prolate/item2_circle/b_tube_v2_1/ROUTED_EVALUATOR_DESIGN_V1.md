# B-TUBE v2.1 — exact-domain routed evaluator design V1

Status: **DESIGN ONLY — IMPLEMENTATION, WORKFLOW CHANGE, TAG, AND RESULT-BEARING RUN NOT AUTHORIZED**

Base commit: `e6502072d52f4ea414465d3d96656fbc3609651d`

Primary decision: **A / routed evaluator is adopted. Plan C is retained only as fallback.**

Contract ID: `EXACT_DOMAIN_ROUTED_DUAL_SUPPLY_V1`

## 1. Purpose

The calibration failure caused by the direct clean-room fixed-domain integrator near the physical boundary is treated as a representation-layer problem, not as evidence that the physical tube or Krawczyk semantics should be clipped or weakened.

The routed evaluator therefore preserves the mathematical quantities `F(r,lambda)` and `F_r(r,lambda)`, preserves the physical tube and Krawczyk definitions, and changes only the enclosure-supply route as an exact function of the input interval.

Numerical failure, NaN, exception type, elapsed time, interval width, or any other runtime symptom is forbidden as a route-selection input.

## 2. Frozen backends and pins

### 2.1 Interior backend

The existing clean-room kernel remains byte-invariant and is not rewritten:

- path: `CERTIFICATES/prolate/item2_circle/vendor/prolate_circle_F_cleanroom.py`
- SHA-256: `77e7a93c594ba66ac7d98df29ec3c03107b0c63962a5aa60f8503559082c10ac`
- required API: `F_arb`, `dFdr_arb`, `angle_data`

Because these bytes are unchanged, the existing 224-leaf rigorous regression and derivative difference-quotient audit remain logically valid for this backend. Re-running them is a regression control, not a prerequisite to re-certify changed kernel bytes.

### 2.2 Boundary backend

The boundary backend is the already audited B-LOCAL v2.2 finite route, not a new formula:

- `blocal_v22_boundary.py` SHA-256: `aea768c02644fdb08c8c32455207efe7424c7dc34efe378ad545c3ab9418abf9`
- `blocal_v22_symbolic_audit.py` SHA-256: `b75ce97c8ff1342c6472a744cf2b64bf3413a3112190a5ff6fed73f60b40d0a1`
- `blocal_arb_adapter.py` SHA-256: `99e640fba88cfe353ea360190a03df7a9de8840637922f9f56fa6b7168d94e66`
- `blocal_v22_policy.py` SHA-256: `d8bac8535f5146f22906e8cdc604640edd909709998a41d7f377c9802ca7cc65`
- `blocal_v22_model.py` SHA-256: `8e9bcb0d9519cd6feb2375486985dddde43735dcb327cded28e96a33c61acb16`
- transitive `blocal_phase4_model.py` SHA-256: `92bc9010cbaf7e3c61a79aa6bb05e2f717a99486e1faac416e0f3dd3ee5f327a`
- frozen B-LOCAL v2.2 config SHA-256: `dab371fa62ed10a00029cd31b0002e503952277ef072fb8f5d7fd5222965d469`
- F route ID: `BLOCAL_F_ROUTE_V2`
- derivative/H_U route ID: `BLOCAL_K_ROUTE_V2`
- exact negation rule ID: `BLOCAL_INTERVAL_NEGATION_V1`

The boundary F supply is the normalized B-LOCAL `F_ROUTE` enclosure. The boundary `F_r` supply is the exact interval negation of the normalized B-LOCAL `H_U` enclosure because `u=1-r` and therefore `H_U=-F_r`. The checker must reconstruct this sign change; a producer-supplied sign flag is not trusted.

No unpinned helper source may participate in a result-bearing routed evaluation.

## 3. Exact selector and tie-break

Let `R0 = 3/4`.

### 3.1 Point evaluation

For an exact point `r`:

- `0 <= r <= R0` -> `INTERIOR_CLEANROOM_V1`;
- `R0 < r <= 1` -> `BOUNDARY_BLOCAL_FINITE_V1`.

Thus the tie point `r=3/4` belongs uniquely to the interior backend.

### 3.2 Closed interval evaluation

For a closed exact interval `X=[lo,hi]`:

- if `hi <= R0`, use interior only;
- if `lo > R0`, use boundary only;
- if `lo <= R0 < hi`, use the exact closed split
  `X_L=[lo,R0]`, `X_R=[R0,hi]`, evaluate `X_L` by interior and `X_R` by boundary, and return the exact interval hull of the two enclosures.

The shared point `R0` may be enclosed by both subroutes in a straddle evaluation. This does not change point tie-break semantics and cannot create a gap.

A straddle is an enclosure-route split only. The physical tube is not clipped, intersected, shortened, or otherwise changed.

## 4. Route-selection discipline

Route selection is completed before any numerical backend call and is a pure function of exact input endpoints plus the fixed selector constant `R0`.

The following are forbidden:

- try interior first and fall back after NaN/nonfinite output;
- choose a route from Arb midpoint/radius behavior;
- choose a route from interval width, exception class, runtime, or evaluation count;
- retry a failed route using the other backend without a separately authorized proof rule.

Every result record must contain the exact input domain, reconstructed selector outcome, route ID, all source/config pins used by that route, and, for straddles, both exact child domains and the final hull reconstruction.

The independent checker recomputes the route from raw exact endpoints and rejects any route/domain mismatch.

## 5. Route consistency certificate

A new machine-readable `ROUTE_CONSISTENCY_CERTIFICATE.json` is a mandatory release gate for the routed evaluator bundle.

This bridge is not a substitute for the existing symbolic audits; it is an independent machine falsification/consistency gate tying the two frozen backend implementations together on an overlap where both are finite.

### 5.1 Exact overlap grid

Use the fixed overlap band `[3/4,63/64]` and the exact dyadic grid

- `r = k/64` for every integer `k=48,...,63`;
- `lambda in {17/8, 5/2, 3, 7/2, 4, 9/2}`.

This gives 96 exact `(r,lambda)` points. The grid is normative and reconstructed independently by the checker; the producer may not supply a free-form point list.

### 5.2 Required comparisons

At every grid point compute, from fresh frozen sources:

1. interior `F_arb(r,lambda)`;
2. boundary `F_ROUTE(r,lambda)`;
3. interior `dFdr_arb(r,lambda)`;
4. boundary `F_r = -H_U` from `K_ROUTE` plus the exact negation rule.

For both `F` and `F_r`, the two canonical outward enclosures must have nonempty exact intersection.

Any empty intersection is an immediate `ROUTE_CONSISTENCY_FAILED` terminal condition and blocks implementation approval/tagging. No widening, tolerance relaxation, or selective point removal is permitted.

The certificate records both enclosures, their exact intersection, source hashes, route IDs, precision/policy IDs, and a deterministic digest over the normative ordered grid.

## 6. A0B start-anchor requirement

The A0B start-anchor evaluation must call the routed evaluator, not the direct clean-room API.

The refined B-LOCAL start-root bracket lies above `r=3/4`; therefore the checker must verify that its A0B residual and derivative evaluations deterministically select `BOUNDARY_BLOCAL_FINITE_V1` (or, only if an exact input interval genuinely straddles `3/4`, the normative split/hull route).

A0B is not considered executable under this design unless that route selection is reconstructible and all boundary pins validate before the first numerical evaluation.

## 7. Boundary-route evaluation budget estimate

The inherited B-LOCAL route policy has `max_evaluations = 24000` angular proof evaluations per F or H_U route call.

The current Krawczyk cell protocol performs three mathematical kernel enclosures in the full-evaluation case: one residual F enclosure, one derivative enclosure over the tube, and one derivative enclosure at the center. Therefore a conservative all-boundary upper estimate is

`3 * 24000 = 72000`

boundary angular proof evaluations per cell.

With the current calibration `max_cells=64`, the corresponding worst-case candidate bound is

`64 * 72000 = 4,608,000`

boundary angular proof evaluations. With the existing 9 candidate pairs, the naive all-boundary campaign bound is

`9 * 4,608,000 = 41,472,000`.

A straddle can additionally require an interior direct evaluation for the interior child, but that does not increase the boundary-route count above the three boundary calls per full Krawczyk cell.

This worst-case does **not** establish that the current calibration wall-clock budget is safe. Therefore implementation must add a separate exact `boundary_route_evaluation_budget` and a cumulative `boundary_route_evaluation_count` equal to the sum of the B-LOCAL proof `evaluation_count` values actually consumed. Exceeding the configured budget fails closed.

Before an approval tag, static/chat audit must also review a representative measured boundary-call timing and show that the configured boundary budget fits the Actions job limit with explicit margin. No runtime estimate may silently enlarge a result-bearing budget.

## 8. New negative controls

The routed evaluator test/checker suite must reject at least:

1. a record whose route ID disagrees with the exact selector for its domain;
2. a straddle record that omits either child, changes `R0`, or returns anything other than the exact hull;
3. a boundary-route source SHA mismatch;
4. a symbolic-audit SHA mismatch;
5. an Arb adapter SHA mismatch;
6. a policy/model/config pin mismatch;
7. a boundary derivative record that omits or changes the exact `H_U -> -F_r` negation;
8. any post-failure fallback from interior to boundary or boundary to interior;
9. a bridge-grid point with empty F intersection;
10. a bridge-grid point with empty F_r intersection;
11. an A0B record that bypasses the routed evaluator or selects the interior route for a strictly-above-`3/4` start domain;
12. a boundary evaluation count exceeding the normative boundary budget.

Positive controls must include interior-only, boundary-only, exact tie-point, exact straddle, and unequal-width enclosure fixtures whose expected selector result is reconstructed without importing producer helper output.

## 9. Checker reconstruction obligations

The independent checker must reconstruct from frozen bytes and exact inputs:

- every SHA listed in Section 2;
- selector constant `R0=3/4`;
- point tie-break;
- interval selector;
- exact straddle split and hull;
- route IDs;
- `H_U -> -F_r` sign transform;
- the 96-point bridge grid and every nonempty-intersection result;
- boundary evaluation counts and budget accounting;
- A0B boundary-backend selection.

A producer field that is reconstructible from these inputs is evidence only and is never trusted as a decision input.

## 10. Lifecycle and fallback

This design adopts routed evaluator A as the primary route. Plan C remains fallback only if route consistency, budget feasibility, or later implementation audit cannot be made GREEN without weakening the exact-domain/Krawczyk contracts.

The required lifecycle remains:

`design commit -> chat audit -> implementation -> implementation audit -> new approval tag -> calibration run`

This design commit authorizes none of the stages after chat audit. It does not change the current workflow, create a tag, run calibration, change a production B-TUBE configuration, modify the frozen clean-room kernel, or alter the frozen B-LOCAL/C-G artifacts.
