# Contract 45 / Piece 3 — Audit Package (CHAT AUDIT target)

Status: SUBMITTED FOR INDEPENDENT CHAT AUDIT.  D-P2 overall: NOT_CERTIFIED.
Author of certificate: Code.  Audit: chat (independent).  Nothing in this package changes any frozen contract or budget.

## 1. Identifiers (pinned)

| item | value |
|---|---|
| repository / branch | `cotaxxxx/basepoint-geometry` / `claude/d-ob-p2-resumable-i8dgpn` |
| certificate file | `tools/d_ob_p2/ftq_cert/north_far_piece3_cert.py` |
| certificate commit | `9cb723c0b424297f3ce572109daf312fbe42b675` (parent `7ba339a8c54278dd0165020f394fdb583ca7e0da`) |
| SHA-256 of file | `308e626e0f864222c6e1176ac4d3a69333186c59aaa100a1d7965c727581fada` |
| git blob | `3beb1e7b0597f9072211a25cf7fb09fc4a323d4a` |
| dependencies | Python 3, sympy only (no python-flint, no floating point in any assertion) |
| inherited, already audited | chain (S0)-(S3): `north_far_piece1_cert.py` (99c9b62, PASS); `north_far_piece2_cert.py` (7ba339a8, PASS); contracts 44/46: `n3_identities_cert.py` (79588e2, PASS) |

Reproduction:
```
git fetch origin claude/d-ob-p2-resumable-i8dgpn && git checkout 9cb723c0b424297f3ce572109daf312fbe42b675
sha256sum tools/d_ob_p2/ftq_cert/north_far_piece3_cert.py      # expect 308e626e0f864222c6e1176ac4d3a69333186c59aaa100a1d7965c727581fada
python3 tools/d_ob_p2/ftq_cert/north_far_piece3_cert.py        # expect ALL CERTIFICATES PASS, exit 0
```

## 2. Statement proved

On the box L in [4/25, 8649/40000], m in [112/113, 1], rho^2 = 1 - m^2, the piece-3 contribution of the audited chain satisfies

    U_3 := 2 pi int_(1/4)^(1/2) F(s)/(w(s) D_0(s)^5) ds  <=  U_3^cert  <  2907/10000,

with U_3^cert the exact rational printed in the log below (the comparison U_3^cert < 2907/10000 is exact; 2906/10000 does NOT hold).

## 3. Proof chain (every step one-sided; direction and validity stated in the file docstring)

- (P3.1) bracket <= B(s): sum-of-squares form (3/16)(a^2 - 4k/3)^2 + k^2/6 with a^2 - 4k/3 = (2ms - 3s^2 - rho^2)/3 >= 0 [Bernstein];
  a^2 = 1 - (m-s)^2 <= 1 - (112/113 - s)^2, k <= r^2 + (112/113) s, (m - (1-L)s)^2 <= (1 - (1 - L_hi) s)^2; and B - bracket >= 0
  certified directly by 3-variable Bernstein on (L, m, s).
- (P3.2) D_0 with L s^2 kept: X = a - rho >= s(c - s)/T(s), Y = sqrt(L) s >= (2/5) s, Cauchy-Schwarz (kappa = 1/4):
  D_0 >= (X + Y/4)/sqrt(17/16); T >= 805/1000 [Bernstein] gives 1/D_0^5 <= (17/16)^(5/2) T^5/(s^5 (c~ - s)^5), c~ = c + t0/10;
  (17/16)^(5/2) <= 11637/10000 by squaring; T >= a + rho re-certified for t = sqrt(s) in [1/2, 7072/10000].
