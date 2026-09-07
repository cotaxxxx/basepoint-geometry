"""停留集合の抽出。

いずれも倍精度・有限標本であり、検出されなかったことは非存在の証明ではない
（RESEARCH_RULES §7）。返り値はその旨を証拠クラスとして保持する。
"""
from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np

from .evidence import Derivation, Evidence, Quantity
from .functional import Functional


@dataclass
class StationaryPoint:
    position: np.ndarray
    gradient_norm: float
    converged: bool
    seed: np.ndarray | None = None
    extra: dict = field(default_factory=dict)

    def __repr__(self) -> str:
        x, y, z = self.position
        return (f"StationaryPoint(({x:+.6f}, {y:+.6f}, {z:+.6f}), "
                f"|grad|={self.gradient_norm:.2e}, converged={self.converged})")


def newton_refine(F: Functional, p0, tol: float = 1e-9, max_iter: int = 30,
                  step: float = 1e-4) -> StationaryPoint:
    """3次元の Newton 反復。対象の外へ出たら発散として打ち切る。"""
    p = np.asarray(p0, dtype=float).copy()
    for _ in range(max_iter):
        g = F.grad(p, step)
        if np.linalg.norm(g) < tol:
            break
        H = F.hessian(p, step * 10)
        try:
            dp = np.linalg.solve(H, -g)
        except np.linalg.LinAlgError:
            return StationaryPoint(p, float(np.linalg.norm(g)), False, np.asarray(p0, float))
        p = p + dp
        if not F.body.contains(p):
            return StationaryPoint(p, float("inf"), False, np.asarray(p0, float))
    gn = float(np.linalg.norm(F.grad(p, step)))
    return StationaryPoint(p, gn, gn < 1e-7, np.asarray(p0, dtype=float))


def axis_roots(F: Functional, axis: int, r_max: float | None = None,
               samples: int = 160, tol: float = 1e-12) -> Quantity:
    """座標軸上の非自明な停留点（方向微分の符号変化を二分法で追う）。"""
    if r_max is None:
        r_max = 0.985 * F.body.semiaxes[axis]
    e = np.eye(3)[axis]

    def g(r):
        return float(F.grad(r * e)[axis])

    rs = np.linspace(r_max / samples, r_max, samples)
    vs = np.array([g(r) for r in rs])
    roots = []
    for k in range(len(rs) - 1):
        if vs[k] * vs[k + 1] < 0:
            lo, hi, flo = rs[k], rs[k + 1], vs[k]
            while hi - lo > tol:
                m = (lo + hi) / 2
                fm = g(m)
                if flo * fm <= 0:
                    hi = m
                else:
                    lo, flo = m, fm
            roots.append((lo + hi) / 2)
    return Quantity(
        roots, Derivation.FLOAT, Evidence.DIAGNOSTIC_ONLY,
        method=f"sign change on {samples} samples then bisection, axis={axis}",
        provenance={"body": F.body.name, "lens": F.lens.name,
                    "claim_limit": "finite sampling; absence is not a nonexistence proof"},
    )


def meridian_census(F: Functional, samples: int = 30, margin: float = 0.985,
                    dedup: float = 2e-3) -> Quantity:
    """回転対称体の子午半平面 (r ≥ 0, z ≥ 0) における停留点の全数探索。

    |∇E| の格子上の局所最小を種に Newton を回す。
    """
    a1, a2, a3 = F.body.semiaxes
    if abs(a1 - a2) > 1e-12:
        raise ValueError("meridian_census requires a body with a1 == a2")
    rs = np.linspace(0.0, margin * a1, samples)
    zs = np.linspace(0.0, margin * a3, samples)

    def gn(r, z):
        g = F.grad(np.array([r, 0.0, z]))
        return float(np.hypot(g[0], g[2]))

    N = np.full((samples, samples), np.inf)
    for i, r in enumerate(rs):
        for j, z in enumerate(zs):
            if (r / a1) ** 2 + (z / a3) ** 2 <= margin**2:
                N[i, j] = gn(r, z)
    found: list[StationaryPoint] = []
    for i in range(samples):
        for j in range(samples):
            if not np.isfinite(N[i, j]):
                continue
            nb = N[max(i - 1, 0):i + 2, max(j - 1, 0):j + 2]
            if N[i, j] > nb.min() + 1e-15:
                continue
            sp = newton_refine(F, [rs[i], 0.0, zs[j]])
            if not sp.converged:
                continue
            q = np.array([max(sp.position[0], 0.0), 0.0, max(sp.position[2], 0.0)])
            if any(np.linalg.norm(q - f.position) < dedup for f in found):
                continue
            found.append(StationaryPoint(q, sp.gradient_norm, True, sp.seed))
    found.sort(key=lambda s: (s.position[0], s.position[2]))
    return Quantity(
        found, Derivation.FLOAT, Evidence.DIAGNOSTIC_ONLY,
        method=f"meridian gradient-norm minima seeds, {samples}x{samples}, margin={margin}",
        provenance={"body": F.body.name, "lens": F.lens.name,
                    "claim_limit": "finite sampling; absence is not a nonexistence proof"},
    )


def center_index(F: Functional, tol: float = 1e-9) -> int:
    """中心のモース指数（Hessian の負固有値の個数）。"""
    q = np.asarray(F.center_coefficients().value)
    return int((q < -tol).sum())
