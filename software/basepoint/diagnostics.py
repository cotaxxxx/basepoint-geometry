"""数値が信用できるかを、結果そのものから確かめる層。

二つの独立な検査を提供する。

  * 格子収束      同じ量を細かい格子で再評価し、差を記録する。
  * 対称性残差    軸の置換 S₃ で移り合う形状点は同じ指紋を持たねばならない。
                  一致しなければ求積誤差であり、結果ではない。

対称性検査は追加の理論を要さず、しかも極端な軸比で最初に破れる。
本パッケージではこれを既定の健全性検査として使う。
"""
from __future__ import annotations

from itertools import permutations

import numpy as np

from .evidence import Derivation, Evidence, Quantity
from .functional import Functional
from .geometry import Ellipsoid
from .quadrature import Grid

DEFAULT_LADDER = (Grid(64, 64), Grid(96, 96), Grid(160, 96), Grid(240, 128))


def grid_convergence(evaluate, grids=DEFAULT_LADDER) -> Quantity:
    """evaluate(grid) を格子列で評価し、値と逐次差を返す。"""
    values = [np.asarray(evaluate(g), dtype=float) for g in grids]
    diffs = [float(np.max(np.abs(values[i + 1] - values[i]))) for i in range(len(values) - 1)]
    return Quantity(
        {"grids": [g.describe() for g in grids], "values": values, "successive_diff": diffs,
         "last_diff": diffs[-1] if diffs else float("nan")},
        Derivation.FLOAT, Evidence.DIAGNOSTIC_ONLY,
        method=f"grid ladder of {len(grids)} refinements",
        provenance={"claim_limit": "successive differences bound nothing rigorously"},
    )


def converged_value(evaluate, grids=DEFAULT_LADDER, tol: float = 1e-6) -> Quantity:
    """逐次差が tol を下回った時点の値。下回らなければ収束せずと記録する。"""
    rec = grid_convergence(evaluate, grids).value
    for i, d in enumerate(rec["successive_diff"]):
        if d < tol:
            return Quantity(
                rec["values"][i + 1], Derivation.FLOAT, Evidence.DIAGNOSTIC_ONLY,
                method=f"converged at {rec['grids'][i + 1]} (Δ={d:.2e} < {tol:g})",
                provenance={"ladder": rec["grids"][:i + 2],
                            "successive_diff": rec["successive_diff"][:i + 1]})
    return Quantity(
        None, Derivation.FLOAT, Evidence.NOT_BINDING,
        method=f"NOT CONVERGED on the given ladder (last Δ={rec['last_diff']:.2e} ≥ {tol:g})",
        provenance={"ladder": rec["grids"], "successive_diff": rec["successive_diff"],
                    "values": [v.tolist() for v in rec["values"]],
                    "claim_limit": "no value is reported; refine the grid or reduce the range"},
    )


def s3_residual(lens, semiaxes, grid: Grid | None = None) -> Quantity:
    """半軸の6通りの置換にわたる中心係数の不一致。

    レンズが軸に依存しないなら、置換した対象の中心係数は同じ多重集合になる。
    残差は純粋に求積誤差であり、その形状・格子における精度の上界になる。
    """
    grid = grid or Grid()
    a = tuple(float(v) for v in semiaxes)
    sets = []
    for perm in permutations(range(3)):
        body = Ellipsoid(tuple(a[i] for i in perm))
        q = np.asarray(Functional(body, lens, grid).center_coefficients().value)
        sets.append(np.sort(q[list(np.argsort(perm))]))
    sets = np.array(sets)
    residual = float(np.max(sets.max(0) - sets.min(0)))
    return Quantity(
        residual, Derivation.FLOAT, Evidence.DIAGNOSTIC_ONLY,
        method="max spread of sorted center coefficients over the 6 axis permutations",
        provenance={"semiaxes": a, "axis_ratio": max(a) / min(a), "lens": lens.name,
                    "grid": grid.describe(),
                    "interpretation": "a nonzero residual is quadrature error, not structure"},
    )
