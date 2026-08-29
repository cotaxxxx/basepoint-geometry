# PRODUCTION_HU_DOMAIN_CONTRACT_V1.2 release ledger

- Contract: `PRODUCTION_HU_DOMAIN_CONTRACT_V1_2`
- Status: `RELEASED`
- Release SHA: `6d705c6fbf37ae77d35232a40842692a3e92713e`
- Stable branch: `btube-v2-3-native-flambda`
- Release tag: `hu-domain-v1.2` -> `6d705c6fbf37ae77d35232a40842692a3e92713e`.
- Release evidence: contract + pinned independent checker + cell-0 positive control.
- Cell-0 positive-control evidence class: `POSITIVE_CONTROL_NOT_BINDING`.
- Cell-0 positive control is not a substitute for any cell-specific production execution.
- Production H_U domain runs for the actual MONOTONE_TUBE cells remain outstanding and must each produce their own production receipt under the released V1.2 stage semantics.

## Checker roles

The checker frozen in the V1.2 release remains unchanged:

- `hu_domain_v1_2_independent_checker.py`
- SHA256 `d83d5767c2fcaede1adc0f1c97cd10920b358b402d24d632b0b31bb5f9d26327`
- Role: `POSITIVE_CONTROL_SPECIFIC_CHECKER`.
- It retains the historical positive-control baseline, execution-head, and result-SHA pins. It is not the checker for production-cell receipts.

Post-release production checking is supplied by:

- shared semantic core: `hu_domain_v1_2_checker_core.py`
- core SHA256: `16a8ab78fef3cbd6754d17b015ea8b90059af1145beec8c5ca3316ca0d33f628`
- production checker: `hu_domain_v1_2_production_checker.py`
- production checker SHA256: `34add1065baad6fbc35bfd557ccbdbc0de498b99762c984c3b902fc403e79f2d`
- Role: `CELL_INDEPENDENT_PRODUCTION_CHECKER`.
- The production checker has no positive-control result-SHA pin and no positive-control execution-head equality pin.
- It gates on the released policy/producer pins, production-attestation provenance, receipt-internal pins, and existence of the receipt execution head as a Git commit, then reconstructs stage order, first-passing semantics, immutable terminal leaves, raw budget accounting, exact cover, and certified cover margin through the shared core.

Because the release commit/tag is immutable, the frozen positive-control checker is intentionally not rewritten to import the post-release core. Its released bytes remain the authoritative historical positive-control verifier; the shared core is the extracted production semantic implementation.

## Promotion rule

A production-checker PASS leaves the evidence at `PRODUCTION_CANDIDATE`. It may record `READY_FOR_JUDGE_PROMOTION`, but it must keep `binding_use_authorized=false` and must not authorize the MONOTONE narrow interface. Binding use requires a separate Judge promotion/signature.

After Judge promotion, MONOTONE_TUBE may consume only the narrow H_U interface of the promoted production receipt:

- `ALL_TERMINAL_LO_POSITIVE`
- `UNION_EQUALS_PARENT`
- `CERTIFIED_COVER_MARGIN_POSITIVE` with exact certified cover margin retained and `COVER_MARGIN_IS_TRUE_MINIMUM=NO`.
