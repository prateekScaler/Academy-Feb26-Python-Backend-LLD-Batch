"""You can't create an instance of an ABC directly."""
from abc import ABC, abstractmethod

class Shape(ABC):
    @abstractmethod
    def area(self):
        pass

# Can't create Shape directly:
try:
    s = Shape()
except TypeError as e:
    print(f"Shape() → {e}")

# Must use a concrete child:
class Circle(Shape):
    def __init__(self, radius):
        self.radius = radius
    def area(self):
        return 3.14159 * self.radius ** 2

c = Circle(5)
print(f"Circle area: {c.area():.2f}")
