"""証拠クラスと導出クラス（RESEARCH_RULES §1–2 の符号化）。

このパッケージが返す数値は、すべて導出クラスを伴う。既定は FLOAT / DIAGNOSTIC_ONLY
であり、認証済みを名乗ることはできない。CERTIFIED は本パッケージからは決して
生成されない ―― 認証は producer/checker 分離と clean-room 実行を要するため。
"""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class Derivation(str, Enum):
    EXACT = "EXACT"
    CERTIFIED_ENCLOSURE = "CERTIFIED_ENCLOSURE"
    HIGH_PRECISION = "HIGH_PRECISION"
    FLOAT = "FLOAT"
    EXTRAPOLATED = "EXTRAPOLATED"


class Evidence(str, Enum):
    DIAGNOSTIC_ONLY = "DIAGNOSTIC_ONLY"
    NOT_BINDING = "NOT_BINDING"
    PROTOTYPE = "PROTOTYPE"
    NOT_AUDITED = "NOT_AUDITED"
    AUDITED_SOURCE = "AUDITED_SOURCE"


@dataclass(frozen=True)
class Quantity:
    """値と、その値がどう作られたかの記録。"""

    value: Any
    derivation: Derivation = Derivation.FLOAT
    evidence: Evidence = Evidence.DIAGNOSTIC_ONLY
    method: str = ""
    provenance: dict = field(default_factory=dict)

    def __float__(self) -> float:
        return float(self.value)

    def __repr__(self) -> str:
        return (f"Quantity({self.value!r}, {self.derivation.value},"
                f" {self.evidence.value}, method={self.method!r})")

    def certified(self) -> bool:
        """本パッケージは認証を生成しない。常に False。"""
        return False
