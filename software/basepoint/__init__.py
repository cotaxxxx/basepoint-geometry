"""basepoint ―― 基点幾何の実験台。

汎関数をレンズとして固定し、基点を動かして対象の停留構造を抽出し、
その構造が形状の変形に沿ってどう変わるかを追う。

    from basepoint import Ellipsoid, ConeVolumeAngleLens, Functional
    F = Functional(Ellipsoid((1, 1, 4.7243834)), ConeVolumeAngleLens())
    F.center_coefficients().value      # 中心 Hessian の主係数

本パッケージが返す数値はすべて倍精度・診断用（DIAGNOSTIC_ONLY）である。
認証は producer/checker 分離と clean-room 実行を要し、ここでは行わない。
"""
from .evidence import Derivation, Evidence, Quantity
from .family import ConstantVolumeEllipsoid, ConstantVolumeSpheroid
from .functional import Functional
from .geometry import Body, Ellipsoid
from .labels import Label, label_point, orbit_of
from .lens import AreaAngleLens, ConeVolumeAngleLens, CustomLens, Lens
from .quadrature import Grid
from .stationary import (StationaryPoint, axis_roots, center_index,
                         meridian_census, newton_refine)

__version__ = "0.1.0"
__all__ = [
    "Body", "Ellipsoid", "Grid", "Lens", "ConeVolumeAngleLens", "AreaAngleLens",
    "CustomLens", "Functional", "ConstantVolumeSpheroid", "ConstantVolumeEllipsoid",
    "StationaryPoint", "axis_roots", "meridian_census", "newton_refine",
    "center_index", "Label", "label_point", "orbit_of",
    "Quantity", "Derivation", "Evidence",
]
