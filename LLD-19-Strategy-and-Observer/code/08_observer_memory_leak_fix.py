"""
LLD-19 · Observer · Example 8 — The classic memory leak, and the fix.

Run:  python3 08_observer_memory_leak_fix.py

The single most-asked Observer-pattern interview gotcha:

  "If you keep subscribing observers but never unsubscribe them, the
   Subject's observer list holds them alive forever. Even after the
   application drops its references, the observers can't be collected."

Demonstrated with `weakref.ref` so the runtime confirms what's actually
in memory. Two implementations side by side:

  UnsafeFeed — uses a plain list, leaks
  SafeFeed   — uses weakref.WeakSet, GC reclaims dropped observers
"""

from __future__ import annotations
import gc
import weakref


# =====================================================================
# Subject implementations
# =====================================================================
class UnsafeFeed:
    """Stores observers in a plain list — strong references → leak."""
    def __init__(self) -> None:
        self._observers: list = []

    def subscribe(self, observer) -> None:
        self._observers.append(observer)        # strong ref, will keep observer alive

    def publish(self, price: float) -> None:
        for obs in self._observers:
            obs.on_price(price)


class SafeFeed:
    """Stores observers in a WeakSet — GC can reclaim dropped observers."""
    def __init__(self) -> None:
        self._observers: weakref.WeakSet = weakref.WeakSet()

    def subscribe(self, observer) -> None:
        self._observers.add(observer)           # weak ref — does not keep alive

    def publish(self, price: float) -> None:
        for obs in self._observers:             # dead refs auto-skipped
            obs.on_price(price)


# =====================================================================
# Observer
# =====================================================================
class Cart:
    counter = 0
    def __init__(self) -> None:
        Cart.counter += 1
        self.id = Cart.counter
    def on_price(self, p: float) -> None: pass


# =====================================================================
# Demo
# =====================================================================
def simulate(feed_cls, label: str) -> None:
    feed = feed_cls()

    # Track observers via weakref so we can see whether they're collected
    refs: list[weakref.ref] = []

    # Create 5 carts and subscribe them. Then "let them go out of scope."
    carts: list = []
    for _ in range(5):
        c = Cart()
        carts.append(c)
        feed.subscribe(c)
        refs.append(weakref.ref(c))

    # Application drops its references
    carts.clear()
    del c

    # Force garbage collection
    gc.collect()

    # How many of the 5 observers were actually reclaimed?
    alive = sum(1 for r in refs if r() is not None)
    print(f"  [{label}] after dropping all 5 carts and gc: {alive}/5 still alive")


if __name__ == "__main__":
    print("--- UnsafeFeed (plain list — leak) ---")
    simulate(UnsafeFeed, "Unsafe")

    print("\n--- SafeFeed (weakref.WeakSet — fixed) ---")
    simulate(SafeFeed, "Safe")

    print("""
The fix is one import and one container swap. Django Signals uses weak
references by default for the same reason: a model save shouldn't pin
every transient view object that ever connected a handler.

(Caveat: bound methods need weakref.WeakMethod or WeakValueDictionary.
 WeakSet on a plain object works as shown above.)
""")
