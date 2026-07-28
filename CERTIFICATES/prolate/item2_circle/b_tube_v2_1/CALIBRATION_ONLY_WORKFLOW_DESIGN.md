# B-TUBE v2.1 calibration-only workflow design

Status: **DESIGN FOR STATIC AUDIT — NOT AN EXECUTABLE WORKFLOW**

Base: main merge `21618e1b0096de83db7bac5f11eed2b419681b32`

Audited harness source: `CERTIFICATES/prolate/item2_circle/b_tube_v2_1/`

## 1. Purpose and non-purpose

This stage selects candidate numerical operating parameters for the later production
B-TUBE run. It may measure Krawczyk margins, interval inflation, JOIN widths,
subdivision counts, and runtime. It does **not** certify a branch, emit a B-TUBE
verdict, alter theorem endpoints, or discharge any paper-level dependency.

The only permitted terminal states are:

- `CALIBRATION_COMPLETE`
- `CALIBRATION_INCOMPLETE`
- `CALIBRATION_FAILED`

The strings `CERTIFIED_B_TUBE_FULL`, `CERTIFIED_CORE_INTERVAL`, and any other
`CERTIFIED_*` value are forbidden in calibration output.

`lambda_start` is a fixed external exact-rational input from B-LOCAL. Calibration
must not discover, optimize, move, or round it. The terminal endpoint remains the
exact rational `118/25`.

## 2. Source and dependency boundary

The implementation must start from the audited v2.1 checker/schema source without
copying or forking its canonical-byte, dyadic, chain, JOIN, or affine-evaluation
rules. Calibration code may call shared audited helpers but must not weaken them.

Before importing the production kernel, the runner must hash the actual bytes of:

`CERTIFICATES/prolate/item2_circle/vendor/prolate_circle_F_cleanroom.py`

and require SHA-256:

`77e7a93c594ba66ac7d98df29ec3c03107b0c63962a5aa60f8503559082c10ac`

The check must use `Path(imported_module.__file__).read_bytes()` after resolving the
module path, not a module label, exported constant, manifest string, or configured
filename alone. The resolved path must remain inside the checked-out repository.
Symlinks and path escape are rejected.

The C-G terminal dependency remains pinned to the already frozen identity tuple:

- artifact ZIP SHA-256 `c0f624a955657f906c09c45b016a92f7bcdfa70d26c2508efeb3f06dd7d27381`;
- source head `1e0f671c91798b9c044c04c7a4224a21e1e67830`;
- config SHA-256 `bb6a3655d335240549cbe1f6eec2a9e68e00219eb9c1a2be65796e2e342a0d17`;
- fixed-slice identity `F_G_FIXED_SLICE_IDENTITY_V1`;
- exact match parameter `118/25` and bracket `(1/64,11/256)`.

Calibration may report a diagnostic endpoint margin, but it must not emit the
production MATCH conclusion.

## 3. Immutable calibration configuration

A later implementation commit must add one canonical JSON configuration whose
normative fields are limited to:

- exact `lambda_start` and exact `lambda_end = 118/25`;
- a finite ordered list of candidate dyadic parameter widths;
- a finite ordered list of candidate dyadic tube radii;
- exact predictor refresh cadence;
- Arb working precision and checker precision, with `checker_dps >= dps`;
- explicit maximum cells, maximum subdivisions, and evaluation budget;
- the audited-source commit and all external dependency pins;
- a schema version and calibration design version.

No floating JSON numbers are permitted. Candidate order is normative and provides
the deterministic tie-break rule. Environment variables may not override
normative configuration values.

Calibration is fresh-only. Resume files, caches, prior artifacts, and untracked
workspace state are not accepted as mathematical or operational input.

## 4. Evaluation protocol

For each candidate pair, the runner must process the entire fixed interval in a
deterministic order and record every attempted cell, including failures. It may use
rigorous Arb evaluations, but the result remains calibration evidence only.

Required diagnostics per cell are:

- exact parameter endpoints;
- exact affine predictor endpoints;
- exact stored tube interval;
- reconstructed Krawczyk image;
- strict-inclusion margin or the precise failure reason;
- `sup F_r` diagnostic enclosure;
- JOIN intersection width at every shared endpoint;
- evaluation and subdivision counts.

