# Item 3 centered-form calibration

This package calibrates the centered-form bound used to choose the initial
radial cell width for C-G-TUBE.

## Certification rule

All certification decisions remain in Arb arithmetic:

```text
C = upper(abs(G''(I)))
slack = C * rad
sign_certified = (G'(m) has a certified sign) and
                 (slack < lower(abs(G'(m))))
```

Binary `float` values are never used for a verdict.

## Fail-closed resume rules

A resumed report must match the complete metadata tuple:

- `lambda`, `m`;
- `dps`, point/box tolerances, depth, evaluation limit;
- base-kernel and F_rr-extension SHA-256 values.

Legacy reports have no schema version and are rejected. Use `--fresh` for a
new strict report. `--force-recompute` replaces selected normalized radii only.
All rows are recalculated from the stored raw Arb balls before the report is
written and by `--verify-only`.

## Actions sequence

```bash
python3 prolate_item3_centered_calibration.py --fresh --rads 1/256
python3 prolate_item3_centered_calibration.py --rads 1/1024
python3 prolate_item3_centered_calibration.py --rads 1/4096
python3 prolate_item3_centered_calibration.py --verify-only
```

The original result is retained as `item3_centered_calibration_legacy.json` for
numerical provenance only. Its `sign_certified` field was computed through
binary floats and is not a proof node. The Actions-produced schema-v2 JSON is
the intended machine-readable calibration record.
