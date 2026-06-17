"""config.py — policy as DATA, the FR-2 promise made concrete.

"Can a bike take a car spot?" is a one-line change HERE — never an edit to a
class. Adding SCOOTER or BUS is one entry each. Cross-parking rules (a bike may
also fit a MEDIUM spot) would graduate this to dict[VehicleType, list[SpotSize]]
— still data, still one place.

It imports only `enums`, so it stays near the bottom of the graph."""

from __future__ import annotations

from enums import SpotSize, VehicleType

# Every vehicle type maps to exactly one spot size it needs.
SPOT_SIZE_FOR = {
    VehicleType.BIKE: SpotSize.SMALL,
    VehicleType.CAR: SpotSize.MEDIUM,
    VehicleType.TRUCK: SpotSize.LARGE,
}
