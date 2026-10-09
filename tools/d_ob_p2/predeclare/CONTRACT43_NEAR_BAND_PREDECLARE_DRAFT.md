# Contract 43 — North near band — PREDECLARE DRAFT v3.4 (FREEZE candidate, 4 of 4 conditions met; FREEZE ruling pending)

STATUS: DRAFT v3 / SUBMITTED FOR CHAT DESIGN AUDIT / NOT FROZEN / NOT AUTHORIZED FOR CERTIFICATE EXECUTION.
Contract 43 OPEN (countersign in progress).  D-P2 NOT_CERTIFIED.  No diagnostic value appears in this document.
Supersedes v2 (3665f33e, CONDITIONAL PASS).  v3 (459abecf) design audit: CHAT AUDIT PASS (FREEZE condition 1 of 4); v3.1 (06f5bd2b) pin update audit PASS; v3.2 = Astra pins filled
(verified by Code readback in the same repository), Lemma V source pin filled; v3.3 = ledger update per chat ruling (FREEZE condition 2 PASS, condition 3 CLOSED);
v3.4 = canonical 22'' v1.2 pin (condition 4 PASS), (C6) number fixed, Lemma V dependency note; still NOT FROZEN until the explicit chat ruling.  Basis: chat instruction "Predeclare v3 作成・独立証明書準備 (CHAT AUDIT 裁定統合版)".
The formal proof route of Contract 43 is the Astra L43 single-piece chain (5.5) -> (5.7) -> (6.5) -> §7.  The former route (C1)-(C5)
is SHELVED: preserved at commit a6479efe3d173a5952087f9bd3df67da02856fb5, not an alternative route of this contract, not used here.
Any change of the main chain is re-submitted to CHAT AUDIT before implementation.

## 0. Evidence and inputs (pins; PENDING = not received by Code, never guessed)

### 0.1 Code certificates (repository `cotaxxxx/basepoint-geometry`, branch `claude/d-ob-p2-resumable-i8dgpn`)
| item | commit | git blob | SHA-256 | status |
|---|---|---|---|---|
| decomposition of N, pointwise \|N\| <= C D^2: `ftq_cert/n43_decomposition_cert.py` | a3bed35b7b9912081afd7f8819fb2306840ab49e | bde5a8453d1a7beea4dcb0a6fe66385ff32fae90 | 04e7358375c81328a8cd4c628cead339477233f831e21bd8a623ac5395090c6d | CHAT AUDIT PASS (identity class) |
| xi-antiderivatives: `ftq_cert/n43_xi_antiderivative_cert.py` | db8ef8da590329d207aa8d8b18d7198bf1b7e251 | 136ff5ac21d0b27dc0ca3fcffa904472b9a84cfd | a0aad6ae55e257fb0bd2aeb73e97d62f0177401f305fc3f748dbcd687696801a | CHAT AUDIT PASS (identity class; not used by the formal route) |
| contracts 44 (N1-N3) / 46: `ftq_cert/n3_identities_cert.py` | 79588e2e9373c06aa80589a5ab7ffe1611be99d7 | 6a40bede832c462917f16ae024437c6c93f93b98 | a5ba8a338b6d17af33df1b2e3765f155edf7d9ebbecd8e4727a5c5844f0ea66c | PASS (contract 46 not used here) |
| far piece 1: `ftq_cert/north_far_piece1_cert.py` | 99c9b62aae9a6baa14e95b1892cab8c9da28d17a | 7944d8b825e1d2a4eeed8a4a79f4927497f69893 | ad564945f7a11f6d61e892116382e365d45334ab1d29981b5c65d13c7e2d9256 | CHAT AUDIT PASS |
| far piece 2: `ftq_cert/north_far_piece2_cert.py` | 7ba339a8c54278dd0165020f394fdb583ca7e0da | 85b00c4e599ee71016d9a1fe5ff8d227b822a0fa | 8910105df4e9acddb9d273710fe60503edac2cd0ee280840cf0eb1a13552f678 | CHAT AUDIT PASS |
| far piece 3: `ftq_cert/north_far_piece3_cert.py` | 9cb723c0b424297f3ce572109daf312fbe42b675 | 3beb1e7b0597f9072211a25cf7fb09fc4a323d4a | 308e626e0f864222c6e1176ac4d3a69333186c59aaa100a1d7965c727581fada | CHAT AUDIT PASS |
| far total: U_1 + U_2 + U_3 < 5481/10000 (exact sum of the three certified fractions) | — | — | — | derived from the three rows above |
| Code collation of the Astra report: `ftq_cert/astra_l43_collation_check.py` | 53bdb0bcd25027db88ea0b2e063d27a0bbe7b418 | 31d1ff80b1475063264e42b32fc26fe960457868 | c5f4060012fd59da8315860b4d1f32638ff0d55df55454213f86a65950c863ff | chat: collation run, disclosed, separate class; NOT the certificate |
| collation note: `ftq_cert/CONTRACT43_ASTRA_COLLATION_NOTE.md` | ec3282fa3850b2ab51c46321603ce80f47743d62 | fe5897035fcd9d5831ccab563b2d82011bab744c | 07e1c86f258fb6929e90c1a03a9da3ebff8b3025a1dabe8a34d29cde9c7a436e | Code note |