- (P3.3) w^2 >= Wq(s) = (112/113 - s)^2 + (4/25)(2 (112/113) s - s^2) (L a^2 term kept).
- (P3.4) W = Wq^(-1/2) (c~ - s)^(-5) convex (product of positive increasing convex functions; convexity of Wq^(-1/2) by
  (3/4) Wq'^2 - (1/2) Wq Wq'' >= 0 [Bernstein]); chord bound with rational endpoint upper bounds (checked by squaring).
- (P3.5) M(s) = B T^5 ell / s^5 >= 0 (checked), a Laurent polynomial in sqrt(s) (powers -15..19, 34 terms).
- (P3.6) exact interval integration: (1/4)^q exact; (1/2)^q via sqrt(2) in [14142/10000, 14143/10000]; ln 2 in
  [6931/10000, 6932/10000] certified by exact Taylor partial sums of exp with a geometric tail bound; each signed term takes
  the end of its interval that increases the sum.

Bernstein internal bisection (in `bern_min`) is a polynomial-inequality certification device; it is NOT an integration piece
split.  The integration region of piece 3 is the single piece I_3 = [1/4, 1/2] (piece cap: 8 total, 3 used on north far).

## 4. Execution log (verbatim, this commit)

exit code: 0;  checks: 23 PASS, 0 FAIL

```
(box) 1 - (112/113)^2 == (15/113)^2: PASS 
(P3.1.i) 3a^4/16 - k a^2/2 + k^2/2 == (3/16)(a^2 - 4k/3)^2 + k^2/6;  a^2 - 4k/3 == (2ms - 3s^2 - rho^2)/3: PASS 
(P3.1.i) a^2 == 1 - (m-s)^2,  k == 1 - m(m-s): PASS 
(P3.1.ii) 2ms - 3s^2 - rho^2 >= 0 on m in [112/113,1], s in [1/4,1/2]: PASS Bernstein lower bound = 11417/51076
(P3.1.iii) m - (1-L)s > 0 on the box: PASS 
(P3.1.iii) (m-s)^2 >= (c'-s)^2 (a^2 <= A) and m(m-s) >= c'(c'-s) (k <= K) on the box: PASS 
(P3.1) B(s) - bracket(L,m,s) >= 0 on the box x [1/4,1/2] (direct 3-variable Bernstein): PASS lower bound = 17275726451232087/170553487573729280000
(P3.2) [1/2, sqrt(1/2)] inside [1/2, 7072/10000]: PASS 
(P3.2) P(t) >= 0 on t-box: PASS lower bound = 53797/160000
(P3.2) P(t)^2 - t^2 A(t^2) >= 0 on t-box  (=> a + rho <= sqrt(A) + r <= T(s)): PASS lower bound = 123382641721/326886400000000
(P3.2) a >= rho (a^2 - rho^2 == s(2m-s)), c - s > 0, L s^2 >= (4/25) s^2: PASS 
(P3.2) T(s) >= t0 = 805/1000 on [1/4,1/2]: PASS lower bound of t(T - t0) = 1861/18080000
(P3.2) kappa5 >= (17/16)^{5/2}  (kappa5^2 >= (17/16)^5)  [Cauchy-Schwarz, kappa = 1/4: 1 + kappa^2 = 17/16]: PASS c~ = 466193/226000 (~2.06280)
(P3.3) 2c's - s^2 >= 0 and L a^2 >= (4/25)(2c's - s^2) on the box; Wq > 0 on [1/4,1/2]: PASS 
(P3.3) w^2 - Wq == (m-s)^2 - (c'-s)^2 + L a^2 - (4/25)(2c's - s^2)  [identity, both differences >= 0]: PASS 
(P3.4) Wq' == (42/25)(s - c') < 0 on [1/4,1/2]: PASS 
(P3.4) (3/4)Wq'^2 - (1/2)Wq Wq'' >= 0 on [1/4,1/2]  (=> Wq^{-1/2} convex); c~ > 1/2: PASS lower bound = 3326169/15961250
(P3.4) W_a >= W(alpha), W_b >= W(beta)  (q^2 Wq >= 1), both > 0: PASS W_a = 749616419735913568000000000/11542309577382698481659731693 (~0.06495), W_b = 982888759130044352000000000/5496173554442888951236949193 (~0.17883)
(P3.5) M >= 0 on [1/4,1/2]: A > 0 (so B >= 0), T - r = P(t)/t >= 0, ell > 0: PASS 
(P3.5) M(t) expanded as finite Laurent polynomial in t with rational coefficients: PASS powers -15..19, 34 terms
(P3.6) sqrt(2) in [14142/10000, 14143/10000]: PASS 
(P3.6) ln 2 in [6931/10000, 6932/10000]  (exp(ln_hi) >= 2 >= exp(ln_lo), exact Taylor bounds): PASS 
(P3.6) all intervals consistent (lo <= hi): PASS 
int_(1/4)^(1/2) M(s) ds <= 2454912741374152347587860264880938825101515818985468154700402233908289485728758204986600325033064231/83957906828399468573157959161310946468527560282220857980727769194953162508861440000000000000000000000  (~0.029240)
U_3 <= 2 pi * 2 lambda^2 pi * kappa5 * int M = 11184830395887516884997397740684310261983841324395510445098657318311791634218280986497654727483468975923331/38476781094197287318413206125179913738850079066861410784284144131619013869568000000000000000000000000000000  (~0.29069)   [valid for all parameters in the box]
ALL CERTIFICATES PASS
```

## 5. Far-band total (exact rational comparisons; rounded values are NOT used as bounds)

| quantity | exact comparison | budget-ledger notation |
|---|---|---|
| U_1 (99c9b62) | < 802/10000 | U_1 < 0.0802 |
| U_2 (7ba339a8) | < 1772/10000 | U_2 < 0.1772 |
| U_3 (this) | < 2907/10000, not < 2906/10000 | U_3 < 0.2907 |
| U_1 + U_2 + U_3 (exact sum of the three certified fractions) | < 5481/10000, not < 5480/10000 | U_north,far < 0.5481 |

Against frozen / pending budgets (no budget changed here):
- 22'' v1.1 official budget 104/625 = 0.1664: EXCEEDED by the far band alone; failing inequality 5481/10000 < 104/625 (difference -0.3817).
- 22'' v1.2 design target S''_lb = 635530452759/817216000000 ~ 0.77768 (DRAFT / NOT FROZEN): S''_lb - 5481/10000 = 187614363159/817216000000 ~ 0.22958 would remain for the near band.

## 6. Open items and audit notes

1. Method (A) is intrinsically unable to meet 104/625: the chain value itself (diagnostic, NOT_EVIDENCE) is ~0.36 at worst
   parameters, above 104/625; tightening the piece majorants cannot recover the v1.1 budget.  Only adoption of 22'' v1.2 makes the
   far-band route viable; that decision belongs to the research team.
2. Piece-3 majorant loss vs chain value is ~1.30x (diagnostic): tangent bound T(s) (~4%), decoupling rho <= r from m >= 112/113,
   separate lambda^2 upper / L lower bounds.
3. Contract 43 (near band, OPEN): the D_0 lower bound degenerates as s -> rho; a local lemma handling the anisotropic vanishing
   N = O(D^2) near coincidence (N/D^2 ~ sqrt(rho/2) at s ~ rho) is required and not yet drafted.
4. Candidate propositions for Astra (decision: research team): (i) structure of a rho-uniform near-band majorant for [-K_H]_+;
   (ii) final proof-structure check for 22'' v1.2 adoption.
