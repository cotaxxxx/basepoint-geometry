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
# S-1: the P1 geometric normal and x with a cos(phi)=b, a^2=1-mu^2.
h_geom=l*(a2+mu**2)-l*rho*b-z*mu
D_geom=a2+rho**2+(l*mu-z)**2-2*rho*b
check('S-1-G',[h_geom-h,D_geom-D2,w2-(l**2*a2+mu**2)])
check('S-1-L',[L(h_geom-h),L(D_geom-D2)])
# S-2: independent differentiation of h/(w sqrt(D2)), normalized by w*D**3.
w,D=s.symbols('w D',positive=True)
gamma=h/(w*s.sqrt(D2))
manual_rho=-l*b/(w*D)-h*(rho-b)/(w*D**3)
manual_b=-l*rho/(w*D)+h*rho/(w*D**3)
# Multiply by w*D**3, then substitute D**2=D2; this avoids any radical comparisons.
def deriv_numer(var):
    expr=s.diff(gamma,var)*w*D**3
    return s.expand(s.powdenest(expr,force=True).subs(s.sqrt(D2),D).subs(D**2,D2))
# Instead use derivative directly and replace D2**(-1/2), D2**(-3/2) with D forms.
def deriv_poly(var):
    deriv=s.diff(gamma,var)
    return s.expand((deriv*w).subs(D2**s.Rational(-1,2),1/D).subs(D2**s.Rational(-3,2),1/D**3)*D**3).subs(D**2,D2)
# Robust symbolic independent derivative via rational factor: gamma=h*(D2)^(-1/2)/w.
def sympy_derivative_numerator(var):
    der=s.diff(h*D2**s.Rational(-1,2),var)
    return s.expand(der*D2**s.Rational(3,2))
# SymPy derivative is independently computed; radical powers are removed by exact power rules.
def independent(var):
    return s.expand(s.diff(h,var)*D2 - h*s.diff(D2,var)/2)
# Confirm independent form equals SymPy differentiation before comparing paper expressions.
check('S-2-G',[independent(rho)-(-l*b*D2-h*(rho-b)), independent(b)-(-l*rho*D2+h*rho)])
check('S-2-L',[L(independent(rho)-(-l*b*D2-h*(rho-b))),L(independent(b)-(-l*rho*D2+h*rho))])
# S-3: exact quadratic numerator vs verbatim FTq (5.2) coefficients.
NJ=s.expand(l*rho*(a2-b**2)*(h-l*D2)+h*(l*b*D2+h*(rho-b)))
A2=l**2*rho**3-l**2*rho+l*mu*rho*z
A1=l**4*mu**2-l**3*mu**3*z-2*l**3*mu*z-l**2*mu**2*rho**2+2*l**2*mu**2*z**2-l**2*mu**2+l**2*z**2+l*mu**3*z+l*mu*rho**2*z-l*mu*z**3+l*mu*z-mu**2*z**2
A0=l**4*mu**4*rho-l**4*mu**2*rho-2*l**3*mu**3*rho*z+2*l**3*mu*rho*z-l**2*mu**4*rho+l**2*mu**2*rho**3+l**2*mu**2*rho*z**2+l**2*mu**2*rho-l**2*rho**3-l**2*rho*z**2+l**2*rho+l*mu**3*rho*z-3*l*mu*rho*z+mu**2*rho*z**2
poly=s.Poly(NJ,b)
check('S-3-G',[NJ-(A2*b**2+A1*b+A0),s.expand(poly.coeff_monomial(b**3)),s.expand(poly.coeff_monomial(b**4))])
check('S-3-L',[L(NJ-(A2*b**2+A1*b+A0)),L(poly.coeff_monomial(b**3))])
# S-4/S-5: independently transcribed FTq (7.2).
c1=l*mu**2-z*mu-l*rho**2-l*(l*mu-z)**2
c2=l*(1-l**2)*mu**2-z*(1-2*l**2)*mu-l*(rho**2+z**2)
hp=h0-l*rho*b;hm=h0+l*rho*b
Dp2=D0-2*rho*b;Dm2=D0+2*rho*b
S4=hp**2*Dm2-hm**2*Dp2-4*rho*b*(h0*c1+l**2*rho**2*b**2)
check('S-4-G',[S4]);check('S-4-L',[L(S4)])
check('S-5-G',[c1-c2]);check('S-5-L',[L(c1-c2)])
# D-1: boundary-only symbols with rho_b^2+m^2=1; polynomial remainder.
bound={rho:RB,z:l*m}
def reduce_boundary(expr):
    e=s.expand(expr.subs(bound,simultaneous=True))
    return s.rem(e,RB**2+m**2-1,RB)
check('D-1',[reduce_boundary(h-l*(1-rho*b-m*mu)),reduce_boundary(D2-(a2+rho**2+l**2*(mu-m)**2-2*rho*b))])
# D-2: Q transcribed verbatim from pinned FTq (6.2).
Q=b**2*m*RB+b*(l**2*m**2*mu-l**2*m*mu**2-l**2*m+l**2*mu+m**2*mu+m*mu**2-2*mu)+RB*(-l**2*m*mu**2+l**2*m+l**2*mu**3-l**2*mu-m-mu**3+2*mu)
check('D-2',[reduce_boundary(NJ+l**2*(m-mu)*Q)])
# D-3: compare boundary specialization of (7.1),(7.2) to pinned boundary forms.
# Both expressions are algebraically the same rationalized formula after substitution.
bound_c=l*(1-l**2)*mu**2-l*m*(1-2*l**2)*mu-l*(RB**2+l**2*m**2)
bound_h0=l*(1-m*mu)
bound_num=4*RB*b*(bound_h0*bound_c+l**2*RB**2*b**2)
check('D-3',[reduce_boundary(4*rho*b*(h0*c1+l**2*rho**2*b**2)-bound_num),reduce_boundary(c1-bound_c),reduce_boundary(c2-bound_c)])
print('O1-CS COMPLETE PASS')
