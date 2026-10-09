#!/usr/bin/env python3
"""O1 C-S exact symbolic check; fixed FREEZE a35ae39553b9fd4a0fc29c890887415a43f96e6f."""
import sys
import sympy as s

def blocked(cid, reason):
    print(f'O1-CS {cid} BLOCKED {reason}')
    raise SystemExit(1)

def check(cid, residuals):
    for residual in residuals:
        value = s.cancel(residual)
        numerator = s.together(value).as_numer_denom()[0]
        value = s.expand(numerator)
        if value != 0:
            print(f'O1-CS {cid} FAIL residual={s.srepr(value)}')
            raise SystemExit(1)
    print(f'O1-CS {cid} PASS')

if sys.version_info[:3] != (3, 13, 5) or s.__version__ != '1.14.0':
    print('O1-CS ENV FAIL Python/SymPy version mismatch')
    raise SystemExit(1)
print('O1-CS ENV Python=3.13.5 SymPy=1.14.0')
l,mu,rho,z,b,r,tau,m,RB=s.symbols('lambda mu rho z b r tau m rho_b', real=True)
a2=1-mu**2
w2=l**2*a2+mu**2
h=l*(1-rho*b)-z*mu
D2=a2+rho**2+(l*mu-z)**2-2*rho*b
h0=l-z*mu
D0=a2+rho**2+(l*mu-z)**2
rho_b=(1-tau**2)/(1+tau**2)
mt=2*tau/(1+tau**2)
subL={rho:r*rho_b,z:l*r*mt}
def L(expr):return s.cancel(expr.subs(subL, simultaneous=True))
# S-1-G / S-1-L: P1 line 9 x=(a*cos(phi),a*sin(phi),lambda*mu),
# nu=(lambda*a*cos(phi),lambda*a*sin(phi),mu)/w, b=a*cos(phi), a2=1-mu**2.
# The x·nu calculation and |x-p|^2 expansion are compared to A2.
# Independent dot products from the pinned P1 x and outward unit normal.
A,phi=s.symbols('a phi', real=True)
x=s.Matrix([A*s.cos(phi), A*s.sin(phi), l*mu])
wnu=s.Matrix([l*A*s.cos(phi),l*A*s.sin(phi),mu])
pvec=s.Matrix([rho,0,z])
# First simplify the trigonometric unit-circle identity, then set a*cos(phi)=b.
def geom_reduce(expr):
    expr=s.trigsimp(s.expand(expr))
    expr=s.expand(expr.subs(s.cos(phi),b/A))
    return s.cancel(expr.subs(A**2,a2))
h_geom=geom_reduce((x-pvec).dot(wnu))
D_geom=geom_reduce((x-pvec).dot(x-pvec))
wnu_norm=geom_reduce(wnu.dot(wnu))
check('S-1-G',[h_geom-h,D_geom-D2,wnu_norm-w2])
check('S-1-L',[L(h_geom-h),L(D_geom-D2)])
# S-2-G / S-2-L: independently differentiate the A2 definition
# gamma=h/(w*sqrt(D2)) with SymPy.diff, then compare against I-9 paper targets.
# w is independent of rho and b. No FTq (5.1) is imported as an identity.
w = s.Symbol('w', positive=True)
gamma = h/(w*s.sqrt(D2))
paper_rho = -l*b/(w*s.sqrt(D2)) - h*(rho-b)/(w*D2**s.Rational(3,2))
paper_b = -l*rho/(w*s.sqrt(D2)) + h*rho/(w*D2**s.Rational(3,2))
# Clear the common w*D2^(3/2) denominator symbolically, not numerically.
# The independent derivative is s.diff(gamma, variable) on the left.
# Use exact rational-power cancellation through SymPy's symbolic power rules.
# powsimp(force=True) is valid here because D2>0 by I-2 on the L1 interior segment.
# The two sides are formed independently before the common denominator is cleared.
def s2_residual(var, paper):
    sympy_derivative = s.diff(gamma, var)
    return s.simplify(s.cancel(s.powsimp((sympy_derivative-paper)*w*D2**s.Rational(3,2), force=True)))
check('S-2-G', [s2_residual(rho,paper_rho), s2_residual(b,paper_b)])
check('S-2-L', [L(s2_residual(rho,paper_rho)), L(s2_residual(b,paper_b))])
# S-3-G / S-3-L: independently build J from the actual SymPy derivatives
# of gamma (S-2), rather than entering the paper factorization as N_J.
# Simplify NJ_comp=w*D2**(3/2)*J; D2>0 by I-2, so exact power
# cancellation is legitimate. Then check, in order: (i) polynomial in b,
# without any surviving sqrt(D2); (ii) equality to I-10 factorization;
# (iii) equality to the verbatim FTq (5.2) quadratic target.
gamma_rho_comp=s.diff(gamma,rho)
gamma_b_comp=s.diff(gamma,b)
J_comp=l*(a2-b**2)*gamma_b_comp-h*gamma_rho_comp
NJ_comp=s.powsimp(s.expand(J_comp*w*D2**s.Rational(3,2)),force=True)
NJ_comp=s.cancel(NJ_comp)
NJ_I10=l*rho*(a2-b**2)*(h-l*D2)+h*(l*b*D2+h*(rho-b))
def polynomial_residual(expr):
    # The b-polynomial conversion must fail closed if radicals survive.
    if expr.has(s.sqrt(D2)) or expr.has(s.Pow(D2,s.Rational(1,2))):
        blocked('S-3-G','uncancelled sqrt(D2)')
    try:
        poly=s.Poly(expr,b)
    except (s.PolynomialError,ValueError,TypeError) as exc:
        blocked('S-3-G',f'nonpolynomial NJ_comp: {exc}')
    if any(term.has(s.Pow(D2,s.Rational(1,2)),s.Pow(D2,s.Rational(-1,2))) for term in poly.all_coeffs()):
        blocked('S-3-G','uncancelled D2 radical')
    return poly
