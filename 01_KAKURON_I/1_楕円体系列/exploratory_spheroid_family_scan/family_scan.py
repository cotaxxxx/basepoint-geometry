# 回転楕円体族 K_a = {x^2+y^2+z^2/a^2<=1} 全体 (扁平 a<1, 球 a=1, 扁長 a>1) で
# 中心 Hessian の赤道方向係数 Q(a), 軸方向係数 Qz(a) を定義から直接評価する。
from mpmath import mp, mpf, acos, sin, cos, sqrt, diff, findroot, legendre
mp.dps = 30

def Feq(r, th, u, a):
    s=sin(th); c=cos(th); W=a*a*s*s+c*c; ell=s*s+a*a*c*c
    g=a*(1-r*u)/(sqrt(W)*sqrt(ell-2*r*u+r*r)); g=min(g,mpf(1))
    return (1-r*u)*acos(g)**2
def Fz(t, th, a):
    s=sin(th); c=cos(th); W=a*a*s*s+c*c; ell=s*s+a*a*c*c
    w=c/a; v=a*c
    g=a*(1-w*t)/(sqrt(W)*sqrt(ell-2*v*t+t*t)); g=min(g,mpf(1))
    return (1-w*t)*acos(g)**2

def gl(n,A,B):
    xs=[];ws=[]
    for i in range(1,n+1):
        x=mp.cos(mp.pi*(i-mpf(1)/4)/(n+mpf(1)/2))
        for _ in range(60):
            p=legendre(n,x); dp=n*(x*p-legendre(n-1,x))/(x*x-1); dx=p/dp; x-=dx
            if abs(dx)<mpf(10)**(-mp.dps+4): break
        dp=n*(x*legendre(n,x)-legendre(n-1,x))/(x*x-1)
        xs.append((A+B)/2+(B-A)/2*x); ws.append((B-A)/2*2/((1-x*x)*dp*dp))
    return xs,ws
nodes,wts=gl(60,mpf(0),mp.pi/2)

def Q(a):
    a=mpf(a); tot=mpf(0)
    for th,w in zip(nodes,wts):
        s=sin(th)
        f0=diff(lambda r:Feq(r,th,mpf(0),a),0,2); fp=diff(lambda r:Feq(r,th,s,a),0,2); fm=diff(lambda r:Feq(r,th,-s,a),0,2)
        tot+=w*s*(f0+(fp+fm-2*f0)/4)
    return tot
def Qz(a):
    a=mpf(a); return sum(w*sin(th)*diff(lambda t:Fz(t,th,a),0,2) for th,w in zip(nodes,wts))
def Hz4(a):   # 軸方向4次係数 d^4E/dt^4 (0)
    a=mpf(a); return sum(w*sin(th)*diff(lambda t:Fz(t,th,a),0,4) for th,w in zip(nodes,wts))

if __name__=="__main__":
    print("   a       Q(a)        Qz(a)")
    for a in ['0.15','0.2','0.25','0.3','0.4','0.5','0.6','0.7','0.8','0.9','1.0','1.25','1.5','2','3','4','4.5','4.7','4.75','5','6']:
        print(f"{float(a):6.2f}  {mp.nstr(Q(a),8):>12}  {mp.nstr(Qz(a),8):>12}")
