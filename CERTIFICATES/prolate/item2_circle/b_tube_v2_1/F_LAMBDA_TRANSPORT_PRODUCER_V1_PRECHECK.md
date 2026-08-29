# F_lambda transport producer v1 — API / precision precheck

Status: `PROTOTYPE / BINDING_CANDIDATE_DESIGN / NOT_PROMOTED`

Producer source: `flambda_transport_producer_v1.py`  
Producer source commit: `e6b33ed67952beaed005c9a2ee633bd4a6c19b6c`  
Producer-source SHA-256 is harvested from these committed UTF-8 bytes and pinned only in `F_LAMBDA_TRANSPORT_PRODUCER_V1_PINS.json`; this document does not self-pin that value.  
Byte authority remains the repository file plus the subsequent hash-harvest/pin step.

## Target claim

For one exact reconstructed calibration parent and its derived strict-interior physical tube endpoints, produce candidate evidence for

- `F(r_hi, lambda) < 0` throughout the parent; and
- `F(r_lo, lambda) > 0` throughout the parent,

using exact endpoint anchors plus strict native `F_lambda < 0` transport.

This is an endpoint-sign transport producer. It does **not** prove Krawczyk contraction and does not replace the separate existing `F_r < 0` evidence.

## Existing API surface

No new mathematical evaluator is introduced.

1. Candidate geometry is reconstructed through the existing production helpers:
   - `_candidate_pairs`;
   - `_cell_partition`;
   - `_load_a0_start_interval`;
   - `exact_newton_predictor` from `exact_lambda_transport.py`;
   - `AffinePredictor.range_hull`;
   - `_adaptive_radius`.
   The producer calls `exact_newton_predictor` directly with `ExactLambdaRoutedEvaluator`; this is the same exact-lambda predictor that `install_exact_lambda_call_sites()` installs into the binding production candidate path, avoiding an unpinned raw-kernel predictor reconstruction.
2. Exact `F` anchors use the existing `ExactLambdaRoutedEvaluator._evaluate_exact` API with `quantity="F"`, a point `r` interval, exact point lambda, `f_nonzero=True`, and `record=False`. The frozen API returns `(value, interval, evidence)`; the producer reads the per-call count from `evidence["boundary_route_evaluation_count_delta"]` and the route detail from `evidence["detail"]`. It does not assume a fourth return value.
3. Native derivative tiles use the audited B-LOCAL v2.3 API `blocal_v23_boundary.enclose_route("F_lambda", ...)` with explicit `required_sign="NEG"`, no custom accept predicate, and the pinned native route.
4. The producer is orchestration/receipt glue only. It does not alter the shared mathematical kernel, frozen v2.2 files, route normalization, or candidate geometry rules.

## Runtime dependency closure

Before any numerical work, the producer reads the pinned v2.3 source manifest and verifies the exact SHA-256 of every file named by its `legacy_snapshot` against the repository bytes in `dependencies/blocal_v23_source/`. This includes the frozen adapter, v2.2 boundary/model/policy support, phase4 model, symbolic-audit source, and `config.blocal-v2.2-run.json`.

The producer also requires:

- source-manifest `binding_use_authorized=false`;
- native route ID and quantity pins;
- explicit mandatory `required_sign=NEG` policy;
- boundary and shared-kernel SHA agreement with the source manifest;
- `symbolic_reaudit_required=false` and `symbolic_reaudit_status=PASS_CONTENT_LEVEL`;
- formula IDs present in the source manifest;
- the transport receipt and external Judge signature to match the current transport pins with Judge verdict `PASS` and strict-interior scope.

Thus a frozen runtime-support byte mismatch is an abort, not a warning.

## Native proof-object closure

Every native `F_lambda` tile must satisfy the strict NEG sign and cover checks and must also agree with the runtime-pinned proof contract. The producer verifies:

