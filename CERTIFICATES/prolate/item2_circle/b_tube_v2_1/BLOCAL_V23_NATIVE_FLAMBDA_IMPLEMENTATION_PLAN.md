# B-LOCAL v2.3 native F_lambda implementation plan

Status: `DESIGN_DRAFT_ONLY / NOT_BINDING / NOT_PROMOTED`  
Base commit: `52b98b6bd93382a47ed4cf5cbc7067edb0cebe45`  
Working branch: `btube-v2-3-native-flambda`

## Non-mutation rule

B-LOCAL v2.2 is immutable. No file below `dependencies/blocal_v22_source/` may be edited, replaced, renamed, or repinned by this work. Existing v2.2 certificates keep their existing meaning under their existing pins. B-LOCAL v2.3 is a new dependency lineage.

## Target contract

Implement `F_lambda` as a native B-LOCAL quantity under a versioned v2.3 route. The intended binding API is conceptually:

```python
enclose_route(
    quantity="F_lambda",
    ...,
    required_sign="NEG",
)
```

Binding execution must not monkeypatch `_geometry_jet`, `_duffy_eval`, or any other route internals. A strict positive `F_lambda` result is `FAIL_SIGN`; a zero-containing result is `FAIL_UNRESOLVED`; budget exhaustion is `FAIL_BUDGET`; nonfinite evaluation is `FAIL_NONFINITE`.

## Pre-implementation API / precision audit

- Target claim: for each derived physical-tube endpoint `r_hi` and `r_lo`, certify `F_lambda(r, lambda) < 0` on the exact lambda parent, then combine with the correct endpoint anchor to transport the sign of `F` across the parent.
- Existing API surface: frozen v2.2 `enclose_route` authorizes only `F` and `H_U`; it has no supported injection point for a third native quantity. Therefore v2.3 is required.
- Proof direction: additive lambda transport. `R_HI` uses left-endpoint `F<0`; `R_LO` uses right-endpoint `F>0`. No radial subtraction/cancellation proof is used.
- Observed diagnostic strict-negative margins: R_HI limiting cell about `8.25654442933e-5`; R_LO limiting cell about `1.39732087934e-4`.
- Anchor scale: existing diagnostic point signs are much smaller (R_HI zero-side margin about `2.66e-9`; R_LO about `1.316e-8`) and therefore anchor evaluation is the cost-sensitive component.
- Precision policy: producer dps is read from the pinned config; checker dps must be separately pinned and satisfy `checker_dps >= producer_dps`. Current baseline config uses 60 dps, but the implementation must not hard-code an unpinned assumption.
- Abort conditions before any promotion: source/config/kernel pin mismatch; audited F_lambda kernel body mismatch; transport lemma not human-audited; derived tube geometry mismatch; lambda parent/residual tiling mismatch; any F_lambda cell not strict NEG; wrong anchor side/sign; any declared cap exceeded; checker dps below producer dps; dirty source state or HEAD movement during a binding run.

## Version policy

`BLOCAL_VERSION_POLICY=VERSIONED_IMMUTABILITY`.

- v2.2 remains frozen and is not modified.
- v2.3 is a new source bundle with new source/config/checker/symbolic-audit pins.
- `F_lambda` is native only in v2.3.
- Diagnostic monkeypatch results are provenance/design-feasibility evidence only and are never binding proof objects.

## Shared-kernel / independent-glue policy

The mathematical `F_lambda` kernel is a single shared, pinned dependency. Producer and checker may use the same frozen kernel bytes. Checker independence is placed in the surrounding reconstruction:

- candidate and adaptive physical-tube geometry;
- exact lambda parent reconstruction from candidate/cell index;
- exact 1/16-plus-final-residual tiling;
- route/glue orchestration;
- normalization and exact child-sum reconstruction;
- sign predicate and budget accounting;
- anchor profile validation/evaluation;
- transport implication and final evidence classification.

The checker must not import producer glue or producer verdict logic.

## Formula identities and audit lineage

Required formula IDs:

- `BLOCAL_FLAMBDA_ORDINARY_V1`
- `BLOCAL_FLAMBDA_DUFFY_V1`

