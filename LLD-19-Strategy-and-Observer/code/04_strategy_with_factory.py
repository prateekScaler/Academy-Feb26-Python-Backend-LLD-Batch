"""
LLD-19 · Strategy · Example 4 — Strategy + Factory (two patterns combined).

Run:  python3 04_strategy_with_factory.py

Real production code rarely uses Strategy alone. Almost always there's
a "pick the strategy by name from config" layer — which is exactly
what Factory does. The combination:

  - Factory hides WHICH concrete Strategy to instantiate (per config)
  - Strategy hides HOW to do the work (one class per algorithm)

Caller sees one uniform interface. Adding a new strategy = one new
class + one new line in the factory.
"""

from __future__ import annotations
from abc import ABC, abstractmethod
from dataclasses import dataclass


# ====================================================================
# The data
# ====================================================================
@dataclass(frozen=True)
class Shipment:
    weight_kg: float
    distance_km: float
    insured: bool = False


# ====================================================================
# Strategy interface
# ====================================================================
class ShippingRateStrategy(ABC):
    @abstractmethod
    def rate(self, s: Shipment) -> float: ...


class GroundShipping(ShippingRateStrategy):
    def rate(self, s: Shipment) -> float:
        return 50 + s.weight_kg * 8 + s.distance_km * 0.5


class AirShipping(ShippingRateStrategy):
    def rate(self, s: Shipment) -> float:
        return 200 + s.weight_kg * 25 + s.distance_km * 1.2


class SameDayShipping(ShippingRateStrategy):
    def rate(self, s: Shipment) -> float:
        if s.distance_km > 100:
            raise ValueError("Same-day not available beyond 100 km")
        return 500 + s.weight_kg * 40


class FreightShipping(ShippingRateStrategy):
    """For weights above 50 kg."""
    def rate(self, s: Shipment) -> float:
        if s.weight_kg < 50:
            raise ValueError("Freight requires >= 50 kg")
        return 1000 + s.weight_kg * 5 + s.distance_km * 0.8


# ====================================================================
# Factory — picks the right Strategy by name
# ====================================================================
class ShippingStrategyFactory:
    _registry: dict[str, type[ShippingRateStrategy]] = {
        "ground":   GroundShipping,
        "air":      AirShipping,
        "same_day": SameDayShipping,
        "freight":  FreightShipping,
    }

    @classmethod
    def create(cls, kind: str) -> ShippingRateStrategy:
        if kind not in cls._registry:
            raise ValueError(f"unknown shipping kind: {kind}")
        return cls._registry[kind]()

    @classmethod
    def available(cls) -> list[str]:
        return sorted(cls._registry)


# ====================================================================
# Context — uses whichever Strategy the Factory returns
# ====================================================================
class ShippingCalculator:
    """The application code stays vendor-agnostic."""
    @staticmethod
    def quote(shipment: Shipment, kind: str) -> float:
        strategy = ShippingStrategyFactory.create(kind)   # ← Factory picks
        return strategy.rate(shipment)                     # ← Strategy runs


# ====================================================================
# Demo
# ====================================================================
def main() -> None:
    shipment = Shipment(weight_kg=12.5, distance_km=420)

    print(f"Shipment: {shipment}")
    print("\nQuotes from each shipping mode:")
    for kind in ShippingStrategyFactory.available():
        try:
            price = ShippingCalculator.quote(shipment, kind)
            print(f"  {kind:>10} → ₹{price:.2f}")
        except ValueError as e:
            print(f"  {kind:>10} → not available ({e})")

    print("\nAdding a new shipping mode = a new ShippingRateStrategy subclass")
    print("+ one new line in ShippingStrategyFactory._registry. Caller unchanged.")


if __name__ == "__main__":
    main()
