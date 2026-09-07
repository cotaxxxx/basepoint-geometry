"""実装前に固定された厳密期待値に対する control。

これらの値は閉形式または既存の認証チェーンに由来し、本パッケージの評価器から
生成してはならない（RESEARCH_RULES §5）。
"""
import sys
import unittest
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from basepoint import (ConeVolumeAngleLens, ConstantVolumeEllipsoid,
                       ConstantVolumeSpheroid, Ellipsoid, Functional, Grid,
                       axis_roots, center_index, label_point)
from basepoint.scan import degeneracy_parameter

LENS = ConeVolumeAngleLens()
GRID = Grid(96, 192)   # パッケージ既定

# 実装前に固定された厳密値
SPHERE_Q = 4.0 / 3.0            # 中心 Hessian 主係数（等方）
SPHERE_H4 = -16.0 / 3.0         # 中心4次係数（等方）
A_C = 4.72438340452113340672    # 扁長・赤道退化（Paper 1 の認証区間左端）
A_Z = 0.407958860300946364      # 扁平・軸方向退化（bg-oblate の候補値）


class SphereControls(unittest.TestCase):
    def setUp(self):
        self.F = Functional(Ellipsoid((1, 1, 1)), LENS, GRID)

    def test_measure_is_probability(self):
        """錐体積測度は確率測度: ∫dμ = 1。定数レンズで確認する。"""
        from basepoint.lens import CustomLens
        one = CustomLens(lambda g: np.ones_like(g), lambda d, nu: (d * nu).sum(-1), "one")
        self.assertAlmostEqual(Functional(Ellipsoid((1, 1, 1)), one, GRID).value([0.2, -0.1, 0.3]),
                               1.0, places=12)

    def test_center_energy_vanishes(self):
        """球の中心では動径方向と法線が一致し α ≡ 0。"""
        self.assertAlmostEqual(self.F.value([0, 0, 0]), 0.0, places=12)

    def test_center_coefficients_isotropic(self):
        q = np.asarray(self.F.center_coefficients().value)
        for v in q:
            self.assertAlmostEqual(v, SPHERE_Q, places=10)

    def test_quartic_coefficient_isotropic(self):
        for e in np.eye(3):
            self.assertAlmostEqual(self.F.quartic_coefficient(e).value, SPHERE_H4, places=5)

    def test_labels_at_sphere_center(self):
        lab = label_point(self.F, [0, 0, 0])
        self.assertEqual(lab.dimension, 0)
        self.assertEqual(lab.normal_morse_index, 0)
        self.assertEqual(lab.nullity_normal, 0)


class SimilarityInvariance(unittest.TestCase):
    """命題3.1: E_{sK}(sp) = E_K(p)。体積一定化が正規化の選択にすぎない根拠。"""

    def test_uniform_scaling(self):
        body = Ellipsoid((1.0, 1.3, 2.7))
        p = np.array([0.1, -0.2, 0.5])
        base = Functional(body, LENS, GRID).value(p)
        for s in (0.37, 2.9):
            scaled = Functional(body.scaled(s), LENS, GRID).value(s * p)
            self.assertAlmostEqual(scaled, base, places=10)


class SpheroidFamilyControls(unittest.TestCase):
    """既存チェーンの臨界軸比を再現する（倍精度、包絡ではない）。"""

    def setUp(self):
        self.fam = ConstantVolumeSpheroid()

    def test_prolate_equatorial_degeneracy(self):
        a = degeneracy_parameter(self.fam, LENS, (4.0, 5.5), 0, GRID).value
        self.assertAlmostEqual(a, A_C, places=7)

    def test_oblate_axial_degeneracy(self):
        a = degeneracy_parameter(self.fam, LENS, (0.35, 0.5), 2, GRID).value
        self.assertAlmostEqual(a, A_Z, places=7)

    def test_center_index_across_family(self):
        for a, expected in [(0.30, 1), (0.50, 0), (1.00, 0), (3.50, 0), (6.00, 2)]:
            F = Functional(self.fam.body(a), LENS, GRID)
            self.assertEqual(center_index(F), expected, msg=f"a={a}")


