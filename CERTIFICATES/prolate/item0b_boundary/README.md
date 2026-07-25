# Item 0b — boundary-band certificate

Status: **CERTIFIED**

## Statement

For every

\[
1\le\lambda\le\frac{206539}{100000},
\qquad
\frac34\le r\le1,
\]

one has

\[
F_r(r,\lambda)<0.
\]

For every `lambda < lambda_partial`, items 0a and Stage 1 give
`F(1,lambda)>0`. Since `F` is strictly decreasing as a function of `r` on
this band,

\[
F(r,\lambda)\ge F(1,\lambda)>0
\qquad (3/4\le r\le1).
\]

Together with items 0c and 0d, this completes item 0:

\[
F(r,\lambda)>0
\qquad
(0<r<1,\ 1<\lambda<\lambda_\partial).
\]

## Certified leaf data

- total leaves: 435
- `Fr_negative_riemann`: 226
- `Fr_negative`: 155
- `Fr_negative_infsup`: 54
- pending queue: 0
- terminal failures: 0
- exact rational atomic coverage: `28 x 101 = 2828` cells
- uncovered cells: 0

The independent audit records 97 multiply covered atomic cells. Every
covering leaf has `negative_certified=true`; the theorem requires complete
coverage, not a disjoint partition.

## Files

- `certificate_0b_combined.json` — compact machine-readable theorem record.
- `AUDIT.md` — independent hash, leaf, coverage, and syntax audit.
- `SHA256SUMS.txt` — hashes of the delivered ZIP and all seven original files.

The uploaded `item0b_certified.zip` was independently extracted and verified
against SHA-256
`7a07e9c687ed59bec40103daf6b55c348f9c2cac5dcecf61bc7de64655b8d9be`.
The repository stores the compact certificate and audit record; the original
ZIP remains the immutable delivery artifact identified by that hash.

The final certificate uses three leaf labels. The analytic corner-cap method
was part of the certification search and is documented in the certificate,
but the remaining corner terminals were ultimately discharged by the
correlation-preserving inf-sup v5 kernel.
