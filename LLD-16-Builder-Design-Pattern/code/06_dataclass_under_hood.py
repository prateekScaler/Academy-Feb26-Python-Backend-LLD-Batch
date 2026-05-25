"""
06 - How @dataclass works (toy implementation)
==============================================

The real `@dataclass` decorator in the stdlib has knobs like `frozen`,
`order`, `slots`, `kw_only`, `field(default_factory=...)` - many edge cases.

But the CORE mechanic is just 4 ideas:

  1. A decorator is a function that takes a class and returns it modified
  2. cls.__annotations__ gives you the type-hinted fields
  3. You can attach methods to the class at runtime
  4. Return the class - Python treats it like any other class

This file builds a homemade @my_dataclass in ~30 lines that gives you
the same headline features as @dataclass: auto __init__, __repr__, __eq__.

Connects to:
  - LLD-11 decorators (functions that wrap other things)
  - LLD-15 metaclass primer (classes are objects you can modify)
"""

# ---------------------------------------------------------------------------
# The toy decorator
# ---------------------------------------------------------------------------

def my_dataclass(cls):
    """Add __init__, __repr__, and __eq__ derived from cls.__annotations__."""
    # Step 1: read the type hints written on the class
    #   e.g. {'x': int, 'y': int}
    fields = cls.__annotations__

    # Step 2: generate __init__ that assigns each annotated field
    def __init__(self, **kwargs):
        for name in fields:
            if name not in kwargs:
                raise TypeError(f"missing field: {name}")
            setattr(self, name, kwargs[name])

    # Step 3: generate __repr__ like "Point(x=1, y=2)"
    def __repr__(self):
        parts = [f"{name}={getattr(self, name)!r}" for name in fields]
        return f"{cls.__name__}({', '.join(parts)})"

    # Step 4: generate __eq__ that compares all field values
    def __eq__(self, other):
        if not isinstance(other, cls):
            return False
        return all(getattr(self, n) == getattr(other, n) for n in fields)

    # Step 5: attach the generated methods to the class and return it
    cls.__init__ = __init__
    cls.__repr__ = __repr__
    cls.__eq__   = __eq__
    return cls


# ---------------------------------------------------------------------------
# Demo - use it like the real @dataclass
# ---------------------------------------------------------------------------

@my_dataclass
class Point:
    x: int
    y: int


@my_dataclass
class Database:
    host: str
    port: int
    username: str


def demo():
    print("--- Auto-generated __init__ ---")
    p = Point(x=1, y=2)
    print(f"p.x = {p.x}, p.y = {p.y}")

    print("\n--- Auto-generated __repr__ ---")
    print(p)                                  # Point(x=1, y=2)

    print("\n--- Auto-generated __eq__ ---")
    print(f"Point(1,2) == Point(1,2): {Point(x=1, y=2) == Point(x=1, y=2)}")
    print(f"Point(1,2) == Point(1,3): {Point(x=1, y=2) == Point(x=1, y=3)}")

    print("\n--- Works on any class with annotations ---")
    db = Database(host="localhost", port=5432, username="admin")
    print(db)

    print("\n--- Missing field is caught ---")
    try:
        Point(x=1)
    except TypeError as e:
        print(f"TypeError: {e}")


# ---------------------------------------------------------------------------
# Comparison: real @dataclass gives you the same things
# ---------------------------------------------------------------------------

def compare_with_real_dataclass():
    print("\n=== Same result with the real @dataclass ===")
    from dataclasses import dataclass

    @dataclass
    class RealPoint:
        x: int
        y: int

    p = RealPoint(1, 2)                # positional args also work (real one is fancier)
    print(p)                            # RealPoint(x=1, y=2)
    print(RealPoint(1, 2) == RealPoint(1, 2))

    # Things the real one has that our toy doesn't:
    #   - positional args
    #   - default values via `field(default=...)` and `field(default_factory=...)`
    #   - frozen=True for immutability
    #   - order=True for __lt__/__le__/__gt__/__ge__
    #   - slots=True for memory efficiency
    #   - asdict(), astuple(), replace() utilities
    # ...but the CORE - "read annotations, generate methods, attach them" -
    # is what we just did in 15 lines.


if __name__ == "__main__":
    demo()
    compare_with_real_dataclass()
