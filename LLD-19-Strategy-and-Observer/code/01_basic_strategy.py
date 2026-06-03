"""
LLD-19 · Strategy · Example 1 — The minimal Strategy pattern.

Run:  python3 01_basic_strategy.py

Three roles, spelled out:
    Strategy           — the interface every algorithm implements
    ConcreteStrategy   — one class per algorithm
    Context            — holds whichever Strategy was injected and uses it

Sneha's discount engine, from the class notes, reduced to its smallest
form.
"""

from __future__ import annotations
from abc import ABC, abstractmethod
from dataclasses import dataclass


# ====================================================================
# Strategy — the common interface
# ====================================================================
class DiscountStrategy(ABC):
    @abstractmethod
    def calculate(self, order: "Order") -> float: ...


# ====================================================================
# ConcreteStrategies — each is one algorithm
# ====================================================================
class NoDiscount(DiscountStrategy):
    def calculate(self, order: "Order") -> float:
        return 0.0


class PercentageDiscount(DiscountStrategy):
    def __init__(self, pct: float) -> None:
        self.pct = pct

    def calculate(self, order: "Order") -> float:
        return order.total * self.pct


class FlatDiscount(DiscountStrategy):
    def __init__(self, amount: float) -> None:
        self.amount = amount

    def calculate(self, order: "Order") -> float:
        return min(self.amount, order.total)  # don't refund more than the order


class BulkDiscount(DiscountStrategy):
    """15% off for >= 10 items, 8% for >= 5 items, otherwise nothing."""
    def calculate(self, order: "Order") -> float:
        if order.item_count >= 10:
            return order.total * 0.15
        if order.item_count >= 5:
            return order.total * 0.08
        return 0.0


# ====================================================================
# Context — holds a Strategy and uses it
# ====================================================================
@dataclass
class Order:
    total: float
    item_count: int


class Checkout:
    def __init__(self, discount: DiscountStrategy) -> None:
        self._discount = discount

    def final_total(self, order: Order) -> float:
        return order.total - self._discount.calculate(order)


# ====================================================================
# Demo — same Order, three different strategies
# ====================================================================
def main() -> None:
    order = Order(total=500.0, item_count=12)

    for strategy in [
        NoDiscount(),
        PercentageDiscount(0.10),
        FlatDiscount(75.0),
        BulkDiscount(),
    ]:
        checkout = Checkout(discount=strategy)
        final = checkout.final_total(order)
        saved = order.total - final
        print(f"  {strategy.__class__.__name__:>22} → final ₹{final:7.2f}  (saved ₹{saved:.2f})")

    print("\nAdding a new discount = a new class. Checkout.final_total never changes.")


if __name__ == "__main__":
    main()
