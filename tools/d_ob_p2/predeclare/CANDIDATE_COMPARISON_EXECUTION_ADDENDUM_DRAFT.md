# D-OB P2 SPEC V3 candidate comparison — execution addendum draft

Status: DRAFT FOR CHAT AUDIT / DIAGNOSTIC / NOT_EVIDENCE / EXECUTION BLOCKED

## D1 — C-regular derived producer
Base producer SHA-256: `dff79bc40d78d53a1491c3edbe368034b2d28a4894da45ac13b3b04c3ad0f19b`.
Derived producer SHA-256: `b7ad3fbf7ca41539b43959fd3645a2e34d397decb175cf7511daa127cb6297d2`.
The only byte-level source-line change is `take=(nreg+3)//4` -> `take=(nreg+1)//2`; `verify_c_regular_delta.py` fails closed otherwise.
Every output row records `used_producer_sha256`. C-regular uses only the derived producer; all other candidates use only the base producer. Both are DIAGNOSTIC / NOT_EVIDENCE.
Verifier SHA-256: `7339506ce354507868c1860c733e75859beeb8e360d384057c86d60d66dccf59`.

## D2 — full driver and frozen inputs
Config SHA-256: `4014210732502fa6c3f4f4aa9348b1df8c7384a921b3ba8f426891c66725226e`.
Driver SHA-256: `27d3fe68083df1d70f736194eb45425571c1d95638a1035e1ffdb196156625eb`.
C1: `results_192.tsv`, SHA `6ad29461e42c265ce136e8df114400072e939335d72e2033b79741461e93fa90`, exactly 192 rows.
C2: `independent_H_sign_N7_result.tsv`, SHA `ea166df49d8d0486fe836088fdbc13acbd0154811c882ae98b2a3f92275a8b9c`, provenance basepoint-geometry commit `dabc2a3b`. Loader asserts 9 rows, class from field 1, key from field 2, exactly 2 A + 7 N, and reconstructs exact r/t/lambda/rho/z from the key; TSV float rho/z/lambda are reference-only.
C3: Phase-0 `phase0_points.tsv`, SHA `361db4a7c5fbe3bc6c8afc335282af8b26a1bf653dd5edf1dde56d08e634b4e0`, exactly 44 POSITIVE rows.
C4: `P003_lambda251.tsv`, SHA `85d6146ac1b92d50fac85a6560b2679f7aa74fa89afd904f5d3838309ccca360`; independent-J input SHA `0a1ac7708a462868597bc94de38899bb381dd226514ff693c187dc52927d52ee`; exact seven frozen targets asserted.
C5: `full_terminal_map.tsv`, SHA `0584110495c9d3b98a96d88e3d9fbe717bde326f2b76dcc465db784ad3bd26f8`. C1 requires containing 7,7,0 depth-12 terminal box; C4 requires containing terminal 0,0,3 box with no artificial depth-12 restriction. Half-open membership with global-upper closure is applied and exactly-one is fail-closed. Expected count = 199.

The driver has the v2 section-9 schema explicitly frozen, includes explicit baseline C0 execution, and records candidate/set output identity and producer SHA. Missing independent-J values are represented by empty value plus `missing_reason`; they are never synthesized.
A2-type precheck requires producer RHO0 to have the exact Fraction type used by the override and all three resource globals to remain ints. Both base and derived producer must pass before execution.

## D3 — repository separation
Diagnostic tooling home is the basepoint-geometry repository. This branch was created from basepoint-geometry `origin/main` at `abf704b8701f3da8eb41d8a99408570a413b2214`.
No comparison harness commit is to be merged/cherry-picked into the canonical D-OB certification repository. Future canonical push may carry D-OB documentation commits only; diagnostic harness history remains in basepoint-geometry.
Formal producer/checker RUN_DIR is never used by this driver or wrapper.

## D4 — execution identity and staged plan
Executor: `/home/daybreak/.pyenv/versions/3.11.16/bin/python`.
Host: `daybreak-works`.
Workers field: `10` (recorded by G7 wrapper; current point/box driver is serial, so this is provenance only and does not alter computation).
Repository/worktree at audit: `/tmp/dob-p2-comparison-clean`.
Diagnostic output root: `/home/daybreak/basepoint-geometry-artifacts/D_OB_P2_candidate_comparison/` only.
G7 wrapper SHA-256: `6bbb1a1fd91e37efd43c94a3fc3c0ae2117e20a88480ebe561c626bb26d4e360`.

Staging is candidate-by-set. No stage may begin before this addendum and all source bytes are countersigned. For each stage, one unique output directory is created and G7 records host, PID, UTC start/end, actual exit code, log SHA, script/input identities, candidate, set, and workers.
Order: C0 C1..C5; C-count C1..C5; C-cell-depth C1..C5; C-box-depth C1..C5; C-regular C1..C5; D-rho-1-16 C1..C5; D-rho-3-32 C1..C5; D-rho-5-32 C1..C5; D-rho-1-4 C1..C5. `D-rho-1-8` is the frozen C0 alias and is not rerun.
Expected successful driver terminal line is exactly: `EXECUTION_COMPLETE candidate=<CID> set=<SET> rows=<N> output=<ABSOLUTE_TSV>`, with N = 192,9,44,7,199 for C1..C5 respectively. Any `INVALID ...`, nonzero exit, pin mismatch, exactly-one failure, A2 type failure, schema failure, or unexpected row count invalidates that stage and stops progression.

Ignition command requires explicit `--execute-token AUDITED_ADDENDUM_REQUIRED`; absence of the token is fail-closed. This token is only a mechanical post-countersign gate and MUST NOT be supplied before chat countersign.

## Pre-ignition audit state
Check-only must report exactly `C2_classes={A:2,N:7}`, counts C1=192 C2=9 C3=44 C4=7 C5=199, two `A2_TYPE_PRECHECK_OK`, `SECTION9_SCHEMA_OK`, baseline C0 explicit, and alias `D-rho-1-8 -> C0`.
Execution remains BLOCKED pending chat byte audit and countersign.
