"""Callable explained — what it is, why you need it, simple examples.

KEY IDEA: In Python, functions are objects. You can pass them around
just like you pass integers or strings. Callable is how you TYPE that.
"""

# ─── PART 1: Functions are objects ───

def add(a, b):
    return a + b

def multiply(a, b):
    return a * b

# You can store a function in a variable:
operation = add          # NOT add() — no parentheses = the function itself
print(operation(3, 4))   # 7 — calling the variable calls the function

operation = multiply
print(operation(3, 4))   # 12 — same variable, different function


# ─── PART 2: Passing a function to another function ───

def do_math(a, b, func):
    """Takes two numbers AND a function, calls that function."""
    return func(a, b)

print(do_math(5, 3, add))       # 8   — we passed the add function
print(do_math(5, 3, multiply))  # 15  — we passed the multiply function

# But what TYPE is 'func'? Looking at the signature:
#   def do_math(a, b, func):
# A new developer asks: "What should func look like?"
# "Does it take 2 args? 3? What does it return?"
# NO WAY TO KNOW without reading the implementation.


# ─── PART 3: Callable — typing a function parameter ───

from typing import Callable

# Callable[[<parameter types>], <return type>]
#
# Callable[[int, int], int]  means:
#   - A function that takes (int, int)
#   - And returns int
#
# That's it. It's the TYPE of a function.

def do_math_typed(a: int, b: int, func: Callable[[int, int], int]) -> int:
    """Now it's clear: func takes 2 ints, returns an int."""
    return func(a, b)

# These work (signature matches):
print(do_math_typed(5, 3, add))       # 8
print(do_math_typed(5, 3, multiply))  # 15

# This would be a mypy error:
# do_math_typed(5, 3, len)  # len takes 1 arg, not 2


# ─── PART 4: More examples ───

# Example: a function that takes NO args and returns a string
def get_greeting() -> str:
    return "Hello!"

greeter: Callable[[], str] = get_greeting
#         ^^^^^^^^^^^^^^^^^^
#         [] = no parameters
#         str = returns string

print(greeter())  # "Hello!"


# Example: a function that takes a string and returns nothing
def log_message(msg: str) -> None:
    print(f"[LOG] {msg}")

logger: Callable[[str], None] = log_message
#        ^^^^^^^^^^^^^^^^^^^
#        [str] = one string parameter
#        None = returns nothing

logger("Server started")


# Example: a callback / event handler
def on_click(handler: Callable[[int, int], None]) -> None:
    """Simulates a click at position (x, y)."""
    x, y = 100, 200
    handler(x, y)  # call the function the user passed in

def my_handler(x: int, y: int) -> None:
    print(f"Clicked at ({x}, {y})")

on_click(my_handler)  # "Clicked at (100, 200)"


# ─── SUMMARY ───
print("\n" + "=" * 50)
print("Callable cheatsheet:")
print("=" * 50)
print()
print("  Callable[[int, int], int]   → takes (int, int), returns int")
print("  Callable[[str], None]       → takes (str), returns nothing")
print("  Callable[[], str]           → takes nothing, returns str")
print("  Callable[[dict], list[str]] → takes dict, returns list of strings")
print()
print("  When to use:")
print("  • Any function that accepts another function as a parameter")
print("  • Callbacks, event handlers, strategies, decorators, middleware")
print("  • Without it, no one knows what shape the function should be")