The new native v2.3 kernel must be compared byte-for-byte at function-body level with the independently audited diagnostic implementations where possible. Diagnostic lineage references:

- diagnostic module SHA-256: `d3f73cacc26e40df8a1aa05aaddd5810239178d8138eb4cb48c27c1016a2abf4`
- ordinary function source SHA-256: `c11d4e3322593f22fd96f64bc6d5a14080c8b2a1ba62b2255e66c454b73df9fd`
- Duffy function source SHA-256: `2b6cda67b845ad299331061c4a93cc72ea12e9c90a6fee224e825f32cf35c549`

These are audit-lineage references, not the future v2.3 binding source pin.

Any function-body difference from the independently audited diagnostic formulas requires a new symbolic audit before promotion.

## Transport lemma gate

A human-audited mathematical precondition must be pinned under:

`F_LAMBDA_IS_LAMBDA_DERIVATIVE_OF_ROUTE_F_V1`.

It must establish, for each fixed derived endpoint `r` and exact lambda parent:

1. `lambda -> F(r, lambda)` is C1 on the parent;
2. differentiation may pass through the ordinary/Duffy regularized integral representation;
3. the differentiated native kernel is the lambda derivative of the frozen route F integrand;
4. density/eps/area/measure normalization factors used outside the differentiated core are handled consistently and the normalization policy is lambda-independent;
5. the derived `r` endpoint is held fixed while lambda varies over the transport parent.

Stage 10 transport is forbidden unless this lemma has a pinned human-audit PASS.

## Exact parent and residual tiling

The runner's nominal candidate widths remain `{1/4, 1/8, 1/16}`. The actual candidate parent is reconstructed from candidate/cell index and clipped by `lambda_end`:

```text
lambda_L = lambda_start + j * W_nom
lambda_R = min(lambda_L + W_nom, lambda_end)
P        = lambda_R - lambda_L
```

For `b=1/16`:

```text
m     = floor(P / b)
delta = P - m*b
```

Use `m` full cells of width `1/16`; if `delta>0`, append exactly one final residual cell `[lambda_L+m/16, lambda_R]` with `0 < delta < 1/16`.

Baseline arithmetic:

- full span `118/25 - 3307749/1600000 = 4244251/1600000`;
- nominal 1/4: 10 full parents plus terminal parent width `244251/1600000`; terminal F_lambda tiling is two full 1/16 cells plus residual `44251/1600000`;
- nominal 1/8: 21 full parents plus terminal parent width `44251/1600000`; terminal F_lambda tiling is one residual cell;
- nominal 1/16: 42 full parents plus terminal parent width `44251/1600000`; terminal F_lambda tiling is one residual cell.

Producer-supplied parent endpoints or cell lists are redundant metadata, never authority. The checker reconstructs them independently.

## Tube geometry authority

`r_lo` and `r_hi` are derived values, not contract constants. Authority is the candidate geometry:

```text
candidate inputs
 -> q_left
 -> q_right / Newton predictor
 -> predictor.range_hull()
 -> adaptive radius rho
 -> physical_tube(...)
 -> domain
 -> r_lo=domain.lo, r_hi=domain.hi
```

The checker must reconstruct exact endpoints from the pinned candidate inputs and reject any literal endpoint mismatch.

## Anchor profiles

### Profile A: future binding-reference anchor

Defined but disabled. It becomes executable only when separately binding point-anchor evidence exists and is SHA-pinned. Current diagnostic point evidence cannot satisfy Profile A.

### Profile B: exact-F re-evaluation

Initial executable profile.

- R_HI target NEG: evaluate `F(derived_r_hi, lambda_L)` and require strict NEG.
- R_LO target POS: evaluate `F(derived_r_lo, lambda_R)` and require strict POS.

Wrong anchor side is a contract failure even if the sampled sign happens to agree.

## Budget contract

Declare producer and checker budgets independently before the run:

```text
PRODUCER_ANCHOR_CALL_CAP=24000
PRODUCER_FLAMBDA_CELL_CALL_CAP=24000
CHECKER_ANCHOR_CALL_CAP=24000
CHECKER_FLAMBDA_CELL_CALL_CAP=24000
POST_HOC_CAP_INCREASE=FORBIDDEN
```

