# Item 0d — middle-band direct positivity certificate

Status: **CERTIFIED**

## Theorem

For every

\[
1\le\lambda\le\frac{206539}{100000},
\qquad
\frac9{20}\le r\le\frac34,
\]

one has

\[
F(r,\lambda)>0.
\]

Every accepted leaf proves the direct strict inequality `F>0`; no induction or monotonicity transfer is used in this stage.

## Certificate structure

- driver `F` leaves: 118
- mixed-runner leaves: 80
- Riemann harvest leaves: 26
- total leaves: 224
- terminal failures: 0
- pending boxes: 0
- exact atomic grid: `25 x 38`
- uncovered cells: 0
- multiply-covered cells: 0

## Archived files

- `item0d_certified.zip` — immutable delivery archive
- `certificate_0d_combined.json` — combined theorem statement and provenance
- `MANIFEST.sha256` — SHA-256 snapshot
- `AUDIT.md` — independent structural audit and signature analysis

## Consequence with item 0c

Item 0c proves `F>0` on `0<r<=9/20`; item 0d proves `F>0` on `9/20<=r<=3/4`. Hence

\[
F(r,\lambda)>0
\quad\text{for}\quad
0<r\le\frac34,
\quad
1\le\lambda\le2.06539.
\]

The remaining part of item 0 is item 0b on `3/4 <= r < 1`.
