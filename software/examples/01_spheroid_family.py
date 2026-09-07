"""例1: 体積一定回転楕円体族（扁平 → 球 → 扁長）の大域停留構造。

Paper 1 / bg-oblate-spheroid が扱う2つの臨界軸比と、両側の非自明軌道、
球を含む静穏帯を、族に沿って一度に取り出す。すべて DIAGNOSTIC_ONLY。
"""
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from basepoint import ConeVolumeAngleLens, ConstantVolumeSpheroid, Functional, Grid
from basepoint.scan import (boundary_entry, branch_positions,
                            center_coefficients_along, degeneracy_parameter)

fam, lens, grid = ConstantVolumeSpheroid(), ConeVolumeAngleLens(), Grid(96, 96)

print("=== 中心主係数と中心モース指数 ===")
res = center_coefficients_along(fam, [0.3, 0.5, 1.0, 2.0, 3.5, 6.0], lens, grid).value
for a, q, i in zip(res["params"], res["Q"], res["center_index"]):
    print(f"  a={a:4.1f}  Q=({q[0]:+.5f}, {q[2]:+.5f})  center index={i}")

print("\n=== 退化点（中心係数の符号反転）===")
az = degeneracy_parameter(fam, lens, (0.35, 0.50), 2, grid)
ac = degeneracy_parameter(fam, lens, (4.00, 5.50), 0, grid)
print(f"  a_z (軸方向, 扁平) = {az.value:.12f}   [{az.derivation.value}]")
print(f"  a_c (赤道方向, 扁長) = {ac.value:.12f} [{ac.derivation.value}]")
print(f"  ln a_z = {np.log(az.value):+.4f},  ln a_c = {np.log(ac.value):+.4f}  （球に対し非対称）")

print("\n=== 境界進入（軌道が境界から生まれるパラメータ）===")
ze = boundary_entry(fam, lens, (0.55, 0.75), 2, grid)
re_ = boundary_entry(fam, lens, (1.90, 2.60), 0, grid)
print(f"  極から:   λ_entry ≈ {ze.value:.6f}  [{ze.derivation.value}] "
      f"slope={ze.provenance['slope']:+.2f}")
print(f"  赤道から: a_entry ≈ {re_.value:.6f}  [{re_.derivation.value}] "
      f"slope={re_.provenance['slope']:+.2f}")

print("\n=== 軌道の位置（1 = 境界）===")
for label, params, axis in [("軸上対 (扁平)", [0.42, 0.50, 0.60], 2),
                            ("赤道円 (扁長)", [2.2, 3.0, 4.0, 4.6], 0)]:
    b = branch_positions(fam, params, axis, lens, grid).value
    cells = "  ".join(f"a={p:.2f}:{r:.4f}" for p, r in zip(b["params"], b["relative"]))
    print(f"  {label}: {cells}")

print(f"\n静穏帯（中心のみ）≈ ({ze.value:.4f}, {re_.value:.4f})  ln 幅 "
      f"{np.log(re_.value) - np.log(ze.value):.3f} — 球 (a=1) を含む")
