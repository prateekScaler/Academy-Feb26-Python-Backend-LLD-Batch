"""
03 - Programming Paradigms Comparison
======================================
Same problem solved in 4 different paradigms:
"Calculate total price of vegetarian dishes"

Shows exactly HOW each paradigm differs.
"""

# Sample data
dishes = [
    {"name": "Butter Chicken", "price": 350, "is_veg": False},
    {"name": "Paneer Tikka", "price": 280, "is_veg": True},
    {"name": "Dal Makhani", "price": 220, "is_veg": True},
    {"name": "Chicken Biryani", "price": 300, "is_veg": False},
    {"name": "Aloo Gobi", "price": 180, "is_veg": True},
]


# =============================================
# PARADIGM 1: Procedural
# YOU tell the computer every step.
# YOU loop, YOU check, YOU add.
# =============================================

print("=== PROCEDURAL ===")
print("(You control every step)\n")

total = 0                          # Step 1: initialize counter
for dish in dishes:                # Step 2: loop through each dish
    if dish["is_veg"]:             # Step 3: check if veg
        print(f"  + {dish['name']}: Rs.{dish['price']}")
        total += dish["price"]     # Step 4: add to total
print(f"  = Total: Rs.{total}\n")  # Step 5: print result

# Key: YOU wrote the loop, the if-check, and the addition.
# The variable 'total' is MUTATED (changed) at each step.


# =============================================
# PARADIGM 2: Object-Oriented
# Ask an OBJECT to do it for you.
# =============================================

print("=== OBJECT-ORIENTED ===")
print("(Ask the object to do it)\n")


class Menu:
    def __init__(self, dishes):
        self.dishes = dishes

    def get_veg_dishes(self):
        return [d for d in self.dishes if d["is_veg"]]

    def veg_total(self):
        return sum(d["price"] for d in self.get_veg_dishes())


menu = Menu(dishes)
for d in menu.get_veg_dishes():
    print(f"  + {d['name']}: Rs.{d['price']}")
print(f"  = Total: Rs.{menu.veg_total()}\n")

# Key: The Menu OBJECT knows how to filter and sum.
# You just ASK it — menu.veg_total(). You don't write the loop.


# =============================================
# PARADIGM 3: Functional
# Transform data with functions. No mutation.
# =============================================

print("=== FUNCTIONAL ===")
print("(Transform data, don't mutate)\n")

# filter: keep only veg dishes (doesn't change original list)
veg_dishes = list(filter(lambda d: d["is_veg"], dishes))

# map: extract just the prices (doesn't change original)
prices = list(map(lambda d: d["price"], veg_dishes))

# sum: reduce to a single number
total = sum(prices)

for d in veg_dishes:
    print(f"  + {d['name']}: Rs.{d['price']}")
print(f"  = Total: Rs.{total}\n")

# Key difference from Procedural:
# - No 'total' variable being MUTATED
# - Each step creates NEW data, doesn't change the original
# - dishes list is UNTOUCHED after all operations
print(f"  Original dishes still intact: {len(dishes)} items")


# =============================================
# PARADIGM 4: Declarative (SQL-like)
# Describe WHAT you want, not HOW.
# =============================================

print("\n=== DECLARATIVE (SQL) ===")
print("(Say what you want, not how)\n")

print("  SELECT SUM(price)")
print("  FROM dishes")
print("  WHERE is_veg = TRUE;")
print()
print("  You didn't write a loop.")
print("  You didn't write an if-check.")
print("  You didn't create a counter variable.")
print("  You just SAID what you want → database figures out HOW.")


# =============================================
# THE KEY DIFFERENCES
# =============================================

print("\n" + "=" * 55)
print("HOW THEY DIFFER:")
print("=" * 55)
print()
print("PROCEDURAL vs FUNCTIONAL:")
print("  Procedural: total = 0 → total += price (MUTATES total)")
print("  Functional: sum(map(prices)) → creates NEW data, never mutates")
print()
print("PROCEDURAL vs DECLARATIVE:")
print("  Procedural: 'loop, check if veg, add price' (says HOW)")
print("  Declarative: 'give me sum of veg prices' (says WHAT)")
print()
print("FUNCTIONAL vs DECLARATIVE:")
print("  Functional: filter → map → sum (still step-by-step transforms)")
print("  Declarative: one statement, no steps at all")
