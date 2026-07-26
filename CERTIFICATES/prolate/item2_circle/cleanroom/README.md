# B-KERNEL clean-room audit package

This directory records the new implementation and its audit harness. It is
not a recovery of the historical `prolate_general_r_arb_kernels.py`.

- package: `item2_bkernel_cleanroom_filled.zip`
- package SHA-256: `a7d46705fbdf7b1702a8040ad81d4f13fc9a1cc89d25ccbf53bc1dcc832b40fd`
- implementation SHA-256: `77e7a93c594ba66ac7d98df29ec3c03107b0c63962a5aa60f8503559082c10ac`
- historical unrecovered hash, comparison only: `ef065381abd802239f5fb107c3e87f64a12259deccbf98d6909bcd975da7157d`

The formula is derived from the manuscript's fixed-domain expression for
`E_lambda(r)`. The package contains the all-224-leaf item0d regression fixture,
pure symbolic audits, positive and negative harness controls, and the
integrated Arb audit.

The B-KERNEL CI deliberately does not run the old `[5,6]` circle-tube pilot.
That interval is not the established noncentral branch range; branch-range
repair belongs to B-SEED/B-TUBE after B-KERNEL is accepted.
