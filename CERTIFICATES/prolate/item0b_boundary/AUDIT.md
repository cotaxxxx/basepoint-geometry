# Independent audit of item 0b

Audit date: 2026-07-25

## Hashes

- delivery ZIP SHA-256: `7a07e9c687ed59bec40103daf6b55c348f9c2cac5dcecf61bc7de64655b8d9be`
- combined certificate SHA-256: `f7a577cf208ee1db64c4aa1faa27c1d78c58dbf64a34010471b367ffe7a18690`

Both equal the values reported at delivery.

## Package integrity

The uploaded ZIP extracts successfully and contains seven files:

- `certificate_0b_combined.json`
- `ckpt_0b.json`
- `kernels_v5_infsup.py`
- `corner_fr_0b.py`
- `continue_0b.py`
- `runner_0b.py`
- `rescue_v5_0b.py`

All five Python files pass `python -m py_compile`.

## Leaf audit

`ckpt_0b.json` contains 435 records and an empty queue. Every record has
`negative_certified=true`. The labels are exactly:

- `Fr_negative_riemann`: 226
- `Fr_negative`: 155
- `Fr_negative_infsup`: 54

The event log records the final v5 rescues with zero remaining terminals.

## Exact coverage audit

Collecting every exact rational endpoint from the 435 boxes gives:

- 28 atomic `r` intervals
- 101 atomic `lambda` intervals
- 2828 atomic cells

Exact rational midpoint membership gives:

- uncovered cells: 0
- singly covered cells: 2731
- multiply covered cells: 97

The overlaps arise from certified rescue leaves and do not weaken the sign
proof: every covering record certifies the same strict inequality
`F_r<0`. No claim of a disjoint partition is made for item 0b.

## Monotonicity interface

The certificate proves `F_r<0` on the closed boundary band. Therefore, for
`r<=1`, `F(r,lambda)>=F(1,lambda)`. Items 0a and Stage 1 provide the strict
right-anchor sign for `lambda<lambda_partial`; this yields `F>0` throughout
the band and completes the equatorial exclusion when joined to 0c and 0d.

## Reversible ZIP representation

The 34,025-byte uploaded ZIP is split into 6 raw byte ranges.
Each range is Base64-encoded independently. `reconstruct_zip.py` decodes the
parts in offset order and rejects the output unless both conditions hold:

- reconstructed size = `34025`
- reconstructed SHA-256 = `7a07e9c687ed59bec40103daf6b55c348f9c2cac5dcecf61bc7de64655b8d9be`
