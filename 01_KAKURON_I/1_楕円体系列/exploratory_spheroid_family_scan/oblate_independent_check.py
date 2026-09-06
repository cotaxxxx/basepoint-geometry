#!/usr/bin/env python3
"""bg-oblate-spheroid の候補値に対する第三者独立再計算（DIAGNOSTIC_ONLY / NOT_BINDING）

リポジトリのコード・級数・チャートを一切使わず、E_K(p) の定義から直接評価する。
  * family_scan.py（θ パラメータ、Gauss-Legendre、mpmath.diff）で中心係数 Qz, Hz4, Q
  * 本ファイル（μ パラメータ、tanh-sinh）で軸上勾配 g_axis_ob(t,λ)=∂_t E_λ(t)
正規化: p=(0,0,λt), t∈[-1,1];  H_axis_ob = λ²·Qz,  c3_ob = Hz4·λ⁴/6.
実行: python3 oblate_independent_check.py   （要 mpmath; family_scan.py と同ディレクトリ）
"""
from mpmath import mp, mpf, acos, sqrt, quad, diff, findroot, pi
import family_scan as F

mp.dps = 30

def g_axis(t, lam):
    lam = mpf(lam); t = mpf(t)
    def dF(mu):
        def Fm(tt):
            q = 1 - mu*mu + lam*lam*(mu - tt)**2
            w = sqrt(lam*lam*(1 - mu*mu) + mu*mu)
            g = lam*(1 - tt*mu)/(w*sqrt(q)); g = min(g, mpf(1))
            return (1 - tt*mu)*acos(g)**2
        return diff(Fm, t, 1)
    return quad(dF, [-1, 0, mpf('0.9'), 1 - mpf('1e-6'), 1])/2

def b_ob(lam):            # 極端点値 g_axis_ob(1, λ)
    return g_axis(mpf(1), lam)

if __name__ == "__main__":
    print("[球の厳密期待値]  b_ob(1) =", mp.nstr(b_ob(1), 20), "  π²/32 =", mp.nstr(pi**2/32, 20))
    print("[端点符号]  b_ob(0.60) =", mp.nstr(b_ob('0.60'), 8), "  b_ob(0.70) =", mp.nstr(b_ob('0.70'), 8))
    lam_e = findroot(b_ob, (mpf('0.60'), mpf('0.70')), solver='bisect', tol=mpf(10)**-22)
    print("[境界進入]  λ_entry_ob =", mp.nstr(lam_e, 22))
    h = mpf('1e-10')
    bp = (b_ob(lam_e+h) - b_ob(lam_e-h))/(2*h)
    gt = (g_axis(1-h, lam_e) - g_axis(1-2*h, lam_e))/h
    print("            b_ob' =", mp.nstr(bp, 8), "  ∂_t g(1⁻) =", mp.nstr(gt, 8), "  C_ob = b'/(-g_t) =", mp.nstr(bp/(-gt), 8))
    print("[census 下端]  g_axis_ob(63/64, 5/8) =", mp.nstr(g_axis(mpf(63)/64, mpf(5)/8), 10))
    az = findroot(lambda a: F.Qz(a), (mpf('0.40'), mpf('0.42')), solver='bisect', tol=mpf(10)**-26)
    print("[中心軸]  λ_axis_ob =", mp.nstr(az, 24))
    for lam in ('0.4', '0.415'):
        print(f"          H_axis_ob({lam}) = λ²Qz =", mp.nstr(mpf(lam)**2*F.Qz(lam), 8),
              "   c3_ob =", mp.nstr(F.Hz4(lam)*mpf(lam)**4/6, 8))
    print("          c3_ob(1) = Hz4(1)/6 =", mp.nstr(F.Hz4(mpf(1))/6, 12), "  (期待 -8/9)")
    hh = mpf('1e-8')
    Ap = az**2*(F.Qz(az+hh) - F.Qz(az-hh))/(2*hh); C = F.Hz4(az)*az**4/6
    print("[正規形]  A'_ob =", mp.nstr(Ap, 10), "  C_ob =", mp.nstr(C, 10), "  -A'/C =", mp.nstr(-Ap/C, 10))
    print("[横方向]  Q_perp_ob(center, λ_axis) =", mp.nstr(F.Q(az), 12))
