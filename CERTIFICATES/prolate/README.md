# Prolate global-classification certificates

長球（prolate spheroid）の大域分類に用いる機械可読証明書を保存する。

## Item 0 — equatorial positivity

目的は

\[
F(r,\lambda)=\partial_r E_\lambda(r,0)>0
\]

を、境界侵入値より下のパラメータ範囲で証明することである。

| Stage | Region | Certified quantity | Status |
|---|---|---|---|
| 0c | `0 < r <= 9/20` | `F_r > 0`, hence `F > 0` from `F(0,lambda)=0` | CERTIFIED |
| 0d | `9/20 <= r <= 3/4` | `F > 0` directly | CERTIFIED |
| 0a / Stage 1 | `r = 1` | boundary sign and unique boundary-entry parameter | CERTIFIED |
| 0b | `3/4 <= r < 1` | planned proof by `F_r < 0` plus analytic corner cap | IN PROGRESS |

The common parameter range for 0c and 0d is

\[
1\le\lambda\le\frac{206539}{100000}=2.06539.
\]

Stages 0c and 0d overlap at `r=9/20`; together they certify `F>0` on
`0 < r <= 3/4` throughout this lambda range.

## Directories

- `item0c_center/` — completion record for the center band.
- `item0d_interior/` — archived ZIP, certificate, manifest, and independent audit for the middle band.

Binary artifacts are immutable. Any replacement must use a new filename and a new SHA-256 manifest.
