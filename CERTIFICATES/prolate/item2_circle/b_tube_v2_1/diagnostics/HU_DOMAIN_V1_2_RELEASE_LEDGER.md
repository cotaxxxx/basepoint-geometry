# PRODUCTION_HU_DOMAIN_CONTRACT_V1.2 release ledger

- Contract: `PRODUCTION_HU_DOMAIN_CONTRACT_V1_2`
- Status: `RELEASED`
- Release SHA: `6d705c6fbf37ae77d35232a40842692a3e92713e`
- Stable branch: `btube-v2-3-native-flambda`
- Release tag: `hu-domain-v1.2` -> `6d705c6fbf37ae77d35232a40842692a3e92713e`.
- Release evidence: contract + pinned independent checker + cell-0 positive control.
- Cell-0 positive-control evidence class: `POSITIVE_CONTROL_NOT_BINDING`.
- Cell-0 positive control is not a substitute for any cell-specific production execution.

## V1.2 policy scope

The released `hu_domain_v1_2_stage_policy.json` remains byte-frozen. Its `stage_semantics`, `stages`, `per_box_cap=24000`, and `dps=60` are the shared V1.2 production semantics. Its embedded `parent` field is **positive-control-only** and is not a production parent authority.

For production, the parent rectangle is reconstructed from MONOTONE_TUBE_V1.1 Component 1 exact candidate inputs `q_left`, `q_right`, `sigma`, `rho_cap`, `lambda_start`, `W_nom`, `lambda_end`, and `cell_index`; the H_U checker requires exact equality with `receipt.parent`. No hand-written production-parent constant is trusted.

`TUBE_GEOMETRY_PROVENANCE = REPRODUCIBILITY_ONLY_NOT_LOAD_BEARING`.

`LOAD_BEARING = CROSS_COMPONENT_RECTANGLE_IDENTITY`.

The Component-1 geometry receipt is the single source of rectangle identity. H_U, F_lambda, and join receipts must pin the same Component-1 receipt SHA, and the MONOTONE assembly checker must require SHA identity across those components. The recorded origin of `q_left/q_right`, predictor history, sigma/rho-cap selection, source head, and source SHA exists for reproducibility and audit; the H_U checker does not numerically replay Newton/predictor generation.

Exact reconstruction module:

- `hu_domain_v1_2_tube_geometry.py`
- SHA256 `b0489c3c6201b44c54838b3d72c8692a99a25c939d692074761c51da73e63300`
- schema gate: `monotone-tube-v1.1-component1-geometry-receipt-v1`
- role: `MONOTONE_COMPONENT1_PARENT_RECONSTRUCTOR`
- for cell 0 only, the reconstructed parent must additionally equal historical policy `parent`; this remains a cross-check only.

## Producer roles

Frozen release producer:

- `hu_domain_v1_2_cell0_positive_control.py`
- SHA256 `e5bc568172befe3a368c4fc7c6f0ae18f70dffe685e560a638bf3efb20fb6f50`
- roles: `RELEASE_POSITIVE_CONTROL_PRODUCER` and `CELL0_REPLAY_PRODUCER` only.

Cell-independent production producer:

- `hu_domain_v1_2_production_producer.py`
- SHA256 `56b28657f3d8483bcd0e63de2f97a0e3867f1d274b4b2bd05a427f8473bc40a4`
- role: `CELL_INDEPENDENT_PRODUCTION_PRODUCER`
- policy `parent` is ignored; parent comes from the Component-1 geometry receipt.
- execution requires explicit `--expected-head`, `SOURCE_TREE_PRE=CLEAN`, `SOURCE_TREE_POST=CLEAN`, and `HEAD_UNCHANGED_DURING_RUN=TRUE`.

Runtime dependency content pins mirror the F_lambda precheck dependency set: model, adapter, boundary v2.2, boundary v2.3, policy, symbolic audit, B-LOCAL config, route fragment, `calibration_runner.py`, and `exact_lambda_transport.py`; the v2.3 shared kernel and production kernel are pinned as well. Existing F_lambda SHA256 pins are reused where available. `calibration_runner.py` and `exact_lambda_transport.py` are pinned by Git blob SHA-1 at the explicitly pinned clean execution HEAD (`a98e95f0696fd8a43e69676df2bba594d2501d7e`, `e4c5be230fe6d86269c764f750baa1f9ff9b5202`).

## Status vocabulary

Production raw status vocabulary is fixed:

- `PASS_POS`: resolved positive leaf.
- `UNRESOLVED_SIGN`: complete angular cover but lower bound `<= 0`; refinable.
- `ABORT_BUDGET`: evaluation budget abort; refinable.
- `ABORT_INCOMPLETE_COVER`: incomplete angular cover; refinable.
- `ABORT_NONFINITE`: hard fail.
- `ABORT_INTERNAL`: hard fail.

The shared checker core accepts the first four states, rejects both hard-fail states, reconstructs first-passing semantics, and reports reason-separated refinable counts. The frozen cell-0 replay receipt uses historical `ABORT`; the production checker applies one explicit compatibility adapter only for `ABORT + ANGULAR_EVALUATION_BUDGET -> ABORT_BUDGET` before shared-core validation. No other legacy abort is normalized.

## Checker roles

The checker frozen in the V1.2 release remains unchanged:

- `hu_domain_v1_2_independent_checker.py`
- SHA256 `d83d5767c2fcaede1adc0f1c97cd10920b358b402d24d632b0b31bb5f9d26327`
- role: `POSITIVE_CONTROL_SPECIFIC_CHECKER`.

Post-release production checking uses:

- shared semantic core: `hu_domain_v1_2_checker_core.py`
- core SHA256 `1075d0fefe31117a0cebe99b24321e9cb4e011590102011fb4d1873fcd2af4b2`
- production checker: `hu_domain_v1_2_production_checker.py`
- production checker Git blob SHA-1 `5815cb3a3eddfa1ecf4764a189c2edb7438ac92e`
- role: `CELL_INDEPENDENT_PRODUCTION_CHECKER`.

The production checker allowlists exactly the frozen cell-0 replay producer and the cell-independent production producer. It has no positive-control result-SHA pin and no positive-control execution-head equality pin. It requires the Component-1 geometry receipt SHA in the production attestation, reconstructs the exact parent from that receipt, checks `receipt.parent` exactly, verifies the receipt execution head exists as a Git commit, and delegates finite-stage semantics, budgets, exact cover, and margin to the shared core.

## Promotion rule

A production-checker PASS leaves evidence at `PRODUCTION_CANDIDATE`. It may record `READY_FOR_JUDGE_PROMOTION`, but it must keep `binding_use_authorized=false` and `monotone_narrow_interface_authorized=false`. Binding use requires a separate Judge promotion/signature.

After Judge promotion, MONOTONE_TUBE may consume only:

- `ALL_TERMINAL_LO_POSITIVE`
- `UNION_EQUALS_PARENT`
- `CERTIFIED_COVER_MARGIN_POSITIVE`, retaining the exact certified cover margin and `COVER_MARGIN_IS_TRUE_MINIMUM=NO`.

The promoted H_U receipt must retain `component1_geometry_receipt_sha256`; assembly must match it exactly against the corresponding F_lambda and join receipts.
