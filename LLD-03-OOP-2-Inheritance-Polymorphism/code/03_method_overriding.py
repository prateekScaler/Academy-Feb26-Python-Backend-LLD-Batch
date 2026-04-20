"""
Method Overriding -- Child Changes Parent Behavior
====================================================
- Parent has a method
- Child OVERRIDES it (same name, different body)
- Same method name, different results
- super().method() to EXTEND instead of fully replacing

Run: python 03_method_overriding.py
"""


# ============================================================
# 1. Parent has a method, child overrides it
# ============================================================
print("=" * 60)
print("1. Basic Method Overriding")
print("=" * 60)
print()


class Restaurant:
    def __init__(self, name):
        self.name = name

    def greeting(self):
        return f"Welcome to {self.name}!"

    def serve(self, dish):
        return f"Here is your {dish}. Enjoy!"


class FancyRestaurant(Restaurant):
    def greeting(self):
        # OVERRIDES the parent's greeting completely
        return f"Good evening. Welcome to the exquisite {self.name}."

    def serve(self, dish):
        # OVERRIDES the parent's serve completely
        return f"Your {dish} has been artfully plated by our chef. Bon appetit!"


class Dhaba(Restaurant):
    def greeting(self):
        return f"Aao ji! {self.name} mein swagat hai!"

    def serve(self, dish):
        return f"Ye lo {dish}! Garam garam khaao!"


# Same method name, different behavior
places = [
    Restaurant("Scaler Canteen"),
    FancyRestaurant("Le Cordon Bleu"),
    Dhaba("Highway Dhaba"),
]

for place in places:
    print(f"[{place.__class__.__name__}]")
    print(f"  {place.greeting()}")
    print(f"  {place.serve('Paneer Tikka')}")
    print()


# ============================================================
# 2. How Python decides which method to call
# ============================================================
print("=" * 60)
print("2. How Python Decides Which Method to Call")
print("=" * 60)
print()
print("When you call obj.method():")
print("  Step 1: Look in the object's OWN class")
print("  Step 2: If not found, look in the PARENT class")
print("  Step 3: If not found, look in the GRANDPARENT class")
print("  ... and so on until object (the root of all classes)")
print()
print("If FancyRestaurant defines greeting(), Python uses THAT one.")
print("It never even looks at Restaurant.greeting().")
print()


# ============================================================
# 3. super().method() -- EXTEND instead of Replace
# ============================================================
print("=" * 60)
print("3. super().method() -- Extend Instead of Replace")
print("=" * 60)
print()


class Order:
    def __init__(self, items):
        self.items = items

    def calculate_total(self):
        return sum(self.items)

    def receipt(self):
        lines = ["--- Receipt ---"]
        for i, item in enumerate(self.items, 1):
            lines.append(f"  Item {i}: Rs.{item}")
        lines.append(f"  Total: Rs.{self.calculate_total()}")
        return "\n".join(lines)


class PremiumOrder(Order):
    """Adds priority delivery fee on top of parent's total."""

    def __init__(self, items, priority_fee):
        super().__init__(items)
        self.priority_fee = priority_fee

    def calculate_total(self):
        # EXTEND: use parent's total, then add more
        base_total = super().calculate_total()
        return base_total + self.priority_fee

    def receipt(self):
        # EXTEND: get parent's receipt, then append extra info
        base_receipt = super().receipt()
        return base_receipt + f"\n  Priority Fee: Rs.{self.priority_fee}" \
                            + f"\n  Grand Total: Rs.{self.calculate_total()}"


regular = Order([199, 149, 99])
premium = PremiumOrder([199, 149, 99], 50)

print("Regular Order:")
print(regular.receipt())
print()
print("Premium Order:")
print(premium.receipt())
print()


# ============================================================
# 4. Override vs Extend -- Summary
# ============================================================
print("=" * 60)
print("4. Override vs Extend -- Summary")
print("=" * 60)
print()
print("OVERRIDE (replace completely):")
print("  def greeting(self):")
print("      return 'Totally new greeting'")
print()
print("EXTEND (add to parent's behavior):")
print("  def greeting(self):")
print("      base = super().greeting()")
print("      return base + ' We have live music tonight!'")
print()
print("Use EXTEND when the parent does useful work you don't want to repeat.")
print("Use OVERRIDE when the parent's behavior is completely wrong for the child.")
