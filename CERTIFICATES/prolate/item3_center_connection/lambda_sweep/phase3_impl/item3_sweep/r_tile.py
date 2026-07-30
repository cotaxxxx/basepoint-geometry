from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from typing import Protocol

from .enums import RunnerFailureReason


@dataclass(frozen=True)
class RCell:
    lo: Fraction
    hi: Fraction

    @property
    def midpoint(self) -> Fraction:
        return (self.lo + self.hi) / 2


@dataclass(frozen=True)
class RTileResult:
    accepted_leaves: tuple[RCell, ...]
    split_count: int

    @property
    def partition_leaf_count(self) -> int:
        return 1 + self.split_count


class DerivativeOracle(Protocol):
    def strict_negative(self, cell: RCell) -> bool:
        ...


class RTileFailure(RuntimeError):
    def __init__(self, reason: RunnerFailureReason):
        super().__init__(reason.value)
        self.reason = reason


def adaptive_r_bisection(
    root: RCell,
    oracle: DerivativeOracle,
    *,
    max_r_cells_per_box: int,
) -> RTileResult:
    """ADAPTIVE_R_BISECTION_V1, lower-r child first.

    The callback is the only numerical boundary.  This function itself is exact
    control logic and does not import or call Arb.
    """
    if max_r_cells_per_box < 1:
        raise ValueError("max_r_cells_per_box must be >= 1")
    stack = [root]
    accepted: list[RCell] = []
    split_count = 0
    while stack:
        cell = stack.pop()
        if oracle.strict_negative(cell):
            accepted.append(cell)
            continue
        # partition_leaf_count would increase by one after the split.
        if 1 + split_count + 1 > max_r_cells_per_box:
            raise RTileFailure(RunnerFailureReason.R_CELL_BUDGET_EXCEEDED)
        midpoint = cell.midpoint
        if midpoint == cell.lo or midpoint == cell.hi:
            raise RTileFailure(RunnerFailureReason.NONFINITE_ENCLOSURE)
        lower = RCell(cell.lo, midpoint)
        upper = RCell(midpoint, cell.hi)
        split_count += 1
        # LIFO: push upper then lower so lower is processed first.
        stack.append(upper)
        stack.append(lower)
    accepted.sort(key=lambda cell: cell.lo)
    return RTileResult(tuple(accepted), split_count)


def rederive_r_partition(
    root: RCell,
    oracle: DerivativeOracle,
    expected: RTileResult,
    *,
    max_r_cells_per_box: int,
) -> bool:
    """Reconstruct the deterministic r-partition and require exact equality."""
    try:
        actual = adaptive_r_bisection(
            root,
            oracle,
            max_r_cells_per_box=max_r_cells_per_box,
        )
    except RTileFailure:
        return False
    return actual == expected
