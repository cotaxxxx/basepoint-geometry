"""汎関数の評価と、基点についての微分。

微分はすべて中心差分（DIAGNOSTIC_ONLY）。厳密包絡はこのパッケージの役割ではない。
"""
from __future__ import annotations

import warnings

import numpy as np

from .evidence import Derivation, Evidence, Quantity
from .geometry import Body
from .lens import Lens
from .quadrature import Grid

# 中心差分ステンシル: order -> (offsets, coefficients, h の冪)
# _ACCURACY[order] は打ち切り誤差の次数。Richardson の倍率は 2**accuracy。
_ACCURACY = {1: 2, 2: 4, 3: 2, 4: 2}
_STENCIL = {
    1: ((-1, 1), (-0.5, 0.5), 1),
    2: ((-2, -1, 0, 1, 2), (-1 / 12, 4 / 3, -5 / 2, 4 / 3, -1 / 12), 2),
    3: ((-2, -1, 1, 2), (0.5, -1.0, 1.0, -0.5), 3),
    4: ((-2, -1, 0, 1, 2), (1.0, -4.0, 6.0, -4.0, 1.0), 4),
}


class Functional:
    """固定した (対象, レンズ) の組に対する基点汎関数 E(p)。"""

    def __init__(self, body: Body, lens: Lens, grid: Grid | None = None):
        self.body = body
        self.lens = lens
        self.grid = grid or Grid()
        X, N, J = body.surface(self.grid)
        self._X = X
        self._N = N
        self._nu = N / np.sqrt((N * N).sum(-1))[..., None]
        _, _, W = self.grid.nodes
        self._WJ = W * J

    # ---- 評価 -------------------------------------------------------------
    def value(self, p) -> float:
        p = np.asarray(p, dtype=float)
        d = self._X - p
        dn = (d * self._nu).sum(-1)
        dl = np.sqrt((d * d).sum(-1))
        gamma = np.clip(dn / dl, -1.0, 1.0)
        w = self.lens.weight(d, self._nu) * self._WJ
        return float((self.lens.h(gamma) * w).sum() / w.sum())

    __call__ = value

    # ---- 微分 -------------------------------------------------------------
    def derivative_along(self, p, direction, order: int = 2, step: float = 1e-2,
                         richardson: bool = False) -> float:
        """p において direction 方向の order 階方向微分。

        richardson=True なら step と step/2 の2回評価から打ち切り誤差の主項を消す。
        """
        if order not in _STENCIL:
            raise ValueError(f"order must be one of {sorted(_STENCIL)}")
        p = np.asarray(p, dtype=float)
        e = np.asarray(direction, dtype=float)
        e = e / np.linalg.norm(e)
        offs, coeffs, power = _STENCIL[order]

        def raw(h):
            total = sum(c * self.value(p + k * h * e) for k, c in zip(offs, coeffs))
            return float(total / h**power)

        if not richardson:
            return raw(step)
        f = 2.0 ** _ACCURACY[order]
        return (f * raw(step / 2) - raw(step)) / (f - 1.0)

    def grad(self, p, step: float = 1e-4) -> np.ndarray:
        p = np.asarray(p, dtype=float)
        g = np.empty(3)
        for i in range(3):
            e = np.zeros(3)
            e[i] = 1.0
            g[i] = (self.value(p + step * e) - self.value(p - step * e)) / (2 * step)
        return g

    def hessian(self, p, step: float = 1e-3) -> np.ndarray:
        p = np.asarray(p, dtype=float)
        H = np.empty((3, 3))
        f0 = self.value(p)
        for i in range(3):
            e = np.zeros(3)
            e[i] = 1.0
            H[i, i] = (self.value(p + step * e) - 2 * f0 + self.value(p - step * e)) / step**2
        for i in range(3):
            for j in range(i + 1, 3):
                ei, ej = np.zeros(3), np.zeros(3)
                ei[i] = ej[j] = 1.0
                v = (self.value(p + step * ei + step * ej)
                     - self.value(p + step * ei - step * ej)
                     - self.value(p - step * ei + step * ej)
                     + self.value(p - step * ei - step * ej)) / (4 * step**2)
                H[i, j] = H[j, i] = v
        return H

    # ---- 中心の主係数 -----------------------------------------------------
    def center_coefficients(self, step: float = 2e-2, richardson: bool = True) -> Quantity:
        """中心 Hessian の3主係数 Q_i（座標軸方向の2階方向微分）。"""
        if not getattr(self.lens, "smooth_at_normal_incidence", True):
            warnings.warn(
                f"lens {self.lens.name!r} は γ=1 で解析的でない。中心係数は"
                " 発散し、刻み幅と格子に依存する値になる。", RuntimeWarning, stacklevel=2)
        q = [self.derivative_along(np.zeros(3), np.eye(3)[i], order=2, step=step,
                                   richardson=richardson) for i in range(3)]
        return Quantity(
            np.array(q),
            Derivation.FLOAT,
            Evidence.DIAGNOSTIC_ONLY,
            method=(f"5-point 2nd derivative, step={step}"
                    f"{', Richardson' if richardson else ''}, {self.grid.describe()}"),
            provenance={"body": self.body.name, "lens": self.lens.name},
        )

    def quartic_coefficient(self, direction, step: float = 5e-2,
                            richardson: bool = True) -> Quantity:
        """指定方向の中心4次係数（E = E0 + Q r²/2 + H4 r⁴/24 の H4）。"""
        v = self.derivative_along(np.zeros(3), direction, order=4, step=step,
                                  richardson=richardson)
        return Quantity(
            v, Derivation.FLOAT, Evidence.DIAGNOSTIC_ONLY,
            method=(f"5-point 4th derivative, step={step}"
                    f"{', Richardson' if richardson else ''}, {self.grid.describe()}"),
            provenance={"body": self.body.name, "lens": self.lens.name},
        )
