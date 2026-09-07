"""停留成分のラベル ―― 指紋の語彙。

  * 成分次元        軌道の次元（孤立点 0、円 1）
  * 軌道サイズ      0 次元軌道の点の個数
  * 法方向モース指数 軌道の法空間に制限した Hessian の負固有値の個数
  * 核次元          零固有値の個数（接方向と法方向を分けて報告）
  * 等方型          その点の固定部分群

基点分岐は、これらのラベルを保存する局所自明化が存在しないことをいう。
"""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from .functional import Functional


@dataclass(frozen=True)
class Orbit:
    dimension: int
    size: int | str
    isotropy: str
    tangents: tuple


@dataclass(frozen=True)
class Label:
    dimension: int
    orbit_size: int | str
    normal_morse_index: int
    nullity_normal: int
    nullity_tangential: int
    isotropy: str
    eigenvalues: tuple

    def key(self) -> tuple:
        """局所自明化が保存すべき量の組。"""
        return (self.dimension, self.orbit_size, self.normal_morse_index,
                self.nullity_normal, self.isotropy)

    def __repr__(self) -> str:
        return (f"Label(dim={self.dimension}, orbit={self.orbit_size}, "
                f"normal_index={self.normal_morse_index}, "
                f"nullity={self.nullity_normal}+{self.nullity_tangential}t, "
                f"isotropy={self.isotropy})")


def orbit_of(body, p, tol: float = 1e-7) -> Orbit:
    """楕円体の等長群による軌道。半軸の一致から対称性を決める。"""
    p = np.asarray(p, dtype=float)
    a = np.asarray(body.semiaxes, dtype=float)
    zero = np.abs(p) < tol
    sym = body.symmetry()

    if zero.all():
        return Orbit(0, 1, sym + " (center, fully fixed)", ())

    if sym == "D_2h":
        return Orbit(0, int(2 ** (~zero).sum()), "mirror subgroup of D_2h", ())

    if sym == "O(3)":
        return Orbit(2, "S^2", "C_inf_v", ())

    # 回転楕円体: 他の2軸と異なる半軸が対称軸
    if abs(a[0] - a[1]) < tol:
        k = 2
    elif abs(a[1] - a[2]) < tol:
        k = 0
    else:
        k = 1
    perp = [i for i in range(3) if i != k]
    r = float(np.hypot(p[perp[0]], p[perp[1]]))
    on_axis = r < tol

    if on_axis:
        return Orbit(0, 2, "C_inf_v (on symmetry axis)", ())
    t = np.zeros(3)
    t[perp[0]] = -p[perp[1]] / r
    t[perp[1]] = p[perp[0]] / r
    if abs(p[k]) < tol:
        return Orbit(1, "S^1", "C_2v (equatorial circle)", (tuple(t),))
    return Orbit(1, "S^1 x Z_2", "C_s (off-equator circle pair)", (tuple(t),))


def label_point(F: Functional, p, tol: float = 1e-6, step: float = 1e-3) -> Label:
    """停留点 p の属する成分にラベルを付ける。"""
    p = np.asarray(p, dtype=float)
    orb = orbit_of(F.body, p)
    H = F.hessian(p, step)
    evals, evecs = np.linalg.eigh(H)

    if orb.tangents:
        T = np.array(orb.tangents).T                       # 3 x k（接空間）
        Qt, _ = np.linalg.qr(T)
        Qf, _ = np.linalg.qr(np.hstack([Qt, np.eye(3)]))    # 先頭 k 列が接空間
        B = Qf[:, len(orb.tangents):]                       # 法空間の正規直交基底
        nvals = np.linalg.eigvalsh(B.T @ H @ B)
        tang = int(sum(abs(float(t @ H @ t)) < tol for t in np.array(orb.tangents)))
    else:
        nvals = evals
        tang = 0

    return Label(
        dimension=orb.dimension,
        orbit_size=orb.size,
        normal_morse_index=int((nvals < -tol).sum()),
        nullity_normal=int((np.abs(nvals) < tol).sum()),
        nullity_tangential=tang,
        isotropy=orb.isotropy,
        eigenvalues=tuple(float(v) for v in evals),
    )