### 0.2 S''_lb: derivation source and input certificate (two distinct evidence rows; not the same evidence)
| row | item | commit | git blob | SHA-256 | evidence class | audit state |
|---|---|---|---|---|---|---|
| 1 | South positive mass paper proof: `ftq_paper_proof/D_OB_P2_D_AN1_FT_Q_SOUTH_POSITIVE_MASS_DRAFT.md` | 05668a47216e243450211f0cf438702dc6d1527c | a66ac60edfc75e70ae198bdea7807e6d5c14b360 | f320acb964cb278d1dd8ef6240fcc88bc9bdf77ae75edd4c77f86ce78da93d3c | DERIVATION SOURCE of S''_lb | CHAT AUDIT done (south paper-proof audit PASS); canonical import NOT done |
| 2 | Kernel extension certificate: `ftq_cert/kernel_extension_cert.py` | 1ac44469f33fb74b1b4cbfcd62621dce3f6fa12e | 3600e0771c73456698035484eb267415111acc4d | 3c4b0d452d87072c2c7a27d432048691c4cce47da871bfad0a50630436146e85 | one INPUT certificate to the derivation of S''_lb | CHAT AUDIT PASS |
S''_lb = 635530452759/817216000000.  Dependency: 22'' v1.2 budget text (row 0.4) -> cites S''_lb -> derived in row 1 -> uses row 2 (and the
certificate-39' south lemma inputs listed in row 1's pin table).  Row 1 and row 2 are never cited as one piece of evidence.