poly=polynomial_residual(NJ_comp)
# Check (i) before (ii)/(iii); the degree test is exact.
# The three residual groups are emitted under ONE S-3-G stdout line.
A2=l**2*rho**3-l**2*rho+l*mu*rho*z
A1=l**4*mu**2-l**3*mu**3*z-2*l**3*mu*z-l**2*mu**2*rho**2+2*l**2*mu**2*z**2-l**2*mu**2+l**2*z**2+l*mu**3*z+l*mu*rho**2*z-l*mu*z**3+l*mu*z-mu**2*z**2
A0=l**4*mu**4*rho-l**4*mu**2*rho-2*l**3*mu**3*rho*z+2*l**3*mu*rho*z-l**2*mu**4*rho+l**2*mu**2*rho**3+l**2*mu**2*rho*z**2+l**2*mu**2*rho-l**2*rho**3-l**2*rho*z**2+l**2*rho+l*mu**3*rho*z-3*l*mu*rho*z+mu**2*rho*z**2
# (iii) Compare computed numerator with the independent FTq transcription.
check('S-3-G',[s.expand(poly.coeff_monomial(b**3)),s.expand(poly.coeff_monomial(b**4)),NJ_comp-NJ_I10,NJ_comp-(A2*b**2+A1*b+A0)])
# Stage L repeats (i)-(iii) without setting r=1.
NJ_L=L(NJ_comp)
poly_L=s.Poly(NJ_L,b)
check('S-3-L',[NJ_L-L(NJ_I10),NJ_L-L(A2*b**2+A1*b+A0),s.expand(poly_L.coeff_monomial(b**3)),s.expand(poly_L.coeff_monomial(b**4))])
# S-4-G / S-4-L: paired squared-numerator identity.
# S-5-G / S-5-L: both c(mu) forms independently transcribed from FTq (7.2).
c1=l*mu**2-z*mu-l*rho**2-l*(l*mu-z)**2
c2=l*(1-l**2)*mu**2-z*(1-2*l**2)*mu-l*(rho**2+z**2)
hp=h0-l*rho*b;hm=h0+l*rho*b
Dp2=D0-2*rho*b;Dm2=D0+2*rho*b
S4=hp**2*Dm2-hm**2*Dp2-4*rho*b*(h0*c1+l**2*rho**2*b**2)
check('S-4-G',[S4]);check('S-4-L',[L(S4)])
check('S-5-G',[c1-c2]);check('S-5-L',[L(c1-c2)])
# D-1: ONLY HERE specialize rho=rho_b, z=lambda*m and reduce
# modulo rho_b**2+m**2-1. Earlier stages never use this relation.
bound={rho:RB,z:l*m}
def reduce_boundary(expr):
    e=s.expand(expr.subs(bound,simultaneous=True))
    return s.rem(e,RB**2+m**2-1,RB)
check('D-1',[reduce_boundary(h-l*(1-rho*b-m*mu)),reduce_boundary(D2-(a2+rho**2+l**2*(mu-m)**2-2*rho*b))])
# D-2: boundary-only N_J=-lambda**2*(m-mu)*Q; Q verbatim FTq (6.2).
Q=b**2*m*RB+b*(l**2*m**2*mu-l**2*m*mu**2-l**2*m+l**2*mu+m**2*mu+m*mu**2-2*mu)+RB*(-l**2*m*mu**2+l**2*m+l**2*mu**3-l**2*mu-m-mu**3+2*mu)
check('D-2',[reduce_boundary(NJ_comp+l**2*(m-mu)*Q)])
# D-3: boundary-only (7.1) numerator and both (7.2) c expressions.
# Both expressions are algebraically the same rationalized formula after substitution.
bound_c=l*(1-l**2)*mu**2-l*m*(1-2*l**2)*mu-l*(RB**2+l**2*m**2)
bound_h0=l*(1-m*mu)
bound_num=4*RB*b*(bound_h0*bound_c+l**2*RB**2*b**2)
check('D-3',[reduce_boundary(4*rho*b*(h0*c1+l**2*rho**2*b**2)-bound_num),reduce_boundary(c1-bound_c),reduce_boundary(c2-bound_c)])
print('O1-CS COMPLETE PASS')
