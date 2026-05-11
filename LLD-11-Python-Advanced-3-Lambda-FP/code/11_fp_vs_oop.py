"""Functional Programming vs OOP — when to use which."""


# --- The same problem, two styles ---

# Data
orders = [
    {"item": "Laptop", "price": 80000, "qty": 1},
    {"item": "Mouse", "price": 500, "qty": 3},
    {"item": "Keyboard", "price": 2000, "qty": 2},
    {"item": "Monitor", "price": 25000, "qty": 1},
    {"item": "Cable", "price": 200, "qty": 5},
]


# --- OOP style ---
class OrderProcessor:
    def __init__(self, orders):
        self.orders = orders

    def get_expensive(self, min_price):
        result = []
        for order in self.orders:
            if order["price"] * order["qty"] >= min_price:
                result.append(order)
        return result

    def get_names(self, orders):
        return [o["item"] for o in orders]

    def total_value(self):
        total = 0
        for order in self.orders:
            total += order["price"] * order["qty"]
        return total

processor = OrderProcessor(orders)
expensive = processor.get_expensive(5000)
print("OOP style:")
print(f"  Expensive items: {processor.get_names(expensive)}")
print(f"  Total value: ₹{processor.total_value():,}")


# --- FP style ---
print("\nFP style:")

# Filter: expensive orders (total >= 5000)
expensive_fp = list(filter(lambda o: o["price"] * o["qty"] >= 5000, orders))

# Map: extract names
names_fp = list(map(lambda o: o["item"], expensive_fp))
print(f"  Expensive items: {names_fp}")

# Reduce: total value
from functools import reduce
total_fp = reduce(lambda acc, o: acc + o["price"] * o["qty"], orders, 0)
print(f"  Total value: ₹{total_fp:,}")


# --- Pythonic style (best of both) ---
print("\nPythonic style:")

expensive_py = [o["item"] for o in orders if o["price"] * o["qty"] >= 5000]
total_py = sum(o["price"] * o["qty"] for o in orders)

print(f"  Expensive items: {expensive_py}")
print(f"  Total value: ₹{total_py:,}")


# --- When to use which ---
print("\n" + "=" * 55)
print("FP vs OOP — Decision Guide:")
print("=" * 55)
print()
print("  Use FP (lambda, map, filter, comprehensions) when:")
print("    • Transforming data: clean, filter, reshape")
print("    • One-off data pipelines")
print("    • No shared state to manage")
print("    • Simple, stateless operations")
print()
print("  Use OOP (classes) when:")
print("    • Managing state over time (user, order, game)")
print("    • Complex behavior with multiple methods")
print("    • Need inheritance / polymorphism")
print("    • Building frameworks / libraries")
print()
print("  Pythonic = mix both:")
print("    • Classes for structure + comprehensions for data transforms")
print("    • sorted(users, key=lambda u: u.age)  ← FP inside OOP")
print("    • Django: OOP models + FP querysets")
