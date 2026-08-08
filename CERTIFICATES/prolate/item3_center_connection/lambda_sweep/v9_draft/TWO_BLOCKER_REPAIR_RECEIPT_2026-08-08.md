# Item 3 sweep v9 — repair receipt

Status: **FOCUSED REGRESSION PASS / FREEZE STILL NOT AUTHORIZED**

Date: 2026-08-08

## Repairs

1. Dependency builder binds the existing `v9_candidate/SOURCE_FORMULA_MAP_CANDIDATE_V2.md`.
2. Aggregate verifier rejects any shard evidence whose `driver_id` is not exactly `ITEM3_SWEEP_V9_REHEARSAL_DRIVER_CANDIDATE_V3`.
3. Driver/config parsing now uses the same eight-key common source map as the plan/aggregate layer, including the pinned aggregate-verifier bytes.

## Focused controls

The workflow compiled and ran dependency-builder, plan/config-builder, aggregate-verifier, and driver-v3 binding control suites. This receipt is written only after all focused controls pass.

## Source identities after repair

- build_dependency_snapshot_v9.py sha256: `ab34923ebd906188ed0994e7edb7f796151416e53040ce1e0f6f98b880c2069f`
- aggregate_verifier_v9_candidate_v2.py sha256: `bdb0eaa12f241108fbdd03e38cde34d1f1ffe085cff8fef89b413fe4dd255001`
- rehearsal_driver_v9_candidate_v3.py sha256: `00716ac58dbc7a6d9a6a2f8d651a550b45a4c8e6e0697efcea6ae7f7bb40438a`
- test_rehearsal_driver_v3_binding.py sha256: `f1d3144225d16b5be5fccb61fe1f7ec8e47562ede3c7f862fbd6a190a15803fa`

This repair does not issue a production tag, freeze receipt, production rehearsal, `CERTIFIED_LAMBDA_RANGE`, or paper-level completion claim.