### 0.3 Astra deliverables (five items) — repository `cotaxxxx/basepoint-geometry`, branch `codex/l43-independent-audit-20261009`,
evidence commit ff1e1a5351e2c8ed4bd816e168a08f5b17310e88 (parent 0c1189f9af5eb221abfc518b110e11dda345b4b0); pin-table commit
fcbfdaa6007706a65a168fc8a8f5012036c148e4.  Path prefix `tools/d_ob_p2/ftq_cert/l43_independent_audit_2026_10_09/`.
Code verification (2026-10-09): every row below was read back by Code at commit ff1e1a53 from the same repository; git blob, SHA-256,
byte count and line count all match Astra's `delivery_pins.json`.  This is a pin verification, NOT the CHAT AUDIT of the content.
| # | item (path = prefix + name) | git blob | SHA-256 | lines | state |
|---|---|---|---|---|---|
| 1 | `l43_graph_majorant_exact.py` | 5ab1f7d2ca4343f43c9e520253ec9d904e791397 | 6187c2b0c22d3e1b75ede72da3f470185eb6d93722b25265974ce2e01488cf18 | 216 | pinned; SHA matched to the file; executed by Astra (46 PASS / exit 0, raw log); CHAT AUDIT of script/report consistency PASS (FREEZE condition 2); not executed by Code |
| 2 | `exact_checks.stdout.txt` (raw stdout) | 2dcfc808918f5310b051b6cc8afd8adff334ec4e | 8790c7912043b4c68f5a75fb2b51aa8895b41407d299e1b1db2d964556f9d2d8 | 47 | pinned; with `exact_checks.json` (5dd85c2c…, 2c3a1e42…, 288), `exact_checks.stderr.txt` (empty), `EXECUTION_PROVENANCE.json` (6a13cf4d…, 27764700…, 56) |
| 3 | `source_manifest.json` | 279332bc6801702004395109d0f70d8d7b18bce7 | bb4caa9a0795b4f40242aa136f6f9fd5f746a848b70185b3283948f7b812b58d | 370 | pinned |
| 4 | `D_OB_P2_L43_INDEPENDENT_AUDIT_2026_10_09.md` | 3f95ef5b82980affcc1e453393308acd099544ad | 9fc500bd486d325451ae049806673bdef400987c06f07cc16a4c174130e1b615 | 660 | pinned (updated version; main bound unchanged) |
| 5 | `E43_CORRECTION_NOTICE_2026_10_09.md` | 75068f4ba0a903ba811138592a78f1f182389dd6 | eadeda81783078826f51e7dd9baf8499997ed57c573e2aad4cfd23c2bbffd2d6 | 27 | pinned; self-applied in item 4; no direct external sending |
| + | `H43_ENDPOINT_LEMMA.md` (H-43-1(ii) independent lemma) | 303d1d7c6aa1640590eb83434888c8c19ab44c3a | b1a906edeb21cef356d3d7810dbdc11d30773364620b174a425c441b826d6276 | 198 | pinned; CHAT AUDIT done; H-43-1(ii) CLOSED by chat ruling (FREEZE condition 3) |
| + | `EXACT_CHECK_MAP.md` / `HANDOFF_NOTES.md` / `SHA256SUMS` / `reproduction_manifest.json` | a3215e0c… / 22601a5c… / 76f5a724… / e126fda7… | cdbe0097… / ebe36df9… / 500bb3ba… / 05ccc26e… | 94 / 56 / 12 / 12 | pinned (auxiliary) |
| + | `FULL_PIN_TABLE.md` / `delivery_pins.json` at fcbfdaa6 | fc4f904e65edf2ce6ea00721bdc58f8fbc333e11 / c918fbcbec54d78c4aa9ee148ea6a87f3565649d | 3af88bd4211846b07e7e997120980f4e20e3e63742c7152a78cde1608d9a1919 / c0059a562e3215a9ddcf4b476ffde2831401ef3497c95a538fd599d2c52774a0 | 60 / 261 | pinned (index) |

### 0.4 Budget evidence
| # | item | commit | git blob | SHA-256 | state |
|---|---|---|---|---|---|
| 6 | 22'' v1.2 budget document: `analysis/D_OB_P2_D_AN1_FT_Q_CONTRACT_20_DOUBLE_PRIME_TO_23_DOUBLE_PRIME_V1_2.md` in `cotaxxxx/bg-oblate-spheroid`, branch `design/d-ob-p2` | d445b302bd879b5dc5211c7ba310d5aef036f31e | 6340cb3e1dcb7387e4044013fb9f77a9cd21788a | 3ef26f903d15c11449e583a917723ffcbaff7217b76f3fc65284e02b820b4640 | CHAT AUDIT raw pin PASS (FREEZE condition 4); byte-identical to the audited draft 1b5a4199; 101 lines; Code read-only readback agrees; drafting-gate deviation EXEC-22-V12-GATE-001 recorded by chat, commit not reverted |
| — | 22'' v1.1 (frozen text in force): `analysis/D_OB_P2_D_AN1_FT_Q_CONTRACT_20_DOUBLE_PRIME_TO_23_DOUBLE_PRIME_V1_1.md` in `cotaxxxx/bg-oblate-spheroid` (verified by Code in the read-only canonical clone) | b1a10ea6f0ef127aaf4a40a93070cf270d03e073 | 49e658b0487123249eb81d70bde1ef188ff640d7 | db975daba9d712246ed5e27465437f34450b356f453729a5fb78ec8ceab468cb | FROZEN; official budget 104/625 |

