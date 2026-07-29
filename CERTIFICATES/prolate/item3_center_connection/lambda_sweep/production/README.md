# Item 3 lambda sweep — production config draft

This package drafts the closed-schema production configuration without authorizing a tag or run.

## Candidate decision requiring user approval

`lambda_target = 483303/102400 = 118/25 - 2^-12`.

The proposed first range is deliberately short. It does not assert numerical sufficiency or any relation to `a_c`.

Other candidate values are fixed in `CONFIG_DECISIONS.candidate.json`:

- `w0 = [1/64, 11/256]`
- `min_lambda_width_exp = 20`
- `delta_overlap_min = 2^-12`
- `window_grid_exp = 16`
- `window_min_width_exp = 12`
- `global_eval_limit = 500000`
- `per_box_eval_limit = 20000`
- `max_lambda_depth = 20`
- `max_r_cells_per_box = 4096`
- `dps = 50`
- `checker_dps = 70`

The budget and precision values are candidates only. No Arb or mathematical calculation was performed.

## Identity assets

The pilot identity receipt and logical dependency snapshot are canonical JSON candidates derived from canonical pilot run `30334858060`. Their mutual hashes and five logical dependency hashes are checked by `audit_config_draft.py`.

## Materialization

From a clean checkout at this branch:

```bash
cd CERTIFICATES/prolate/item3_center_connection/lambda_sweep/production
python3 audit_config_draft.py
python3 materialize_config.py --write
```

The materializer computes the actual design SHA-256 and all source SHA-256 values from checkout bytes, runs the Phase 3 closed-schema validator, and runs the Phase 3 preflight identity gates. It writes a candidate config and its complete SHA-256.

## Mandatory hold

The materialized candidate intentionally binds the Phase 3 audited adapter *protocol* file only. It is not an executable Arb adapter. The Phase 4 workflow also has no pinned Python-Flint installation step, and the required production entrypoint is absent.

Therefore:

```text
run_authorized = false
tag_created = false
workflow_executed = false
```

A production adapter/entrypoint and deterministic Arb runtime pin require a separate audited revision before the candidate config can become a run-authorized final config.