The runner must never substitute a midpoint for a correlated interval expression.
The only affine rule remains `exact_endpoint_convex_hull_v1`.

The selected recommendation is the first candidate, in configured order, for which
all calibration diagnostics complete within the fixed budgets. This is an
engineering recommendation only. Production parameters must be copied into a new,
separately audited production-config commit; calibration output must not rewrite
production configuration automatically.

## 5. Independent calibration verifier

The workflow implementation must run a verifier in a fresh process after the
runner exits. The verifier must:

1. parse stored bytes using the audited canonical JSON/JSONL routines;
2. reject duplicate keys, floats, BOM, CR, final JSONL LF, and noncanonical bytes;
3. verify the record chain over canonical object bytes, excluding JSONL linefeeds;
4. recompute candidate completeness and deterministic recommendation selection;
5. re-hash the imported production-kernel file bytes independently;
6. reject every `CERTIFIED_*` string and every production verdict field;
7. require `real_analytic: false` if a machine-conclusion-shaped diagnostic object
   is retained; omission, `true`, and extra fields are rejected;
8. return nonzero unless the stored result and receipt are byte-consistent.

Runner success alone is never sufficient for artifact upload.

## 6. In-run receipt byte closure

The delivery payload is assembled before upload in a new empty directory. It must
contain the canonical configuration, calibration records, summary, checker report,
source/dependency manifest, and exact source files needed for replay.

The workflow then performs this closed loop:

1. hash the actual bytes of every payload file in sorted path order;
2. write canonical `PAYLOAD_SHA256SUMS.json` with no trailing newline;
3. re-read every payload file and verify the recorded hashes;
4. build one deterministic local archive from the verified payload;
5. hash the actual archive bytes;
6. write canonical `DELIVERY_RECEIPT.json` containing the archive hash, payload
   manifest hash, source head, workflow source hash, configuration hash, kernel
   file-byte hash, and terminal calibration state;
7. re-read the receipt bytes and independently reconstruct the expected canonical
   receipt bytes;
8. require exact byte equality and re-check every referenced digest;
9. upload only the already verified archive and receipt.

The platform-generated outer artifact ZIP is transport only and is not a proof
node. No later observer is allowed to repair or complete the receipt.

## 7. Workflow security and lifecycle

The eventual workflow must use least privilege:

```yaml
permissions:
  contents: read
```

Checkout must use `persist-credentials: false`. No secrets, GitHub API writes,
issue/PR comments, branch writes, release writes, or observer writes are permitted.
Dependency versions and accepted wheel hashes must be locked in committed input.

No executable workflow file is included in this design commit. After design audit,
the implementation workflow is temporary and calibration-only. It must be removed
before any result-bearing branch is merged to main, so the probe/calibration entry
does not remain in the Actions UI. The accepted result commit retains the workflow
source bytes and SHA-256 inside the delivery payload for replay.

## 8. Required controls

The implementation must add at least these fail-closed controls:

1. production kernel file-byte SHA mismatch;
2. imported module path escape or symlink substitution;
3. C-G artifact, source-head, config, reference-kernel, or lemma mismatch;
4. `lambda_start` changed by calibration;
5. terminal endpoint not exactly `118/25`;
6. `checker_dps < dps`;
7. unordered or duplicate candidate list;
8. float or noncanonical numeric field;
9. midpoint/correlation-destroying affine fallback detected;
10. missing attempted-cell record;
11. candidate recommendation not equal to deterministic first passing candidate;
12. any `CERTIFIED_*` output;
13. payload file changed after manifest creation;
14. archive byte changed after receipt creation;
15. receipt canonical-byte mismatch;
16. attempted GitHub write or credential persistence;
17. stale resume/cache input present;
18. executable workflow surviving in the merge diff.

Positive controls must include the precision equality boundary and an incomplete
calibration that uploads a valid diagnostic artifact with state
`CALIBRATION_INCOMPLETE` but no recommendation.

## 9. Static-audit gate

The next implementation stage may begin only after this design is audited for:

- exact scope separation between calibration and certification;
- actual production-kernel file-byte pinning;
- complete in-run receipt byte closure;
- deterministic configuration and recommendation rules;
- no persistent workflow/UI residue;
- preservation of all audited v2.1 canonical and JOIN semantics.

Design acceptance authorizes implementation only. It does not authorize a
calibration run or production B-TUBE run.