## 1. Region, variables, normalization (frozen sources)
s := m - mu (mu the surface coordinate, m = 2 tau/(1 + tau^2)).  Formal band (contract 24, kappa = 1): |mu - m| <= rho, i.e. s in [-rho, rho].
Physical region = formal band intersected with mu <= 1:  mu in [m - rho, 1],  s in [m - 1, rho]  (m - 1 = -rho^2/(1+m) > -rho; cap side s < 0
included).  |xi| <= rho, phi in [0, pi].  Box: L = lambda^2 in [4/25, 8649/40000] (lambda in [2/5, 93/200]), m in [112/113, 1], rho^2 = 1 - m^2
<= (15/113)^2.  Diagonal singular points (D = 0): (s, phi, xi) = (0, 0, rho) and (0, pi, -rho) only; both on the surface (base-segment endpoints).
(S0) contract 44: [-K_H]_+ <= pi * mean_xi M,  M := [2N^2 - h^2 T]_+/(w D^5) = (w/D)[Phi]_+,  pointwise wherever D > 0, with
mean_xi := (1/(2 rho)) int_{-rho}^{rho} (.) dxi.
U_near := int_{m-rho}^{1} [-G(mu)]_+ dmu <= U_43^{N3} := pi int_{m-rho}^{1} int_0^pi mean_xi M dphi dmu.
Normalization (P units): the same outer factor pi, the same xi-mean 1/(2 rho), the same measure dmu dphi and the same P units as the far band
of contract 45, so U_near,cert + U_far,cert is unit-consistent; see CONTRACT43_ASTRA_COLLATION_NOTE.md §2 (normalization paragraph).
Area change used below: dmu dphi = db dy / mu with u = (b, y) = a (cos phi, sin phi); it is kept throughout (never dropped).
NOT inherited: (S1) D >= D_0 and contract 46 (need a >= rho; false on the cap and degenerate at s -> 0).

## 2. Integration structure
ONE integration piece: the whole physical region of §1.  The only boundaries are the band |mu - m| <= rho, the surface mu <= 1 and the
geometric projection of §3 (A3); no phi split, no xi split, no interior boundary.  Piece count: far 3 + near 1 = 4 of the cap 8.
No boundary, constant or threshold is chosen from a diagnostic.

