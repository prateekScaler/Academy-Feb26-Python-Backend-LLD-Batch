"""
LLD-19 · Observer · Example 10 — Async Observer with asyncio.gather.

Run:  python3 10_async_observer.py

When observers do I/O (HTTP calls, DB writes, email sends), running
them synchronously in a `for` loop makes the publisher wait for the
sum of all observer latencies. With asyncio.gather, they run
concurrently — the publisher waits only for the slowest one.

Real-world payoff: in a Django + asyncio app or an aiohttp service,
an order-paid handler that fires four observers (each ~200 ms of
remote I/O) goes from ~800 ms to ~200 ms.
"""

from __future__ import annotations
import asyncio
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass(frozen=True)
class OrderPaidEvent:
    order_id: str
    total: float


# =====================================================================
# Async observer interface
# =====================================================================
class AsyncObserver(ABC):
    @abstractmethod
    async def on_paid(self, event: OrderPaidEvent) -> None: ...


# =====================================================================
# Three observers, each simulating remote I/O (sleeps)
# =====================================================================
class EmailObserver(AsyncObserver):
    async def on_paid(self, event):
        await asyncio.sleep(0.2)            # mimic SMTP latency
        print(f"  [email]     sent for {event.order_id}")


class WarehouseObserver(AsyncObserver):
    async def on_paid(self, event):
        await asyncio.sleep(0.3)            # mimic warehouse API
        print(f"  [warehouse] queued {event.order_id}")


class AnalyticsObserver(AsyncObserver):
    async def on_paid(self, event):
        await asyncio.sleep(0.15)           # mimic analytics POST
        print(f"  [analytics] tracked ₹{event.total:.2f}")


# =====================================================================
# Subject with TWO notify strategies — sync-style and async-gather
# =====================================================================
class AsyncOrder:
    def __init__(self) -> None:
        self._observers: list[AsyncObserver] = []

    def subscribe(self, obs: AsyncObserver) -> None:
        self._observers.append(obs)

    async def mark_paid_sequential(self, event: OrderPaidEvent) -> None:
        """Naive — `await` each observer one after the other. Slow."""
        for obs in self._observers:
            await obs.on_paid(event)

    async def mark_paid_concurrent(self, event: OrderPaidEvent) -> None:
        """Right — asyncio.gather runs them concurrently. Fast."""
        # return_exceptions=True so one failure doesn't cancel siblings
        results = await asyncio.gather(
            *[obs.on_paid(event) for obs in self._observers],
            return_exceptions=True,
        )
        # Log any exceptions (handlers should never crash the publisher)
        for obs, r in zip(self._observers, results):
            if isinstance(r, Exception):
                print(f"  [order] {obs.__class__.__name__} failed: {r}")


# =====================================================================
# Demo
# =====================================================================
async def main() -> None:
    order = AsyncOrder()
    order.subscribe(EmailObserver())
    order.subscribe(WarehouseObserver())
    order.subscribe(AnalyticsObserver())
    event = OrderPaidEvent(order_id="ORD-001", total=2499.0)

    print("--- Sequential notify (await each in turn) ---")
    t0 = time.monotonic()
    await order.mark_paid_sequential(event)
    print(f"  total wall-clock: {(time.monotonic() - t0) * 1000:.0f} ms\n")

    print("--- Concurrent notify (asyncio.gather) ---")
    t0 = time.monotonic()
    await order.mark_paid_concurrent(event)
    print(f"  total wall-clock: {(time.monotonic() - t0) * 1000:.0f} ms")

    print("""
Sequential ≈ sum of observer latencies (0.2 + 0.3 + 0.15 ≈ 650 ms).
Concurrent ≈ max of observer latencies (~300 ms — bound by the slowest).

asyncio.gather + return_exceptions=True is the idiomatic shape for
in-process Observer when your codebase is already async.
""")


if __name__ == "__main__":
    asyncio.run(main())
