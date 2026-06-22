"""PricingStrategy — FR-5. The price of a seat. A new scheme is one new class; the
engine never changes. Base prices themselves are data (config.BASE_PRICE)."""

from abc import ABC, abstractmethod

from ..config import BASE_PRICE
from ..models import Seat


class PricingStrategy(ABC):
    @abstractmethod
    def price(self, seat: Seat) -> float: ...


class TierPricing(PricingStrategy):
    """Base price by seat type."""

    def price(self, seat: Seat) -> float:
        return BASE_PRICE[seat.seat_type]


class WeekendSurge(PricingStrategy):
    """Same seats, +20% — FR-5's 'price varies by day' axis, swapped in."""

    def price(self, seat: Seat) -> float:
        return BASE_PRICE[seat.seat_type] * 1.2