## 3. Formal chain (Astra (5.5) -> (5.7) -> (6.5) -> §7), to be certified by Code INDEPENDENTLY (`ftq_cert/north_near_l43_cert.py`)
 (A1) identity:  N = lambda [ xi D^2 + (t/2)( D^2 - (1-L) s^2 - delta ) ],  t := b - xi,  delta := rho^2 - xi^2 = mu_xi^2 - m^2 >= 0,
      mu_xi := sqrt(1 - xi^2) in [m, 1],  l := mu_xi - m >= 0,  delta = (mu_xi + m) l,  2 m l <= delta <= 2 l.
 (A2) 2h/lambda = D^2 + (1-L) s^2 + delta >= D^2  =>  0 <= gamma = h/(wD) <= 1;  with n = (lambda b, lambda y, mu)/w, e = (b - xi, y, -lambda s)/D
      (unit vectors), nu = n.e_x, kappa = e.e_x:  N/(w D^2) = nu - gamma kappa = (n - gamma e).(e_x - kappa e),  hence |N| <= w D^2 (Cauchy-Schwarz);
      Gram identity (1 - gamma^2)(1 - kappa^2) - (nu - gamma kappa)^2 = (mu + L s)^2 y^2/(w^2 D^2).
 (A3) projection: u = (b, y), y = a sin phi >= 0, |u| = a <= R_* := sqrt(2 m rho) (a^2 = 1 - mu^2 <= 1 - (m - rho)^2 = 2 m rho);
      Jacobian dmu dphi = db dy / mu (mu dmu = -a da, db dy = a da dphi), mu >= mu_0 := 97/113 on the band;  r := |u - (xi, 0)|,
      D^2 = r^2 + L s^2 >= r^2.  g(u) := sqrt(1 - |u|^2) on the convex disk |u| <= R_*:  |grad g| = |u|/g <= R_*/(m - rho) < k := 3/5,
      because with z := rho/m in [0, 15/112]:  k^2 (1 - z)^2 - 2 z > 0  [Bernstein, degree 2, coefficients 9/25, 249/1400, 681/313600];
      both u and (xi, 0) lie in the disk (|xi| <= rho <= R_*), so |mu_xi - mu| = |s + l| <= k r.
 (A4) Young:  s^2 <= (5/4)(s + l)^2 + 5 l^2 <= (9/20) r^2 + 5 l^2  [SOS: (5/4)(s+l)^2 + 5 l^2 - s^2 = (s/2 + 5 l/2)^2];
      (1 - L) s^2 <= (21/25)[(9/20) r^2 + 5 l^2] = (189/500) r^2 + (21/5) l^2 <= (189/500) r^2 + delta/50,  using (21/5) l^2/delta <= (21/5) l/(2m)
      <= (21/20) z^2 < 1/50  [Bernstein: 1/50 - (21/20) z^2 on z in [0, 15/112], coefficients 1/50, 1/50, 209/179200];
      l^2 <= 4 (s + l)^2 + (4/3) s^2  [SOS: 4(s+l)^2 + (4/3)s^2 - l^2 = (4s + 3l)^2/3],  so  r^2 + L l^2 <= (1 + 4 L k^2) r^2 + (4/3) L s^2 <= (4/3) D^2
      [Bernstein: 1/12 - (9/25) L on L in [4/25, 8649/40000], coefficients 193/7500, 16477/3000000],  i.e.  D^2 >= (3/4)(r^2 + L l^2).
 (A5) zeta := 1 - ((1-L) s^2 + delta)/D^2 in [-c_g delta/D^2, 1],  c_g := 51/50 (from (A4): (1-L)s^2 <= D^2 + delta/50);  N/D^2 = lambda (xi + t zeta/2);
      N^2/D^4 <= L [ xi^2 + |xi t| + t^2/4 + c_g delta |xi t|/D^2 + c_g^2 delta^2 t^2/(4 D^4) ]  (|zeta| <= 1 + v, zeta^2 <= 1 + v^2, v = c_g delta/D^2);
      M <= 2 N^2/(w D^5)  (positive part and -h^2 T dropped, one-sided)  =>  pointwise majorant
      M <= (2L/w) [ (xi^2 + |xi t| + t^2/4)/D + c_g delta |xi t|/D^3 + c_g^2 delta^2 t^2/(4 D^5) ].
 (A6) one-piece integration.  Plane polar coordinates (t, y) = r (cos theta, sin theta), theta in [0, pi]; the projected half-disk is contained in
      {r <= R_e := R_* + rho, y >= 0} (one-sided extension for a nonnegative majorant).  With D >= r for the first three terms and
      D^2 >= (3/4)(r^2 + d_l^2), d_l := lambda l, for the last two:
        curvature terms:  int int (xi^2 + |xi t| + t^2/4)/r  r dr dtheta <= pi xi^2 R_e + |xi| R_e^2 + pi R_e^3/24;  xi-mean (<xi^2> = rho^2/3, <|xi|> = rho/2):
                          A(rho, R_e) := pi rho^2 R_e/3 + rho R_e^2/2 + pi R_e^3/24;
        cross term:       (4/3)^{3/2} c_g delta |xi| * 2 * int_0^{R_e} r^2 (r^2 + d_l^2)^{-3/2} dr,  int = arsinh(R_e/d_l) - R_e/sqrt(R_e^2 + d_l^2) <= log(1 + 2 R_e/d_l),
                          d_l >= delta/5 (l >= delta/2, lambda >= 2/5),  x log(1 + c/x) increasing  =>  <= (4/3)^{3/2} c_g |xi| rho^2 log(1 + 10 R_e/rho^2);
                          xi-mean:  c_g (4/3)^{3/2} rho^3 log(1 + 10 R_e/rho^2);
        depth term:       (4/3)^{5/2} (c_g^2 delta^2/4) (pi/2) int_0^inf r^3 (r^2 + d_l^2)^{-5/2} dr = (4/3)^{5/2} c_g^2 pi delta^2/(12 d_l) <= (4/3)^{5/2} c_g^2 pi delta/(6 lambda)
                          (delta^2/d_l <= 2 delta/lambda);  xi-mean (<delta> = 2 rho^2/3):  pi c_g^2 (4/3)^{5/2} rho^2/(9 lambda);
        prefactor:        pi (outer) * (2L/w) * (1/mu)  with  lambda^p/(mu w) <= lambda_bar^p/(mu_0 W(lambda_bar)),  W(lambda)^2 := mu_0^2 + lambda^2 (1 - mu_0^2),
                          lambda_bar := 93/200, p = 2 (curvature, cross) and p = 1 (depth, after lambda^2/lambda), since w >= W(lambda) for mu >= mu_0 and
                          lambda^p/W(lambda) is increasing in lambda.
      Result (6.5):  U_43^{N3} <= [2 pi lambda_bar^2/(mu_0 W(lambda_bar))] { A(rho, R_e) + c_g (4/3)^{3/2} rho^3 log(1 + 10 R_e/rho^2) } + [2 pi lambda_bar/(mu_0 W(lambda_bar))] pi c_g^2 (4/3)^{5/2} rho^2/9.
 (A7) rational constants and monotonicity.  Define r_0 := 15/113 (rho <= r_0) and H_0 := 13/20 (R_e <= sqrt(2 rho) + rho <= sqrt(2 r_0) + r_0 < H_0, checked as
      2 r_0 < (H_0 - r_0)^2).  Each term is increasing in rho and in R_e, so it is evaluated at (r_0, H_0).  (4/3)^{3/2} < 77/50, (4/3)^{5/2} < 103/50,
      pi < 22/7 (applied to every pi), W(lambda_bar) > 89/100 (W(lambda_bar)^2 - (89/100)^2 = 211911/127690000 > 0).
      Logarithm:  rho^3 log(1 + 10 H_0/rho^2) is increasing in rho (3 log(1+x) >= 2x/(1+x), x = 10 H_0/rho^2), and at rho = r_0:
      1 + 10 H_0/r_0^2 = 166447/450 < sum_{j<=10} 6^j/j! = 67591/175 < e^6,  so  rho^3 log(1 + 10 H_0/rho^2) <= 6 r_0^3.
 (A8) exact rational result (Astra; reproduced by Code's collation 53bdb0bc):
      curvature 20682286967199/152962947200000 + cross 4323211299/110234777000 + depth 3014712459/59751151250 = 3887073979116207/17284813033600000 < 9/40,
      9/40 - sum = 2008953443793/17284813033600000 > 0.   The Code certificate re-derives this value independently and compares exactly.

## 4. Analytic obligations
 H-43-1(i)  interchange of differentiation and the surface integral in the FT_q density derivation: the mathematical argument of Astra §3 is
            confirmed by chat; the formal pin of the source statement and the final evidence closure are separate and remain to be recorded.
 H-43-1(ii) CLOSED (chat ruling 2026-10-09) on the basis of Astra's independent lemma H-43-1(ii)-E (§0.3, `H43_ENDPOINT_LEMMA.md`,
            SHA-256 b1a906ed…), which establishes (a) the one-sided limits at the band boundary, (b) agreement with the Lemma V boundary values,
            (c) the improper-integral representation.  Code did not close (ii) and relies only on the chat ruling for this status.
            Lemma V source pin (named by the Astra lemma, verified by Code in the read-only canonical clone): `cotaxxxx/bg-oblate-spheroid`,
            `analysis/D_OB_P1_DESIGN_NOTE.md`, commit 69e104602e939817b6f4d71df3f6bd63cbc729e0, blob f81e120e44a866d206117d4fab5fac627f26ccd1,
            SHA-256 2c304ee6159f6cf7012ca8fb6068d9e14a4bf8a9d01ceb756395d759145012e9, 164 lines, §5 "Lemma V" (E_beta(p) = (1/(4 pi lambda))
            int_{bd K \ {p}} partial_p^beta F dA/w; (a) absolute convergence, (b) C^2 on int K, (c) continuity of E_beta on closure(K) via Vitali);
            recorded status in the source: CHAT_ANALYTIC_DERIVATION_PASS / EXTERNAL_AUDIT_PENDING / NOT_BINDING (not changed here).
            Dependency note: H-43-1(ii) CLOSED relies on the Lemma V boundary-value DEFINITION of that source and on the independent L^1 convergence
            proved in the Astra lemma; the source's own NOT_BINDING status is not upgraded by this contract, and the closure of (ii) does not
            certify the P1 note.  If the P1 note is later revised, the pin above identifies the version used.
 L43-I (paper): nonnegativity => Tonelli for the order xi, then (phi, mu); {D = 0} is two points (surface-measure zero).

