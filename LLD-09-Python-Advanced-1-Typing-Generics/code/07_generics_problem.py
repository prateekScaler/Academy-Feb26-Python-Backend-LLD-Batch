"""The problem that Generics solve — type safety with reusable code."""


# --- A simple container ---
class Box:
    def __init__(self, item):
        self.item = item

    def get(self):
        return self.item


# Works with anything — but no type safety
int_box = Box(42)
str_box = Box("hello")

# What type is result? Python and IDE have NO IDEA.
result = int_box.get()

result.upper()  # Runtime crash! But IDE can't warn you.
print(f"int_box.get() = {result}")
print(f"  type: {type(result)}")
print(f"  IDE thinks: 'Any' — no autocomplete, no warnings\n")


# --- Attempt 1: Separate classes for each type? ---
class IntBox:
    def __init__(self, item: int):
        self.item = item

    def get(self) -> int:
        return self.item


class StrBox:
    def __init__(self, item: str):
        self.item = item

    def get(self) -> str:
        return self.item


int_box2 = IntBox(42)
str_box2 = StrBox("hello")

# Now IDE knows the types! But...
print("Separate classes work but...")
print(f"  IntBox(42).get() = {int_box2.get()}")
print(f"  StrBox('hello').get() = {str_box2.get()}")
print("  Problem: we need a new class for EVERY type.")
print("  IntBox, StrBox, FloatBox, UserBox, OrderBox...")
print("  This doesn't scale.\n")


# --- Attempt 2: Use Any? ---
from typing import Any


class AnyBox:
    def __init__(self, item: Any):
        self.item = item

    def get(self) -> Any:
        return self.item


# No type safety at all — we're back to square one
any_box = AnyBox(42)
result2: Any = any_box.get()
print("Using Any:")
print(f"  AnyBox(42).get() = {result2}")
print("  Problem: mypy can't catch errors. 'Any' means 'give up type checking'.")
print("\nWe need: ONE class that works with ANY type,")
print("         but remembers WHICH type was put in.")
print("         → That's what Generics do.")
