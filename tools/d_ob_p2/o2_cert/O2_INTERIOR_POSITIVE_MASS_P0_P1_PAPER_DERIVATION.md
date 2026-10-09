# D-OB P2 / D-AN-1 / L1 / O2 — Stage P0–P1 Paper Derivation

**STATUS: PAPER DERIVATION P0–P1 / SUBMITTED FOR CHAT AUDIT**
**Date:** 2026-10-10. **Authority:** Judge ruling A (2026-10-10), paper derivation P0–P1 only.
**Controlling frozen O2 predeclare v1:** commit `7fb2bfb8cad75469b04454f452f68e7b4cd4bb05`; blob `80fc22f9aac4abaef39f621d732bb45a23f9ccb6`; SHA-256 `1488d6c125322c5877176835ab4ab30404709fe872ff413b0efdfa488755b279`.
**O1 paper source:** `tools/d_ob_p2/o1_cert/O1_INTERIOR_PAPER_DERIVATION_DRAFT.md`, commit `805cba881d0c374a6301f3c068ffba9a3688c991`, blob `008cf68b2ea070708e1f836c48cc3c32490095c7`, SHA-256 `6a90ee13c8281395bd9c2ef820cd26841924e8d436806030a0adea4765dc18fa`.
**Evidence qualification:** O1 CLOSED conditionally on P1 note (NOT_BINDING, external audit pending). This paper neither changes O1 nor certifies O2. No code, numerical search, machine algebra, sampling, or checker was executed.

## P0. Interior geometry and positive denominators

Set `lambda in [2/5,93/200]`, `tau in [7/8,1]`, `r_rad in [7/8,1)`, `mu in I_+=[-1,1/2]`, `phi in [0,pi]`. Put
`rho_b=(1-tau^2)/(1+tau^2)`, `m=2tau/(1+tau^2)`,
`rho=r_rad*rho_b`, `z=lambda*r_rad*m`, `delta=1-r_rad^2`,
`a=sqrt(1-mu^2)`, `b=a*cos(phi)`, `w=sqrt(lambda^2*a^2+mu^2)`,
`x=(a*cos(phi),a*sin(phi),lambda*mu)`,
`p_xi=(xi,0,z)`, `xi in [-rho,rho]`.
Here `rho_b^2+m^2=1` is a parameterization identity; at the **interior** point `rho^2+(z/lambda)^2=r_rad^2<1`. Never substitute `rho^2=1-m^2` or `z=lambda*m`.

O1 geometry at the general interior point `p_xi` is
`h_xi=lambda*(1-xi*b)-z*mu`,
`D_xi^2=a^2+xi^2+(lambda*mu-z)^2-2*xi*b`,
`gamma_xi=h_xi/(w*D_xi)`.
For `xi=+rho` or `-rho`, denote these by `h_+,D_+` and `h_-,D_-` with the appropriate sign of `xi` and paired azimuth `b`. For the b-pair at fixed rho, O1 also defines `h_+=h0-lambda*rho*b`, `h_-=h0+lambda*rho*b`, `D_+^2=D0-2rho*b`, `D_-^2=D0+2rho*b`, `h0=lambda-z*mu`, `D0=a^2+rho^2+(lambda*mu-z)^2`.

**P0-D: distance.** For every `xi in [-rho,rho]`, vertical-coordinate separation yields
`D_xi >= lambda*|mu-r_rad*m|`. Indeed `z=lambda*r_rad*m` does not vary with xi. As `m>=112/113`, `r_rad*m>=(7/8)*(112/113)=98/113`, and `mu<=1/2`, one has
`D_xi >= (2/5)*(98/113-1/2)=83/565=:d_plus>0`.
This holds jointly for the entire xi segment, both b-paired points, the axis, and all delta>0. No boundary specialization is used.

**P0-w:** Since `w^2=lambda^2+(1-lambda^2)*mu^2` and `lambda<=93/200<1`, `w>=lambda>=2/5>0`.

**P0-h:** The bound `rho<=rho_b<=15/113` follows because `rho_b(tau)` decreases for positive tau and `rho_b(7/8)=15/113`. Since `|b|<=a<=1` and `z=lambda*r_rad*m<=lambda`, for `mu<=1/2` the inequality `z*mu<=lambda/2` holds (for negative mu it is automatic). Thus for every `|xi|<=rho`,
`h_xi=lambda*(1-xi*b)-z*mu >= lambda*(1-15/113-1/2)=lambda*83/226>=83/565>0`.
This proves the lower bound on h directly on I_+ without using a boundary support-plane identity. Both `h_+,h_-` inherit it.

**P0-pair denominator:** Since `D_+,D_->=d_plus` and `h_+,h_->=d_plus`,
`h_+*D_-+h_-*D_+ >=2*d_plus^2>0`.
Moreover `w*D_+*D_-*(h_+*D_-+h_-*D_+) >=(2/5)*d_plus^2*(2*d_plus^2)=(4/5)*d_plus^4>0`.
These are paper inequalities for possible later rationalization; **they do not authorize switching to the R·J or P density**. All inequalities remain valid at rho=0 as algebraic endpoint bounds, even though a rho-divided formula must not be evaluated there.

## P1. Direct K-form density and cancellation-preserving xi average

