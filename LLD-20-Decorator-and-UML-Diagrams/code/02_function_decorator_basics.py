"""
LLD-20 · Decorator · Example 2 — Python's @-syntax, from first principles.

Run:  python3 02_function_decorator_basics.py

Same pattern as Example 1, but applied to FUNCTIONS instead of
objects. The @-syntax is Python sugar; this file shows what it
actually expands to so the magic is gone.

Demonstrates:
  - The desugared form: greet = log_calls(greet)
  - @functools.wraps and why it matters
  - A decorator that takes arguments
"""

from __future__ import annotations
import functools
import time


# ====================================================================
# 1. The simplest possible decorator
# ====================================================================
def log_calls(func):
    @functools.wraps(func)                          # preserve func metadata
    def wrapper(*args, **kwargs):
        print(f"  [log] calling {func.__name__}({args}, {kwargs})")
        result = func(*args, **kwargs)
        print(f"  [log] → {result!r}")
        return result
    return wrapper


# ====================================================================
# 2. Decorator with arguments — one extra wrapping layer
# ====================================================================
def retry(attempts: int):
    """A parametrised decorator. @retry(attempts=3) on a function."""
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            last_exc: BaseException | None = None
            for i in range(attempts):
                try:
                    return func(*args, **kwargs)
                except Exception as exc:
                    last_exc = exc
                    print(f"  [retry] attempt {i+1} failed: {exc}")
                    time.sleep(0.05 * (2 ** i))
            raise last_exc  # type: ignore[misc]
        return wrapper
    return decorator


# ====================================================================
# Demo usage
# ====================================================================
@log_calls
def greet(name: str) -> str:
    """Greet a person."""
    return f"Hello, {name}"


@retry(attempts=3)
def flaky_network_call(url: str) -> str:
    """Simulates a network call that fails twice then succeeds."""
    flaky_network_call.calls = getattr(flaky_network_call, "calls", 0) + 1
    if flaky_network_call.calls < 3:
        raise ConnectionError(f"could not reach {url}")
    return f"<response for {url}>"


# Two decorators stacked — bottom-up
@log_calls
@retry(attempts=2)
def maybe_works(value: int) -> int:
    """Equivalent to: maybe_works = log_calls(retry(attempts=2)(maybe_works))."""
    if value < 0:
        raise ValueError(f"negative input {value}")
    return value * 2


# ====================================================================
# Main
# ====================================================================
def main() -> None:
    print("--- 1. Simplest decorator: @log_calls ---")
    greet("Ada")
    print(f"\n  greet.__name__ = {greet.__name__!r}  (thanks to functools.wraps)")
    print(f"  greet.__doc__  = {greet.__doc__!r}")

    print("\n--- 2. Equivalent desugared form ---")
    def hi(name: str) -> str:
        return f"Hi, {name}"
    hi = log_calls(hi)                  # exactly what @log_calls does
    hi("Grace")

    print("\n--- 3. Parametrised decorator: @retry(attempts=3) ---")
    print("  result:", flaky_network_call("https://api.example.com"))

    print("\n--- 4. Stacked decorators: @log_calls @retry(attempts=2) ---")
    try:
        maybe_works(5)
        maybe_works(-1)                 # this will retry twice then raise
    except ValueError as e:
        print(f"  caught: {e}")


if __name__ == "__main__":
    main()
