# B-KERNEL clean-room audit

The historical `prolate_general_r_arb_kernels.py` was not recovered. No file
in this directory is represented as that historical source. Its recorded
SHA-256 remains, for comparison only:

`ef065381abd802239f5fb107c3e87f64a12259deccbf98d6909bcd975da7157d`

The current kernel is a new implementation derived from the manuscript's
fixed-domain integral for `E_lambda(r)`. The user-supplied intake package was
verified before normalization:

- intake package SHA-256:
  `a7d46705fbdf7b1702a8040ad81d4f13fc9a1cc89d25ccbf53bc1dcc832b40fd`
- clean-room implementation SHA-256:
  `77e7a93c594ba66ac7d98df29ec3c03107b0c63962a5aa60f8503559082c10ac`

The binary intake package is not used as repository transport. The integrated
auditor rebuilds the exact 224-leaf fixture directly from the certified item0d
ZIP; the result must have SHA-256 `800b12fd…`.

CI first performs provenance, symbolic, independent midpoint, checker-control,
and interface checks. It then runs the rigorous regression as 16 disjoint
14-leaf shards and the interval difference-quotient audit as four 6-point
shards. The final aggregation requires the exact global leaf index set
`{0,...,223}`, 24 successful difference-quotient points, and zero failures.

The old `[5,6]` circle-tube pilot is outside this audit. Its branch range must
be repaired in the subsequent B-SEED/B-TUBE work.
