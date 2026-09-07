"""例2: 体積一定三軸楕円体の形状平面における中心分岐集合。

原点（球）から各方位へ射線を延ばし、最初に Q_i = 0 となる半径を求める。
index 0 領域（中心が局所極小）の境界が極座標で得られる。
"""
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from basepoint import (ConeVolumeAngleLens, ConstantVolumeEllipsoid, Functional,
                       Grid)
from basepoint.scan import bisect

fam, lens, grid = ConstantVolumeEllipsoid(), ConeVolumeAngleLens(), Grid(64, 64)


def min_coefficient(r, angle):
    u = (r * np.cos(angle), r * np.sin(angle))
    return float(np.min(Functional(fam.body(u), lens, grid).center_coefficients().value))


print("方位ごとの index 0 領域の境界半径（r = |ln 軸比|·√(2/3)）")
print("  角度   境界半径 r   種類")
radii = {}
for deg in range(0, 360, 15):
    ang = np.deg2rad(deg)
    r = bisect(lambda rr: min_coefficient(rr, ang), 0.15, 2.0)
    radii[deg] = r
    kind = ""
    if deg in (90, 210, 330):
        kind = "← 鏡映軸・扁長（頂点）"
    elif deg in (30, 150, 270):
        kind = "← 鏡映軸・扁平（辺の中点）"
    print(f"  {deg:3d}°   {r:.5f}    {kind}")

v = np.mean([radii[d] for d in (90, 210, 330)])
e = np.mean([radii[d] for d in (30, 150, 270)])
print(f"\n頂点 r = {v:.4f}（3方位の一致 {np.ptp([radii[d] for d in (90,210,330)]):.1e}）"
      f"  → 軸比 {np.exp(1.5 * v * 2 / np.sqrt(6)):.4f}")
print(f"辺中点 r = {e:.4f}（一致 {np.ptp([radii[d] for d in (30,150,270)]):.1e}）"
      f"  → 軸比 {np.exp(-1.5 * e * 2 / np.sqrt(6)):.4f}")
print(f"直線三角形なら辺中点は頂点の半分 {v/2:.4f} のはず → 実際は {e:.4f}、"
      f"外側へ {100*(e/(v/2)-1):.1f}% 膨らむ")
