"""
Duck Typing -- "If It Quacks Like a Duck..."
=============================================
Python doesn't care about the TYPE of an object.
It only cares whether the object has the METHOD you're calling.

"If it walks like a duck and quacks like a duck, it's a duck."

Run: python 06_duck_typing.py
"""


# ============================================================
# 1. The concept
# ============================================================
print("=" * 60)
print("1. Duck Typing -- The Concept")
print("=" * 60)
print()
print('"If it walks like a duck and quacks like a duck, it\'s a duck."')
print()
print("Python doesn't ask: 'Are you a Duck?'")
print("Python asks: 'Can you quack?'")
print()


# ============================================================
# 2. Duck typing in action
# ============================================================
print("=" * 60)
print("2. Duck Typing in Action")
print("=" * 60)
print()


class DeliveryBike:
    def deliver(self, order):
        return f"Bike delivering {order} through narrow lanes"


class DeliveryDrone:
    def deliver(self, order):
        return f"Drone delivering {order} by air"


class DeliveryRobot:
    def deliver(self, order):
        return f"Robot delivering {order} on the sidewalk"


class Intern:
    """Not a vehicle at all, but has a deliver() method!"""
    def deliver(self, order):
        return f"Intern running to deliver {order} on foot"


def dispatch_order(courier, order):
    """This function works with ANY object that has deliver().
    It doesn't check if courier is a vehicle, a robot, or a person."""
    print(f"  {courier.deliver(order)}")


couriers = [DeliveryBike(), DeliveryDrone(), DeliveryRobot(), Intern()]

for courier in couriers:
    dispatch_order(courier, "Butter Chicken")

print()
print("dispatch_order doesn't check types. It just calls deliver().")
print("Bike, Drone, Robot, Intern -- all work because all have deliver().")
print()


# ============================================================
# 3. What happens when a duck can't quack?
# ============================================================
print("=" * 60)
print("3. What If the Object DOESN'T Have the Method?")
print("=" * 60)
print()


class BrokenVehicle:
    """Has no deliver() method."""
    def honk(self):
        return "HONK!"


broken = BrokenVehicle()
try:
    dispatch_order(broken, "Pizza")
except AttributeError as e:
    print(f"  AttributeError: {e}")
    print()
    print("  Python didn't complain when we CREATED BrokenVehicle.")
    print("  It only complained when we tried to CALL deliver().")
    print("  That's duck typing: errors happen at RUNTIME, not at definition time.")
print()


# ============================================================
# 4. Contrast with Java-style type checking
# ============================================================
print("=" * 60)
print("4. Contrast: Java-Style vs Python-Style")
print("=" * 60)
print()

print("JAVA STYLE (strict type checking):")
print("  // Java requires a specific type or interface")
print("  void dispatch(DeliveryVehicle courier, String order) {")
print("      courier.deliver(order);")
print("  }")
print("  // Intern can't be passed unless it implements DeliveryVehicle!")
print()

print("PYTHON STYLE (duck typing):")
print("  def dispatch(courier, order):")
print("      courier.deliver(order)")
print("  # Any object with deliver() works. No interface needed.")
print()


# ============================================================
# 5. Real Python example: len() uses duck typing
# ============================================================
print("=" * 60)
print("5. Built-in Example: len() Uses Duck Typing")
print("=" * 60)
print()


class Menu:
    """Custom class with __len__. Now len() works on it!"""
    def __init__(self):
        self.dishes = ["Pasta", "Pizza", "Burger", "Salad"]

    def __len__(self):
        return len(self.dishes)


# len() works on strings, lists, dicts, and OUR custom class
examples = [
    "Hello",               # str has __len__
    [1, 2, 3],             # list has __len__
    {"a": 1, "b": 2},     # dict has __len__
    Menu(),                # our class has __len__
]

for obj in examples:
    print(f"  len({obj!r:30s}) -> {len(obj)}")

print()
print("len() doesn't care about the type.")
print("It just calls obj.__len__(). If it exists, it works.")
print("That's duck typing everywhere in Python.")
print()


# ============================================================
# Summary
# ============================================================
print("=" * 60)
print("Summary")
print("=" * 60)
print()
print("  Duck Typing = Python checks for METHOD existence, not TYPE.")
print("  Advantage: Flexible, less boilerplate, no interfaces needed.")
print("  Risk: Errors only show up at runtime if a method is missing.")
print("  Tip: Use clear naming and docstrings so other devs know")
print("       what methods an object is expected to have.")
