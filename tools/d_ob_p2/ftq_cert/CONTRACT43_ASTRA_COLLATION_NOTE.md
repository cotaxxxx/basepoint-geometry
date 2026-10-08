# Contract 43 — Code collation of the Astra independent report (2026-10-09)

Status: CODE COLLATION / NOT A COUNTERSIGN.  Contract 43 OPEN.  D-P2 NOT_CERTIFIED.  Received from the research team:
`D_OB_P2_L43_INDEPENDENT_AUDIT_2026_10_09.md` (report text only; Astra's script `l43_graph_majorant_exact.py`, SHA-256 6187c2b0...,
its exact output and `source_manifest.json` were NOT received by Code) and the E-43 correction notice (status "未送付").

## 1. What Code re-derived exactly (`astra_l43_collation_check.py`, 26 checks, exit 0)
- identities (5.5) N = lambda[xi D^2 + (t/2)(D^2 - (1-L)s^2 - delta)], (2.0) 2h/lambda = D^2 + (1-L)s^2 + rho^2 - xi^2, (2.4), (2.2') and the
  Gram identity (2.2) (x w^2 D^4), all modulo the ring relations y^2 = a^2 - b^2, rho^2 = 1 - m^2, L = lambda^2;
- the three Bernstein tables of §8 (coefficients reproduced exactly: minima 681/313600, 16477/3000000, 209/179200);
- the integral and angular facts of §6: int_0^inf r^3 (r^2+d^2)^{-5/2} dr = 2/(3d), d/dr[arsinh(r/d) - r/sqrt(r^2+d^2)] = r^2 (r^2+d^2)^{-3/2},
  int_0^pi |cos| = 2, int_0^pi cos^2 = pi/2, <xi^2> = rho^2/3, <|xi|> = rho/2, <delta> = 2 rho^2/3;
- the Young steps (5.3) and (5.4) as exact sum-of-squares identities;
- all constants of §7 (R_e < 13/20, (4/3)^{3/2} < 77/50, (4/3)^{5/2} < 103/50, W(93/200)^2 - (89/100)^2 = 211911/127690000,
  1 + 10 H_0/r_0^2 = 166447/450 < sum_{j<=10} 6^j/j! = 67591/175) and the three component fractions, their sum
  3887073979116207/17284813033600000, 9/40 - sum = 2008953443793/17284813033600000, B_near - 9/40 = 3740763159/817216000000.

## 2. Paper steps checked by reading (no gap found by Code)
- n, e unit vectors, gamma = n.e = h/(wD), kappa = e.e_x, nu = n.e_x; N/(wD^2) = nu - gamma kappa = (n - gamma e).(e_x - kappa e)
  => |N| <= wD^2 (Cauchy-Schwarz).  Consistent with Code's (43.2) (different constant, same conclusion).
- measure: u = (b, y) = a(cos phi, sin phi), d mu d phi = db dy/mu (mu d mu = -a da, db dy = a da d phi), mu >= mu_0 = 97/113 on the band;
  projected band = half-disk |u| <= R_* = sqrt(2 m rho), y >= 0; D >= r = |u - (xi, 0)|; region extension to r <= R_e = R_* + rho one-sided.
- Lipschitz: |grad g| <= R_*/(m - rho) < 3/5 on the (convex) disk, both endpoints in the disk => |s + l| <= k r.
- w >= W(lambda) for mu >= mu_0; lambda^p/(mu w) increasing in lambda, bounded at 93/200; depth term carries lambda^2/lambda = lambda (p = 1).
- cross term: d_l = lambda l >= delta/5, arsinh(x) <= log(1 + 2x), delta log(1 + 10 R_e/delta) increasing, |xi| delta <= |xi| rho^2 pointwise;
  depth term: delta^2/d_l <= 2 delta/lambda.  rho-monotonicity of each component, so the evaluation at rho = 15/113 bounds all rho.
- normalization: U_near = int [-G]_+ d mu <= pi int int <M>_xi d phi d mu with M = [2N^2 - h^2 T]_+/(w D^5) = (w/D)[Phi]_+ (contract 44.4):
  SAME P-unit normalization and the same outer factor pi as Code's far-band chain (S0).  Hence 5481/10000 + 9/40 is unit-consistent.

## 3. Points for chat's collation decision
1. Astra's chain is ONE piece, uses no rational-majorant machinery, and keeps the structure via the depth variable delta = rho^2 - xi^2 and
   the Lipschitz curvature bound.  It is simpler than Code's draft route (C1)-(C5) (predeclare v1.1) and already gives U_43^{N3} < 9/40.
   Code recommends that the Contract 43 predeclare v2 be based on Astra's chain (5.5)->(5.7)->(6.5), with Code producing an INDEPENDENT
   repository certificate of that chain (not an import of Astra's script), executed only after the predeclare PASS.
2. Margin: B_near - 9/40 = 3740763159/817216000000 ~ 0.0046.  The conditional closure S''_lb - 5481/10000 - 9/40 > 0 depends on
   (a) 22'' v1.2 adoption and pin, (b) the far-band certificates (CHAT AUDIT PASS), (c) S''_lb (kernel extension, PASS).
   The margin is small; any later correction of the far bound by more than 0.0046 reopens the near-band budget.
3. Astra §3 (K_H = (1/2 rho) int F_xixi d xi a.e., Fubini, null set) overlaps with H-43-1(i)/(ii) and Code's L43-I/L43-E; chat to rule
   whether §3 discharges H-43-1 or whether the Lemma V boundary-value matching remains a separate obligation.
4. Not verifiable by Code without the files: the 46-check script, its exact output, the source manifest.  Pins needed for the ledger.
5. Astra cites the pre-audit N3 commit 2b53e13 as "原本" and 79588e2 as the revision; the identities are identical, no issue.
6. Astra §9.3 (M unbounded as rho -> 0 at a cap point, rho^2 M -> 5 sqrt2/8) is consistent with Code's remark that |N| <= C D^2 does not
   bound M; §9.2/9.4 (Theta(rho^{3/2}) of the N3 majorant) is consistent with Code's diagnostic scaling (NOT_EVIDENCE) and is proved there.
