"""
06 - Constructors: __init__
============================
The method that runs AUTOMATICALLY when you create an object.
Covers: self, implicit __init__, non-parameterized, parameterized,
defaults, validation.
"""

from datetime import datetime


# =============================================
# WHAT IS self?
# =============================================

print("=== What is self? ===\n")


class Counter:
    def __init__(self):        # self = the object being created
        self.count = 0         # attach 'count' to THIS object

    def increment(self):       # self = the object calling this method
        self.count += 1        # modify THIS object's count


c1 = Counter()                # Python calls: Counter.__init__(c1)
c2 = Counter()                # Python calls: Counter.__init__(c2)
c1.increment()                # Python calls: Counter.increment(c1)
c1.increment()

print(f"c1.count = {c1.count}")  # 2
print(f"c2.count = {c2.count}")  # 0 — independent!


# The #1 Bug: Forgetting self
print("\n--- The #1 Bug ---")


class BrokenCounter:
    def __init__(self):
        self.count = 0

    def increment(self):
        # count += 1  ← BUG! 'count' is a local variable, not self.count
        # Uncomment the line above to see: UnboundLocalError
        self.count += 1  # ← Correct: use self.count


# =============================================
# WHAT HAPPENS WITHOUT __init__?
# =============================================

print("\n=== What if you don't write __init__? ===\n")


class Empty:
    pass  # No __init__ — Python provides a default empty one


e = Empty()
print(f"e.__dict__ = {e.__dict__}")  # {} — no attributes!
print("Object exists but has no data. It's a blank slate.")
print("You CAN add attributes later...")
e.name = "added later"
print(f"e.name = {e.name}")
print("...but this is messy. Better to use __init__.\n")

# What __init__ truly does:
# Step 1: Python creates an empty object in memory (__new__)
# Step 2: Python calls __init__(self) on that empty object
# Step 3: __init__ attaches attributes to the object (self.name = ...)
# You almost never touch Step 1. Your job is Step 2-3.


# =============================================
# NON-PARAMETERIZED CONSTRUCTOR
# =============================================

print("=== Non-Parameterized ===\n")


class Timer:
    def __init__(self):
        self.seconds = 0
        self.started_at = datetime.now()

    def tick(self):
        self.seconds += 1


t = Timer()
print(f"Timer starts at {t.seconds} seconds")
print("Every Timer starts the same way. Good when that's what you want.")
print("Bad when objects need different initial data.\n")


# =============================================
# PARAMETERIZED CONSTRUCTOR — Objects born ready
# =============================================

print("=== Parameterized — The Fix ===\n")

# BAD: Object created incomplete
print("--- The Problem ---")


class DishBad:
    def __init__(self):
        pass

    def describe(self):
        return f"{self.name} costs Rs.{self.price}"


dish1 = DishBad()
dish1.name = "Biryani"
dish1.price = 300
print(f"dish1: {dish1.describe()}")  # Works this time...

dish2 = DishBad()
dish2.name = "Dosa"
# Forgot to set price!
try:
    dish2.describe()
except AttributeError as e:
    print(f"dish2.describe() → {e}")
    print("Object was incomplete — price was never set!")

# GOOD: Object born ready
print("\n--- The Fix ---")


class DishGood:
    def __init__(self, name, price):  # REQUIRE name and price
        self.name = name
        self.price = price

    def describe(self):
        return f"{self.name} costs Rs.{self.price}"


dish = DishGood("Biryani", 300)
print(f"dish: {dish.describe()}")

# Can't forget required fields:
try:
    DishGood()  # Missing name and price
except TypeError as e:
    print(f"DishGood() → {e}")

try:
    DishGood("Dosa")  # Missing price
except TypeError as e:
    print(f"DishGood('Dosa') → {e}")


# =============================================
# DEFAULTS + VALIDATION
# =============================================

print("\n=== Defaults + Validation ===\n")


class Restaurant:
    def __init__(self, name, cuisine, rating=0.0, is_open=True):
        if not name:
            raise ValueError("Restaurant must have a name")
        if not 0 <= rating <= 5:
            raise ValueError(f"Rating must be 0-5, got {rating}")
        self.name = name        # Required
        self.cuisine = cuisine  # Required
        self.rating = rating    # Optional, default 0.0
        self.is_open = is_open  # Optional, default True

    def __str__(self):
        status = "Open" if self.is_open else "Closed"
        return f"{self.name} ({self.cuisine}) - {self.rating}/5 [{status}]"


# Various ways to create
print(Restaurant("Biryani House", "Indian"))
print(Restaurant("Sushi Bar", "Japanese", rating=4.5))
print(Restaurant("Pizza Place", "Italian", rating=3.8, is_open=False))

# Invalid — caught at creation
for args, reason in [
    (("", "Indian"), "empty name"),
    (("Bad", "Indian"), "rating=7"),
]:
    try:
        if reason == "rating=7":
            Restaurant(*args, rating=7)
        else:
            Restaurant(*args)
    except ValueError as e:
        print(f"  Invalid ({reason}): {e}")

print("\nGood practice:")
print("  1. Required params for essential data")
print("  2. Defaults for optional data")
print("  3. Validation — bad objects should never exist")
