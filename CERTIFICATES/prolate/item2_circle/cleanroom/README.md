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

The binary intake package is not used as a repository transport. Instead,
`bkernel_cleanroom_audit.py` rebuilds the exact 224-leaf fixture directly from
`item0d_certified.zip`. The generated fixture must have SHA-256
`800b12fd6850f1b3dde0d22d3afa13918dbb46687f98ae99f5c8097083ed47eb`.
The auditor's repository-byte SHA is captured by CI before execution and is
frozen into the ledger after the first complete audit.

CI obligations:

1. source ZIP and combined-certificate hashes match;
2. fixture rebuild gives exactly 224 leaves and the fixed fixture hash;
3. pure SymPy identities are exactly zero;
4. independent 224-leaf Gauss--Legendre midpoint reference passes;
5. positive and negative checker controls pass;
6. rigorous Arb regression passes all 224 leaves;
7. the symbolic and interval difference-quotient audit passes;
8. the four-function public B-KERNEL interface is available.

The old `[5,6]` circle-tube pilot is deliberately outside this audit. Its
branch range must be repaired in the subsequent B-SEED/B-TUBE work.