class OrbitLabels(unittest.TestCase):
    def setUp(self):
        self.fam = ConstantVolumeSpheroid()

    def test_equatorial_circle_is_morse_bott(self):
        F = Functional(self.fam.body(3.5), LENS, GRID)
        r = axis_roots(F, 0).value
        self.assertEqual(len(r), 1)
        lab = label_point(F, [r[0], 0, 0])
        self.assertEqual(lab.dimension, 1)
        self.assertEqual(lab.orbit_size, "S^1")
        self.assertEqual(lab.normal_morse_index, 1)
        self.assertEqual(lab.nullity_normal, 0)
        self.assertEqual(lab.nullity_tangential, 1)

    def test_axial_pair_on_oblate(self):
        F = Functional(self.fam.body(0.5), LENS, GRID)
        z = axis_roots(F, 2).value
        self.assertEqual(len(z), 1)
        lab = label_point(F, [0, 0, z[0]])
        self.assertEqual((lab.dimension, lab.orbit_size, lab.normal_morse_index), (0, 2, 1))


class ShapePlaneCoordinates(unittest.TestCase):
    def test_spheroid_axis_maps_to_mirror_line(self):
        tri = ConstantVolumeEllipsoid()
        for a in (0.4, 2.0, 4.72438340452113340672):
            p, q = tri.from_axis_ratio(a)
            self.assertAlmostEqual(p, 0.0, places=12)
            self.assertAlmostEqual(np.hypot(p, q), abs(np.log(a)) * np.sqrt(2 / 3), places=12)

    def test_body_round_trip(self):
        tri = ConstantVolumeEllipsoid()
        for u in [(0.3, -0.5), (-1.1, 0.7)]:
            self.assertTrue(np.allclose(tri.coords(tri.body(u).semiaxes), u))
            self.assertAlmostEqual(np.prod(tri.body(u).semiaxes), 1.0, places=12)


if __name__ == "__main__":
    unittest.main(verbosity=2)


class Diagnostics(unittest.TestCase):
    """数値の信用範囲を、結果自身から確かめる検査。"""

    def test_s3_residual_is_small_where_the_paper_works(self):
        """認証済みの a_c 近傍では、置換対称性の残差が十分小さい。"""
        from basepoint.diagnostics import s3_residual
        fam = ConstantVolumeSpheroid()
        r = s3_residual(LENS, fam.body(A_C).semiaxes, GRID).value
        self.assertLess(r, 1e-7)

    def test_s3_residual_exposes_extreme_axis_ratio(self):
        """極端な軸比では残差が大きく、この格子では構造を読めない。"""
        from basepoint.diagnostics import s3_residual
        fam = ConstantVolumeSpheroid()
        self.assertGreater(s3_residual(LENS, fam.body(25.0).semiaxes, GRID).value, 1e-3)

    def test_converged_value_refuses_when_not_converged(self):
        from basepoint.diagnostics import converged_value
        fam = ConstantVolumeSpheroid()
        q = converged_value(
            lambda g: np.asarray(Functional(fam.body(25.0), LENS, g)
                                 .center_coefficients().value)[2], tol=1e-6)
        self.assertIsNone(q.value)
        self.assertIn("NOT CONVERGED", q.method)


class BisectDoesNotInventRoots(unittest.TestCase):
    def test_no_sign_change_raises(self):
        from basepoint.scan import NoSignChange, bisect
        with self.assertRaises(NoSignChange):
            bisect(lambda x: x * x + 1.0, -1.0, 1.0)

    def test_finds_a_real_root(self):
        from basepoint.scan import bisect
        self.assertAlmostEqual(bisect(lambda x: x * x - 2.0, 0.0, 2.0), np.sqrt(2), places=12)
