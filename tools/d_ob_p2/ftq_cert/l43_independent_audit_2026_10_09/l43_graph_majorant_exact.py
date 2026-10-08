"""Independent exact checks for the corrected Contract 43 near-band paper proof.

Domain: |mu-m| <= rho intersect -1 <= mu <= 1, hence s in [m-1,rho].
This is NOT Contract 45 Piece 1. No quadrature, grids, floating-point assertions,
or method-(B) computation is used. Read the accompanying proof for the analytic
inequalities, changes of variables, absolute continuity and endpoint treatment.
The script checks identities, Bernstein coefficients, elementary antiderivatives,
and every rational constant used in the proof. It is not a proof assistant.
Run: python3 -I l43_graph_majorant_exact.py [--json /absolute/output.json]
"""
from fractions import Fraction as Q
from math import comb, factorial
import argparse
import hashlib
import json
import platform
from pathlib import Path
import sympy as sp

rows = []

def check(name, condition, detail=None):
    passed = bool(condition)
    rows.append(dict(name=name, passed=passed, detail=detail))
    print(f"{name}: {'PASS' if passed else 'FAIL'}" + (f" {detail}" if detail else ""), flush=True)
    if not passed:
        raise AssertionError(name)

def zero(name, expr):
    check(name, sp.cancel(sp.expand(expr)) == 0)

def rq(x):
    return sp.Rational(x.numerator, x.denominator)

def bern1(expr, var, lo, hi):
    t = sp.Dummy('t')
    poly = sp.Poly(sp.expand(expr.subs(var, rq(lo) + rq(hi-lo)*t)), t)
    degree = poly.degree()
    coeff = [Q(int(poly.nth(j).p), int(poly.nth(j).q)) for j in range(degree+1)]
    return [sum((coeff[j]*Q(comb(i,j),comb(degree,j)) for j in range(i+1)), Q(0))
            for i in range(degree+1)]

m, s, b, xi, L = sp.symbols('m s b xi L', real=True)
mu = m-s
rho2 = 1-m*m
a2 = 1-mu*mu
y2 = a2-b*b
t = b-xi
r2 = t*t+y2
D2 = r2+L*s*s
w2 = mu*mu+L*a2
H0 = 1-m*mu-xi*b                 # h = lambda*H0
delta = rho2-xi*xi
A = m-(1-L)*s
Nb = b*s*A-xi*(b*b-rho2-m*s)     # N = lambda*Nb
T = y2+L*s*s

zero('I01 sphere identities', a2-(rho2+2*m*s-s*s))
zero('I02 N/lambda = bD^2-H0(b-xi)', Nb-(b*D2-H0*t))
zero('I03 2h/lambda = D^2+(1-L)s^2+delta', 2*H0-D2-(1-L)*s*s-delta)
zero('I04 projected normal has unit length after normalization', L*b*b+L*y2+mu*mu-w2)
zero('I05 normal dot displacement = h/lambda', b*t+y2-mu*s-H0)
zero('I06 Gram identity', L*Nb**2-((w2*D2-L*H0**2)*T-A*A*y2*D2))
zero('I07 w^2-A^2 = L(rho^2+(1-L)s^2)', w2-A*A-L*(rho2+(1-L)*s*s))
zero('I08 positive numerator identity',
     2*L*Nb**2-L*H0**2*T-(2*L*D2*((rho2+(1-L)*s*s)*y2+w2*s*s)-3*L*H0**2*T))
zero('I09 curvature-depth decomposition',
     Nb-((xi+t/2)*D2-t*((1-L)*s*s+delta)/2))
zero('I10 simultaneous reflection preserves numerator',
     Nb.subs({b:-b,xi:-xi}, simultaneous=True)+Nb)

x, y = sp.symbols('x y', real=True)
zero('I11 Young 1/4 square', sp.Rational(5,4)*x*x+5*y*y-(x+y)**2-(x/2-2*y)**2)
zero('I12 Young 1/3 square', sp.Rational(4,3)*x*x+4*y*y-(x+y)**2-(x-3*y)**2/3)

rho_hi, m_lo, mu_lo = Q(15,113), Q(112,113), Q(97,113)
lam_lo, lam_hi = Q(2,5), Q(93,200)
L_lo, L_hi = lam_lo**2, lam_hi**2
k, c, H_hi, W_hi_parameter = Q(3,5), Q(51,50), Q(13,20), Q(89,100)
pi_hi, C3_hi, C5_hi = Q(22,7), Q(77,50), Q(103,50)
check('C01 sphere endpoint', m_lo*m_lo+rho_hi*rho_hi == 1)
check('C02 mu lower bound', m_lo-rho_hi == mu_lo and mu_lo > 0)
check('C03 cap contained in baseline band: 1-m=rho^2/(1+m)<=rho', rho_hi < 1+m_lo and m_lo > 0)

