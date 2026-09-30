# D-OB P2 SPEC V3 candidate comparison — execution addendum draft

Status: DRAFT FOR CHAT AUDIT / DIAGNOSTIC / NOT_EVIDENCE / EXECUTION BLOCKED

## D1 — C-regular derived producer
Base producer SHA-256: `dff79bc40d78d53a1491c3edbe368034b2d28a4894da45ac13b3b04c3ad0f19b`.
Derived producer SHA-256: `b7ad3fbf7ca41539b43959fd3645a2e34d397decb175cf7511daa127cb6297d2`.
The only source-line delta is `take=(nreg+3)//4` -> `take=(nreg+1)//2`; verifier SHA `7339506ce354507868c1860c733e75859beeb8e360d384057c86d60d66dccf59` fails closed otherwise. Every output row records `used_producer_sha256`. C-regular alone uses the derived producer. Both are DIAGNOSTIC / NOT_EVIDENCE.

## D2 — full driver and frozen inputs
Config SHA: `4014210732502fa6c3f4f4aa9348b1df8c7384a921b3ba8f426891c66725226e`. Driver SHA: `4835b543b188557a554cca97fa7cfb98016298fac79459addd6648e5d4ff093a`.
All frozen input bytes are committed under `tools/d_ob_p2/` and are refuse-on-mismatch. The five host-origin TSVs are marked `-text -diff` in `.gitattributes` solely to preserve their original bytes/CRLF and prevent Git whitespace normalization:
- C1 `results_192.tsv`: `6ad29461e42c265ce136e8df114400072e939335d72e2033b79741461e93fa90`, 192 rows.
- C2 `independent_H_sign_N7_result.tsv`: `ea166df49d8d0486fe836088fdbc13acbd0154811c882ae98b2a3f92275a8b9c`, provenance commit `dabc2a3b`; 9 rows, class/key mechanically read, 2A+7N asserted, exact centre reconstructed from key. TSV float rho/z/lambda are reference-only.
- C3 `phase0_points.tsv`: `361db4a7c5fbe3bc6c8afc335282af8b26a1bf653dd5edf1dde56d08e634b4e0`, 44 POSITIVE rows.
- C4 `P003_lambda251.tsv`: `85d6146ac1b92d50fac85a6560b2679f7aa74fa89afd904f5d3838309ccca360`; C4 independent-J `P003_independent_J_lambda251.tsv`: `0a1ac7708a462868597bc94de38899bb381dd226514ff693c187dc52927d52ee`; exact seven targets asserted.
- C5 `full_terminal_map.tsv`: `0584110495c9d3b98a96d88e3d9fbe717bde326f2b76dcc465db784ad3bd26f8`. C1 requires containing 7,7,0 depth-12 terminal; C4 requires containing terminal 0,0,3 with no artificial depth-12 restriction. Half-open/global-upper-closed membership and exactly-one are fail-closed; expected 199 targets.

C5 evaluation uses a box-tree walk from each frozen C5 terminal box, in producer order: column classification; refine for non-straddle; accept if proved; otherwise terminal unresolved at configured MAX_BOX_DEPTH; otherwise split and recurse. Thus C0 depth-12 frozen boxes remain terminal as frozen, while C-box-depth=13 can perform the permitted extra box split. For C5, the output `max_box_depth` is the achieved depth of the unique target-containing terminal leaf, not the configured ceiling; the ceiling remains in `resource_settings`. Outside C5 no box walk is evaluated, so `max_box_depth` is empty and `missing_reason` records `box_depth_not_evaluated_outside_C5`.

The v2 section-9 schema is explicit and includes baseline C0. Candidate/set identity and row-level producer SHA are mandatory. Missing independent-J is empty plus `missing_reason`, never synthesized. A2 precheck requires RHO0 exact Fraction type and integer resource globals.

G1/G2 diagnostic rule: this comparison driver does NOT claim independent lower/upper reconstruction. It reads producer `L` and `B_cut`, converts enclosure endpoints to float for the comparison table, and forms the displayed upper quantity from producer regular-cell bounds plus B_cut. These are DIAGNOSTIC comparison quantities, not G1/G2 independent evidence and not certification evidence. Any future formal G1/G2 claim requires a separately frozen independent reconstruction.

## D3 — repository separation
Diagnostic tooling home is basepoint-geometry. This branch is based on basepoint-geometry `origin/main` `abf704b8701f3da8eb41d8a99408570a413b2214`. No comparison harness commit is to be merged/cherry-picked into the canonical D-OB certification repository. Future canonical push may carry D-OB documentation commits only. Formal producer/checker RUN_DIR is never used.

## D4 — execution identity and staged plan
Executor: `/home/daybreak/.pyenv/versions/3.11.16/bin/python`. Host: `daybreak-works`. Repository/worktree at audit: `/tmp/dob-p2-comparison-clean`. Diagnostic output root: `/home/daybreak/basepoint-geometry-artifacts/D_OB_P2_candidate_comparison/` only. Workers provenance field: `10`; current driver is serial, so this field records resource intent and does not alter computation. G7 wrapper SHA: `408975e35cdb8b677e0c9a336985de7813c694fd7d0a4657a9a0d0c6bcc0e443`.

The G7 wrapper accepts candidate/set exactly once, constructs all driver paths itself, hashes driver/config/derived producer/base producer and every frozen input TSV, records host/PID/UTC start/end/actual exit/log+result SHA, and rejects output outside the diagnostic root or an existing output directory.

Execution is candidate-by-set after countersign only: C0 C1..C5; C-count C1..C5; C-cell-depth C1..C5; C-box-depth C1..C5; C-regular C1..C5; D-rho-1-16 C1..C5; D-rho-3-32 C1..C5; D-rho-5-32 C1..C5; D-rho-1-4 C1..C5. `D-rho-1-8` is the C0 alias and is not rerun.

Expected successful terminal line is exactly `EXECUTION_COMPLETE candidate=<CID> set=<SET> rows=<N> output=<ABSOLUTE_TSV>`, N=192,9,44,7,199 for C1..C5. Any `INVALID ...`, nonzero exit, pin mismatch, exactly-one failure, A2/schema failure, unexpected count, or G7 path failure invalidates that stage and stops progression.

Ignition requires explicit `--execute-token AUDITED_ADDENDUM_REQUIRED`; it MUST NOT be supplied before chat countersign. Check-only must report C2 A=2/N=7, C1=192 C2=9 C3=44 C4=7 C5=199, two A2 passes, section-9 schema pass, explicit C0 baseline and C0 alias. Execution remains BLOCKED.
