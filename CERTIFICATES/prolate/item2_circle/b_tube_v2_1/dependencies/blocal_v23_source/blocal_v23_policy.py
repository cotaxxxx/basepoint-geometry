#!/usr/bin/env python3
"""B-LOCAL v2.3 deterministic route identities and inherited angular policy."""
from __future__ import annotations

from blocal_v22_policy import *

FLAMBDA_ROUTE_ID = "BLOCAL_FLAMBDA_ROUTE_V1"
FLAMBDA_FORMULA_ORDINARY_ID = "BLOCAL_FLAMBDA_ORDINARY_V1"
FLAMBDA_FORMULA_DUFFY_ID = "BLOCAL_FLAMBDA_DUFFY_V1"
FLAMBDA_REQUIRED_SIGN = "NEG"

__all__ = [name for name in globals() if not name.startswith("__")]
