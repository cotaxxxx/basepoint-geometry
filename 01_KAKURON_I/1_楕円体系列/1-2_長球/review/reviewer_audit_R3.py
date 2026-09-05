#!/usr/bin/env python3
"""査読者による補助記号監査（第3回査読・R3）

著者の3本の記号監査が検査していない2点を独立に検証する。

 (1) h1..h4 の 0F1 表示。h(x)=arccos(x)^2 の1〜4階導関数が、Arb 実装
     prolate_cap_arb_certificate.h_derivatives_from_t が実際に評価する
     0F1 表示（付録B.1）と厳密に一致するか。著者の B2/H4/Qz 監査は
     いずれも h1..h4 を自由記号として扱うため、このリンクは未監査である。

 (2) 軸方向核の切断なし監査。prolate_Qz_symbolic_audit.py は
     h の2次ジェット h0 + h1*delta + h2*delta^2/2 を代入してから微分する。
     Fz''(0) にはこの切断は影響しないが、付録Cの記述「生の重み付き核を
     独立に二階微分」とは異なる。ここでは B2 監査と同じ抽象関数 h を用いて
     切断なしで検証する。

実行: python3 reviewer_audit_R3.py   （要 sympy）
"""
import sympy as sp

ok = True

# ---------- (1) h1..h4 の 0F1 表示 ----------
print("[1] h(x)=arccos(x)^2 の導関数 vs 付録B.1 の 0F1 表示")
x, b = sp.symbols('x b', positive=True)
h = sp.acos(x)**2
dsub = []
for k in range(1, 5):
    e = sp.diff(h, x, k).subs(x, sp.cos(b)).rewrite(sp.sin)
    e = sp.simplify(sp.trigsimp(e.subs(sp.acos(sp.cos(b)), b)))
    dsub.append(e)

z = b**2
F = lambda nu: sp.hyperexpand(sp.hyper((), (nu,), -z/4))
S, T, U, V = (F(sp.Rational(3, 2)), F(sp.Rational(5, 2)),
              F(sp.Rational(7, 2)), F(sp.Rational(9, 2)))
claimed = [
    -2/S,
    2*T/(3*S**3),
    2*U/(15*S**4) - 2*T**2/(3*S**5),
    2*V/(105*S**5) - 4*U*T/(9*S**6) + sp.Rational(10, 9)*T**3/S**7,
]
for k in range(4):
    e = sp.simplify(dsub[k] - claimed[k])
    # beta in (0,pi): |sin b| = sin b, acos(cos b) = b
    e = e.replace(sp.Abs(sp.sin(b)), sp.sin(b)).replace(sp.acos(sp.cos(b)), b)
    d = sp.simplify(sp.trigsimp(sp.expand_trig(e)))
    ok &= (d == 0)
    print("    h%d: 差 = %s" % (k + 1, d))

# ---------- (2) 軸方向核（切断なし・抽象 h） ----------
print("[2] 生の軸方向核 Fz''(0) vs 付録C 式(5)（ジェット切断なし）")
t = sp.symbols('t', real=True)
C, ell, v, w = sp.symbols('C ell v w', positive=True)
hf = sp.Function('h')
h1s, h2s = sp.symbols('h1 h2')
A = 1 - w*t
B = 1 - 2*v*t/ell + t**2/ell
g = C*A*B**sp.Rational(-1, 2)
raw = sp.diff(A*hf(g), t, 2).subs(t, 0)
xi = sp.Symbol('_xi_1')
raw = raw.xreplace({
    sp.Subs(sp.Derivative(hf(xi), xi), xi, C): h1s,
    sp.Subs(sp.Derivative(hf(xi), (xi, 2)), xi, C): h2s,
    sp.Derivative(hf(C), C): h1s,
    sp.Derivative(hf(C), (C, 2)): h2s,
})
assert not raw.atoms(sp.Derivative, sp.Subs), "未置換の導関数が残存"
expected = (C**2*h2s*(v/ell - w)**2
            + C*h1s*(-1/ell + 3*v**2/ell**2 - 4*w*v/ell + 2*w**2))
d = sp.simplify(sp.expand(sp.simplify(raw) - expected))
ok &= (d == 0)
print("    差 =", d)

print()
print("PASS: 未監査リンクは2点とも厳密に正しい" if ok else "FAIL")
raise SystemExit(0 if ok else 1)
