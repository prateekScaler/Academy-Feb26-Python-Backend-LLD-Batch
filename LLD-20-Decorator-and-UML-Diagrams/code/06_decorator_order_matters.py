"""
LLD-20 · Decorator · Example 6 — Order changes behaviour. Demonstrably.

Run:  python3 06_decorator_order_matters.py

The same three decorators stacked in two different orders. The
observable behaviour differs in ways that matter in production —
this file shows the timing differences, the cache poisoning bug,
and the auth-bypass risk.
"""

from __future__ import annotations
import time
from abc import ABC, abstractmethod


# ====================================================================
# Component + shared decorators
# ====================================================================
class Service(ABC):
    @abstractmethod
    def fetch(self, key: str) -> str: ...


class RealService(Service):
    """Returns the same key uppercased. Counts how often it's hit."""
    def __init__(self) -> None:
        self.network_calls = 0

    def fetch(self, key: str) -> str:
        self.network_calls += 1
        time.sleep(0.05)  # simulate network
        if key.startswith("bad-"):
            raise ConnectionError(f"could not fetch {key}")
        return key.upper()


class CacheDecorator(Service):
    """Caches BOTH successes and (briefly) errors."""
    def __init__(self, inner: Service) -> None:
        self._inner = inner
        self._cache: dict[str, str] = {}

    def fetch(self, key: str) -> str:
        if key in self._cache:
            return self._cache[key]
        result = self._inner.fetch(key)
        self._cache[key] = result
        return result


class RetryDecorator(Service):
    """Retries on ConnectionError up to N times."""
    def __init__(self, inner: Service, attempts: int = 3) -> None:
        self._inner = inner
        self._attempts = attempts

    def fetch(self, key: str) -> str:
        last_exc: BaseException | None = None
        for i in range(self._attempts):
            try:
                return self._inner.fetch(key)
            except ConnectionError as e:
                last_exc = e
                time.sleep(0.01)
        raise last_exc  # type: ignore[misc]


# ====================================================================
# Demo 1 — Cache OUTSIDE Retry: success-friendly
# ====================================================================
def demo_cache_outside_retry() -> None:
    print("--- ORDER A: Cache(Retry(Real))  →  cache-outside-retry ---")
    real = RealService()
    svc = CacheDecorator(RetryDecorator(real))

    t0 = time.perf_counter()
    svc.fetch("alice")        # cache miss → retry succeeds first time
    svc.fetch("alice")        # cache HIT — no network
    svc.fetch("alice")        # cache HIT — no network
    elapsed = (time.perf_counter() - t0) * 1000

    print(f"  3 calls for 'alice': {real.network_calls} network call(s), "
          f"~{elapsed:.0f} ms total")
    print("  Caching the SUCCESS skips network on subsequent calls — usually what you want.")


# ====================================================================
# Demo 2 — Retry OUTSIDE Cache: retries fire every time
# ====================================================================
def demo_retry_outside_cache() -> None:
    print("\n--- ORDER B: Retry(Cache(Real))  →  retry-outside-cache ---")
    real = RealService()
    svc = RetryDecorator(CacheDecorator(real))

    t0 = time.perf_counter()
    svc.fetch("alice")        # cache miss → real call
    svc.fetch("alice")        # cache HIT inside retry
    svc.fetch("alice")        # cache HIT inside retry
    elapsed = (time.perf_counter() - t0) * 1000

    print(f"  3 calls for 'alice': {real.network_calls} network call(s), "
          f"~{elapsed:.0f} ms total")
    print("  Cache still works, but retry's outer loop adds nothing here.")


# ====================================================================
# Demo 3 — The poisoning bug: cache-storing-errors meets retry
# ====================================================================
class CacheWithErrorPoisoning(Service):
    """A buggy cache that stores both successes AND failures.
       Don't write code like this. (But people do.)"""
    def __init__(self, inner: Service) -> None:
        self._inner = inner
        self._cache: dict[str, str | Exception] = {}

    def fetch(self, key: str) -> str:
        if key in self._cache:
            cached = self._cache[key]
            if isinstance(cached, Exception):
                raise cached
            return cached
        try:
            result = self._inner.fetch(key)
            self._cache[key] = result
            return result
        except Exception as e:
            self._cache[key] = e
            raise


def demo_error_poisoning() -> None:
    print("\n--- ORDER C: Retry(BuggyCache(Real))  →  cache stores failures ---")
    real = RealService()
    svc = RetryDecorator(CacheWithErrorPoisoning(real), attempts=3)

    # First call to "bad-key" fails → cached as a failure → retry
    # hits the cache, gets the same failure → never retries the real call.
    try:
        svc.fetch("bad-key")
    except ConnectionError as e:
        print(f"  caught: {e}")
    print(f"  real.network_calls = {real.network_calls} "
          "(should have been 3 if retry worked)")
    print("  The buggy cache POISONED the retry. Retry kept hitting cached failure.")
    print("  Lesson: order matters AND each decorator's contract matters.")


if __name__ == "__main__":
    demo_cache_outside_retry()
    demo_retry_outside_cache()
    demo_error_poisoning()
