"""
02 - Order Builder (variable composition)
=========================================

An Order in any e-commerce backend has a LIST of items, an optional list
of discount codes, and a few flags. The Builder lets each caller add as
many items and discounts as they need - without growing the constructor.

This is the canonical "variable composition" use of Builder: setters that
can be called multiple times to accumulate state.
"""

from dataclasses import dataclass, field
from typing import List, Tuple


@dataclass
class Order:
    customer: str
    items: List[Tuple[str, int]]                          # [(product, qty), ...]
    discount_codes: List[str] = field(default_factory=list)
    gift_wrap: bool = False
    expedited: bool = False

    def summary(self) -> str:
        line_items = ", ".join(f"{p}x{q}" for p, q in self.items)
        flags = []
        if self.discount_codes:
            flags.append("discounts: " + ",".join(self.discount_codes))
        if self.gift_wrap:
            flags.append("gift-wrap")
        if self.expedited:
            flags.append("expedited")
        suffix = f" [{'; '.join(flags)}]" if flags else ""
        return f"{self.customer}: {line_items}{suffix}"


class OrderBuilder:
    def __init__(self):
        self._customer = None
        self._items: List[Tuple[str, int]] = []
        self._discounts: List[str] = []
        self._gift_wrap = False              # sensible defaults
        self._expedited = False

    def for_customer(self, name):
        self._customer = name
        return self

    def add_item(self, product, quantity=1):
        """Call any number of times - each adds a line item."""
        self._items.append((product, quantity))
        return self

    def apply_discount(self, code):
        """Call any number of times - each adds a discount code."""
        self._discounts.append(code)
        return self

    def enable_gift_wrap(self):
        self._gift_wrap = True
        return self

    def expedite(self):
        self._expedited = True
        return self

    def build(self) -> Order:
        if not self._customer:
            raise ValueError("customer required")
        if not self._items:
            raise ValueError("at least one item required")
        # Defensive copies - mutating the builder later must not affect
        # any Order we already produced.
        return Order(
            customer=self._customer,
            items=list(self._items),
            discount_codes=list(self._discounts),
            gift_wrap=self._gift_wrap,
            expedited=self._expedited,
        )


# ---------------------------------------------------------------------------
# Demo
# ---------------------------------------------------------------------------

def demo():
    print("--- A simple order ---")
    simple = (OrderBuilder()
                .for_customer("alice@x.com")
                .add_item("book-101", 2)
                .build())
    print(simple.summary())

    print("\n--- A birthday gift order with discount + gift wrap + expedited ---")
    birthday = (OrderBuilder()
                  .for_customer("bob@x.com")
                  .add_item("book-101", 1)
                  .add_item("pen-set", 1)
                  .add_item("card", 1)
                  .apply_discount("BDAY20")
                  .enable_gift_wrap()
                  .expedite()
                  .build())
    print(birthday.summary())

    print("\n--- A bulk order with stacked discounts ---")
    bulk = (OrderBuilder()
              .for_customer("acme-corp")
              .add_item("ergonomic-chair", 50)
              .add_item("desk", 50)
              .apply_discount("BULK10")
              .apply_discount("CORP5")
              .build())
    print(bulk.summary())

    print("\n--- Missing customer raises early ---")
    try:
        OrderBuilder().add_item("book-101").build()
    except ValueError as e:
        print(f"ValueError: {e}")

    print("\n--- Missing items raises early ---")
    try:
        OrderBuilder().for_customer("ghost").build()
    except ValueError as e:
        print(f"ValueError: {e}")


if __name__ == "__main__":
    demo()
