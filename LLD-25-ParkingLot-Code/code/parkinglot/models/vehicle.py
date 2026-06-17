"""Vehicle — FR-2: plate + type travel together, no behaviour. Frozen, because a
car's identity doesn't mutate while it's parked."""

from __future__ import annotations

from dataclasses import dataclass

from enums import VehicleType


@dataclass(frozen=True)
class Vehicle:
    plate: str
    kind: VehicleType
