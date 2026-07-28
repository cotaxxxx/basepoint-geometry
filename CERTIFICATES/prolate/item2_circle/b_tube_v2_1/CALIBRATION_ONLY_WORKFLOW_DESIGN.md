# B-TUBE v2.1 — calibration-only workflow design

Status: **DESIGN APPROVED; IMPLEMENTATION PRESENT; RUN NOT AUTHORIZED**

Design commit: `4a1b12a2a1e4f89712c33bc554646b44190f6f5b`

Audited harness source: `CERTIFICATES/prolate/item2_circle/b_tube_v2_1/`

## 1. Purpose and non-purpose

This stage selects candidate numerical operating parameters for a later production
B-TUBE run. It may measure Krawczyk margins, interval inflation, JOIN widths,
subdivision counts, and evaluation budgets. It does not certify a branch, alter
theorem endpoints, discharge a paper-level dependency, or emit a production
B-TUBE verdict.

The only permitted terminal states are:

- `CALIBRATION_COMPLETE`
- `CALIBRATION_INCOMPLETE`
- `CALIBRATION_FAILED`

Every `CERTIFIED_*` value and every production verdict field is forbidden in
calibration output.

`lambda_start` is the fixed exact-rational B-LOCAL input. Calibration must not
discover, optimize, move, or round it. The terminal endpoint is exactly `118/25`.

## 2. Source and dependency boundary

The implementation calls the audited v2.1 canonical-byte, dyadic, chain, affine,
Krawczyk, and JOIN primitives. It must not copy or weaken those rules.

The actual imported file bytes of

`CERTIFICATES/prolate/item2_circle/vendor/prolate_circle_F_cleanroom.py`

must hash to

`77e7a93c594ba66ac7d98df29ec3c03107b0c63962a5aa60f8503559082c10ac`.

The resolved imported path must be a regular non-symlink file inside the checkout.
The check uses the actual imported module path and file bytes, not an exported
constant, configured label, manifest name, or wrapper-module identity.

**F and F_r must both be supplied only by this same pinned file. Supplying F_r
from any other module or file is forbidden.** The implementation verifies that
both `F_arb` and `dFdr_arb` are defined by the single loaded module. This closes
carryover G1 and prevents a later separate derivative module from escaping the pin.

The C-G terminal identity tuple remains frozen:

- artifact ZIP SHA-256 `c0f624a955657f906c09c45b016a92f7bcdfa70d26c2508efeb3f06dd7d27381`;
- source head `1e0f671c91798b9c044c04c7a4224a21e1e67830`;
- config SHA-256 `bb6a3655d335240549cbe1f6eec2a9e68e00219eb9c1a2be65796e2e342a0d17`;
- reference-kernel SHA equal to the production-kernel SHA above;
- paper/interface lemma `F_G_FIXED_SLICE_IDENTITY_V1`;
- exact match parameter `118/25`;
- exact bracket `(1/64,11/256)`.

Calibration may record endpoint diagnostics but may not emit the production MATCH
conclusion.

## 3. Immutable configuration

`config.calibration.json` is canonical JSON with no trailing newline, duplicate
keys, floating JSON numbers, BOM, or CR/LF. Its normative fields are limited to:

- exact `lambda_start` and `lambda_end`;
- ordered unique dyadic parameter widths;
- ordered unique dyadic tube radii;
- predictor refresh cadence;
- Arb working and checker precision with `checker_dps >= dps`;
- maximum cells, subdivisions, and evaluation budget;
- audited-source and design commits;
- production and C-G dependency pins;
- exact affine rule, schema, design version, and chain domain.

Candidate order is normative. The cross-product order is parameter-width order
followed by tube-radius order. The first passing pair is the only permitted
recommendation. Environment variables cannot replace normative configuration
values.

Calibration is fresh-only. Resume files, checkpoints, caches, prior output, and
pre-existing output directories are rejected.

## 4. Evaluation protocol

For each candidate pair the runner covers the entire fixed parameter interval in
deterministic exact-rational cells. It records every attempted cell, including
failures.

Predictor endpoint values are exact dyadics. The only affine rule is
`exact_endpoint_convex_hull_v1`; midpoint substitution for correlated interval
expressions is forbidden.

Each cell record contains:

- exact parameter endpoints;
- exact predictor endpoints and tube interval;
- residual and derivative enclosures;
- exact preconditioner;
- reconstructed Krawczyk image;
- strict left and right margins or a precise failure reason;
- derivative-sign diagnostic;
- evaluation and subdivision counts.

Each shared endpoint receives a separate exact JOIN intersection record and width.
A candidate passes only when all cells satisfy strict Krawczyk inclusion, the
derivative enclosure is strictly negative, all JOINs have positive width, and all
fixed budgets are respected.

