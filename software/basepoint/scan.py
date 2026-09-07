"""族に沿った走査 ―― 指紋が変形でどう変わるかを見る層。"""
from __future__ import annotations

import numpy as np

from .evidence import Derivation, Evidence, Quantity
from .functional import Functional
from .lens import Lens
from .quadrature import Grid
from .stationary import axis_roots, center_index


def _F(family, u, lens, grid):
    return Functional(family.body(u), lens, grid)


class NoSignChange(ValueError):
    """与えた区間の両端で符号が同じ ―― 根の存在が示されていない。"""


def bisect(f, lo, hi, iters: int = 44):
    """区間端で符号が変わることを確認してから二分する。

    符号変化がなければ NoSignChange を送出する。区間端を根として黙って返すことは
    しない（RESEARCH_RULES §11: 欠けた入力を推測で埋めない）。
    """
    flo, fhi = f(lo), f(hi)
    if flo == 0:
        return lo
    if fhi == 0:
        return hi
    if flo * fhi > 0:
        raise NoSignChange(f"f({lo})={flo:.6g} and f({hi})={fhi:.6g} have the same sign")
    for _ in range(iters):
        m = (lo + hi) / 2
        fm = f(m)
        if flo * fm <= 0:
            hi = m
        else:
            lo, flo = m, fm
    return (lo + hi) / 2


def center_coefficients_along(family, params, lens: Lens, grid: Grid | None = None) -> Quantity:
    """1パラメータ族に沿った中心主係数 Q_i と中心モース指数。"""
    grid = grid or Grid()
    rows, idx = [], []
    for u in params:
        F = _F(family, u, lens, grid)
        rows.append(np.asarray(F.center_coefficients().value))
        idx.append(center_index(F))
    return Quantity(
        {"params": np.asarray(params, dtype=float), "Q": np.array(rows),
         "center_index": np.array(idx)},
        Derivation.FLOAT, Evidence.DIAGNOSTIC_ONLY,
        method=f"center coefficients on {len(rows)} parameter samples",
        provenance={"family": family.name, "lens": lens.name, "grid": grid.describe()},
    )


def degeneracy_parameter(family, lens: Lens, bracket, component: int,
                         grid: Grid | None = None) -> Quantity:
    """中心主係数 Q_component が符号を変えるパラメータ（退化点）。"""
    grid = grid or Grid()

    def f(u):
        return float(np.asarray(_F(family, u, lens, grid).center_coefficients().value)[component])

    root = bisect(f, *bracket)
    return Quantity(
        root, Derivation.FLOAT, Evidence.DIAGNOSTIC_ONLY,
        method=f"bisection on Q_{component} over {tuple(bracket)}",
        provenance={"family": family.name, "lens": lens.name, "grid": grid.describe(),
                    "claim_limit": "double precision; not a certified enclosure"},
    )


def bifurcation_set(family, ps, qs, lens: Lens, grid: Grid | None = None,
                    max_axis_ratio: float = 60.0) -> Quantity:
    """2次元形状空間上で Q_i を走査する（Q_i = 0 の等高線が分岐集合）。"""
    grid = grid or Grid()
    Q = np.full((3, len(qs), len(ps)), np.nan)
    for j, qv in enumerate(qs):
        for i, pv in enumerate(ps):
            a = np.exp(family.log_semiaxes((pv, qv)))
            if a.max() / a.min() > max_axis_ratio:
                continue
            Q[:, j, i] = np.asarray(
                _F(family, (pv, qv), lens, grid).center_coefficients().value)
    idx = (Q < 0).sum(0).astype(float)
    idx[np.isnan(Q[0])] = np.nan
    return Quantity(
        {"ps": np.asarray(ps, float), "qs": np.asarray(qs, float),
         "Q": Q, "center_index": idx},
        Derivation.FLOAT, Evidence.DIAGNOSTIC_ONLY,
        method=f"{len(ps)}x{len(qs)} shape-plane scan of center coefficients",
        provenance={"family": family.name, "lens": lens.name, "grid": grid.describe()},
    )


def branch_positions(family, params, axis: int, lens: Lens,
                     grid: Grid | None = None) -> Quantity:
    """族に沿った、指定座標軸上の非自明停留点の位置（境界からの相対位置も返す）。"""
    grid = grid or Grid()
    pos, rel = [], []
    for u in params:
        F = _F(family, u, lens, grid)
        roots = axis_roots(F, axis).value
        pos.append(roots[0] if roots else np.nan)
        rel.append(roots[0] / F.body.semiaxes[axis] if roots else np.nan)
    return Quantity(
        {"params": np.asarray(params, float), "position": np.array(pos),
         "relative": np.array(rel)},
        Derivation.FLOAT, Evidence.DIAGNOSTIC_ONLY,
        method=f"first axis root on {len(pos)} parameter samples, axis={axis}",
        provenance={"family": family.name, "lens": lens.name, "grid": grid.describe(),
                    "claim_limit": "first root only; finite sampling"},
    )


def boundary_entry(family, lens: Lens, bracket, axis: int, grid: Grid | None = None,
                   epsilons=(0.015, 0.005, 0.002)) -> Quantity:
    """軌道が境界に到達するパラメータ。境界の内側 ε で解き、ε→0 へ線形外挿する。"""
    grid = grid or Grid()

    def solve(eps):
        def f(u):
            F = _F(family, u, lens, grid)
            e = np.eye(3)[axis]
            return float(F.grad((1.0 - eps) * F.body.semiaxes[axis] * e)[axis])
        return bisect(f, *bracket)

    eps = np.asarray(epsilons, dtype=float)
    vals = np.array([solve(e) for e in eps])
    slope, intercept = np.polyfit(eps, vals, 1)
    return Quantity(
        float(intercept), Derivation.EXTRAPOLATED, Evidence.DIAGNOSTIC_ONLY,
        method=f"linear extrapolation in boundary distance from eps={tuple(epsilons)}",
        provenance={"family": family.name, "lens": lens.name, "grid": grid.describe(),
                    "samples": {float(e): float(v) for e, v in zip(eps, vals)},
                    "slope": float(slope),
                    "claim_limit": "EXTRAPOLATED; requires endpoint-regular evaluation"},
    )
