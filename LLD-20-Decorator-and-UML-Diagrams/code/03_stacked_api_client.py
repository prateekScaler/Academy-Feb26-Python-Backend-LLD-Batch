"""
LLD-20 · Decorator · Example 3 — Stacked decorators for an API client.

Run:  python3 03_stacked_api_client.py

Riya's "5! = 32 subclasses" problem, solved.

Five orthogonal cross-cutting concerns (caching, retry, logging,
auth, rate-limiting) each as one class. Pick any subset, in any
order, at runtime. The Component interface (ApiClient) never
grows.

This file is designed to render cleanly in PyCharm's UML class
diagram view — each decorator implements ApiClient AND has a
composition arrow back to ApiClient.
"""

from __future__ import annotations
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass


# ====================================================================
# Component
# ====================================================================
class ApiClient(ABC):
    @abstractmethod
    def get(self, url: str) -> str: ...


# ====================================================================
# ConcreteComponent — simulated unreliable backend
# ====================================================================
class BasicApiClient(ApiClient):
    """Pretends to be a real HTTP client. First call to any URL fails."""
    def __init__(self) -> None:
        self._seen: set[str] = set()
        self.network_calls = 0

    def get(self, url: str) -> str:
        self.network_calls += 1
        if url not in self._seen:
            self._seen.add(url)
            raise ConnectionError(f"transient error fetching {url}")
        return f"<payload for {url}>"


# ====================================================================
# Five orthogonal Decorators
# ====================================================================
class CachingDecorator(ApiClient):
    def __init__(self, inner: ApiClient, ttl_seconds: float = 60.0) -> None:
        self._inner = inner
        self._ttl = ttl_seconds
        self._cache: dict[str, tuple[float, str]] = {}

    def get(self, url: str) -> str:
        now = time.time()
        if url in self._cache:
            ts, payload = self._cache[url]
            if now - ts < self._ttl:
                print(f"    [cache] hit for {url}")
                return payload
        payload = self._inner.get(url)
        self._cache[url] = (now, payload)
        return payload


class RetryDecorator(ApiClient):
    def __init__(self, inner: ApiClient, attempts: int = 3) -> None:
        self._inner = inner
        self._attempts = attempts

    def get(self, url: str) -> str:
        last_exc: BaseException | None = None
        for i in range(self._attempts):
            try:
                return self._inner.get(url)
            except ConnectionError as e:
                print(f"    [retry] attempt {i+1} failed: {e}")
                last_exc = e
                time.sleep(0.01 * (2 ** i))
        raise last_exc  # type: ignore[misc]


class LoggingDecorator(ApiClient):
    def __init__(self, inner: ApiClient) -> None:
        self._inner = inner

    def get(self, url: str) -> str:
        print(f"  [log] GET {url}")
        result = self._inner.get(url)
        print(f"  [log] GET {url} → {len(result)} bytes")
        return result


@dataclass
class AuthToken:
    token: str


class AuthDecorator(ApiClient):
    def __init__(self, inner: ApiClient, token: AuthToken) -> None:
        self._inner = inner
        self._token = token

    def get(self, url: str) -> str:
        # In real code: add Authorization header here
        print(f"  [auth] attached token {self._token.token[:4]}...")
        return self._inner.get(url)


class RateLimitDecorator(ApiClient):
    def __init__(self, inner: ApiClient, max_per_second: int = 10) -> None:
        self._inner = inner
        self._interval = 1.0 / max_per_second
        self._last = 0.0

    def get(self, url: str) -> str:
        wait = self._interval - (time.time() - self._last)
        if wait > 0:
            time.sleep(wait)
        self._last = time.time()
        return self._inner.get(url)


# ====================================================================
# Demo
# ====================================================================
def main() -> None:
    print("Building: Logging(Auth(Cache(Retry(Basic))))")
    client: ApiClient = LoggingDecorator(
        AuthDecorator(
            CachingDecorator(
                RetryDecorator(
                    BasicApiClient()
                )
            ),
            token=AuthToken(token="abcd-1234"),
        )
    )

    print("\n--- First call: cache miss, first attempt fails, retry succeeds ---")
    print("  result:", client.get("/users/1"))

    print("\n--- Second call to same URL: cache HIT, no network ---")
    print("  result:", client.get("/users/1"))

    print("\n--- New URL: cache miss again ---")
    print("  result:", client.get("/users/2"))

    print("\nObserve the call ordering:")
    print("  log → auth → cache check → retry → basic client")
    print("On the second /users/1 call, the cache decorator short-circuits")
    print("BEFORE retry, before basic — saving auth and basic-client work.")


if __name__ == "__main__":
    main()
