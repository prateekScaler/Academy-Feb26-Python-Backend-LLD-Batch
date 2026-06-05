"""
LLD-20 · Decorator · Example 8 — Class-based decorators (callable instances).

Run:  python3 08_class_based_decorators.py

When a decorator needs to hold state across calls (e.g., a hit
counter for a rate limiter, a cache, an instance ID), implementing
it as a class with __call__ is cleaner than nesting closures.

Demonstrates:
  - Rate limiter as a class-based decorator (holds call count + reset time)
  - Memoiser as a class-based decorator (holds the cache)
  - When to choose class-based vs function-based decorators
"""

from __future__ import annotations
import time
import functools
from typing import Any, Callable


# ====================================================================
# Class-based decorator: RateLimit
# Hold state (call count, window) cleanly as instance attributes.
# ====================================================================
class RateLimit:
    """@RateLimit(max_per_second=5) on a function."""

    def __init__(self, max_per_second: int) -> None:
        self._interval = 1.0 / max_per_second

    def __call__(self, func: Callable) -> Callable:
        last_call = 0.0

        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            nonlocal last_call
            wait = self._interval - (time.time() - last_call)
            if wait > 0:
                time.sleep(wait)
            last_call = time.time()
            return func(*args, **kwargs)

        return wrapper


# ====================================================================
# Class-based decorator: CountCalls
# Direct attribute access on the decorator instance.
# ====================================================================
class CountCalls:
    """@CountCalls on a function. Exposes .calls counter."""

    def __init__(self, func: Callable) -> None:
        functools.update_wrapper(self, func)         # same as @wraps for class-decorators
        self.func = func
        self.calls = 0

    def __call__(self, *args, **kwargs):
        self.calls += 1
        return self.func(*args, **kwargs)


# ====================================================================
# Class-based decorator: Memoize with rich introspection
# ====================================================================
class Memoize:
    """@Memoize on a function. Like functools.cache but with stats."""

    def __init__(self, func: Callable) -> None:
        functools.update_wrapper(self, func)
        self.func = func
        self.cache: dict[tuple, Any] = {}
        self.hits = 0
        self.misses = 0

    def __call__(self, *args, **kwargs):
        key = (args, tuple(sorted(kwargs.items())))
        if key in self.cache:
            self.hits += 1
            return self.cache[key]
        self.misses += 1
        result = self.func(*args, **kwargs)
        self.cache[key] = result
        return result

    def stats(self) -> str:
        total = self.hits + self.misses
        rate = self.hits / total * 100 if total else 0.0
        return f"  hits={self.hits} misses={self.misses} hit_rate={rate:.1f}%"


# ====================================================================
# Usage
# ====================================================================
@CountCalls
def add(a: int, b: int) -> int:
    return a + b


@Memoize
def slow_square(n: int) -> int:
    time.sleep(0.02)        # pretend it's expensive
    return n * n


@RateLimit(max_per_second=3)
def ping() -> str:
    return "pong"


# ====================================================================
# Demo
# ====================================================================
def main() -> None:
    print("--- CountCalls: state visible on the decorator itself ---")
    add(1, 2); add(3, 4); add(5, 6)
    print(f"  add.calls = {add.calls}")
    print(f"  add.__name__ = {add.__name__!r}  (preserved via update_wrapper)")

    print("\n--- Memoize: cache + stats accessible ---")
    for n in [4, 4, 5, 5, 5, 6]:
        slow_square(n)
    print(slow_square.stats())

    print("\n--- RateLimit: enforces gaps between calls ---")
    t0 = time.perf_counter()
    for _ in range(5):
        ping()
    elapsed = time.perf_counter() - t0
    print(f"  5 calls at 3/s rate-limit: took {elapsed:.2f}s (expected ~1.3s)")

    print("\nWhen to pick CLASS-based over function-based:")
    print("  • You need stateful behaviour the caller might want to read")
    print("    (cache stats, call counts, rate-limit windows)")
    print("  • You want to expose helper methods (e.g., decorator.clear_cache())")
    print("  • The decorator takes arguments AND has state")
    print("\nWhen to stick with function-based:")
    print("  • Pure transformation (logging, timing, simple before/after work)")
    print("  • No state to expose")


if __name__ == "__main__":
    main()
