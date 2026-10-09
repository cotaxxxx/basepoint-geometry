# D-OB P2 / D-AN-1 — QM–L3–L1 reverse feasibility report (Code, independent of Astra; 2026-10-09)

Status: READ-ONLY INVESTIGATION / EXACT RATIONAL ARITHMETIC ONLY / SUBMITTED FOR CHAT AUDIT.  No H, E or kernel evaluation, no sampling, no
interval computation of H, no producer/checker, no change to canonical files, m0 unchanged (SET), L1 PAUSED, D-P2 NOT_CERTIFIED.
Exact script: `tools/d_ob_p2/feasibility/qm_l3_reverse_feasibility_exact.py` (SHA-256 c3500bff009780ac1c556f4c8a141b674a5f3cb182b50b5d71bd70bd50d996d2); output
`qm_l3_reverse_feasibility_exact.stdout.txt` (SHA-256 14700f398070395c6b6f4c98a2375337ef20acf5c6a349c96801de44b6085bb7); exit 0.  The script uses only the QM formula (1.1), the frozen L3 condition and m0,
with pi and ln enclosed by exact rational inequalities (3 < pi < 22/7; exact Taylor brackets of e^y).

## §1. Executive summary
- **Current m0 connects, but only with a vanishing layer.**  The frozen condition omega_E(delta0) < m0 holds for delta0 = 1/10^10 and fails for
  delta0 = 1/(5·10^9); the admissible delta0 is about 10^-10 (at most 15/8 larger with the exact 1 - r conversion).  L3 then owns delta in [0, ~10^-10]
  and L1 must cover essentially all of Sigma, delta in [~10^-10, 15/64].
- **Required lower bounds are out of reach.**  For delta = 10^-1, 10^-2, 10^-3 the required lower bound omega_E(delta) exceeds 3300, which is above
  the rigorous ceiling of any lower bound on H, (25/2) C2 < 3175/7 ~ 453.6 (QM (3.1)).  For these widths no improvement of FT_q can ever connect.
  For 10^-4 to 10^-6 the required improvement factors are about 2.7·10^5, 3.3·10^4 and 4.0·10^3.
- **Diagnosis: the obstacle is the QM modulus (second item of §14), not the FT_q bound (first item).**  omega_E(d) >= 50 C2 d > 1813 d, and the
  far-field term 25 C3 d (1 + 2 ln(1/d)) with C3 > 8900 dominates; any lower bound of size O(1) on H gives delta0 of order 10^-4 at best.
- **L1 obstacle (third item) is independent:** both known counterexample points (pointwise-pair at delta = 31/256, G1 at delta = 255/16384) lie in the
  L1 layer for every admissible delta0; they refute the pointwise and fixed-mu routes only, not G2, E_rho > 0 or H > 0.
- **Recommendation: ROUTE C** (redesign the L3–L1 connection; the QM modulus as used by the frozen L3 text cannot produce a useful layer).

## §2. Source and audit ledger (pins read back by Code in the read-only canonical clone `cotaxxxx/bg-oblate-spheroid`)
| source | commit | blob | SHA-256 | file header status | ledger status |
|---|---|---|---|---|---|
| analysis/D_OB_P2_D_AN1_QM_DRAFT.md | 7f9119f7cbe7d5dab95e42300bb9563c974e23f5 | 7e99ce86914df0ef3fc1eda21885fcd9a2ca722f | e8588c1b677e10aceac22e79784e41111cffe2c2cffce1636804485dafb09edc | PAPER-PROOF DRAFT / AWAITING CHAT AUDIT | AUDIT PASS |
| analysis/D_OB_P2_D_AN1_QM1_DRAFT.md (input of QM) | 930b44bb6ce2ab9d7298556e8f5ff1768386857c | (not needed) | dd001338… (as cited by QM) | AWAITING CHAT AUDIT | cited as CHAT AUDIT PASS by QM |
| analysis/D_OB_P2_D_AN1_L3_MRA_DRAFT.md | 5fc0341216f4e0f6722a96f3d8edb2e1c9fbc47c | 256d0baa3db89b021d207235797b08b1b6fdf6de | b13e07d63b3f3035b7b983cc39acbae893d4a184dfa030eaf73bb9f243a0d842 | AWAITING CHAT AUDIT; parent freeze v1.1 (6de8a178) | PASS |
| analysis/D_OB_P2_D_AN1_PREDECLARE_V1_2.md | e9c8b1caa3ad502a3d01dafe354b61108787eed2 | 931c0cdb0e3f9d81430ae7e9029b3704bf099505 | f27a568b2996eb29e3756612dac3cb40ac2796b19dd81729742082a62abcf217 | v1.2 DRAFT / NOT FROZEN | FROZEN |
| analysis/D_OB_P2_D_AN1_FT_Q_DRAFT.md | 20c5c59bd74f940fe0b1e05892bd2169e09d4fde | 1c449fb4fb791f750668c44605156454cfff42af | 46443f0e981f360e57fb70d99754b0e480042d246e22d36732b00b96102a9cd1 | REDUCTION DRAFT | AUDIT PASS (reduction) |
| P1 design note (cited by QM as commit 6c6282a8) | 6c6282a8acbf467bcbe6a7e32236e1d32a91f400 and 69e104602e939817b6f4d71df3f6bd63cbc729e0 | f81e120e… | 2c304ee6… (identical content at both commits) | NOT_BINDING | NOT_BINDING |
All short pins in the instruction match the full values above.  **Label discrepancies (not resolved here):** QM, QM-1 and L3-MRA headers read
"AWAITING CHAT AUDIT" while the ledger records PASS; the predeclare v1.2 header reads "NOT FROZEN" while the ledger records FROZEN.  The computation
below does not depend on the labels, only on the QM formula; its conclusions inherit whatever audit state the ledger assigns to QM.

