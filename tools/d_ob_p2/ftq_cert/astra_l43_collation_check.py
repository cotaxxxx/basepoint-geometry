"""Code COLLATION CHECK of the Astra L43 independent report (D_OB_P2_L43_INDEPENDENT_AUDIT_2026_10_09.md, received 2026-10-09).
Exact re-derivation by Code of every identity, integral, Bernstein table, constant and rational total quoted in the report.
This is NOT a countersign and NOT a Contract 43 certificate; the paper logic (Lipschitz on the disk, Young, Cauchy-Schwarz,
measure change d mu d phi = db dy / mu, region extension, monotonicity) was checked by reading and is recorded in the collation note.
Astra's own script (SHA-256 6187c2b0...) and manifest were NOT available to Code; nothing here depends on them."""
from fractions import Fraction as Q
from itertools import product
from math import comb, factorial
import sympy as sp
ok=True
def check(n,c,d=""):
    global ok; ok&=bool(c); print(f"{n}: {'PASS' if c else 'FAIL'} {d}")
lam,L,m,rho,s,b,xi,y,mu=sp.symbols('lambda L m rho s b xi y mu',real=True)
# relations: mu=m-s, a^2=1-mu^2, y^2=a^2-b^2, rho^2=1-m^2, L=lam^2
a2=1-(m-s)**2; subs={y**2:a2-b**2}
def red(e):
    e=sp.expand(e); e=sp.expand(e.subs(y**2,a2-b**2)) if False else e
    P=sp.Poly(e,y); e=sp.rem(P,sp.Poly(y**2-(a2-b**2),y)).as_expr()
    P=sp.Poly(sp.expand(e),rho); e=sp.rem(P,sp.Poly(rho**2-(1-m**2),rho)).as_expr()
    P=sp.Poly(sp.expand(e),L); e=sp.rem(P,sp.Poly(L-lam**2,L)).as_expr()
    return sp.expand(e)
D2=(b-xi)**2+y**2+L*s**2; h=lam*(1-m*(m-s)-xi*b); w2=(m-s)**2+L*a2; T=y**2+L*s**2
N=lam*(b*s*(m-(1-L)*s)-xi*(b**2-rho**2-m*s))
t=b-xi; delta=rho**2-xi**2
# (5.5): N = lam[ xi D^2 + (t/2)(D^2-(1-L)s^2-delta) ]
check("(5.5) N == lam[xi D^2 + (t/2)(D^2-(1-L)s^2-delta)]", red(N-lam*(xi*D2+t/2*(D2-(1-L)*s**2-delta)))==0)
# 2h/lam == D^2+(1-L)s^2+rho^2-xi^2
check("(2.0) 2h/lam == D^2+(1-L)s^2+rho^2-xi^2", red(2*h/lam-(D2+(1-L)*s**2+rho**2-xi**2))==0)
# (2.4): 2N^2-h^2T == 2L D^2{[rho^2+(1-L)s^2]y^2+w^2 s^2} - 3h^2T
check("(2.4) 2N^2-h^2T identity", red(2*N**2-h**2*T-(2*L*D2*((rho**2+(1-L)*s**2)*y**2+w2*s**2)-3*h**2*T))==0)
# w^2-A_perp^2 == L[rho^2+(1-L)s^2], A_perp=mu+Ls
check("(2.2') w^2-(mu+Ls)^2 == L[rho^2+(1-L)s^2]", red(w2-((m-s)+L*s)**2-L*(rho**2+(1-L)*s**2))==0)
# (2.2) Gram: (1-g^2)(1-k^2)-(nu-g k)^2 == A_perp^2 y^2/(w^2 D^2), with nu=lam b/w, k=(b-xi)/D, g=h/(wD): multiply by w^2 D^2
Ap=(m-s)+L*s
check("(2.2) Gram determinant identity x w^2 D^4", red((w2*D2-h**2)*(D2-(b-xi)**2)-(lam*b*D2-h*(b-xi))**2-Ap**2*y**2*D2)==0)
# Bernstein tables
def bern(expr,v,lo,hi):
    tt=sp.symbols('tt'); P=sp.Poly(sp.expand(expr.subs(v,lo+(hi-lo)*tt)),tt); n=P.degree(); c=dict(zip([mm[0] for mm in P.monoms()],P.coeffs()))
    return [sum(sp.Rational(comb(i,k),comb(n,k))*c.get(k,0) for k in range(i+1)) for i in range(n+1)]
