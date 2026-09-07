"""球面パラメータ (θ, φ) 上の求積格子。

θ: [0, π] の Gauss–Legendre（端点特異性を避ける）
φ: 一様分点の周期台形則（周期解析関数に対し指数収束）
"""
from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache

import numpy as np


@dataclass(frozen=True)
class Grid:
    n_theta: int = 96
    n_phi: int = 192

    @property
    def nodes(self):
        return _build(self.n_theta, self.n_phi)

    def describe(self) -> str:
        return f"Gauss-Legendre({self.n_theta}) x periodic-trapezoid({self.n_phi})"


@lru_cache(maxsize=32)
def _build(n_theta: int, n_phi: int):
    x, w = np.polynomial.legendre.leggauss(n_theta)
    th = (x + 1.0) * np.pi / 2.0
    wth = w * np.pi / 2.0
    ph = np.arange(n_phi) * 2.0 * np.pi / n_phi
    wph = 2.0 * np.pi / n_phi
    TH, PH = np.meshgrid(th, ph, indexing="ij")
    W = wth[:, None] * np.full(n_phi, wph)
    return TH, PH, W
