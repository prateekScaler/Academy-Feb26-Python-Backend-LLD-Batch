"""
05 - When a Factory is OVER-engineering
=======================================

A bad-taste demo. Some classes have zero "which concrete class?" choice -
their constructor is already perfect. Wrapping them in a Factory just adds
ceremony.

Three triggers that justify ANY factory:
  1. Same construction logic appears in many call sites      (DRY)
  2. You add new types and want to stop modifying old code   (OCP)
  3. Products travel in families that must match             (consistency)

If none of these are true: skip the factory.
"""

from dataclasses import dataclass


# ---------------------------------------------------------------------------
# A class that has no business being behind a factory
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class Point:
    x: float
    y: float


# ===========================================================================
# Anti-pattern: PointFactory wraps the constructor for... no reason
# ===========================================================================

class PointFactory:
    @staticmethod
    def create(x: float, y: float) -> Point:
        return Point(x, y)

    @staticmethod
    def origin() -> Point:
        # NOTE: this one ISN'T quite as silly - a 'named constructor' for
        # a common case is fine. But it doesn't need a whole Factory class;
        # a module-level function or @classmethod would do.
        return Point(0.0, 0.0)


# ===========================================================================
# What you should write instead
# ===========================================================================

# Just call the constructor. There's no choice to centralize.
def good_usage():
    p1 = Point(10, 20)
    p2 = Point(3, 4)
    return p1, p2


# If you want a named constructor for a special case, use @classmethod -
# no separate Factory class needed.
@dataclass(frozen=True)
class Point2:
    x: float
    y: float

    @classmethod
    def origin(cls) -> "Point2":
        return cls(0.0, 0.0)

    @classmethod
    def from_polar(cls, r: float, theta: float) -> "Point2":
        # A legitimate alternate construction path. NOT a separate factory.
        import math
        return cls(r * math.cos(theta), r * math.sin(theta))


# ---------------------------------------------------------------------------
# Demo
# ---------------------------------------------------------------------------

def demo():
    print("--- ANTI: silly PointFactory wraps the constructor ---")
    p = PointFactory.create(10, 20)
    print(f"  {p}")
    print(f"  origin = {PointFactory.origin()}")

    print("\n--- GOOD: just use the constructor ---")
    p1, p2 = good_usage()
    print(f"  {p1}, {p2}")

    print("\n--- GOOD: named constructors via @classmethod (no factory class) ---")
    print(f"  Point2.origin()         = {Point2.origin()}")
    print(f"  Point2.from_polar(1,0)  = {Point2.from_polar(1.0, 0.0)}")

    print("""
Rule of thumb: if removing the factory and inlining `ConcreteClass(...)` at
the call site makes the code shorter and equally clear, you didn't need
the factory.
""")


if __name__ == "__main__":
    demo()
