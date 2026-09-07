"""対象（曲面）。基点幾何では対象は変形されるので、族から生成される。

Body が提供するのは、求積格子上の
  * 境界点 x(θ, φ)
  * 外向き法線の非正規化ベクトル n（|n| は面積要素に吸収される）
  * 面積ヤコビアン |r_θ × r_φ|
のみ。これだけで任意のレンズが評価できる。
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence

import numpy as np

from .quadrature import Grid


class Body:
    """曲面のパラメータ表示。サブクラスは surface() を実装する。"""

    name: str = "body"

    def surface(self, grid: Grid):
        """(X, N, J) を返す。X: 点, N: 非正規化外向き法線, J: 面積ヤコビアン。"""
        raise NotImplementedError

    def symmetry(self) -> str:
        return "unknown"

    def contains(self, p) -> bool:
        raise NotImplementedError


@dataclass(frozen=True)
class Ellipsoid(Body):
    """{ Σ x_i²/a_i² ≤ 1 }。a は半軸。"""

    semiaxes: tuple

    def __post_init__(self):
        a = tuple(float(v) for v in self.semiaxes)
        if len(a) != 3 or min(a) <= 0:
            raise ValueError("semiaxes must be three positive numbers")
        object.__setattr__(self, "semiaxes", a)

    @property
    def name(self) -> str:
        a1, a2, a3 = self.semiaxes
        return f"Ellipsoid({a1:.6g}, {a2:.6g}, {a3:.6g})"

    @property
    def volume(self) -> float:
        a1, a2, a3 = self.semiaxes
        return 4.0 * np.pi * a1 * a2 * a3 / 3.0

    def surface(self, grid: Grid):
        TH, PH, _ = grid.nodes
        a1, a2, a3 = self.semiaxes
        S, C = np.sin(TH), np.cos(TH)
        CP, SP = np.cos(PH), np.sin(PH)
        X = np.stack([a1 * S * CP, a2 * S * SP, a3 * C], axis=-1)
        N = np.stack([X[..., 0] / a1**2, X[..., 1] / a2**2, X[..., 2] / a3**2], axis=-1)
        # |r_th x r_ph| = a1 a2 a3 sin(th) |N|   （厳密な恒等式）
        J = a1 * a2 * a3 * S * np.sqrt((N * N).sum(-1))
        return X, N, J

    def symmetry(self) -> str:
        a1, a2, a3 = self.semiaxes
        eq = [abs(a1 - a2) < 1e-12, abs(a2 - a3) < 1e-12, abs(a1 - a3) < 1e-12]
        if all(eq):
            return "O(3)"
        if any(eq):
            return "D_inf_h"
        return "D_2h"

    def contains(self, p) -> bool:
        p = np.asarray(p, dtype=float)
        a = np.asarray(self.semiaxes, dtype=float)
        return float(((p / a) ** 2).sum()) < 1.0

    def scaled(self, s: float) -> "Ellipsoid":
        return Ellipsoid(tuple(s * v for v in self.semiaxes))