## §3. Exact QM modulus
QM (1.1), for 0 < d <= 1/2:  omega_E(d) = 50 C2 d + 25 C3 d [1 + 2 ln(1/d)],  C2 = 9 pi + 8,  C3 = 8788 + 39 pi;  omega_E(d) = omega_E(1/2) for d >= 1/2;
omega_E(0) = 0; nondecreasing (QM §9); uniform in lambda in [2/5, 93/200]; valid on all of closure(K_lambda), hence includes r = 1.
Object: E_rhorho; the H modulus follows from P1 Lemma 6.1(iii) (H = int_0^1 E_rhorho(t rho, z) dt) and |(t rho, z) - (t rho', z')| <= |p - p'| (QM §11,
L3-MRA §5) — this transfer uses the NOT_BINDING Lemma 6.1.  Distance: Euclidean distance in the meridional (rho, z) plane.
Distance conversion (L3-MRA §6, predeclare v1.2 L3 text): p_in = r p_b, |p_b| = sqrt(rho_b^2 + lambda^2 m^2) <= 1, so |p_in - p_b| = (1 - r)|p_b| <= 1 - r
= delta/(1 + r) <= delta, with delta = 1 - r^2 = 1 - rho^2 - z^2/lambda^2 at p_in.  The frozen text uses f(delta) = delta; the sharper f(delta) = 1 - r
<= (8/15) delta (r >= 7/8 on Sigma) changes delta0 by at most 15/8.

## §4. Current m0 -> delta0
m0 = 540861826035521/336806928254720000 ~ 0.00160585 (SET, unchanged).
- omega_E(1/10^10) <= 733827712952132341/700000000000000000000 ~ 0.00104833 < m0  (upper bound: pi < 22/7, ln(10^10) <= 10 · 2302585092997/10^12).
- omega_E(1/(5·10^9)) >= 20336022688821109/10^19 ~ 0.0020336 > m0  (lower bound: pi > 3, certified lower bound of ln).
Hence the admissible range under the frozen condition is 0 < delta0 < delta_max with 10^-10 <= delta_max < 2·10^-10 (largest certified admissible
rational on the grid a·10^-k: 1/10^10).  The strict inequality is preserved by the strict rational comparison.  With f(delta) = 1 - r: at most ~3.75·10^-10.

## §5. Reverse calculation (m_required(delta) = omega_E(delta); exact rational enclosures in the stdout file)
| delta | omega_E(delta) in | R(delta) = omega_E/m0 in | connects with current m0? | attainable by any lower bound <= (25/2)C2 < 3175/7? |
|---|---|---|---|---|
| 10^-1 | [124960, 125045] | [7.78·10^7, 7.79·10^7] | NO | NO |
| 10^-2 | [22748.3, 22763.1] | [1.417·10^7, 1.418·10^7] | NO | NO |
| 10^-3 | [3300.05, 3302.18] | [2.055·10^6, 2.057·10^6] | NO | NO |
| 10^-4 | [432.53, 432.81] | [2.693·10^5, 2.696·10^5] | NO | not excluded (needs m0 > 432) |
| 10^-5 | [53.505, 53.540] | [3.332·10^4, 3.334·10^4] | NO | not excluded |
| 10^-6 | [6.3757, 6.3798] | [3970, 3973] | NO | not excluded |
All six candidates are inside the QM domain (d <= 1/2).  The ceiling (25/2) C2 is rigorous (QM (3.1): |E_rhorho| <= (25/2) C2, hence |H| <= (25/2) C2)
and uses no diagnostic.  This table is a necessary condition on the L3 side only; it says nothing about L1.

