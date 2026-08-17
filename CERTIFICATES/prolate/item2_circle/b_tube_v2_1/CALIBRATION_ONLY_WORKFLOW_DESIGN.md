# B-TUBE v2.1 — calibration-only workflow design

Status: **B-LOCAL DEPENDENCY PINNED; BINDING IMPLEMENTATION PRESENT; STATIC RE-AUDIT REQUIRED; RUN NOT YET AUTHORIZED**

Design commit: `4a1b12a2a1e4f89712c33bc554646b44190f6f5b`

Pinned B-LOCAL source head: `a8997d11850dbd5b63e3064560a1c311e5c9c267`

Audited harness source: `CERTIFICATES/prolate/item2_circle/b_tube_v2_1/`

## 1. Purpose and non-purpose

This stage measures candidate numerical operating parameters for a later production
B-TUBE run. It may inspect Krawczyk margins, interval inflation, JOIN widths,
subdivision counts, and evaluation budgets. It does not certify a branch, alter
theorem endpoints, discharge a paper-level dependency, or emit a production
B-TUBE verdict.

The only permitted terminal states are:

- `CALIBRATION_COMPLETE`
- `CALIBRATION_INCOMPLETE`
- `CALIBRATION_FAILED`

Every `CERTIFIED_*` value and every production verdict field is forbidden in
calibration output.

The value `2/1` came from `SELFTEST_ONLY` material and remains forbidden as a
binding left endpoint. The binding left endpoint is now the exact B-LOCAL result

`lambda_start = 3307749/1600000 = 2.067343125`.

The historical exact diagnostic endpoint `21/10` remains in the configuration
only so that explicit synthetic/local diagnostic controls can still exercise the
nonbinding path. It is not used by the binding workflow.

## 2. B-LOCAL/B-ENTRY dependency pin

The active configuration is a binding profile:

- `mode: "BINDING"`;
- `binding_to_final_lambda_start: true`;
- `blocal_dependency.status: "PINNED"`.

The complete B-LOCAL tuple is frozen to the successful B-LOCAL v2.2 run #5:

- source head
  `a8997d11850dbd5b63e3064560a1c311e5c9c267`;
- artifact ZIP SHA-256
  `7c1748148470426648dd03a483a076b043ed70558258358834671451267e64dc`;
- certificate SHA-256
  `b8d27c01d63f3ea53bfeb165f7e140d739fab6b3949115e0aac3fd64b2d05cb6`;
- B-LOCAL config SHA-256
  `dab371fa62ed10a00029cd31b0002e503952277ef072fb8f5d7fd5222965d469`;
- exact `lambda_start = 3307749/1600000`;
- machine conclusion schema
  `btube-blocal-machine-conclusion-v2-finite-routes`;
- selected candidate index `0`;
- `u_max = 2^-8`;
- J_START root interval `[2047/2048,1]`;
- machine status `BLOCAL_COMPLETE`;
- all finite-route / L3 boundary / authorized-consumer flags equal `true`.

The configuration validator compares the complete dependency object against this
frozen tuple. A changed status string, a changed hash, a changed endpoint, a
changed candidate, a changed root interval, or a changed machine flag is rejected.
The workflow independently checks the canonical configuration SHA-256 and the same
dependency tuple before dependency installation or any result-bearing step.

The B-LOCAL artifact is an external frozen dependency. This calibration source
does not copy, rewrite, or regenerate the B-LOCAL certificate.

## 3. Other frozen dependencies

The production F/F_r kernel remains the single file

`CERTIFICATES/prolate/item2_circle/vendor/prolate_circle_F_cleanroom.py`

with SHA-256

`77e7a93c594ba66ac7d98df29ec3c03107b0c63962a5aa60f8503559082c10ac`.

Both `F_arb` and `dFdr_arb` must come from that same pinned file. Symlinks, path
escape, alternate derivative supply, and post-import byte changes are rejected.

The C-G terminal identity tuple remains unchanged:

- artifact ZIP SHA-256
  `c0f624a955657f906c09c45b016a92f7bcdfa70d26c2508efeb3f06dd7d27381`;
- source head `1e0f671c91798b9c044c04c7a4224a21e1e67830`;
- config SHA-256
  `bb6a3655d335240549cbe1f6eec2a9e68e00219eb9c1a2be65796e2e342a0d17`;
- reference-kernel SHA equal to the production-kernel SHA;
- paper/interface lemma `F_G_FIXED_SLICE_IDENTITY_V1`;
- exact terminal parameter `118/25`;
- exact root bracket `(1/64,11/256)`.

Calibration may record endpoint diagnostics but may not emit the production MATCH
conclusion.

## 4. Immutable configuration

`config.calibration.json` is canonical JSON with no trailing newline, duplicate
keys, floating JSON numbers, BOM, or CR/LF. The binding version has byte length
`2196` and SHA-256

`2a3c7211a244876276182ab316f49881842b90c07dfd755f7f9235dc424c9f75`.

Its normative fields include the exact B-LOCAL dependency, exact
`lambda_end = 118/25`, ordered unique dyadic parameter widths and tube radii,
predictor refresh cadence, Arb working/checker precision with
`checker_dps >= dps`, fixed cell/subdivision/evaluation budgets, source/design
provenance, C-G dependency pins, the affine rule, schema, design version, and
chain domain.

