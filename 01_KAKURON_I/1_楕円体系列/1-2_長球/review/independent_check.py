# 独立再検証スクリプト（査読用・第三者実装）
# 論文の付録B/Cの式を一切使わず、E_K(p) の定義から直接 Q, Q', H4, Qz を数値評価する。
# 実行: python3 independent_check.py   （要 mpmath）

from mpmath import mp, mpf, acos, sin, cos, sqrt, diff, matrix
mp.dps = 45

# K_a = {x^2+y^2+z^2/a^2 <= 1}. Surface: (s cphi, s sphi, a c), s=sin th, c=cos th
# n_vec = (a s cphi, a s sphi, c),  |r_th x r_phi| = s*sqrt(W), W=a^2 s^2 + c^2
# integrand of E: h(gamma) * (d . n_vec)/(4 pi a) * s   ... with 3Vol = 4 pi a
# equatorial basepoint p=(r,0,0):  d.n_vec = a(1-r u), u = s cphi
#   |d|^2 = ell - 2 r u + r^2,  ell = s^2 + a^2 c^2
#   gamma = a(1-ru)/(sqrt(W)*|d|)

def Feq(r, th, u, a):
    s = sin(th); c = cos(th)
    W = a*a*s*s + c*c
    ell = s*s + a*a*c*c
    d2 = ell - 2*r*u + r*r
    g = a*(1 - r*u)/(sqrt(W)*sqrt(d2))
    if g > 1: g = mpf(1)
    return (1 - r*u)*acos(g)**2

def Fz(t, th, a):
    s = sin(th); c = cos(th)
    W = a*a*s*s + c*c
    ell = s*s + a*a*c*c
    w = c/a; v = a*c
    d2 = ell - 2*v*t + t*t
    g = a*(1 - w*t)/(sqrt(W)*sqrt(d2))
    if g > 1: g = mpf(1)
    return (1 - w*t)*acos(g)**2

def gauss_legendre(n, A, B):
    # nodes/weights on [A,B] via mpmath polyroots-free Newton on Legendre
    from mpmath import legendre, mpf, pi as PI
    xs = []; ws = []
    for i in range(1, n+1):
        x = mp.cos(mp.pi*(i - mpf(1)/4)/(n + mpf(1)/2))
        for _ in range(100):
            p = legendre(n, x); dp = n*(x*legendre(n,x) - legendre(n-1,x))/(x*x-1)
            dx = p/dp; x -= dx
            if abs(dx) < mp.mpf(10)**(-mp.dps+5): break
        dp = n*(x*legendre(n,x) - legendre(n-1,x))/(x*x-1)
        xs.append(x); ws.append(2/((1-x*x)*dp*dp))
    # map to [A,B]
    return [ (A+B)/2 + (B-A)/2*x for x in xs ], [ (B-A)/2*w for w in ws ]

N = 70
nodes, wts = gauss_legendre(N, mpf(0), mp.pi/2)

def Q_of(a):
    a = mpf(a); tot = mpf(0)
    for th, wt in zip(nodes, wts):
        s = sin(th)
        # F''(0) is quadratic in u -> phi-average = c0 + (F(u=s)+F(u=-s)-2c0)/4
        f0 = diff(lambda r: Feq(r, th, mpf(0), a), mpf(0), 2)
        fp = diff(lambda r: Feq(r, th,  s, a), mpf(0), 2)
        fm = diff(lambda r: Feq(r, th, -s, a), mpf(0), 2)
        avg = f0 + (fp + fm - 2*f0)/4
        tot += wt*s*avg
    return tot

def Qz_of(a):
    a = mpf(a); tot = mpf(0)
    for th, wt in zip(nodes, wts):
        s = sin(th)
        tot += wt*s*diff(lambda t: Fz(t, th, a), mpf(0), 2)
    return tot

print("Q(1)      =", Q_of(1), "  (expected 4/3 =", mpf(4)/3, ")")
for a in ['4.72438','4.72439']:
    print("Q(%s) = %s" % (a, mp.nstr(Q_of(a), 18)))
for a in ['4.70','4.71','4.72','4.73','4.74','4.75']:
    print("Qz(%s) = %s" % (a, mp.nstr(Qz_of(a), 18)))

# ---- a_c, Q'(a_c), H4(a_c) ----
def Q4_of(a):   # H4 = d^4 E/dr^4 at 0 ; phi-average by periodic trapezoid (exact, deg<=4)
    a = mpf(a); M = 16; tot = mpf(0)
    phis = [2*mp.pi*k/M for k in range(M)]
    for th, wt in zip(nodes, wts):
        s = sin(th); acc = mpf(0)
        for ph in phis:
            u = s*cos(ph)
            acc += diff(lambda r: Feq(r, th, u, a), mpf(0), 4)
        tot += wt*s*acc/M
    return tot

ac = mp.findroot(lambda a: Q_of(a), mpf('4.724383'))
print("a_c        =", mp.nstr(ac, 22))
print("paper a_c  = 4.7243834045211334067")
h = mpf('1e-12')
print("Q'(a_c)    =", mp.nstr((Q_of(ac+h)-Q_of(ac-h))/(2*h), 12))
print("H4(a_c)    =", mp.nstr(Q4_of(ac), 12))
print("H4(4.70)   =", mp.nstr(Q4_of(mpf('4.70')), 12))
print("H4(4.75)   =", mp.nstr(Q4_of(mpf('4.75')), 12))
print("Qz(a_c)    =", mp.nstr(Qz_of(ac), 12))
