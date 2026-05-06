"""Callable types — typing functions that accept other functions."""
from typing import Callable


# --- Problem: what does this 'handler' parameter expect? ---
def bad_retry(func, max_retries):
    """What signature should func have? No idea from this definition."""
    for i in range(max_retries):
        try:
            return func()
        except Exception:
            if i == max_retries - 1:
                raise


# --- Solution: Callable[[param_types], return_type] ---
def retry(func: Callable[[], str], max_retries: int = 3) -> str:
    """func takes no args, returns str. Crystal clear."""
    for i in range(max_retries):
        try:
            return func()
        except Exception:
            if i == max_retries - 1:
                raise
    return ""  # unreachable, but makes mypy happy


# --- More Callable examples ---

# Function that takes (int, int) and returns int
MathOp = Callable[[int, int], int]


def apply_operation(a: int, b: int, op: MathOp) -> int:
    return op(a, b)


def add(x: int, y: int) -> int:
    return x + y


def multiply(x: int, y: int) -> int:
    return x * y


print("Callable types:\n")
print(f"  apply_operation(5, 3, add) = {apply_operation(5, 3, add)}")
print(f"  apply_operation(5, 3, multiply) = {apply_operation(5, 3, multiply)}")


# --- Real-world: event handlers, callbacks, middleware ---
EventHandler = Callable[[str, dict], None]


def on_event(event_name: str, handler: EventHandler) -> None:
    """Register a handler that takes (event_name, data) and returns nothing."""
    data = {"timestamp": "2025-01-01", "source": "system"}
    handler(event_name, data)


def log_handler(event: str, data: dict) -> None:
    print(f"  Event: {event}, Data: {data}")


print("\nEvent handler:")
on_event("user_login", log_handler)

print("\n--- Key insight ---")
print("  Callable[[arg_types...], return_type]")
print("  Callable[[], None]  → no args, returns nothing")
print("  Callable[[int, str], bool]  → takes int and str, returns bool")
print("  This is how you type: decorators, callbacks, strategies, middleware")
