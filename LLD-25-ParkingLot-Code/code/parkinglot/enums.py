"""enums.py — the shared vocabulary. Imports nothing in the package, so it sits
at the very bottom of the import graph: every other module may point DOWN to it,
and a cycle can never start here.

Three small named sets the FRs handed us, plus the payment method.
`SpotStatus` carries the third state — OUT_OF_ORDER — that a bare `occupied: bool`
could never hold (the GameStatus lesson from TTT, repeated)."""

from __future__ import annotations

from enum import Enum


class VehicleType(Enum):
    BIKE = "bike"
    CAR = "car"
    TRUCK = "truck"


class SpotSize(Enum):
    SMALL = "small"
    MEDIUM = "medium"
    LARGE = "large"


class SpotStatus(Enum):
    FREE = "free"
    OCCUPIED = "occupied"
    OUT_OF_ORDER = "out_of_order"    # the third state a bool cannot hold


class PaymentMethod(Enum):
    CASH = "cash"
    CARD = "card"
    UPI = "upi"
