# D-OB P2 / D-AN-1 — O1 interior representation: paper derivation (ChatGPT / Dig, 2026-10-09)

STATUS: PAPER DERIVATION, SUBMITTED FOR CHAT AUDIT. C-S NOT EXECUTED. Algebraic coefficient collation S-1–S-5 and D-1–D-3 NOT VERIFIED BY SYMPY. No positivity claim. D-P2 NOT_CERTIFIED.
Controlling O1 PREDECLARE v1.1 FREEZE: 1e0c772545357bca6da3f3aa23f203b3206f40f5 / blob 660ffd4e780fd84c2e4f413ad547e4df09e52359.
Sources: P1 69e104602e939817b6f4d71df3f6bd63cbc729e0; FTq 20c5c59bd74f940fe0b1e05892bd2169e09d4fde (template only). Original P1 external audit remains pending.

## A. Geometry from P1, independently specialized to the meridional interior
Let lambda in [2/5,93/200], x=(a cos phi,a sin phi,lambda mu), a=sqrt(1-mu^2), b=a cos phi, w=sqrt(lambda^2*a^2+mu^2), nu=(lambda a cos phi,lambda a sin phi,mu)/w, p=(rho,0,z).
Then w(x-p).nu = lambda*a^2+lambda*mu^2-lambda*rho*b-z*mu = lambda*(1-rho*b)-z*mu =:h.
By Euclidean expansion D^2=|x-p|^2=a^2+rho^2+(lambda*mu-z)^2-2*rho*b.
Write h0=lambda-z*mu, D0=a^2+rho^2+(lambda*mu-z)^2. Then h=h0-lambda*rho*b, D^2=D0-2*rho*b. The surface measure is dA=w dmu dphi.
For the paper analysis define G(t)=arccos(t)^2, F(x,p)=h G(gamma), gamma=h/(wD), calF_xi(mu,phi)=F(x,(xi,0,z)). All partial derivatives in xi fix z,mu,phi.

## B. I-1–I-8: interior representation, domination and endpoints
I-1. In the L1 layer rho=r*rho_b(tau), z=lambda*r*m(tau), rho_b(tau)^2+m(tau)^2=1, tau in [7/8,1), rho>0, 7/8<=r<=sqrt(1-delta_L1)<1. For |xi|<=rho, xi^2+z^2/lambda^2<=rho^2+z^2/lambda^2=r^2<1. Thus the entire closed segment p_xi is in int(K). This is a parameterization identity, not the boundary-base-point relation rho^2+m^2=1.
I-2. K=T(B), T=diag(1,1,lambda), B the unit ball. Put u_x=T^{-1}x with |u_x|=1, u_xi=T^{-1}p_xi with |u_xi|<=r. Then D(x,p_xi)=|T(u_x-u_xi)|>=lambda|u_x-u_xi|>=lambda(1-r). Define delta=1-r^2=(1-r)(1+r)<=2(1-r). Since lambda>=2/5, d_*=lambda(1-r)>=lambda*delta/2>=delta/5>=delta_L1/5>0. This holds for every boundary x and every xi in [-rho,rho].
I-3. P1 Lemma 3.1: h(x,p_xi)>0 and 0<gamma<=1 on the segment. P1 Lemma 3.2: G and R=arccos(gamma)/sqrt(1-gamma^2) extend analytically through gamma=1. With D>=d_*, F is C^2 in xi, uniformly in the compact parameter set [-1,1]x[0,2pi]x[-rho,rho] (including surface poles, where b=0). This uses P1 lemmas as source claims, subject to their outstanding external audit.
I-4. From P1 Lemma 3.4, |calF_xi'|<=pi^2/4+2pi and |calF_xi''|<=C2/D<=C2/d_*, C2=9pi+8, for all mu,phi,xi. The parameter rectangle P=[-1,1]x[0,2pi] has measure 4pi. The constant functions M1=pi^2/4+2pi and M2=C2/d_* are integrable on P. Continuity in xi and these dominators justify differentiation under the integral twice, including at xi=+-rho via an interior neighborhood (I-1). Thus E_rho(xi,z)=(1/(4pi lambda))int_P calF_xi' and E_rhorho(xi,z)=(1/(4pi lambda))int_P calF_xi''.
I-5. Reflection (x,y,z)->(-x,-y,z) preserves K, so E(-xi,z)=E(xi,z) and E_rho(-rho,z)=-E_rho(rho,z). Consequently H(p)=E_rho(rho,z)/rho=[E_rho(rho,z)-E_rho(-rho,z)]/(2rho). No boundary trace or axis limit is used; rho>0.
I-6. By I-3/I-4, E_rho is C^1 on the closed segment with derivative E_rhorho, so the ordinary fundamental theorem of calculus yields E_rho(rho,z)-E_rho(-rho,z)=int_{-rho}^{rho}E_rhorho(xi,z) dxi.
I-7. The product [-rho,rho]xP has finite measure, and |calF_xi''|<=M2. Fubini therefore applies to int_xi int_P calF_xi''. For every mu,phi, the integrand is continuously differentiable on the entire segment (D>=d_*), so FTC gives int_{-rho}^{rho}calF_xi'' dxi=calF_xi'(rho)-calF_xi'(-rho). Thus 4pi lambda H=int_P K_H, where K_H=[calF_xi'(rho)-calF_xi'(-rho)]/(2rho).
I-8. Reflection phi->2pi-phi preserves b and the other parameters, hence K_H. Therefore int_0^{2pi}K_H dphi=2int_0^pi K_H dphi and
  2pi lambda H(p)=int_{-1}^1 G_p(mu) dmu,
  G_p(mu)=int_0^pi K_H(mu,phi)dphi.
