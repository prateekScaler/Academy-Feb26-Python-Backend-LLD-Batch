"""Strategy 2 — WHAT to charge (FR-5 + FR-8, open variable #2).

`fee(size, seconds)` bills the resource you OCCUPIED (the spot size), not the
vehicle you drove — a truck in a (wrongly sized) small spot pays the small rate.
The tiered table is itself data: a new city's rates are a dict edit, a new scheme
(`WeekdayPeak`, `FlatDaily`) is a new class. The two axes — placement and price —
move independently, which is the whole point of keeping them separate Strategies."""

from __future__ import annotations

import math
from abc import ABC, abstractmethod

from enums import SpotSize


class PricingStrategy(ABC):
    @abstractmethod
    def fee(self, size: SpotSize, seconds: float) -> float:
        """You pay for the spot you occupied, not the vehicle you drove."""


class TieredHourly(PricingStrategy):
    """First hour at one rate, every extra hour at another — per spot size."""

    RATES = {  # size: (first_hour, each_extra_hour)
        SpotSize.SMALL: (50, 80),
        SpotSize.MEDIUM: (80, 100),
        SpotSize.LARGE: (100, 120),
    }

    def fee(self, size: SpotSize, seconds: float) -> float:
        hours = max(1, math.ceil(seconds / 3600))   # minimum 1 hour, round up
        first, extra = self.RATES[size]
        return first + (hours - 1) * extra


class WeekendFlat(PricingStrategy):
    """Flat ticket regardless of duration — mall promo."""

    def fee(self, size: SpotSize, seconds: float) -> float:
        return 100.0
