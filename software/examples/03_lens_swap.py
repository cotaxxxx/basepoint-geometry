"""例3: レンズを替えると指紋はどう変わるか。

対象の族を固定し、汎関数（レンズ）だけを差し替える。基点幾何の中心的な実験。

重要: 極端な軸比では求積誤差が構造を偽装する。ここでは軸の置換 S₃ による
残差を精度の代理として先に測り、信用できる範囲の中でのみ退化点を報告する。
"""
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from basepoint import (AreaAngleLens, ConeVolumeAngleLens, ConstantVolumeSpheroid,
                       Ellipsoid, Functional, Grid)
from basepoint.diagnostics import s3_residual
from basepoint.scan import NoSignChange, degeneracy_parameter

fam, grid = ConstantVolumeSpheroid(), Grid(96, 96)
LENSES = [ConeVolumeAngleLens(2), ConeVolumeAngleLens(4),
          AreaAngleLens(2), AreaAngleLens(4)]

print("=== まず精度を測る: S₃ 対称性残差（Grid 96x96）===")
print(f"{'軸比':>7s}" + "".join(f"{l.name.split()[0][:12]:>14s}" for l in LENSES))
for a in (2.0, 4.72, 8.0, 12.0, 25.0):
    s = fam.body(a).semiaxes
    print(f"{a:7.2f}" + "".join(f"{s3_residual(l, s).value:14.1e}" for l in LENSES))
TRUST = 8.0
print(f"→ 残差が 1e-4 を超えない軸比 ≲ {TRUST:.0f} を信用範囲とする。"
      f" 以下の探索はこの範囲に限る。")

print("\n=== 信用範囲内での退化点 ===")
print(f"{'レンズ':46s} {'Q(球)':>9s} {'a_z (扁平)':>12s} {'a_c (扁長)':>12s} {'比':>7s}")
print("-" * 92)
for lens in LENSES:
    qs = float(np.asarray(
        Functional(Ellipsoid((1, 1, 1)), lens, grid).center_coefficients().value)[0])
    out = {}
    for key, comp, br in [("a_z", 2, (1 / TRUST, 0.999)), ("a_c", 0, (1.001, TRUST))]:
        try:
            out[key] = degeneracy_parameter(fam, lens, br, comp, grid).value
        except NoSignChange:
            out[key] = None
    ratio = (f"{abs(np.log(out['a_c'])) / abs(np.log(out['a_z'])):7.2f}"
             if out["a_z"] and out["a_c"] else "      -")
    fmt = lambda v: f"{v:12.6f}" if v else f"{'なし':>12s}"
    print(f"{lens.name:46s} {qs:9.5f} {fmt(out['a_z'])} {fmt(out['a_c'])} {ratio}")

print("\n『なし』は信用範囲内に退化点が存在しないという意味であり、")
print("より極端な軸比に存在しないことの証明ではない（RESEARCH_RULES §7）。")
print("比 = |ln a_c| / |ln a_z|。錐体積レンズ^2 の 1.73 は、扁長側の退化が")
print("扁平側より球から遠いこと ―― 形状平面の三角形が扁長側に頂点を向ける理由。")
print()
print("注意: 冪 4 では球そのものが退化する（球の中心では α = O(|p|) ゆえ")
print("h = arccos⁴ = O(|p|⁴)、したがって Q(球) = 0 が厳密）。この場合の指紋は")
print("4次項が支配し、冪 2 の絵とは質的に異なる。表の a_z, a_c をそのまま")
print("冪 2 の三角形と比較してはならない。")
