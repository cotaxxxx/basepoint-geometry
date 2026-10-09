# 22'' v1.2 numeric condition — closure record (Code draft for CHAT AUDIT, 2026-10-09)

Status: DRAFT CLOSURE RECORD / SUBMITTED FOR CHAT AUDIT.  This record does not modify the canonical contract text
(`cotaxxxx/bg-oblate-spheroid`, `design/d-ob-p2`, `analysis/D_OB_P2_D_AN1_FT_Q_CONTRACT_20_DOUBLE_PRIME_TO_23_DOUBLE_PRIME_V1_2.md`,
commit d445b302bd879b5dc5211c7ba310d5aef036f31e, blob 6340cb3e1dcb7387e4044013fb9f77a9cd21788a,
SHA-256 3ef26f903d15c11449e583a917723ffcbaff7217b76f3fc65284e02b820b4640).  If the Judge wants it in canonical, the user places this file
byte-identically as a separate new file (proposed path `analysis/D_OB_P2_D_AN1_FT_Q_CONTRACT_22_DOUBLE_PRIME_V1_2_CLOSURE_RECORD.md`).

## 1. Condition (22'' v1.2, canonical text)
U_north + U_near < S''_lb,  S''_lb = 635530452759/817216000000,  on the box lambda in [2/5, 93/200], m in [112/113, 1], rho^2 = 1 - m^2 (P units,
2 pi lambda H = integral_{-1}^{1} G(mu) dmu).

## 2. Evidence (all CHAT AUDIT PASS)
| term | bound | evidence | state |
|---|---|---|---|
| S''_lb (south, [-1, 1/2]) | integral_{-1}^{1/2} G >= 635530452759/817216000000 | derivation source: south paper proof 05668a47216e243450211f0cf438702dc6d1527c (SHA-256 f320acb9...); input certificate kernel_extension_cert.py 1ac44469f33fb74b1b4cbfcd62621dce3f6fa12e (SHA-256 3c4b0d45...) | CHAT AUDIT PASS; canonical import PENDING |
| U_north (far, s in [rho, 1/2]) | < 5481/10000 (exact sum of three certified fractions) | contract 45 pieces 99c9b62a..., 7ba339a8..., 9cb723c0... | CHAT AUDIT PASS |
| U_near (band, mu in [m - rho, 1]) | <= 3887073979116207/17284813033600000 | contract 43: frozen predeclare 97d85f5914e23f593fc2a41baeb883645f5ce994, frozen certificate 7f71fb433dfabf2e99dc52d9fa775b0ae50dee30, authorized run bd512f535ef2d32531c0e48e5229a8ddca0d3fa1 (38 PASS / exit 0); Astra independent report and exact script (ff1e1a53..., script SHA-256 6187c2b0...); H-43-1(i) closure c4d49d81884a9dfebb82839236c84cee8add1ceb, H-43-1(ii) CLOSED | Contract 43 CERTIFIED (chat ruling 2026-10-09) |
| coverage / overlap | [-1,1/2] U [m-1/2, m-rho] U [m-rho, 1] = [-1,1]; overlap width 1 - m <= 1/113 is safe-side slack | v1.2 §22'' text; collation report A (77c3c77f, items A1-A6) | CHAT AUDIT PASS |

## 3. Exact closure
S''_lb - 5481/10000 - 3887073979116207/17284813033600000 = 1622585478106563/345696260672000000 =: Delta > 0  (computed by the frozen certificate,
check (C6), and printed in stdout.txt of run bd512f53, SHA-256 b377ee8f...).  Hence U_north + U_near < S''_lb and, for every parameter in the box
with rho > 0,  2 pi lambda H >= S''_lb - U_north - U_near > Delta.

## 4. Status after this record
22'' v1.2 numeric condition: CLOSED (on CHAT AUDIT of this record).  c_FT: UNSET (separate predeclare).  Boundary Pair Lemma: OPEN.
D-P2: NOT_CERTIFIED.