This is O1-1. It proves an identity, not a sign.

## C. I-9–I-12: interior algebra
I-9. At fixed z,mu,b, h_rho=-lambda*b, (D^2)_rho=2(rho-b), D_rho=(rho-b)/D. At fixed rho,z,mu, h_b=-lambda*rho, (D^2)_b=-2rho, D_b=-rho/D. Since w is independent of rho and b:
 gamma_rho=-lambda*b/(wD)-h*(rho-b)/(wD^3);
 gamma_b=-lambda*rho/(wD)+h*rho/(wD^3).
These are derived from A, not imported from FTq (5.1).
I-10. Define J=lambda*(a^2-b^2)*gamma_b-h*gamma_rho. Substitution gives the exact general-interior factored numerator
 N_J:=w*D^3*J
   =lambda*rho*(a^2-b^2)*(h-lambda*D^2)
    +h*(lambda*b*D^2+h*(rho-b)).
Every factor is a polynomial in b because h=h0-lambda*rho*b and D^2=D0-2rho*b. The apparent cubic b^3 coefficient cancels: in the first summand the b^3 coefficient is -lambda*rho*(lambda*rho), while the second summand contributes +lambda^2*rho^2, so degree<=2. Thus N_J=A2*b^2+A1*b+A0, where the coefficient definitions below are independent of the FTq boundary factorization:
  A2=lambda^2*rho^3-lambda^2*rho+lambda*mu*rho*z;
  A1=lambda^4*mu^2-lambda^3*mu^3*z-2*lambda^3*mu*z-lambda^2*mu^2*rho^2+2*lambda^2*mu^2*z^2-lambda^2*mu^2+lambda^2*z^2+lambda*mu^3*z+lambda*mu*rho^2*z-lambda*mu*z^3+lambda*mu*z-mu^2*z^2;
  A0=lambda^4*mu^4*rho-lambda^4*mu^2*rho-2*lambda^3*mu^3*rho*z+2*lambda^3*mu*rho*z-lambda^2*mu^4*rho+lambda^2*mu^2*rho^3+lambda^2*mu^2*rho*z^2+lambda^2*mu^2*rho-lambda^2*rho^3-lambda^2*rho*z^2+lambda^2*rho+lambda*mu^3*rho*z-3*lambda*mu*rho*z+mu^2*rho*z^2.
