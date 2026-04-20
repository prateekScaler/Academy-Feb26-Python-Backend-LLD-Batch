"""
11 - Method Overloading in Python
==================================
Python does NOT support method overloading like Java.
The Pythonic alternative: default params, *args, **kwargs.
"""


# =============================================
# In Java, you can have multiple methods with same name:
#   void add(int a, int b) { ... }
#   void add(int a, int b, int c) { ... }
#   void add(double a, double b) { ... }
# Java picks the right one based on argument types/count.
# =============================================

# Python: second definition REPLACES the first!

print("=== Python: No Method Overloading ===\n")


class Calculator:
    def add(self, a, b):
        print(f"  add(a, b) = {a + b}")

    def add(self, a, b, c):  # This REPLACES the version above!
        print(f"  add(a, b, c) = {a + b + c}")


calc = Calculator()
# calc.add(1, 2)      # TypeError! The 2-param version is GONE
calc.add(1, 2, 3)      # Works — only the 3-param version exists

try:
    calc.add(1, 2)
except TypeError as e:
    print(f"  calc.add(1, 2) → TypeError: {e}")
    print("  The 2-param version was REPLACED by the 3-param version!\n")


# =============================================
# The Pythonic Way: Default Parameters
# =============================================

print("=== Pythonic Way: Default Parameters ===\n")


class SmartCalculator:
    def add(self, a, b, c=0):  # c defaults to 0
        result = a + b + c
        print(f"  add({a}, {b}, {c}) = {result}")
        return result


sc = SmartCalculator()
sc.add(1, 2)        # c defaults to 0 → 3
sc.add(1, 2, 3)     # c = 3 → 6


# =============================================
# The Pythonic Way: *args
# =============================================

print("\n=== Pythonic Way: *args ===\n")


class FlexCalculator:
    def add(self, *args):  # Accept ANY number of arguments
        result = sum(args)
        print(f"  add{args} = {result}")
        return result


fc = FlexCalculator()
fc.add(1, 2)
fc.add(1, 2, 3)
fc.add(1, 2, 3, 4, 5)
fc.add()  # Even zero args!


# =============================================
# Real Example: Dish with flexible pricing
# =============================================

print("\n=== Real Example: Flexible Dish ===\n")


class Dish:
    def __init__(self, name, price, discount=0, tax_percent=5):
        self.name = name
        self.price = price
        self.discount = discount
        self.tax_percent = tax_percent

    def final_price(self):
        discounted = self.price * (1 - self.discount / 100)
        with_tax = discounted * (1 + self.tax_percent / 100)
        return round(with_tax, 2)


# Different ways to create — same constructor, default params
d1 = Dish("Biryani", 300)
d2 = Dish("Biryani", 300, discount=10)
d3 = Dish("Biryani", 300, discount=10, tax_percent=12)

print(f"  No discount, 5% tax:    Rs.{d1.final_price()}")
print(f"  10% discount, 5% tax:   Rs.{d2.final_price()}")
print(f"  10% discount, 12% tax:  Rs.{d3.final_price()}")


# =============================================
# Why Python doesn't need overloading
# =============================================

print("\n=== Why Python Doesn't Need Overloading ===\n")
print("  Java needs overloading because it's statically typed.")
print("  You MUST declare argument types, so different signatures = different methods.")
print()
print("  Python is dynamically typed. One method handles any type:")
print("    def add(self, a, b): return a + b")
print("    add(1, 2)       → 3       (int)")
print("    add('hi', '!')  → 'hi!'   (str)")
print("    add([1], [2])   → [1, 2]  (list)")
print()
print("  Default params + *args + **kwargs = all the flexibility you need.")
