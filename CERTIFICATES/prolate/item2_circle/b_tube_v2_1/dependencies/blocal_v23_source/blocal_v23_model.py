#!/usr/bin/env python3
"""B-LOCAL v2.3 model identity wrapper over the frozen v2.2 arithmetic model."""
from __future__ import annotations

from blocal_v22_model import *

DESIGN_VERSION_V23 = "2.3"
FLAMBDA_ROUTE_ID = "BLOCAL_FLAMBDA_ROUTE_V1"
FLAMBDA_TRANSPORT_LEMMA_ID = "F_LAMBDA_IS_LAMBDA_DERIVATIVE_OF_ROUTE_F_V1"

__all__ = [name for name in globals() if not name.startswith("__")]
