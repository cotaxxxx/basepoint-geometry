"""レンズ ―― 停留構造を抽出するために固定する汎関数。

E(p) = ∫ h(γ) w dA / ∫ w dA,   γ = (x−p)·ν / |x−p|

`h` は角度核、`w` は面積要素に対する重み密度。レンズを差し替えると、同じ対象から
別の指紋が得られる。それが基点幾何の実験変数である。
"""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np


class Lens:
    name: str = "lens"

    #: h(γ) が γ=1（法線入射）で解析的か。中心が停留点となる対称体では、
    #: 中心近傍の展開そのものがこの性質に依存する。arccos(γ)^k は k が偶数の
    #: ときのみ (1−γ) について解析的で、奇数のときは √(1−γ) 特異を持つ。
    smooth_at_normal_incidence: bool = True

    def h(self, gamma):
        raise NotImplementedError

    def weight(self, d, nu):
        raise NotImplementedError

    def describe(self) -> str:
        return self.name


@dataclass(frozen=True)
class ConeVolumeAngleLens(Lens):
    """錐体積重み付き動径–法線角。power=2 が Paper 1 の汎関数。"""

    power: int = 2

    @property
    def name(self) -> str:
        return f"cone-volume radial-normal angle^{self.power}"

    @property
    def smooth_at_normal_incidence(self) -> bool:
        return self.power % 2 == 0

    def h(self, gamma):
        return np.arccos(gamma) ** self.power

    def weight(self, d, nu):
        return (d * nu).sum(-1)


@dataclass(frozen=True)
class AreaAngleLens(Lens):
    """面積測度で重み付けした同じ角度核。重みだけを変えた比較用レンズ。"""

    power: int = 2

    @property
    def name(self) -> str:
        return f"area-weighted radial-normal angle^{self.power}"

    @property
    def smooth_at_normal_incidence(self) -> bool:
        return self.power % 2 == 0

    def h(self, gamma):
        return np.arccos(gamma) ** self.power

    def weight(self, d, nu):
        return np.ones(d.shape[:-1])


@dataclass(frozen=True)
class CustomLens(Lens):
    """任意の (h, w) を与える。h: γ→値, w: (d, ν)→値。"""

    h_func: object
    weight_func: object
    name: str = "custom"

    def h(self, gamma):
        return self.h_func(gamma)

    def weight(self, d, nu):
        return self.weight_func(d, nu)