z = sp.symbols('z', real=True)
bern = {}
for name, expr, var, lo, hi in [
    ('C04 graph gradient', sp.Rational(9,25)*(1-z)**2-2*z, z, Q(0), Q(15,112)),
    ('C05 distance comparison', sp.Rational(1,12)-sp.Rational(9,25)*L, L, L_lo, L_hi),
    ('C06 depth error', sp.Rational(1,50)-sp.Rational(21,20)*z*z, z, Q(0), Q(15,112)),
]:
    bb = bern1(expr,var,lo,hi)
    bern[name] = [str(v) for v in bb]
    check(name, min(bb)>0, {'coefficients':bern[name], 'minimum':str(min(bb))})

check('C07 Young curvature coefficient', (1-L_lo)*Q(5,4)*k*k == Q(189,500) < 1)
check('C08 error coefficient c', c == 1+Q(1,50))
check('C09 disk radius bound by squaring', H_hi>rho_hi and (H_hi-rho_hi)**2>2*rho_hi)
W2_at_hi = mu_lo**2+L_hi*(1-mu_lo**2)
check('C10 W(lambda_hi) > 89/100', W2_at_hi>W_hi_parameter**2,
      str(W2_at_hi-W_hi_parameter**2))
check('C11 (4/3)^(3/2) < 77/50', C3_hi**2>Q(4,3)**3)
check('C12 (4/3)^(5/2) < 103/50', C5_hi**2>Q(4,3)**5)

lam = sp.symbols('lam', positive=True)
mu0 = sp.symbols('mu0', positive=True)
W = sp.sqrt(mu0*mu0+lam*lam*(1-mu0*mu0))
zero('I13 d(lambda/W) W^3 = mu0^2', sp.diff(lam/W,lam)*W**3-mu0**2)
zero('I14 d(lambda^2/W) W^3',
     sp.diff(lam**2/W,lam)*W**3-lam*(2*mu0**2+lam**2*(1-mu0**2)))

rr, d = sp.symbols('rr d', positive=True)
J3 = sp.asinh(rr/d)-rr/sp.sqrt(rr*rr+d*d)
J5 = -1/sp.sqrt(rr*rr+d*d)+d*d/(3*(rr*rr+d*d)**sp.Rational(3,2))
zero('A01 cross radial primitive', sp.diff(J3,rr)-rr**2/(rr*rr+d*d)**sp.Rational(3,2))
zero('A02 depth radial primitive', sp.diff(J5,rr)-rr**3/(rr*rr+d*d)**sp.Rational(5,2))
check('A03 depth radial integral to infinity', sp.simplify(sp.limit(J5,rr,sp.oo)-J5.subs(rr,0)-2/(3*d)) == 0)
th = sp.symbols('th', real=True)
check('A04 half-plane angles',
      sp.integrate(sp.cos(th)**2,(th,0,sp.pi))==sp.pi/2 and
      2*sp.integrate(sp.cos(th),(th,0,sp.pi/2))==2)
rho = sp.symbols('rho', positive=True)
check('A05 exact xi moments',
      sp.integrate(xi**2,(xi,-rho,rho))/(2*rho)==rho**2/3 and
      sp.integrate(xi,(xi,0,rho))/rho==rho/2 and
      sp.integrate(rho**2-xi**2,(xi,-rho,rho))/(2*rho)==2*rho**2/3)

zz = sp.symbols('zz', positive=True)
glog = sp.log(1+zz)-zz/(1+zz)
zero('A06 logarithm comparison derivative', sp.diff(glog,zz)-zz/(1+zz)**2)
cc = sp.symbols('cc', positive=True)
zero('A07 rho-cubed-log derivative',
     sp.diff(rho**3*sp.log(1+cc/rho**2),rho)-
     rho**2*(3*sp.log(1+cc/rho**2)-2*cc/(rho**2+cc)))
exp6_lo = sum((Q(6)**j/Q(factorial(j)) for j in range(11)),Q(0))
log_arg_hi = 1+10*H_hi/rho_hi**2
check('C13 log bound < 6 via exp Taylor lower sum', exp6_lo>log_arg_hi,
      {'exp6_lower':str(exp6_lo),'argument_upper':str(log_arg_hi)})

# Exact positive integral proving pi < 22/7, rather than decimal pi data.
xx = sp.symbols('xx', real=True)
check('A08 exact pi upper bound integral',
      sp.integrate(xx**4*(1-xx)**4/(1+xx**2),(xx,0,1)) == sp.Rational(22,7)-sp.pi)

