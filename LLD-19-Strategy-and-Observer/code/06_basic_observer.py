"""
LLD-19 · Observer · Example 6 — The minimal Observer pattern.

Run:  python3 06_basic_observer.py

Two roles, spelled out:
    Subject     — maintains the observer list, emits events
    Observer    — registers a callback, reacts to events

Aryan's order processing from the class notes, distilled to the
smallest workable shape.
"""

from __future__ import annotations
from abc import ABC, abstractmethod
from dataclasses import dataclass


# =====================================================================
# Event — immutable, carries everything observers might want
# =====================================================================
@dataclass(frozen=True)
class OrderPaidEvent:
    order_id: str
    customer_id: str
    total: float


# =====================================================================
# Observer interface
# =====================================================================
class OrderObserver(ABC):
    @abstractmethod
    def on_paid(self, event: OrderPaidEvent) -> None: ...


# =====================================================================
# Concrete Observers — each one does one job
# =====================================================================
class EmailObserver(OrderObserver):
    def on_paid(self, event: OrderPaidEvent) -> None:
        print(f"  [email]     sent confirmation for order {event.order_id} "
              f"to customer {event.customer_id}")


class WarehouseObserver(OrderObserver):
    def on_paid(self, event: OrderPaidEvent) -> None:
        print(f"  [warehouse] queued fulfilment for order {event.order_id}")


class AnalyticsObserver(OrderObserver):
    def on_paid(self, event: OrderPaidEvent) -> None:
        print(f"  [analytics] tracked conversion: ₹{event.total:.2f} from customer {event.customer_id}")


class LoyaltyObserver(OrderObserver):
    """Award 1 point per ₹100 spent."""
    def on_paid(self, event: OrderPaidEvent) -> None:
        points = int(event.total / 100)
        print(f"  [loyalty]   awarded {points} points to customer {event.customer_id}")


# =====================================================================
# Subject — holds the observer list, emits events
# =====================================================================
class Order:
    def __init__(self, order_id: str, customer_id: str, total: float) -> None:
        self.order_id = order_id
        self.customer_id = customer_id
        self.total = total
        self.status = "PENDING"
        self._observers: list[OrderObserver] = []

    def subscribe(self, observer: OrderObserver) -> None:
        self._observers.append(observer)

    def unsubscribe(self, observer: OrderObserver) -> None:
        self._observers.remove(observer)

    def mark_paid(self) -> None:
        self.status = "PAID"
        event = OrderPaidEvent(
            order_id=self.order_id,
            customer_id=self.customer_id,
            total=self.total,
        )
        # Notify — Order has no idea WHO is listening
        for obs in self._observers:
            obs.on_paid(event)


# =====================================================================
# Demo
# =====================================================================
def main() -> None:
    order = Order(order_id="ORD-001", customer_id="cust_42", total=1499.50)

    # Wire up reactions at startup (could be in a config file)
    order.subscribe(EmailObserver())
    order.subscribe(WarehouseObserver())
    order.subscribe(AnalyticsObserver())
    order.subscribe(LoyaltyObserver())

    print("Customer clicks 'Pay'...\n")
    order.mark_paid()

    print("\nNotice: Order.mark_paid() doesn't import email, warehouse,")
    print("analytics, or loyalty. Adding a fifth reaction = one more")
    print(".subscribe(...) call at startup. Order class never changes.")


if __name__ == "__main__":
    main()
