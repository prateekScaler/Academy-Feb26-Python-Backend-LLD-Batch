"""
LLD-20 · Decorator · Example 1 — The minimal class-based Decorator.

Run:  python3 01_basic_class_decorator.py

Three roles, spelled out:
    Component         — the interface every layer implements
    ConcreteComponent — does the real work
    Decorator         — wraps a Component, exposes the same interface,
                        adds behaviour around the wrapped call

Riya's API client, distilled to its smallest shape.
"""

from __future__ import annotations
from abc import ABC, abstractmethod


# ====================================================================
# Component — the common interface
# ====================================================================
class ApiClient(ABC):
    @abstractmethod
    def get(self, url: str) -> str: ...


# ====================================================================
# ConcreteComponent — does the actual work
# ====================================================================
class BasicApiClient(ApiClient):
    def get(self, url: str) -> str:
        # In real code this would be requests.get(url).text
        return f"<response for {url}>"


# ====================================================================
# Decorator — exposes the same interface AND holds a Component
# ====================================================================
class LoggingDecorator(ApiClient):
    def __init__(self, inner: ApiClient) -> None:
        self._inner = inner

    def get(self, url: str) -> str:
        print(f"  [log] GET {url}")
        result = self._inner.get(url)
        print(f"  [log] → {len(result)} bytes")
        return result


class TimingDecorator(ApiClient):
    def __init__(self, inner: ApiClient) -> None:
        self._inner = inner

    def get(self, url: str) -> str:
        import time
        start = time.perf_counter()
        result = self._inner.get(url)
        ms = (time.perf_counter() - start) * 1000
        print(f"  [timing] GET took {ms:.3f} ms")
        return result


# ====================================================================
# Demo
# ====================================================================
def main() -> None:
    print("--- Plain BasicApiClient, no decorators ---")
    plain: ApiClient = BasicApiClient()
    print("  →", plain.get("/users/1"))

    print("\n--- Wrapped with Logging ---")
    logged: ApiClient = LoggingDecorator(BasicApiClient())
    print("  →", logged.get("/users/2"))

    print("\n--- Wrapped with Timing then Logging (Timing outermost) ---")
    stacked: ApiClient = TimingDecorator(LoggingDecorator(BasicApiClient()))
    print("  →", stacked.get("/users/3"))

    print("\nNote: each Decorator IS an ApiClient AND HOLDS an ApiClient.")
    print("That's what allows the wrapping to stack indefinitely.")


if __name__ == "__main__":
    main()