O1 supplies only the **K form**:
`G_p(mu)=int_0^pi K_H(mu,phi)dphi`,
`K_H=[calF_xi'(rho)-calF_xi'(-rho)]/(2rho)` for rho>0, where
`calF_xi=h_xi*g(gamma_xi)`, `g(t)=arccos(t)^2`.
This identity is conditional on O1/P1 as pinned above. No interior R·J formula and no interior R-G identity is assumed.

**P1-K1 (FTC form).** By the fundamental theorem of calculus along the full interior segment,
`K_H(mu,phi)=(1/2)*int_{-1}^{1} calF_xixi(t*rho;mu,phi) dt`.
This is an exact equality for rho>0: substitute `xi=t*rho` in the O1 secant. It keeps the two-sided xi cancellation and contains **no division by rho**. Define the right side also at rho=0, where it equals `calF_xixi(0;mu,phi)`. On the fixed I_+ box, `D_xi>=d_plus`, `w>=2/5`, `h_xi>=d_plus`, and P1 Lemmas 3.1–3.2 (conditional) ensure that g and its derivatives are regular at gamma=1. Continuity of `calF_xixi` on the compact enlarged parameter box (allowing r_rad=1 only for the separated I_+ expression) gives the joint rho->0 limit of this representation. The statement is about the K density on I_+, not the full L1 axis positivity claim.

**P1-K2 (explicit differentiated K integrand).** Let `v=xi-b`. Holding `lambda,mu,phi,z` fixed, the O1 geometry gives
`h_xi'=-lambda*b`, `D_xi'=v/D_xi`,
`gamma_xi'=(-lambda*b)/(w*D_xi)-h_xi*v/(w*D_xi^3)`,
`gamma_xi''=(1/w)*[2*lambda*b*v/D_xi^3-h_xi/D_xi^3+3*h_xi*v^2/D_xi^5]`.
Consequently, by two ordinary chain/product rules,
`calF_xixi=2*(-lambda*b)*g'(gamma_xi)*gamma_xi' + h_xi*[g''(gamma_xi)*(gamma_xi')^2+g'(gamma_xi)*gamma_xi'']`.
Every term is expressed using **interior** `h_xi,D_xi,w,g` only. The apparently singular factor `g''` at gamma=1 is interpreted through the analytic extension of `g` asserted in P1 Lemma 3.2; it is not estimated termwise by a nonuniform gamma-bound. The expression is an exact **paper-derived candidate identity**, pending any separately authorized exact checker.

**P1-K3 (integrated direct-K expression).** Combining K1–K2, the positive-interval contribution can be written
`M_plus(p):=int_{-1}^{1/2}G_p(mu)dmu=(1/2)*int_{-1}^{1/2}int_0^pi int_{-1}^1 calF_xixi(t*rho;mu,phi)dt dphi dmu`.
Interchange of these integrations is justified on I_+ by continuity and the uniform positive denominator bounds, subject to the conditional P1 smoothness claims. This is an integration-ready **identity**, not a minorant and not a positivity certificate. The xi-average is kept intact rather than replacing it with a global absolute-value majorant. No `1/rho` appears. It has a well-defined axis limit at rho=0 by continuity.

**Declared sign strategy:** Stage P1 adopts the **integrated positive-mass strategy**, not an unproved pointwise `G_p(mu)>=0` claim. A later separately authorized P2 must construct and certify a rational minorant for the integrated expression `M_plus` on the full box. If a future pointwise sign lemma is used, its scope is restricted to `mu in I_+` and requires separate proof. Nothing in P1-K1–K3 implies `M_plus>0`.

**Remaining analytic obstacle:** K2 contains the nonlinear `g'(gamma)` and `g''(gamma)` factors. The present paper does **not** establish an exact rational polynomial minorant for their xi/phi/mu integral, nor an analogue of the boundary P-form decomposition. Replacing K by P or R·J to evade this obstacle would trigger the frozen v1 switch gate (new interior (4.2)/(4.4), interior R-G without (6.1), and rho->0 uniformity, with new audited predeclare). This is an explicit STOP boundary for the authorized P0–P1 scope, not a claim of failure of Form II.

## Later exact-check candidates — list only, NOT executed

1. Reconfirm the parameterization identities and general-point h,D²,w², without boundary substitution.
2. Check the exact rational inequalities `m>=112/113`, `rho_b<=15/113`, `D_xi>=83/565`, `h_xi>=83/565`, `w>=2/5`, and the b-pair denominator bound on I_+.
3. Verify P1-K2 by exact differentiation and identity residual; separately verify K1 by FTC.
4. Check endpoint/axis continuity and any required analytic extension of g at gamma=1 against the P1 paper assumptions.
5. Check any **future** integrated minorant only after P2 authorization and an execution predeclare; no minorant is claimed here.

**Out of scope:** P2 positivity, numerical exploration, SymPy, certificate execution, P/R·J switch, E1/E2/G2 materials, boundary-only FT_q (6.1), O3, O6, L1 closure.

**Ledger:** O2 predeclare v1 FROZEN; P0–P1 PAPER DERIVATION SUBMITTED FOR CHAT AUDIT; O2 P2 and machine execution NOT AUTHORIZED; Form II TARGET; ROUTE UNDETERMINED; L1 PAUSED; D-P2 NOT_CERTIFIED.