A recommendation remains engineering evidence only. It cannot rewrite a production
configuration.

## 5. Independent verification

The workflow invokes `calibration.py verify` in fresh Python processes after the
runner and after delivery.

The verifier:

1. parses configuration, records, summaries, manifests, and receipts through the
   audited canonical-byte routines;
2. rejects duplicate keys, floats, BOM, CR, final JSONL LF, and noncanonical bytes;
3. verifies the chain over canonical record-object bytes, excluding JSONL linefeeds;
4. verifies candidate completeness and recomputes the deterministic first passing
   recommendation;
5. independently re-hashes the actual production F/F_r file bytes;
6. rejects every `CERTIFIED_*` string and production verdict field;
7. requires `machine_conclusion` to be exactly `{"real_analytic":false}`;
8. verifies exact receipt, archive, manifest, workflow, config, source-head, and
   kernel-byte consistency.

Runner success alone cannot authorize upload.

## 6. In-run receipt byte closure

Delivery is built in a new empty directory.

1. Copy canonical config, records, summary, checker report, source manifest, exact
   replay sources, pinned production kernel, requirement lock, design, and workflow.
2. Hash every payload file in sorted relative-path order.
3. Write canonical `PAYLOAD_SHA256SUMS.json` without a trailing newline.
4. Re-read every file and verify every recorded digest.
5. Build a deterministic ZIP with sorted paths, fixed timestamps and modes.
6. Hash the actual ZIP bytes.
7. Write canonical `DELIVERY_RECEIPT.json` containing archive, payload-manifest,
   workflow, config, kernel, source-head, and terminal-state identities.
8. Re-read and independently reconstruct the receipt bytes.
9. Re-check all referenced digests and upload only the verified archive and receipt.

The platform outer artifact ZIP is transport only. No observer may repair or
complete the receipt later.

## 7. Authorization, security, and lifecycle

The temporary workflow is not placed on the default branch for dispatch. It has
only this trigger:

```yaml
on:
  push:
    tags:
      - "btube-v2-1-calibration-approved-*"
```

No tag is created by the implementation commit, so implementation publication does
not start a run. After implementation audit and separate run approval, authorization
consists of creating the exact tag

`btube-v2-1-calibration-approved-<40-character audited implementation SHA>`

pointing to that same commit. Before checkout the job requires the tag suffix to
equal `github.sha`; after checkout it independently requires `git rev-parse HEAD`
to equal `github.sha`. Thus the run head is exactly the audited implementation SHA.
This closes carryover G2.

The workflow has only:

```yaml
permissions:
  contents: read
```

Checkout uses `persist-credentials: false`. There is no dispatch, secret, GitHub API
write, issue/PR comment, branch write, release write, observer write, or normative
environment override. Actions are commit-pinned. Python-FLINT is version- and
wheel-SHA-pinned and installed with `--require-hashes --only-binary=:all:`.

The workflow must be deleted before a result-bearing branch is merged to main.
The accepted payload retains the exact workflow bytes and SHA for replay. A removal
gate rejects any result merge diff that still contains the temporary workflow.

## 8. Required controls

The implementation contains fail-closed controls for:

1. production F/F_r file-byte mismatch;
2. path escape or symlink substitution;
3. alternate-module F_r supply;
4. any C-G tuple mismatch;
5. changed `lambda_start`;
6. terminal endpoint not exactly `118/25`;
7. `checker_dps < dps`;
8. duplicate or unordered candidates;
9. floating or noncanonical JSON;
10. forbidden affine/midpoint path;
11. missing attempted candidate/cell record;
12. non-deterministic recommendation;
13. any `CERTIFIED_*` output or production verdict field;
14. payload mutation after manifest creation;
15. archive mutation after receipt creation;
16. noncanonical or inconsistent receipt;
17. stale resume/cache/output input;
18. write-capable or credential-persisting workflow;
19. run tag/head mismatch;
20. executable workflow surviving the result merge.

Positive controls include precision equality and a valid
`CALIBRATION_INCOMPLETE` artifact with no recommendation.

## 9. Whole-source self-scan and static-audit gate

Every Python file recursively under `b_tube_v2_1/` is self-scanned. The scanner
tokenizes source so comments and string literals do not create false positives, and
constructs its forbidden spellings by adjacent string fragments so the scanner does
not detect its own guard vocabulary. This restores the full `.py` self-scan and
closes carryover G3.

This implementation commit authorizes static audit only. It does not authorize
creation of the approval tag, a calibration run, a production configuration, or a
production B-TUBE run.