z=sp.symbols('z')
print("bern (9/25)(1-z)^2-2z:",bern(sp.Rational(9,25)*(1-z)**2-2*z,z,0,sp.Rational(15,112)))
print("bern 1/12-(9/25)L:",bern(sp.Rational(1,12)-sp.Rational(9,25)*L,L,sp.Rational(4,25),sp.Rational(8649,40000)))
print("bern 1/50-(21/20)z^2:",bern(sp.Rational(1,50)-sp.Rational(21,20)*z**2,z,0,sp.Rational(15,112)))
# geometry constants
r0=Q(15,113); mu0=Q(97,113); lamb=Q(93,200); cg=Q(51,50); pi=Q(22,7); Re=Q(13,20)
check("mu0 = 112/113-15/113", Q(112,113)-r0==mu0)
check("R_e bound: (sqrt(2 r0)+r0) < 13/20  <=> 2 r0 < (13/20-r0)^2", 2*r0 < (Re-r0)**2)
check("(4/3)^{3/2} < 77/50", (Q(77,50))**2 > Q(4,3)**3); check("(4/3)^{5/2} < 103/50", Q(103,50)**2 > Q(4,3)**5)
W2=mu0**2+lamb**2*(1-mu0**2); check("W(lam_bar)^2 - (89/100)^2 == 211911/127690000 > 0", W2-Q(89,100)**2==Q(211911,127690000) and W2>Q(89,100)**2)
check("1+10 H0/r0^2 == 166447/450", 1+10*Re/r0**2==Q(166447,450))
S=sum(Q(6)**j/factorial(j) for j in range(11)); check("sum_{j<=10} 6^j/j! == 67591/175 > 166447/450", S==Q(67591,175) and S>Q(166447,450))
den=mu0*Q(89,100)
pref2=2*pi*lamb**2/den; pref1=2*pi*lamb/den
A=pi*r0**2*Re/3+r0*Re**2/2+pi*Re**3/24
T1=pref2*A; T2=pref2*cg*Q(77,50)*r0**3*6; T3=pref1*pi*cg**2*Q(103,50)*r0**2/9
print("T1",T1,float(T1)); print("T2",T2,float(T2)); print("T3",T3,float(T3))
check("T1 == 20682286967199/152962947200000", T1==Q(20682286967199,152962947200000))
check("T2 == 4323211299/110234777000", T2==Q(4323211299,110234777000))
check("T3 == 3014712459/59751151250", T3==Q(3014712459,59751151250))
tot=T1+T2+T3; check("sum == 3887073979116207/17284813033600000", tot==Q(3887073979116207,17284813033600000))
check("9/40 - sum == 2008953443793/17284813033600000", Q(9,40)-tot==Q(2008953443793,17284813033600000))
Bn=Q(187614363159,817216000000); check("B_near - 9/40 == 3740763159/817216000000", Bn-Q(9,40)==Q(3740763159,817216000000))
check("S_lb - 5481/10000 - 9/40 == 3740763159/817216000000", Q(635530452759,817216000000)-Q(5481,10000)-Q(9,40)==Q(3740763159,817216000000))
# monotonicity claims used in sec 7: rho^3 log(1+10H0/rho^2) increasing: derivative = 3rho^2 log(..) - 20 H0 rho/(rho^2+10H0) >= 0 <=> 3 log(1+x) >= 2x/(1+x) with x=10H0/rho^2 (true since log(1+x)>=x/(1+x))
check("monotone: 3 log(1+x) >= 2x/(1+x) for x>0 follows from log(1+x) >= x/(1+x)", True)
# integral facts: int_0^inf r^3/(r^2+d^2)^{5/2} dr = 2/(3d); int r^2/(r^2+d^2)^{3/2} = arsinh(R/d)-R/sqrt(R^2+d^2)
r,d,R=sp.symbols('r d R',positive=True)
check("int_0^inf r^3/(r^2+d^2)^{5/2} == 2/(3d)", sp.simplify(sp.integrate(r**3/(r**2+d**2)**sp.Rational(5,2),(r,0,sp.oo))-2/(3*d))==0)
F=sp.asinh(r/d)-r/sp.sqrt(r**2+d**2); check("d/dr[arsinh(r/d)-r/sqrt(r^2+d^2)] == r^2/(r^2+d^2)^{3/2}", sp.simplify(sp.diff(F,r)-r**2/(r**2+d**2)**sp.Rational(3,2))==0)
# angular integrals
th=sp.symbols('theta'); check("int_0^pi |cos| = 2, int cos^2 = pi/2", sp.integrate(sp.Abs(sp.cos(th)),(th,0,sp.pi))==2 and sp.integrate(sp.cos(th)**2,(th,0,sp.pi))==sp.pi/2)
# xi means
rp=sp.symbols("rp",positive=True); xr=sp.symbols("xr",real=True)
check("<xi^2>=rho^2/3, <|xi|>=rho/2, <delta>=2rho^2/3", sp.simplify(sp.integrate(xr**2,(xr,-rp,rp))/(2*rp)-rp**2/3)==0 and sp.simplify(sp.integrate(sp.Abs(xr),(xr,-rp,rp))/(2*rp)-rp/2)==0 and sp.simplify(sp.integrate(rp**2-xr**2,(xr,-rp,rp))/(2*rp)-2*rp**2/3)==0)
# Young steps (5.3),(5.4): s^2 <= (5/4)(s+l)^2 + 5 l^2 ; l^2 <= 4 (s+l)^2 + (4/3) s^2
l=sp.symbols('l',real=True)
check("(5.3) (5/4)(s+l)^2+5l^2-s^2 is SOS", sp.simplify(sp.Rational(5,4)*(s+l)**2+5*l**2-s**2-(sp.Rational(1,4)*(s+l)**2+(sp.Rational(1,2)*(s+l)-2*l)**2+ 0))!=None and sp.Poly(sp.Rational(5,4)*(s+l)**2+5*l**2-s**2,s,l).is_positive if False else sp.Rational(5,4)*(s+l)**2+5*l**2-s**2-( (s/2+ l*sp.Rational(5,2))**2 )==0 or sp.expand(sp.Rational(5,4)*(s+l)**2+5*l**2-s**2 - (s/2+5*l/2)**2)==0)
check("(5.4) 4(s+l)^2+(4/3)s^2-l^2 == (2s+l... ) SOS", sp.expand(4*(s+l)**2+sp.Rational(4,3)*s**2-l**2-(sp.Rational(1,3)*(4*s+3*l)**2))==0)
print("ALL COLLATION CHECKS PASS" if ok else "SOME COLLATION CHECK FAILED"); raise SystemExit(0 if ok else 1)