# IMPORTANT: plane change of variables dmu dphi = db dy / mu.
# lambda^p/(w*mu) <= lambda_hi^p/(mu_lo*W(lambda_hi)), p=1,2.
den = mu_lo*W_hi_parameter
AA = pi_hi*rho_hi**2*H_hi/3 + rho_hi*H_hi**2/2 + pi_hi*H_hi**3/24
U_curv = 2*pi_hi*L_hi*AA/den
U_cross = 2*pi_hi*L_hi*c*C3_hi*rho_hi**3*6/den
U_depth = 2*pi_hi*pi_hi*lam_hi*c*c*C5_hi*rho_hi**2/(9*den)
U = U_curv+U_cross+U_depth
rounded = Q(9,40)
budget = Q(187614363159,817216000000)
far = Q(5481,10000)
design = Q(635530452759,817216000000)
check('B01 exact sum', U==Q(3887073979116207,17284813033600000), str(U))
check('B02 near upper < 9/40', U<rounded, str(rounded-U))
check('B03 9/40 < design near budget', rounded<budget, str(budget-rounded))
check('B04 stated design subtraction', design-far==budget)
check('B05 conditional design gap', design-far-rounded==Q(3740763159,817216000000))

# Exact multiscale limits, not numerical sampling.
eps = sp.symbols('eps', positive=True)
ll = sp.Rational(2,5)
mm = sp.sqrt(1-eps**2)
bb = ll*eps**2/2
uu = sp.sqrt(1-bb**2)
ss = mm-uu
DD = bb*bb+ll*ll*ss*ss
NN = ll*bb*ss*(mm-(1-ll*ll)*ss)
hh = ll*(1-mm*uu)
ww = sp.sqrt(uu*uu+ll*ll*bb*bb)
Phi_num = 2*NN**2-hh*hh*ll*ll*ss*ss
check('M01 cap-core N/D^2 limit = -1/2', sp.limit(NN/DD,eps,0,dir='+')==-sp.Rational(1,2))
check('M02 cap-core scaled positive numerator',
      sp.limit(Phi_num/eps**8,eps,0,dir='+')==ll**4/16)
check('M03 cap-core rho^2 kernel limit',
      sp.simplify(sp.limit(eps**2*Phi_num/(ww*DD**sp.Rational(5,2)),eps,0,dir='+')-sp.sqrt(2)/(4*ll))==0)

eta, u = sp.symbols('eta u', positive=True)
zz, co = sp.symbols('zz co', real=True)
mo = sp.sqrt(1-eta**4)
so = eta**2*u
xo = eta**2*zz
ao2 = eta**4+2*mo*so-so**2
bo = eta*sp.sqrt(2*mo*u+eta**2*(1-u*u))*co
do2 = ao2-2*xo*bo+xo*xo+L*so*so
ho = eta**4+mo*so-xo*bo
no = bo*so*(mo-(1-L)*so)-xo*(bo*bo-eta**4-mo*so)
to = ao2-bo*bo+L*so*so
check('M04 outer D^2/rho limit', sp.simplify(sp.limit(do2/eta**2,eta,0,dir='+')-2*u)==0)
check('M05 outer numerator/rho^3 limit',
      sp.simplify(sp.limit((2*L*no**2-L*ho**2*to)/eta**6,eta,0,dir='+')-2*L*u**3*(3*co**2-1))==0)
alpha = sp.acos(1/sp.sqrt(3))
check('M06 positive-part angular integral',
      sp.simplify(2*sp.integrate(3*sp.cos(th)**2-1,(th,0,alpha))-alpha-sp.sqrt(2))==0)

result = {
    'status':'ALL EXACT CHECKS PASS',
    'scope':'Checks support the accompanying analytic proof; not a formal Contract 43 freeze or D-P2 certification.',
    'python':platform.python_version(), 'sympy':sp.__version__,
    'script_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
    'checks':rows, 'bernstein':bern,
    'constants':{k:str(v) for k,v in {
        'U_curvature':U_curv,'U_cross':U_cross,'U_depth':U_depth,'U_exact':U,
        'U_near_rounded':rounded,'rounding_slack':rounded-U,
        'design_near_budget':budget,'design_gap':budget-rounded,
    }.items()},
}
parser=argparse.ArgumentParser()
parser.add_argument('--json')
args=parser.parse_args()
if args.json:
    Path(args.json).write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
print(f"ALL EXACT CHECKS PASS ({len(rows)} checks); U_near < 9/40; formal status unchanged.")
