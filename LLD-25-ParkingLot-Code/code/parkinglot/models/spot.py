"""Spot — the Cell analogue: two facts (size, status) and the rules that relate
them. The invariant "a vehicle fits only a free spot of its size" lives HERE,
on the object that owns both facts — not scattered across the service.

`can_fit` is why Spot earns class-hood: a bare `(size, status)` tuple couldn't
carry the rule."""

from __future__ import annotations

from dataclasses import dataclass

from config import SPOT_SIZE_FOR
from enums import SpotSize, SpotStatus
from models.vehicle import Vehicle


@dataclass
class Spot:
    spot_id: str
    size: SpotSize
    status: SpotStatus = SpotStatus.FREE

    def is_free(self) -> bool:
        return self.status is SpotStatus.FREE

    def can_fit(self, vehicle: Vehicle) -> bool:
        return self.is_free() and self.size == SPOT_SIZE_FOR[vehicle.kind]

    def occupy(self) -> None:
        self.status = SpotStatus.OCCUPIED

    def free(self) -> None:
        self.status = SpotStatus.FREE