## §6. L1 feasibility
- L1 target instance (predeclare v1.2 L1 positioning note): Sigma ∩ {delta in [delta0, 15/64]}.  With delta0 ~ 10^-10 this is all of Sigma except a
  sliver of width ~10^-10 at r = 1; it contains the pole/corner layer associated with the old (7,7,0) failure.
- Pointwise-pair counterexample (lambda = 93/200, r = 15/16, tau = 7/8, mu = 5/8, b = 3/4): delta = 31/256 ~ 0.121 — inside the L1 layer.
- G1 counterexample (lambda = 93/200, r = 127/128, tau = 7/8, mu = 15/17): delta = 255/16384 ~ 0.0156 — inside the L1 layer.
- Refuted: uniform pointwise-pair positivity; fixed-mu phi-average positivity (G1).  NOT refuted: G2 (mu-integrated positivity), E_rho > 0, H > 0.
  The counterexamples were not recomputed here (no kernel evaluation); their coordinates are taken from the instruction and only delta is computed.
- Obstacle: L1 currently has no analytic tool beyond G1/pointwise routes; the L3 layer is too thin to move the hard region out of L1.

## §7. Alternative connection analysis (structural only; Task F)
- Why the uniform modulus is lossy: QM bounds |E_rhorho(p) - E_rhorho(p')| for ARBITRARY p, p' in closure(K) with worst-case constants
  (C2 = 9 pi + 8 from Lemma 3.4, C3 = 8788 + 39 pi from QM-1, 1/lambda <= 5/2, 1/w <= 5/2, area 4 pi).  L3 only needs the RADIAL one-sided difference
  H(p_b) - H(r p_b) along a fixed ray, and only the lower side.
- Local lower bound: the FT_q proof gives 2 pi lambda H(p_b) >= S''_lb - U_north - U_near pointwise in (lambda, tau); the margin Delta is uniform, so the
  existing proof yields no larger local bound without re-deriving U_north, U_near pointwise (not done here).
- Local modulus: a one-sided radial estimate of the form H(r p_b) >= H(p_b) - Omega_rad(1 - r) could use the paired-kernel structure (the same N3/R-G
  representation that proved Contract 43) instead of QM-1's global third-derivative majorant; whether such an Omega_rad has constants O(1) is open.
- Finite cover / extremes: the face is compact in (lambda, tau) and the obstacle is uniform (C3 term), so a finite cover does not help unless the
  modulus itself is localized; the extreme tau = 1 and lambda = 93/200 carry the largest constants (1/lambda).
- Risk: any route that again bounds a 1/D-singular kernel by its absolute value near the boundary reproduces the old D-P2 near-column overestimation.
- Unproved conditions: (U1) a radial one-sided modulus with O(1) constants; (U2) a G2-type analytic lemma on Sigma ∩ {delta >= delta0} for a
  delta0 of order 10^-2 or larger.

## §8. Final recommendation: ROUTE C — redesign the L3–L1 connection
Reasons: (i) at the candidate widths 10^-1–10^-3 the required lower bound exceeds the rigorous ceiling (25/2) C2, so ROUTE B (FT_q version-up) cannot
succeed there; (ii) at 10^-4–10^-6 the required factor is 4·10^3–2.7·10^5, far beyond any realistic improvement of a bound whose true size is O(1)
(diagnostics not used for this conclusion; the ceiling argument alone excludes 10^-3 and wider); (iii) ROUTE A leaves L1 with essentially all of
Sigma, including both counterexample regions.  The binding constraint is the QM modulus (item 2 of the instruction's §14), compounded by the L1
structure (item 3); the FT_q bound (item 1) is not the limiting factor.
Remaining mathematical obstacles: U1 and U2 of §7; the audit-label discrepancies of §2.
