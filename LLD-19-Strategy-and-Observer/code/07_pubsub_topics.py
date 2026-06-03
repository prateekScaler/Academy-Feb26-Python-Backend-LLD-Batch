"""
LLD-19 · Observer · Example 7 — Topic-based Pub/Sub (one Subject, many event types).

Run:  python3 07_pubsub_topics.py

In real systems a Subject usually emits MANY kinds of events
("order.paid", "order.refunded", "user.signed_up", ...) and each
observer cares about only one or two. The pub/sub idiom wraps the
basic Observer pattern in a topic dispatcher.

The shape that follows is the same as Django Signals, Node's
EventEmitter, Redis Pub/Sub channels, and Kafka topics.
"""

from __future__ import annotations
from collections import defaultdict
from dataclasses import dataclass
from typing import Callable, Any

# A subscriber is just a callable (event payload) -> None
Subscriber = Callable[[Any], None]


# =====================================================================
# EventBus — generic Subject. Topic-aware.
# =====================================================================
class EventBus:
    def __init__(self) -> None:
        self._subs: dict[str, list[Subscriber]] = defaultdict(list)

    def subscribe(self, topic: str, fn: Subscriber) -> None:
        self._subs[topic].append(fn)

    def unsubscribe(self, topic: str, fn: Subscriber) -> None:
        if fn in self._subs[topic]:
            self._subs[topic].remove(fn)

    def publish(self, topic: str, event: Any) -> None:
        # Snapshot — handlers may modify the list mid-iteration
        for fn in list(self._subs[topic]):
            try:
                fn(event)
            except Exception as e:
                print(f"  [bus] handler {fn.__name__} crashed: {e}")


# =====================================================================
# Event payloads — frozen dataclasses keep them safe across handlers
# =====================================================================
@dataclass(frozen=True)
class OrderPaid:
    order_id: str
    total: float


@dataclass(frozen=True)
class OrderRefunded:
    order_id: str
    amount: float


@dataclass(frozen=True)
class UserSignedUp:
    user_id: str
    email: str


# =====================================================================
# Handlers — each cares about one topic
# =====================================================================
def email_on_paid(e: OrderPaid) -> None:
    print(f"  [email]      receipt sent for {e.order_id}")

def analytics_on_paid(e: OrderPaid) -> None:
    print(f"  [analytics]  conversion ₹{e.total:.2f} tracked")

def email_on_refund(e: OrderRefunded) -> None:
    print(f"  [email]      refund notice sent for {e.order_id}")

def finance_on_refund(e: OrderRefunded) -> None:
    print(f"  [finance]    booked refund of ₹{e.amount:.2f}")

def welcome_email_on_signup(e: UserSignedUp) -> None:
    print(f"  [email]      welcome email sent to {e.email}")

def crm_on_signup(e: UserSignedUp) -> None:
    print(f"  [crm]        created CRM record for {e.user_id}")


# =====================================================================
# Demo
# =====================================================================
def main() -> None:
    bus = EventBus()

    # one-time wiring (looks like Django's signals.connect)
    bus.subscribe("order.paid",     email_on_paid)
    bus.subscribe("order.paid",     analytics_on_paid)
    bus.subscribe("order.refunded", email_on_refund)
    bus.subscribe("order.refunded", finance_on_refund)
    bus.subscribe("user.signed_up", welcome_email_on_signup)
    bus.subscribe("user.signed_up", crm_on_signup)

    print("Publishing user.signed_up:")
    bus.publish("user.signed_up", UserSignedUp(user_id="u_42", email="ada@scaler.com"))

    print("\nPublishing order.paid:")
    bus.publish("order.paid", OrderPaid(order_id="ORD-9001", total=2499.0))

    print("\nPublishing order.refunded:")
    bus.publish("order.refunded", OrderRefunded(order_id="ORD-9001", amount=2499.0))

    print("\nNotice the 'email' handler appears in THREE topics — but as")
    print("THREE separate functions. Each is small, focused, testable.")


if __name__ == "__main__":
    main()