- `native_quantity=true`;
- ordinary formula ID;
- Duffy formula ID;
- transport lemma ID;
- angular, denominator, square-root, gamma, q-lower-bound, and normalization policy IDs;
- route policy object equality with the pinned `F_LAMBDA_ROUTE` policy;
- `effective_evaluation_cap=24000`;
- normalization-bit equality with the frozen model;
- route ID, quantity, explicit NEG sign, complete closed cover, and `monkeypatch_used=false`.

These proof fields are copied into the candidate receipt so the independent checker can compare them without trusting the producer verdict.

## Proof direction

For the upper physical endpoint:

`F(r_hi,lambda) = F(r_hi,lambda_L) + integral_[lambda_L,lambda] F_lambda(r_hi,s) ds`.

Thus a strict negative left anchor together with strict `F_lambda < 0` preserves `F(r_hi,lambda) < 0`.

For the lower physical endpoint:

`F(r_lo,lambda) = F(r_lo,lambda_R) - integral_[lambda,lambda_R] F_lambda(r_lo,s) ds`.

Thus a strict positive right anchor together with strict `F_lambda < 0` preserves `F(r_lo,lambda) > 0`.

The human-audited mathematical precondition is pinned separately as `F_LAMBDA_IS_LAMBDA_DERIVATIVE_OF_ROUTE_F_V1`, scope `CURRENT_STRICT_INTERIOR_ENDPOINT_SCOPE`.

## Precision and margins

Pinned production precision is `dps=60`; checker precision is at least the producer precision.

Previously observed native derivative zero-side limiting margins are approximately:

- upper endpoint: `8.26e-5`;
- lower endpoint: `1.397e-4`.

The expensive exact anchor margins are much smaller:

- upper endpoint left-anchor upper bound approximately `-2.658e-9`;
- lower endpoint right-anchor lower bound approximately `+1.316e-8`.

The derivative transport direction introduces no opposing cancellation term: strict derivative sign is sufficient once the correct strict anchor sign is established. Precision is therefore not increased post hoc; the existing `dps=60` and fixed per-call caps are retained.

## Fixed budgets

- `PRODUCER_ANCHOR_CALL_CAP = 24000` per anchor call.
- `PRODUCER_FLAMBDA_CELL_CALL_CAP = 24000` per derivative tile.
- Base derivative tile width is exactly `1/16`, with the final tile an exact residual if necessary.
- Parent total cap is `2*24000 + 2*n*24000`, where `n` is the exact derivative-tile count.
- Post-hoc cap increase is forbidden.

Therefore the declared parent caps are: `n=4 -> 240000`, `n=3 -> 192000`, `n=2 -> 144000`, and `n=1 -> 96000`. For the nominal parent widths used by the current calibration this corresponds to `1/4 -> 240000`, `1/8 -> 144000`, and `1/16 -> 96000`; an exact residual tiling that yields another tile count uses the formula directly.

## Fail-closed / abort criteria

Abort rather than weaken the claim on any of the following:

- HEAD/source/config/kernel/route/formula/transport-receipt/Judge-signature pin mismatch;
- dirty source tree or unexpected post-baseline file mutation;
- frozen legacy runtime-support SHA mismatch against the source manifest;
- reconstructed candidate/parent/endpoint mismatch or endpoint outside the strict interior scope;
- derivative tiling gap, overlap, reversal, or residual mismatch;
- anchor `CAP_FAIL`, nonfinite result, unresolved sign, or wrong strict sign;
- derivative `CAP_FAIL`, nonfinite result, non-NEG enclosure, incomplete cover, route mismatch, quantity mismatch, implicit/wrong sign contract, proof-contract mismatch, policy mismatch, normalization mismatch, or monkeypatch use;
- any per-call or parent budget excess;
- any evidence-class or authorization-state mismatch.

`CAP_FAIL` is a computational incompleteness result, not a mathematical sign failure.

## Evidence class

Producer output is `BINDING_CANDIDATE` only. It must state:

- `producer_role=AI1_PRODUCER`;
- `checker_required=true`;
- `human_promotion_required=true`;
- `binding_use_authorized=false`.

Independent checker glue must not import producer verdict logic. Binding use remains unauthorized until the independent checker and later human promotion gates are complete.
