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

For production, the parent rectangle is derived from MONOTONE_TUBE_V1.1 Component 1. The checker reconstructs it from exact candidate inputs `q_left`, `q_right`, `sigma`, `rho_cap`, `lambda_start`, `W_nom`, `lambda_end`, and `cell_index`; it then requires exact equality with `receipt.parent`. No hand-written production-parent constant is trusted.

Exact reconstruction module:

- `hu_domain_v1_2_tube_geometry.py`
- SHA256 `9d2a8557d4761b9b30d05bc22c7923f117dba199a63e850c516700ff40097d6a`
- Role: `MONOTONE_COMPONENT1_PARENT_RECONSTRUCTOR`.
- For cell 0 only, the reconstructed parent must additionally equal the historical policy `parent`; this is a cross-check, not the source of production geometry.

## Producer roles

The producer frozen in the V1.2 release is:

- `hu_domain_v1_2_cell0_positive_control.py`
- SHA256 `e5bc568172befe3a368c4fc7c6f0ae18f70dffe685e560a638bf3efb20fb6f50`
- Roles: `RELEASE_POSITIVE_CONTROL_PRODUCER` and `CELL0_REPLAY_PRODUCER` only.
- It is not the general producer for cell 1 and later.

Cell-independent production execution is supplied by:

- `hu_domain_v1_2_production_producer.py`
- SHA256 `760100397141d3e8983190e256e3e49aefb1b320fdb7d52cc94434321dec99b3`
- Role: `CELL_INDEPENDENT_PRODUCTION_PRODUCER`.
- It consumes the released stage semantics/cap/dps but intentionally ignores policy `parent`.
- Its exact parent is reconstructed from the Component-1 tube-geometry input before any H_U evaluation.

## Checker roles

The checker frozen in the V1.2 release remains unchanged:

- `hu_domain_v1_2_independent_checker.py`
- SHA256 `d83d5767c2fcaede1adc0f1c97cd10920b358b402d24d632b0b31bb5f9d26327`
- Role: `POSITIVE_CONTROL_SPECIFIC_CHECKER`.
- It retains the historical positive-control baseline, execution-head, and result-SHA pins. It is not the checker for production-cell receipts.

Post-release production checking uses:

- shared semantic core: `hu_domain_v1_2_checker_core.py`
- core SHA256 `16a8ab78fef3cbd6754d17b015ea8b90059af1145beec8c5ca3316ca0d33f628`
- production checker: `hu_domain_v1_2_production_checker.py`
- production checker SHA256 `12fda2bed3c74aa16b232c125eae1ef6281dd96b1057c3b11ff4d29f83121c4e`
- Role: `CELL_INDEPENDENT_PRODUCTION_CHECKER`.

The production checker allowlists exactly two producer roles: the cell-0 replay producer above and the cell-independent production producer above. It has no positive-control result-SHA pin and no positive-control execution-head equality pin. It requires the receipt execution head to exist as a Git commit, reconstructs the production parent from Component-1 candidate inputs and requires exact equality with `receipt.parent`, then delegates stage order, first-passing, resolved-leaf immutability, raw budget accounting, exact cover, and certified cover margin to the shared core.

Because the release commit/tag is immutable, the frozen positive-control checker is intentionally not rewritten to import the post-release core. Its released bytes remain the authoritative historical positive-control verifier.

## Promotion rule

A production-checker PASS leaves evidence at `PRODUCTION_CANDIDATE`. It may record `READY_FOR_JUDGE_PROMOTION`, but it must keep `binding_use_authorized=false` and `monotone_narrow_interface_authorized=false`. Binding use requires a separate Judge promotion/signature.

After Judge promotion, MONOTONE_TUBE may consume only:

- `ALL_TERMINAL_LO_POSITIVE`
- `UNION_EQUALS_PARENT`
- `CERTIFIED_COVER_MARGIN_POSITIVE`, retaining the exact certified cover margin and `COVER_MARGIN_IS_TRUE_MINIMUM=NO`.
