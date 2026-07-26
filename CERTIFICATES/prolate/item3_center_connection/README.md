# Prolate item 3 — center connection prerequisites

This directory stages the three clean-room prerequisites for C-G-TUBE and
C-MATCH:

- `vendor/`: endpoint-regular F_rr extension based on the accepted item-2
  clean-room kernel;
- `audit/`: symbolic and high-precision audit of the F_rr formulas;
- `calibration/`: fail-closed centered-form calibration harness.

The calibration establishes only a justified initial radial cell width. It does
not certify C-G-TUBE itself. The production tube must include the Actions-
produced schema-v2 calibration JSON in its certificate dependency chain.

The retained legacy JSON preserves the original numerical run, but its
`sign_certified` field used binary-float comparisons and is not a proof node.
