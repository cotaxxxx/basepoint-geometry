#!/usr/bin/env python3
"""Run the budget-adaptive pole certificate with depth-first compact covers."""
from __future__ import annotations

import prolate_axis_pole_modulus_budgeted_arb as budgeted
import prolate_axis_pole_modulus_compact_dfs_arb as compact_dfs


def main() -> None:
    budgeted.compact = compact_dfs
    budgeted.main()


if __name__ == "__main__":
    main()
