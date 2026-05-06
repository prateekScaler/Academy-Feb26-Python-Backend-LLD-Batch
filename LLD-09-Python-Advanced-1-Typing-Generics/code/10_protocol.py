"""Protocol — structural typing (duck typing with type safety)."""
from typing import Protocol, runtime_checkable


# --- Problem: ABC forces inheritance ---
# With ABC, every class MUST inherit from the base:
#   class Drawable(ABC):
#       @abstractmethod
#       def draw(self): ...
#
#   class Circle(Drawable):  ← forced to inherit
#       def draw(self): ...
#
# What if you have a third-party class with a draw() method?
# You can't make it inherit from YOUR ABC!


# --- Solution: Protocol — "if it has these methods, it's valid" ---
class Drawable(Protocol):
    """Any class with a draw() method satisfies this — no inheritance needed."""

    def draw(self) -> str: ...


# These classes DON'T inherit from Drawable — they just have draw()
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
        return f"T \"{self.content}\""


# This function accepts ANYTHING with a draw() → str method
def render_all(shapes: list[Drawable]) -> None:
    for shape in shapes:
        print(f"  {shape.draw()}")


print("Protocol — structural typing:\n")
render_all([Circle(5), Square(3), Text("Hello")])
# All 3 classes work — none inherit from Drawable!


# --- runtime_checkable: isinstance() with Protocols ---
@runtime_checkable
class Sized(Protocol):
    def __len__(self) -> int: ...


print("\n\nruntime_checkable Protocol:")
print(f"  isinstance([1,2,3], Sized) = {isinstance([1,2,3], Sized)}")
print(f"  isinstance('hello', Sized) = {isinstance('hello', Sized)}")
print(f"  isinstance(42, Sized) = {isinstance(42, Sized)}")


# --- When to use Protocol vs ABC ---
print("\n--- Protocol vs ABC ---")
print("  ABC: You OWN the hierarchy. Subclasses must inherit.")
print("       → Use for your own class families (Shape, Animal, etc.)")
print("  Protocol: You DON'T control the classes. Just need a contract.")
print("       → Use for third-party code, duck typing, plugins")
print("       → This is how Go interfaces work!")