These are the paper coefficient targets transcribed from FTq (5.2); exact coefficient collation remains an S-3 obligation, not yet independently machine-verified. The factored expression above is the direct derivation.
I-11. For b-paired points, h_plus=h0-lambda*rho*b, h_minus=h0+lambda*rho*b, D_plus^2=D0-2rho*b, D_minus^2=D0+2rho*b.
Direct difference of squares yields
 h_plus^2*D_minus^2-h_minus^2*D_plus^2
 =4rho*b*[h0*(h0-lambda*D0)+lambda^2*rho^2*b^2].
Now h0-lambda*D0
 =lambda-z*mu-lambda*[1-mu^2+rho^2+(lambda*mu-z)^2]
 =lambda*(1-lambda^2)*mu^2-z*(1-2lambda^2)*mu-lambda*(rho^2+z^2)
 =:c(mu).
Thus the two forms of c(mu) in FTq (7.2) coincide by direct expansion, with rho and z independent.
Provided the denominator is positive (I-12), rationalization gives
 gamma_plus-gamma_minus
 =4rho*b*[h0*c(mu)+lambda^2*rho^2*b^2]/
 [w*D_plus*D_minus*(h_plus*D_minus+h_minus*D_plus)].
This is an interior identity, not an imported boundary formula.
I-12. Both paired surface points are on bd(K), while p lies in int(K). P1 Lemma 3.1 yields h_plus,h_minus>0, and I-2 yields D_plus,D_minus>=d_*>0. Hence h_plus*D_minus+h_minus*D_plus>0. Also w>=lambda>0, so the entire denominator in I-11 is strictly positive. No quantitative lower bound is claimed.

## D. Boundary consistency, not an interior assumption
Only here put rho=rho_b, z=lambda*m, rho_b^2+m^2=1, corresponding to r->1.
D-1: h=lambda*(1-rho*b-m*mu), D^2=a^2+rho^2+lambda^2*(mu-m)^2-2rho*b, exactly FTq section 2.
D-2: the expected polynomial specialization is N_J=-lambda^2*(m-mu)*Q_FTq, with Q_FTq as in pinned FTq (6.2). This is an explicit symbolic-reduction obligation; not yet checked independently by S-D-2.
D-3: the rationalized gamma-pair expression and c(mu) reduce by z=lambda*m to the boundary formula of FTq (7.1),(7.2); the algebraic substitutions are direct, but the exact scripted D-3 residual check is pending.
At r=1 the denominator may vanish at a coincident surface point; this section asserts only algebraic consistency where defined, not a uniform boundary denominator bound.

## E. Scope and status
C-P paper items I-1–I-12 have been addressed, conditional on the P1 lemmas explicitly noted above. S-1–S-5 in Stage G/L and D-1–D-3 are NOT EXECUTED. No O1 completion certificate is claimed, no numerical evaluation or interval calculation performed. No FTq boundary-only sign factorization was used in I-1–I-12. Axis rho=0, O4, remains outside O1.

## F. Relevance to the L1 positivity mountain (O2/O3/O6)
O1-1 supplies an exactly normalized, signed azimuthally averaged kernel G_p(mu), so O2 and O3 can estimate favorable and unfavorable latitude contributions without replacing the entire outside integral by its absolute value. I-10 supplies a general-interior quadratic N_J in b, and I-11 supplies a rationalized gamma-pair difference with a strictly positive denominator, allowing later sign-correlation analysis of the secant term. These are algebraic materials, not a positivity proof: the interior validity of FTq's integration-by-parts R*J representation is explicitly NOT an O1 claim, and any use of it requires its own justification. O6 still requires a uniform strict lower bound and coverage of the full L1 compact domain, including endpoints and the separate axis obligation.
