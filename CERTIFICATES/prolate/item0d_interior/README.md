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

- `item0d_certified.zip.parts/` — exact Base64-encoded byte ranges of the immutable delivery ZIP
- `reconstruct_zip.py` — reconstructs the original `item0d_certified.zip` and rejects any size or SHA mismatch
- `certificate_0d_combined.json` — combined theorem statement and provenance
- `MANIFEST.sha256` — SHA-256 snapshot
- `AUDIT.md` — independent structural audit and signature analysis

Reconstruction:

```bash
python3 reconstruct_zip.py
```

Expected output:

- size: `29502` bytes
- ZIP SHA-256: `db1c68e4bbf43fcb49bd5f27de5d45a36b44f1f8e77141477832ce16ae68df2a`

The multipart representation is necessary because the GitHub text-contents connector used for ingestion cannot write binary ZIP data directly. Each Base64 part was checked by Git blob SHA against the locally generated source text.

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
