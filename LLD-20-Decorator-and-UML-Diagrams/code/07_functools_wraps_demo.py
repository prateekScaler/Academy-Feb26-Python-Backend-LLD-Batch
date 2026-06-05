"""
LLD-20 · Decorator · Example 7 — @functools.wraps. Why it matters, demonstrably.

Run:  python3 07_functools_wraps_demo.py

Every Python decorator you write should use @functools.wraps on the
inner wrapper function. This file shows what breaks without it and
how the fix is one line.
"""

from __future__ import annotations
import functools
import inspect


# ====================================================================
# A decorator WITHOUT functools.wraps — the common bug
# ====================================================================
def bad_log(func):
    def wrapper(*args, **kwargs):
        print(f"  calling")
        return func(*args, **kwargs)
    return wrapper


# ====================================================================
# Same decorator WITH @functools.wraps — the fix
# ====================================================================
def good_log(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        print(f"  calling")
        return func(*args, **kwargs)
    return wrapper


# ====================================================================
# Two functions decorated each way
# ====================================================================
@bad_log
def add_bad(a: int, b: int) -> int:
    """Add two numbers and return the result."""
    return a + b


@good_log
def add_good(a: int, b: int) -> int:
    """Add two numbers and return the result."""
    return a + b


# ====================================================================
# Demo: what breaks without @wraps
# ====================================================================
def show_metadata(label: str, fn) -> None:
    print(f"\n--- {label} ---")
    print(f"  __name__  : {fn.__name__!r}")
    print(f"  __doc__   : {fn.__doc__!r}")
    print(f"  __module__: {fn.__module__!r}")
    print(f"  signature : {inspect.signature(fn)}")
    print(f"  source    : {inspect.getsourcefile(fn)}")


def main() -> None:
    show_metadata("WITHOUT @functools.wraps (add_bad)", add_bad)
    show_metadata("WITH @functools.wraps (add_good)", add_good)

    print("\nWhat breaks without @wraps:")
    print("  • Sphinx / mkdocs / pydoc all document the function as 'wrapper'")
    print("  • Stack traces show 'wrapper' instead of the real function name")
    print("  • Type checkers and IDE autocomplete lose the original signature")
    print("  • pytest fixture matching / mocking-by-name silently misses targets")
    print("  • Pydantic and FastAPI runtime introspection breaks")

    print("\nRule: every decorator's inner function gets @functools.wraps(func).")
    print("There is no situation in production Python where you should skip it.")


if __name__ == "__main__":
    main()