Candidate order is normative: parameter-width order, then tube-radius order.
Environment variables cannot replace normative configuration values.

Calibration is fresh-only. Resume files, checkpoints, caches, prior output, and
pre-existing output directories are rejected.

## 5. Execution modes and evaluation protocol

The ordinary command

`python calibration.py run --out <path>`

is the binding path. It calls exact B-LOCAL tuple validation before loading the
production kernel and starts at `3307749/1600000`.

The explicit local command

`python calibration.py run --diagnostic --out <path>`

is accepted only when supplied a deliberately unpinned
`mode: "DIAGNOSTIC_ONLY"` configuration with all B-LOCAL tuple values null and
`binding_to_final_lambda_start: false`. The repository's active binding
configuration therefore cannot silently enter diagnostic mode.

The GitHub workflow never passes `--diagnostic`.

For each candidate pair the runner covers the entire exact interval
`[3307749/1600000,118/25]` in deterministic exact-rational cells.

Predictor endpoint values are exact dyadics. The only affine rule is
`exact_endpoint_convex_hull_v1`; midpoint substitution for correlated interval
expressions is forbidden.

Each cell record contains exact parameter endpoints, predictor endpoints and tube
interval, residual and derivative enclosures, exact preconditioner, reconstructed
Krawczyk image, strict margins or precise failure reason, derivative-sign
diagnostic, and evaluation/subdivision counts.

Each shared endpoint receives a separate exact JOIN intersection record and width.
A candidate passes only when all cells satisfy strict Krawczyk inclusion, the
derivative enclosure is strictly negative, all JOINs have positive width, and all
fixed budgets are respected. The first passing candidate in configured order is
the only permitted calibration recommendation.

A recommendation remains engineering evidence only. It cannot rewrite a
production B-TUBE configuration.

## 6. Independent verification and byte closure

The workflow invokes `calibration.py verify` in fresh Python processes after the
runner and after delivery. Both the standard verifier and the independent full
record-layout verifier:

1. parse configuration and result files through canonical-byte routines;
2. reject duplicate keys, floats, BOM, CR, final JSONL LF, and noncanonical bytes;
3. verify the chain over canonical record-object bytes, excluding JSONL linefeeds;
4. reconstruct candidate order independently from raw configuration;
5. verify candidate completeness and ordered indices;
6. recompute the first passing candidate;
7. require binding recommendation/state/coverage semantics for the active profile;
8. require `machine_conclusion` to equal `{"real_analytic":false}`;
9. reject every `CERTIFIED_*` string and production verdict field;
10. require the exact pinned B-LOCAL tuple for pre-delivery verification.

Delivery is assembled in a new empty directory. It copies canonical results, exact
replay sources, the pinned production kernel, requirement lock, design, and
workflow; hashes payload files in sorted order; builds a deterministic ZIP; hashes
the actual ZIP bytes; writes a canonical receipt; and independently rechecks every
referenced digest.

The platform outer artifact ZIP is transport only. No observer may repair or
complete the receipt later.

## 7. Authorization and lifecycle

The temporary workflow has only this trigger:

```yaml
on:
  push:
    tags:
      - "btube-v2-1-calibration-approved-*"
```

The approval tag must be exactly

`btube-v2-1-calibration-approved-<40-character audited implementation SHA>`

and point to the same commit. The job requires the tag suffix to equal
`github.sha`, requires the checked-out HEAD to equal that SHA, then checks the
canonical binding-config SHA and exact B-LOCAL tuple.

The workflow has only `contents: read`; checkout uses
`persist-credentials: false`; actions are commit-pinned; Python-FLINT is
version- and wheel-SHA-pinned and installed with `--require-hashes
--only-binary=:all:`. There is no dispatch or write-capable token path.

This pinning commit authorizes **static re-audit only**. It does not itself create
an approval tag, run calibration, merge to main, create a production
configuration, or run production B-TUBE. A separate GREEN audit is required
before an approval tag is created.

The temporary workflow must be deleted before a result-bearing branch is merged
to main. The accepted payload retains exact workflow bytes and SHA for replay.

## 8. Required controls

Fail-closed controls cover production-kernel mismatch, path escape, alternate
derivative supply, C-G tuple mismatch, every B-LOCAL tuple member, machine
conclusion tampering, binding-flag demotion, mode mismatch, terminal endpoint
mismatch, `checker_dps < dps`, duplicate/unordered candidates, noncanonical JSON,
forbidden affine paths, missing records, shared-helper candidate reconstruction,
forbidden result vocabulary, stale inputs, workflow authorization mismatch, and
surviving temporary workflow files in a result merge.

Positive controls include exact binding-profile acceptance, exact B-LOCAL tuple
acceptance, precision equality, explicit diagnostic-profile acceptance through a
synthetic unpinned fixture, and independent record-layout fixtures.

## 9. Static-audit gate

Every Python file recursively under `b_tube_v2_1/` is self-scanned. The scanner
tokenizes source so comments and string literals do not create false positives and
constructs forbidden spellings by adjacent string fragments.

The next action after this commit is a byte-level/static audit of the pinning diff.
Only after that audit is GREEN may the approval tag be created.
