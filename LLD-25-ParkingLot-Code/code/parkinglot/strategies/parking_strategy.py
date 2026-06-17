"""Strategy 1 — WHERE to put the vehicle (FR-8, open variable #1).

`pick` takes `floors` and a `vehicle`, never the whole `ParkingLot` — the narrow
parameter is the Interface Segregation Principle enforced by the signature: a
placement policy can't reach for payment state it has no business touching.

Adding `NearestToExit` or `ReserveForEV` is one new class docking at the ABC —
the service that calls `pick` never changes."""

from __future__ import annotations

from abc import ABC, abstractmethod

from config import SPOT_SIZE_FOR
from models.floor import Floor
from models.spot import Spot
from models.vehicle import Vehicle


class ParkingStrategy(ABC):
    @abstractmethod
    def pick(self, floors: list[Floor], vehicle: Vehicle) -> tuple[Floor, Spot] | None:
        """Return (floor, spot) for the vehicle, or None when nothing fits."""


class FirstFit(ParkingStrategy):
    """First free spot of the right size on the lowest floor — minimises walking."""

    def pick(self, floors: list[Floor], vehicle: Vehicle) -> tuple[Floor, Spot] | None:
        for floor in floors:
            for spot in floor.spots:
                if spot.can_fit(vehicle):
                    return floor, spot
        return None


class LeastCrowded(ParkingStrategy):
    """Floor with the most free spots of that size — spreads congestion."""

    def pick(self, floors: list[Floor], vehicle: Vehicle) -> tuple[Floor, Spot] | None:
        size = SPOT_SIZE_FOR[vehicle.kind]
        best = max(floors, key=lambda f: f.free_count(size), default=None)
        if best is None or best.free_count(size) == 0:
            return None
        return best, best.free_spots(size)[0]