## 5. Budget clause (C6) — FIXED by the canonical 22'' v1.2 pin (row 0.4 #6)
Budget text in force (22'' v1.2, commit d445b302…):  U_north + U_near < S''_lb,  S''_lb = 635530452759/817216000000, with
U_north < 5481/10000 certified (row 0.1).  Hence the near-band comparison value is
  BUDGET_V12 := S''_lb - 5481/10000 = 187614363159/817216000000,
and the certificate asserts  U_43^{N3} < BUDGET_V12  by exact rational comparison and prints the final margin  S''_lb - 5481/10000 - U_43^{N3}
as an exact rational.  Expected (Astra value, Code collation): margin >= 3740763159/817216000000 if U_43^{N3} <= 3887073979116207/17284813033600000.
The superseded v1.1 condition U < 207/5000 (and the derived figure 104/625) is not used; see v1.2 amendment record.

## 6. Governance
 FREEZE requires all four: (1) v3 design audit CHAT AUDIT PASS — MET (459abecf); (2) Astra five deliverables pinned and the exact script
 CHAT AUDITED — MET (pins §0.3, chat ruling 2026-10-09); (3) H-43-1(ii) independent lemma confirmed — MET (CLOSED by chat ruling);
 (4) 22'' v1.2 commit/blob/SHA-256 pinned — MET (d445b302…, CHAT AUDIT raw pin PASS).  All four conditions are met; FREEZE itself only by
 explicit chat ruling naming the frozen commits (this predeclare and the certificate source).  Sequence after this: Judge/user commit of 22'' v1.2
 in the canonical repository -> CHAT AUDIT of its pin -> Code fills §0.4 #6 and (C6) and sets BUDGET_V12 in the certificate -> CHAT AUDIT FREEZE
 ruling -> first execution of the certificate.
 Code certificate `ftq_cert/north_near_l43_cert.py`: source committed (static review by chat done; S-1/S-2/R-S1 applied); syntax check by ast.parse
 permitted and done; EXECUTION and use of its output as evidence only after FREEZE.  Its final line distinguishes machine-checked items, paper
 steps and external obligations, and reads "C6 PENDING; NOT CERTIFIED" while 22'' v1.2 is unpinned.
 Independence: Code and Astra may share decompositions, notes and mathematical reports (both directions opened by chat); certificate CODE is
 never copied in either direction; the Code implementation and the Astra implementation remain separate evidence.
 Method (B) not used.  Diagnostics NOT_EVIDENCE, not cited.

