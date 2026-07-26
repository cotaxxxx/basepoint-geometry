# vendor/ — B-KERNEL status

The historical modules `prolate_general_r_arb_kernels.py` and
`riemann_rescue.py` were not recovered. In particular, no file is represented
as the historical kernel unless its SHA-256 equals
`ef065381abd802239f5fb107c3e87f64a12259deccbf98d6909bcd975da7157d`.

The current public interface is wired to a NEW clean-room implementation:

- `prolate_circle_F_cleanroom.py`
- `prolate_circle_kernels.py`
- `SHA256SUMS_VENDOR.txt`

The formula is derived from the manuscript's fixed-domain integral for
`E_lambda(r)`. Equivalence to the historical item0d behavior is accepted only
if the all-224-leaf Arb regression and the symbolic/difference-quotient audit
both pass. The immutable audit package and its provenance are stored in
`../cleanroom/`.

The four public functions are:

- `F_arb(r, lam)`
- `dFdr_arb(r, lam)`
- `F_float(r, lam)`
- `dFdr_float(r, lam)`

The old `[5,6]` B-TUBE pilot remains disabled as mathematical content; its
branch interval must be repaired separately after B-KERNEL acceptance.
