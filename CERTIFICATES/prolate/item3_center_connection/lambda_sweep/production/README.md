# Item 3 lambda sweep — production implementation candidate

Status: `STATIC_AUDIT_CANDIDATE`; no production run, tag, PR, or certification claim is authorized.

## Candidate configuration requiring user approval

The first pipeline-validation range remains

```text
lambda_target = 483303/102400 = 118/25 - 2^-12
interval      = [483303/102400, 118/25]
```

The budget, precision, and target values are candidates only. The complete canonical config SHA-256 is intentionally not materialized in this commit.

## R-1 production source

The production layer now contains:

- `arb_adapter.py` — pinned clean-room kernel adapter for `G=F/r` and `G_r=F_r/r-F/r^2`, with exact dyadic endpoint extraction;
- `run_item3_sweep.py` — preflight, runner, fresh checker, chain serialization, evidence, and manifest entrypoint;
- `verify_pilot_artifact.py` — independent pilot artifact verifier;
- `materialize_config.py` — closed-schema candidate config materializer.

These files are candidates for chat-side `AUDITED_SOURCE` review. Their presence does not inherit the Phase 3 source audit.

## Independent pilot source rederivation

`pilot_source_sha256 = 9da05b2c44119c9937c19a2184ea9722de7876442235896f1f0e0dbc076f2ecc` is accepted only after all of the following match:

1. canonical artifact ZIP SHA-256 `c0f624a955657f906c09c45b016a92f7bcdfa70d26c2508efeb3f06dd7d27381`;
2. exact 15-member ZIP set with no duplicate or unsafe path;
3. every hash in the artifact-internal `SHA256SUMS.txt`;
4. direct SHA-256 of `c_g_tube_pilot.py` member bytes;
5. byte equality between the ZIP members and the extracted directory;
6. receipt, dependency snapshot, decisions, and materialized config relation.

A receipt-supplied value alone cannot pass this gate.

## R-2 deterministic runtime candidate

`requirements-python-flint.txt` fixes the single Linux x86-64 stable-ABI wheel with `--require-hashes`. The production workflow uses pinned `actions/setup-python`, installs with `--no-deps --only-binary=:all: --require-hashes`, downloads the fixed pilot artifact by ID, and verifies its ZIP digest before execution.

Because the workflow bytes changed after the prior Phase 4 PASS, the new workflow is `PHASE4_REAUDIT_REQUIRED`. The prior Phase 4 report is historical evidence for the old bytes only.

## Target range policy

`TARGET_RANGE_POLICY.json` and `.md` distinguish:

- the short downward pipeline-validation interval permitted by v8.1;
- the unresolved final mathematical coverage objective;
- the historical upward phrase `lambda_match -> a_c`;
- the certified `a_c` bracket strictly above the anchor.

Any upward or bidirectional sweep requires a design-contract revision and a new Phase 1 freeze. Endpoint order may not be silently reinterpreted.

## Candidate materialization

From a clean checkout, after obtaining the canonical pilot artifact:

```bash
cd CERTIFICATES/prolate/item3_center_connection/lambda_sweep/production
python3 audit_production_source.py
python3 test_production_source.py
python3 materialize_config.py \
  --pilot-artifact-zip /path/item3-cgtube-pilot-certified-30334858060.zip \
  --pilot-artifact-dir /path/extracted \
  --write
```

Materialization still produces candidate filenames. Promotion to `config.item3-sweep-run.json`, approval of its complete SHA-256, and tag creation remain separate user decisions.
