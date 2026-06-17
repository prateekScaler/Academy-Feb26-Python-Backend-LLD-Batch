"""Floor — FR-1 + FR-7: identity (a number) plus its own queries. Unlike TTT's
board rows — which stayed bare lists because nothing addressed them by name — a
floor is asked questions directly ("how many free medium spots on floor 2?"), so
it earns a class."""

from __future__ import annotations

from enums import SpotSize
from models.spot import Spot


class Floor:
    def __init__(self, number: int, spots: list[Spot]):
        self.number = number
        self.spots = spots

    def free_spots(self, size: SpotSize) -> list[Spot]:
        return [s for s in self.spots if s.is_free() and s.size == size]

    def free_count(self, size: SpotSize) -> int:
        return len(self.free_spots(size))
