"""形状族 ―― 対象を動かすパラメータ空間。

基点幾何では対象は変形される。族は「どう変形するか」を固定し、パラメータ点から
Body を生成する。相似不変性により体積一定化は正規化の選択にすぎず、族の次元は
半軸比のみで決まる。
"""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from .geometry import Ellipsoid

_SQ2, _SQ6 = np.sqrt(2.0), np.sqrt(6.0)


class ShapeFamily:
    name: str = "family"
    dim: int = 1

    def body(self, u):
        raise NotImplementedError

    def describe(self, u) -> str:
        return f"{self.name}({u})"


@dataclass(frozen=True)
class ConstantVolumeSpheroid(ShapeFamily):
    """体積一定回転楕円体。パラメータは軸比 a = 極半軸/赤道半軸。

    a < 1 扁平、a = 1 球、a > 1 扁長。半軸は (s, s, s·a), s = a^(-1/3)。
    """

    name: str = "constant-volume spheroid"
    dim: int = 1

    def body(self, a) -> Ellipsoid:
        a = float(a)
        if a <= 0:
            raise ValueError("axis ratio must be positive")
        s = a ** (-1.0 / 3.0)
        return Ellipsoid((s, s, s * a))

    def describe(self, a) -> str:
        kind = "oblate" if a < 1 else ("sphere" if a == 1 else "prolate")
        return f"spheroid a={a:.6g} ({kind}), ln a={np.log(a):+.4f}"


@dataclass(frozen=True)
class ConstantVolumeEllipsoid(ShapeFamily):
    """体積一定三軸楕円体。形状平面 {u_i = ln a_i, Σu_i = 0} の座標 (p, q)。

        u1 = p/√2 − q/√6,  u2 = −p/√2 − q/√6,  u3 = 2q/√6

    原点が球。軸の置換 S₃ が (p,q) 平面に二面体群 D₃ として作用し、
    3本の鏡映軸が回転楕円体に対応する。
    """

    name: str = "constant-volume triaxial ellipsoid"
    dim: int = 2

    def body(self, u) -> Ellipsoid:
        p, q = (float(v) for v in u)
        return Ellipsoid(tuple(np.exp(self.log_semiaxes((p, q)))))

    @staticmethod
    def log_semiaxes(u) -> np.ndarray:
        p, q = (float(v) for v in u)
        return np.array([p / _SQ2 - q / _SQ6, -p / _SQ2 - q / _SQ6, 2 * q / _SQ6])

    @staticmethod
    def coords(semiaxes) -> tuple:
        """半軸 → (p, q)。体積は自動的に正規化される。"""
        u = np.log(np.asarray(semiaxes, dtype=float))
        u = u - u.mean()
        return float((u[0] - u[1]) / _SQ2), float(u[2] * _SQ6 / 2)

    @staticmethod
    def from_axis_ratio(a: float) -> tuple:
        """回転楕円体（軸比 a、対称軸 z）の形状平面上の座標。"""
        return 0.0, float(2.0 / 3.0 * np.log(a) * _SQ6 / 2)

    def describe(self, u) -> str:
        p, q = u
        a = np.exp(self.log_semiaxes(u))
        return (f"(p,q)=({p:+.4f},{q:+.4f})  semiaxes="
                f"({a[0]:.4f},{a[1]:.4f},{a[2]:.4f})  r={np.hypot(p,q):.4f}")
