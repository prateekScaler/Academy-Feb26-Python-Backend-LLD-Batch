"""Protocol — duck typing with type safety (from last class, uncovered).

KEY IDEA: ABC forces inheritance. Protocol doesn't.
"If it has the right methods, it's valid." — like Go interfaces.
"""
from typing import Protocol, runtime_checkable


# --- Problem: ABC forces inheritance ---
# from abc import ABC, abstractmethod
# class Drawable(ABC):
#     @abstractmethod
#     def draw(self) -> str: ...
#
# class Circle(Drawable):   # MUST inherit Drawable
#     def draw(self) -> str: return "○"
#
# What if Circle comes from a third-party library?
# You CAN'T make it inherit from YOUR ABC!


# --- Solution: Protocol — structural typing ---
class Drawable(Protocol):
    """Any class with a draw() -> str method satisfies this."""
    def draw(self) -> str: ...


# These DON'T inherit from Drawable — they just have draw()
class Circle:
    def __init__(self, radius: float):
        self.radius = radius

    def draw(self) -> str:
        return f"○ Circle(r={self.radius})"


class Square:
    def __init__(self, side: float):
        self.side = side

    def draw(self) -> str:
        return f"□ Square(s={self.side})"


class Text:
    def __init__(self, content: str):
        self.content = content

    def draw(self) -> str:
        return f'T "{self.content}"'


# Accepts ANYTHING with draw() -> str
def render_all(shapes: list[Drawable]) -> None:
    for shape in shapes:
        print(f"  {shape.draw()}")


print("Protocol — structural typing:\n")
render_all([Circle(5), Square(3), Text("Hello")])
# All 3 work — none inherit from Drawable!


# --- runtime_checkable: isinstance() with Protocol ---
@runtime_checkable
class Sized(Protocol):
    def __len__(self) -> int: ...


print(f"\nruntime_checkable:")
print(f"  isinstance([1,2,3], Sized) = {isinstance([1,2,3], Sized)}")
print(f"  isinstance('hello', Sized) = {isinstance('hello', Sized)}")
print(f"  isinstance(42, Sized)      = {isinstance(42, Sized)}")


# --- When to use which ---
print("\n--- Protocol vs ABC ---")
print("  ABC:      You OWN the class hierarchy. Subclasses must inherit.")
print("  Protocol: You DON'T control the classes. Just need a contract.")
print("            Works with third-party code, plugins, duck typing.")
