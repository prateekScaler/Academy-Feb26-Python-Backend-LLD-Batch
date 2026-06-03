"""
LLD-19 · Strategy · Example 3 — Three wirings of Strategy (UML-friendly).

Run:  python3 03_payment_pricing_strategy.py

The same Checkout context wired with the same family of PricingStrategy
in three different idioms:

  1. Constructor injection — strategy is fixed for the object's lifetime
  2. Setter / property      — strategy can change after construction
  3. Per-call argument      — strategy is request-scoped

Designed to render cleanly in PyCharm's UML class-diagram view:

        PricingStrategy (ABC)
              △
              |
   ┌──────────┼──────────┐
   │          │          │
RegularPricing   FestivalPricing   StudentPricing
              │
              ◇  (held by)
   ┌──────────┴──────────┐
   │                     │
Checkout            CheckoutFlexible
"""

from __future__ import annotations
from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass(frozen=True)
class Cart:
    subtotal: float
    item_count: int


# ====================================================================
# Strategy interface
# ====================================================================
class PricingStrategy(ABC):
    @abstractmethod
    def total(self, cart: Cart) -> float: ...


class RegularPricing(PricingStrategy):
    """Subtotal + 18% GST."""
    def total(self, cart: Cart) -> float:
        return cart.subtotal * 1.18


class FestivalPricing(PricingStrategy):
    """10% off the subtotal, then 18% GST on the discounted value."""
    def total(self, cart: Cart) -> float:
        discounted = cart.subtotal * 0.90
        return discounted * 1.18


class StudentPricing(PricingStrategy):
    """15% off, no GST (educational exemption)."""
    def total(self, cart: Cart) -> float:
        return cart.subtotal * 0.85


# ====================================================================
# Wiring 1 — constructor injection (most common, simplest)
# ====================================================================
class Checkout:
    def __init__(self, pricing: PricingStrategy) -> None:
        self._pricing = pricing

    def final(self, cart: Cart) -> float:
        return self._pricing.total(cart)


# ====================================================================
# Wiring 2 — setter (strategy swappable mid-flight)
# ====================================================================
class CheckoutSwappable:
    def __init__(self) -> None:
        self._pricing: PricingStrategy = RegularPricing()

    @property
    def pricing(self) -> PricingStrategy:
        return self._pricing

    @pricing.setter
    def pricing(self, value: PricingStrategy) -> None:
        self._pricing = value

    def final(self, cart: Cart) -> float:
        return self._pricing.total(cart)


# ====================================================================
# Wiring 3 — per-call argument (request-scoped)
# ====================================================================
class CheckoutPerCall:
    @staticmethod
    def final(cart: Cart, pricing: PricingStrategy) -> float:
        return pricing.total(cart)


# ====================================================================
# Demo
# ====================================================================
def main() -> None:
    cart = Cart(subtotal=1000.0, item_count=3)

    print("--- Wiring 1: constructor injection ---")
    for strategy in [RegularPricing(), FestivalPricing(), StudentPricing()]:
        co = Checkout(strategy)
        print(f"  {strategy.__class__.__name__:>16} → ₹{co.final(cart):.2f}")

    print("\n--- Wiring 2: setter (swap mid-flight) ---")
    co = CheckoutSwappable()
    print(f"  default (Regular)        → ₹{co.final(cart):.2f}")
    co.pricing = FestivalPricing()
    print(f"  after switching Festival → ₹{co.final(cart):.2f}")
    co.pricing = StudentPricing()
    print(f"  after switching Student  → ₹{co.final(cart):.2f}")

    print("\n--- Wiring 3: per-call argument ---")
    co = CheckoutPerCall()
    print(f"  Regular  → ₹{co.final(cart, RegularPricing()):.2f}")
    print(f"  Festival → ₹{co.final(cart, FestivalPricing()):.2f}")
    print(f"  Student  → ₹{co.final(cart, StudentPricing()):.2f}")


if __name__ == "__main__":
    main()
