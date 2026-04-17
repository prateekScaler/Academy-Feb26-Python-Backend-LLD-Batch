"""
10 - self: What It Is and Why It Matters
=========================================
self = "this specific object"

self appears in TWO places:
  1. In __init__ — to attach attributes to the newly created object
  2. In methods — to access/modify THIS object's attributes

Forgetting self is the #1 Python OOP bug.
"""


# =============================================
# self in __init__ — attaching attributes
# =============================================

print("=== self in __init__ ===\n")


class Dish:
    def __init__(self, name, price):
        # self = the object being created right now
        self.name = name     # attach 'name' to THIS object
        self.price = price   # attach 'price' to THIS object
        print(f"  Created: {self.name} at Rs.{self.price}")


# When you write:
biryani = Dish("Biryani", 300)
# Python actually does:
# 1. Creates empty object in memory
# 2. Calls Dish.__init__(that_object, "Biryani", 300)
# 3. Inside __init__, self IS that_object

dosa = Dish("Dosa", 120)
# self IS dosa here — different object!

print(f"\nbiryani.name = {biryani.name}")
print(f"dosa.name = {dosa.name}")
print("Each object has its own copy of the attributes.")


# =============================================
# self in methods — accessing THIS object's data
# =============================================

print("\n=== self in methods ===\n")


class Counter:
    def __init__(self):
        self.count = 0

    def increment(self):
        self.count += 1  # self.count = THIS object's count

    def get_count(self):
        return self.count


c1 = Counter()
c2 = Counter()

c1.increment()
c1.increment()
c1.increment()

# c1.increment() → Python calls Counter.increment(c1) → self = c1
# c2 is untouched because self was c1, not c2

print(f"c1.get_count() = {c1.get_count()}")  # 3
print(f"c2.get_count() = {c2.get_count()}")  # 0 — independent!

# Proof that method calls work like this:
print("\nBehind the scenes:")
print("  c1.increment() == Counter.increment(c1)")
Counter.increment(c1)  # Same thing!
print(f"  c1 after explicit call: {c1.get_count()}")  # 4


# =============================================
# BUG #1: Forgetting self. on attribute access
# =============================================

print("\n=== Bug #1: Forgetting self. ===\n")


class BrokenCounter:
    def __init__(self):
        self.count = 0

    def increment(self):
        try:
            count += 1  # BUG! 'count' is a local variable, not self.count
        except UnboundLocalError as e:
            print(f"  count += 1 → {e}")
            print("  Fix: change to self.count += 1")


c = BrokenCounter()
c.increment()


# =============================================
# BUG #2: Forgetting self in method definition
# =============================================

print("\n=== Bug #2: Missing self parameter ===\n")


class BadGreeter:
    def __init__(self, name):
        self.name = name

    def greet():  # BUG! Missing self
        return "Hello"


g = BadGreeter("Rahul")
try:
    g.greet()
except TypeError as e:
    print(f"  g.greet() → {e}")
    print("  Fix: change 'def greet()' to 'def greet(self)'")


# =============================================
# What happens WITHOUT __init__?
# =============================================

print("\n=== Without __init__ ===\n")


class EmptyClass:
    pass


e = EmptyClass()
print(f"e.__dict__ = {e.__dict__}")  # {} — no attributes
print("Object exists but is a blank slate.")
print("Python provided an implicit empty __init__.")

# You CAN add attributes later, but it's unreliable:
e.name = "added after creation"
print(f"e.name = {e.name}")
print("This works but is BAD practice — use __init__ instead.\n")

# With __init__, the object is COMPLETE from birth:
print("Good practice: parameterized __init__ = object always ready to use")
d = Dish("Paneer", 250)
print(f"d.name = {d.name}, d.price = {d.price}")