## 7. Compliance table
| item | where |
|---|---|
| 1 identity certs as fixed evidence | §0.1 |
| 2 (C5) route (i) | see a6479efe; outside this contract |
| 3 route (ii) | see a6479efe; outside this contract |
| 4 H-43-1 split, L43-I separate | §4 |
| 5 no O(rho) motivation | none present |
| 6 singular points, non-inheritance | §1 |
| 7 (C6) fixed after v1.2 pin | §5 |
| 8 submission after Astra report | v2, v3 |
| A H-43-1 original meaning | §4 |
| B, C, D (former route) | see a6479efe; outside this contract |
| R-1 former route removed | this document |
| R-2 external evidence pins | §0.3 filled and Code-verified (v3.2); §0.4 #6 canonical v1.2 pin filled (v3.4) |
| R-3 audit states of former versions | §8 |
| R-4 S''_lb source vs input separated | §0.2 |

## 8. Changelog and audit states of former versions
 v0  7cebf22c  chat pre-review (no formal CHAT AUDIT PASS).
 v1  bd890d9164f5d075e5f2743ceceb79d2e71199eb  formal CHAT AUDIT PASS NOT obtained (pre-review only).
 v1.1 a6479efe3d173a5952087f9bd3df67da02856fb5  formal CHAT AUDIT PASS NOT obtained (pre-review corrections A-D applied).  The former route
      (C1)-(C5), appendices A and B are preserved at this commit and are NOT used in this contract.
 v2  3665f33e82ee1cfa5a1ea1166d8cf1d8bcb3958a  CONDITIONAL PASS; superseded by v3.
 v3  459abecf3249ace4789e4a94708218fa0128363e  design audit CHAT AUDIT PASS (FREEZE condition 1/4).
 v3.4 this document: §0.4 #6 canonical v1.2 pin (d445b302, blob 6340cb3e, SHA 3ef26f90), (C6) fixed to BUDGET_V12 = 187614363159/817216000000,
      §4 Lemma V dependency note, §6 FREEZE 4/4 (ruling pending); no mathematical change.
 v3.3 b4f04601175e83f63d36a1c7ecbf43e107d99733 CHAT AUDIT PASS (submission C): ledger update only (condition 2 PASS, condition 3 CLOSED, FREEZE 3/4); no mathematical change.
 v3.2 e4e58f6138521a84c3ef81dd861bf6f5da6d6263: §0.3 Astra pins filled from the evidence commit ff1e1a53 / pin commit fcbfdaa6 and verified by Code readback;
      §4 Lemma V source pin filled and verified; H-43-1(ii) stays OPEN pending CHAT AUDIT of the Astra lemma; 22'' v1.2 still PENDING.
 v3.1 06f5bd2b69ce94a0dbe65dc6ff9a1c7025f0bf10 pin update audit PASS: §0.4 v1.1 row completed with full commit/blob/SHA-256 verified in the canonical clone; §6 certificate status updated.
 v3  content: R-1 former route removed (history kept); R-2 pin tables with PENDING; R-3 this list; R-4 S''_lb rows separated;
     (A7) defines (r_0, H_0) and the logarithm/monotonicity bookkeeping; §1 cites the collation note for the normalization.
