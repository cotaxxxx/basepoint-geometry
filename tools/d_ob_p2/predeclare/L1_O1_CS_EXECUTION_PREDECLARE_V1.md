# D-OB P2 / D-AN-1 — O1 C-S execution PREDECLARE v1 (ChatGPT / Dig, 2026-10-09)

STATUS: DRAFT FOR CHAT AUDIT ONLY. No symbolic script authored or run. No C-S execution authorized.
Parent O1 PREDECLARE v1.1 FREEZE: commit 1e0c772545357bca6da3f3aa23f203b3206f40f5, blob 660ffd4e780fd84c2e4f413ad547e4df09e52359, SHA-256 e75334374c8959df95c02a5d7cd28589df5ab843db774fa8eb547a806a166b38.
The O1 paper derivation (I-1–I-12, C-P) is separately authorized. This file authorizes no numerical evaluation, diagnostics, sampling, interval computation, or script execution.

## 1. Pinned environment and paths
- Execution environment: the authorized ChatGPT container runtime (not GitHub Actions or a user's machine); versions must be verified there before any C-S run. If the versions differ, STOP with ENV FAIL.
- Interpreter: CPython 3.13.5.
- SymPy: 1.14.0.
- These versions were inspected from the available environment metadata; no SymPy algebra was executed.
- Script (to be created ONLY after CHAT audit and Judge execution authorization): `tools/d_ob_p2/o1_cert/o1_interior_symbolic_check.py`.
- Log (same authorization): `tools/d_ob_p2/o1_cert/o1_interior_symbolic_check.stdout.txt`.
- Inputs pinned by O1 v1.1: P1 in cotaxxxx/bg-oblate-spheroid commit 69e104602e939817b6f4d71df3f6bd63cbc729e0, FTq in cotaxxxx/bg-oblate-spheroid commit 20c5c59bd74f940fe0b1e05892bd2169e09d4fde, O1 FREEZE in cotaxxxx/basepoint-geometry as above.
- L0 parameter source: cotaxxxx/bg-oblate-spheroid commit 3cabe008 (short pin as supplied by Judge; full SHA not independently established).
- No dependencies other than Python standard library and SymPy 1.14.0. All arithmetic symbolic/exact; `Float`, `evalf`, numerical substitution, sampling and plotting forbidden.

## 2. Symbol and algebra protocol
- S-1-G geometry from P1 line 9, fixed verbatim in mathematical notation: x(mu,phi)=(a cos(phi),a sin(phi),lambda*mu), nu=(lambda*a*cos(phi),lambda*a*sin(phi),mu)/w, b=a*cos(phi), a=sqrt(1-mu**2).
- Stage G: independent symbols `lambda,mu,rho,z,b`; `a2=1-mu**2`, `w2=lambda**2*a2+mu**2`, `h=lambda*(1-rho*b)-z*mu`, `D2=a2+rho**2+(lambda*mu-z)**2-2*rho*b`. Derivatives in rho and b hold all other Stage-G symbols fixed.
- Stage L source definitions: rho_b(tau)=(1-tau**2)/(1+tau**2), m(tau)=2*tau/(1+tau**2) (L0 commit 3cabe008).
- Stage L: substitute `rho=r*rho_b(tau)`, `z=lambda*r*m(tau)` AFTER Stage-G expressions have been formed. Keep `r,tau,lambda,mu,b` symbolic, `r` free. Use the pinned L1 parameter definitions; NEVER set `r=1` in Stage L.
- The paper I-9 expressions are independent comparison targets for S-2. SymPy independently differentiates `h/(w*sqrt(D2))` using A2; FTq (5.1), including any `m -> z/lambda` substitution, is NOT a comparison target.
- Rationalize expressions in `D` using `D**2=D2`; `w**2=w2`. Compare exact polynomial numerators after clearing denominators, never by approximate evaluation.
- For S-3, transcribe the three A2,A1,A0 coefficients from pinned FTq (5.2) verbatim, and compare each coefficient. Do not redefine target coefficients from the computed result.
- For S-4 and S-5, transcribe the two forms of c from pinned FTq (7.2) verbatim, independently of the generated numerator.

## 3. Fixed check order
S-1-G: h and D2 obtained directly from geometry equal A2 forms.
S-1-L: the same two residuals after Stage L.
S-2-G: paper I-9 gamma_rho and gamma_b each equal independent SymPy derivatives from A2.
S-2-L: the same two residuals after Stage L.
S-3-G: N_J is quadratic in b, contains no uncancelled odd D powers, and its three coefficients equal verbatim FTq (5.2).
S-3-L: same identities after Stage L.
S-4-G: `h_plus**2*D_minus**2-h_minus**2*D_plus**2-4*rho*b*(h0*c+lambda**2*rho**2*b**2)` vanishes.
S-4-L: same identity after Stage L.
S-5-G: the two FTq (7.2) forms of c agree.
S-5-L: same identity after Stage L.
D-1: substitute rho=rho_b, z=lambda*m; reduce modulo rho_b**2+m**2-1; check boundary h and D2.
D-2: under the same boundary-only reduction check N_J = -lambda**2*(m-mu)*Q with Q transcribed verbatim from FTq (6.2).
D-3: under the same boundary-only reduction check the general gamma-pair difference (7.1) and both c forms (7.2) reduce to pinned boundary formulas.
Boundary substitutions are prohibited before D-1. Stage G/L and D checks are mandatory and run in the listed order.

## 4. Fixed stdout on complete success
```text
O1-CS ENV Python=3.13.5 SymPy=1.14.0
O1-CS S-1-G PASS
O1-CS S-1-L PASS
O1-CS S-2-G PASS
O1-CS S-2-L PASS
O1-CS S-3-G PASS
O1-CS S-3-L PASS
O1-CS S-4-G PASS
O1-CS S-4-L PASS
O1-CS S-5-G PASS
O1-CS S-5-L PASS
O1-CS D-1 PASS
O1-CS D-2 PASS
O1-CS D-3 PASS
O1-CS COMPLETE PASS
```

## 5. Fail-closed STOP rule
On ANY nonzero exact residual, print `O1-CS <CHECK-ID> FAIL residual=<verbatim SymPy srepr of the first nonzero residual>` and exit nonzero immediately. No repair, fallback, alternate interpretation, new algebraic target, or rerun in the same execution. A mismatch in Python/SymPy versions, source pin, or required parameter definitions prints `O1-CS ENV FAIL <reason>` and exits nonzero before any check. Any missing or undefined source target is `O1-CS <CHECK-ID> BLOCKED <reason>` with nonzero exit, not a PASS. No additional stdout on a successful run.

## 6. Submission gate
CHAT audits this draft, then Judge decides FREEZE and explicit execution permission. Only after both may the script be authored and executed, with exact stdout retained, script/log pinned by commit/blob/file SHA-256. Paper analytic obligations cannot be discharged by C-S. O1 does not prove positivity, L1 remains open, D-P2 NOT_CERTIFIED.