For Profile B with `n` F_lambda tiles per endpoint:

```text
parent_total_cap = 2*anchor_call_cap + 2*n*flambda_cell_call_cap
```

Thus, per role:

- n=4 -> 240000
- n=3 -> 192000
- n=2 -> 144000
- n=1 -> 96000

`ANCHOR_CAP_HEADROOM=THIN_OBSERVED`. Cap exhaustion returns to contract revision; the run may not increase its cap after starting.

## Implementation phases

### Phase 0 — baseline pin

Create the v2.3 work branch from exact commit `52b98...`; record v2.2 source/config pins and diagnostic audit lineage. No v2.2 mutation.

### Phase 1 — new v2.3 dependency bundle

Create a new directory such as `dependencies/blocal_v23_source/`. Start from the v2.2 baseline but give all versioned modules/config/checker/symbolic-audit artifacts v2.3 identities. Unchanged low-level files may be copied byte-for-byte, but the resulting v2.3 bundle receives its own manifest and pins.

### Phase 2 — native F_lambda route

Add native `F_lambda` authorization to the v2.3 route. Integrate the audited ordinary and Duffy derivative kernels without runtime monkeypatching. Add `BLOCAL_FLAMBDA_ROUTE_V1`; `required_sign=NEG` is mandatory for binding use.

### Phase 3 — v2.3 symbolic and transport audits

Add a v2.3 symbolic-audit artifact that verifies the native kernel/formula lineage and the human-audited transport lemma pin. This is distinct from the earlier diagnostic receipt.

### Phase 4 — producer glue

Add B-TUBE glue that reconstructs the candidate parent, residual tiling, derived tube endpoints, Profile B anchors, three-layer budgets, and evidence object. Producer output remains `BINDING_CANDIDATE` until checker/human promotion.

### Phase 5 — checker glue

Implement the 10 reconstruction stages independently of producer glue. The checker may import the pinned shared v2.3 mathematical kernel but not producer orchestration/verdict code.

### Phase 6 — tests and negative controls

Implement NC01-NC31 from the audited contract, including unsupported nominal width, residual-tiling mutation, self-promotion of evidence class, checker precision downgrade, candidate-parent mismatch, source-state mismatch, v2.2 attempted F_lambda use, binding monkeypatch use, and v2.3 baseline pin mismatch. Expected failure codes are part of the contract.

### Phase 7 — replay and determinism reporting

Run producer and checker on the exact diagnostic target parents. Report, but do not gate on, producer/checker bitwise enclosure and evaluation-count agreement. Required gates are independent exact-domain reconstruction plus strict sign proof.

### Phase 8 — human promotion gate

No automatic authorization. Promotion requires complete v2.3 source/config/checker/audit pins, transport-lemma human audit, producer and checker PASS, negative controls expected-fail PASS, clean source state, and explicit human Judge approval.

## 10-stage checker order

1. contract/config/source pins;
2. native quantity, route, formula/version authorization;
3. candidate and tube geometry reconstruction;
4. exact candidate parent and residual tiling;
5. shared F_lambda kernel and transport-lemma pins;
6. normalization reconstruction;
7. independent per-cell F_lambda strict NEG reconstruction;
8. exact full closed-cover reconstruction;
9. anchor profile, endpoint side, sign, and budget reconstruction;
10. transport implication and final endpoint-sign verdict.

## Baseline status

```text
F_LAMBDA_CONTRACT_DRAFT_V1_1=DESIGN_AUDIT_PASS
IMPLEMENTATION_BOUNDARY=BLOCAL_V2_3_NATIVE_F_LAMBDA_ROUTE
BLOCAL_V22_MUTATION=FORBIDDEN
PROFILE_A_CURRENTLY_EXECUTABLE=NO
INITIAL_ANCHOR_PROFILE=PROFILE_B_REEVALUATE
CONTROL_SANITY=NOT_ESTABLISHED
DESIGN_DRAFT_ONLY
NOT_BINDING
NOT_PROMOTED
BINDING_USE_AUTHORIZED=NO
```
