"""
D-OB P2 / FT_q diagnostic tool

STATUS: DIAGNOSTIC_ONLY / NOT_EVIDENCE

This script is not a mathematical proof certificate.
Its numerical outputs must not be used to select
proof partitions, constants, or thresholds.
"""
import json, sys
from fractions import Fraction as Q
from itertools import product
from math import comb
import sympy as sp
J=json.load(open(sys.argv[1]))
L,m,mu=sp.symbols('L m mu')
r2=1-m**2; a2=1-mu**2; d=a2+r2+L*(m-mu)**2; e=4*r2*a2
B1=m*(1-L)*mu**2+((1+L)*m**2+L-2)*mu-L*m
C0=(L-1)*mu**3-L*m*mu**2+(2-L)*mu-m*(1-L); g=m*a2+C0
def bern(expr,box):
    ts=sp.symbols('t0:%d'%len(box))
    sub={v:sp.Rational(lo.numerator,lo.denominator)+sp.Rational((hi-lo).numerator,(hi-lo).denominator)*t for (v,lo,hi),t in zip(box,ts)}
    P=sp.Poly(sp.expand(expr.subs(sub)),*ts); degs=P.degree_list()
    a={k:Q(int(sp.fraction(c)[0]),int(sp.fraction(c)[1])) for k,c in zip(P.monoms(),P.coeffs())}
    res={}
    for idx in product(*[range(dd+1) for dd in degs]):
        s=Q(0)
        for k,c in a.items():
            if all(ki<=ii for ki,ii in zip(k,idx)):
                w=Q(1)
                for ki,ii,dd in zip(k,idx,degs): w*=Q(comb(ii,ki),comb(dd,ki))
                s+=w*c
        res[idx]=s
    return degs,res
box=[(L,Q(4,25),Q(8649,40000)),(m,Q(112,113),Q(1)),(mu,Q(-1,4),Q(3,5))]
for t in ("3","14/5"):
    tt=sp.Rational(t)
    # interpretation: B := B1, d := a^2+rho^2+L s^2
    Pi=-(g+sp.Rational(3,100)*a2)*d - tt*B1*a2
    degs,res=bern(Pi,box)
    jj=J["Bernstein"][t]; claimed={tuple(c["index"]):Q(c["value"]) for c in jj["coefficients"]}
    same=claimed==res
    print(f"Pi_t t={t}: degree {degs} (claimed {jj['degree']}); all {len(res)} coefficients identical to JSON: {same}; min {min(res.values())} (claimed {jj['minimum']})")
    if not same:
        diff=[k for k in res if res[k]!=claimed.get(k)]; print("   mismatches:",len(diff),diff[:3])
# theta lower bound needed for the B1<=0 branch: theta >= (14/5)/d  <=>  2 d^2 (3d^2-e) - (14/5)(2d^2-e)(d^2+e) >= 0
degs,res=bern(sp.expand(2*d**2*(3*d**2-e)-sp.Rational(14,5)*(2*d**2-e)*(d**2+e)),box)
print("theta_lo*d >= 14/5 on mu in [-1/4,3/5]: min Bernstein coeff",min(res.values()), "->", "CERTIFIED" if min(res.values())>0 else "NOT certified by plain Bernstein")
print("arith: 10778024217619399/81721600000000000 =",float(Q(10778024217619399,81721600000000000))," >= 1/8:",Q(10778024217619399,81721600000000000)>=Q(1,8))
print("arith: 207/5000 + 1/8 =",Q(207,5000)+Q(1,8)," == 104/625:",Q(207,5000)+Q(1,8)==Q(104,625))
