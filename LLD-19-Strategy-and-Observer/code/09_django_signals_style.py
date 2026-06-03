"""
LLD-19 · Observer · Example 9 — Django-Signals-style API, from scratch.

Run:  python3 09_django_signals_style.py

This is the EXACT shape Django uses for `post_save`, `pre_delete`, etc.
Built from primitives so you can see the pattern. The @receiver
decorator is the most idiomatic Observer registration in the Python
ecosystem — once you see how it's just a wrapper around .connect(),
Django's signals module reads itself.
"""

from __future__ import annotations
import weakref
from typing import Callable, Any


# =====================================================================
# Signal — the Subject. Holds receivers (weak refs!).
# =====================================================================
class Signal:
    def __init__(self, name: str = "<unnamed>") -> None:
        self.name = name
        self._receivers: list[weakref.ref] = []

    def connect(self, receiver: Callable, sender: type | None = None) -> Callable:
        """Connect a receiver. Returns the receiver so it can be used as a decorator."""
        ref = weakref.ref(receiver)
        # Store sender via closure for filtering at dispatch time
        receiver._sender_filter = sender  # type: ignore[attr-defined]
        self._receivers.append(ref)
        return receiver

    def disconnect(self, receiver: Callable) -> None:
        self._receivers = [r for r in self._receivers if r() is not None and r() is not receiver]

    def send(self, sender: type, **kwargs: Any) -> None:
        """Notify every receiver whose sender filter matches."""
        for ref in list(self._receivers):
            fn = ref()
            if fn is None:
                continue  # GC reclaimed it
            sender_filter = getattr(fn, "_sender_filter", None)
            if sender_filter is None or sender_filter is sender:
                try:
                    fn(sender=sender, **kwargs)
                except Exception as e:
                    print(f"  [signal {self.name}] receiver {fn.__name__} crashed: {e}")


# =====================================================================
# Decorator sugar — exactly Django's @receiver
# =====================================================================
def receiver(signal: Signal, sender: type | None = None) -> Callable:
    """Decorator that connects the wrapped function to the signal."""
    def decorator(fn: Callable) -> Callable:
        return signal.connect(fn, sender=sender)
    return decorator


# =====================================================================
# Define some signals (analogous to django.db.models.signals.post_save)
# =====================================================================
post_save = Signal("post_save")
user_logged_in = Signal("user_logged_in")


# =====================================================================
# Model classes (the senders)
# =====================================================================
class Order:
    def __init__(self, order_id: str, total: float) -> None:
        self.id = order_id; self.total = total

    def save(self) -> None:
        post_save.send(sender=Order, instance=self, created=True)


class User:
    def __init__(self, email: str) -> None:
        self.email = email

    def login(self) -> None:
        user_logged_in.send(sender=User, user=self)


# =====================================================================
# Receivers — exactly the Django pattern
# =====================================================================
@receiver(post_save, sender=Order)
def send_order_confirmation(sender, instance, created, **kwargs):
    print(f"  [email]      order #{instance.id} confirmation sent (₹{instance.total})")


@receiver(post_save, sender=Order)
def update_analytics(sender, instance, created, **kwargs):
    print(f"  [analytics]  +1 order, +₹{instance.total} GMV")


@receiver(post_save)  # no sender filter — listens to EVERY post_save
def audit_log(sender, instance, **kwargs):
    print(f"  [audit]      {sender.__name__} saved")


@receiver(user_logged_in, sender=User)
def record_login(sender, user, **kwargs):
    print(f"  [audit]      {user.email} logged in")


# =====================================================================
# Demo
# =====================================================================
if __name__ == "__main__":
    print("Saving an Order:")
    Order("ORD-001", 999.0).save()

    print("\nLogging in a User:")
    User("ada@scaler.com").login()

    print("""
This is exactly the Django Signals API:

    from django.db.models.signals import post_save
    from django.dispatch import receiver

    @receiver(post_save, sender=MyModel)
    def my_handler(sender, instance, created, **kwargs):
        ...

The @receiver decorator + signal.send() pair IS the Observer pattern —
weakly held, sender-filterable, exception-isolated. ~100 lines above
covers 80% of what Django's `dispatch` module gives you.
""")
