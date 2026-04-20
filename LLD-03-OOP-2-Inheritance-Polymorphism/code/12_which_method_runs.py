"""
12 - Which Method Gets Called?
===============================
When parent and child both have the same method,
which one runs? It depends on the OBJECT's type, not the variable's type.
"""


# =============================================
# Setup
# =============================================

class MenuItem:
    def __init__(self, name, price):
        self.name = name
        self.price = price

    def calculate_price(self):
        return self.price

    def describe(self):
        return f"{self.name} - Rs.{self.calculate_price():.2f}"


class Food(MenuItem):
    def __init__(self, name, price, calories):
        super().__init__(name, price)
        self.calories = calories

    def calculate_price(self):
        return self.price * 1.05  # 5% GST

    def describe(self):
        return f"{self.name} - Rs.{self.calculate_price():.2f} ({self.calories} cal)"


class Beverage(MenuItem):
    def __init__(self, name, price, volume_ml):
        super().__init__(name, price)
        self.volume_ml = volume_ml

    def calculate_price(self):
        return self.price + 10  # Container deposit


# =============================================
# SCENARIO 1: Which describe() runs?
# =============================================

print("=== Scenario 1: Which describe() runs? ===\n")

biryani = Food("Biryani", 300, 450)
chai = Beverage("Chai", 40, 200)

# Food has its own describe() → Food's version runs
print(f"  biryani.describe() = {biryani.describe()}")

# Beverage does NOT have describe() → MenuItem's version runs
print(f"  chai.describe()    = {chai.describe()}")
print()
print("  Rule: Python looks at the OBJECT's class first.")
print("        If the method isn't there, it goes UP to the parent.")


# =============================================
# SCENARIO 2: List of parent type, child objects
# =============================================

print("\n=== Scenario 2: List of MenuItems ===\n")

# Type hint says MenuItem, but actual objects are Food/Beverage
items: list[MenuItem] = [
    Food("Biryani", 300, 450),
    Beverage("Chai", 40, 200),
    Food("Naan", 50, 200),
]

print("  items is typed as list[MenuItem], but contains Food and Beverage objects.")
print("  Which calculate_price() runs?\n")

for item in items:
    price = item.calculate_price()
    print(f"    {item.name}: Rs.{price:.2f} ← {type(item).__name__}.calculate_price()")

print()
print("  The OBJECT's type determines the method, not the variable's type hint.")
print("  This IS polymorphism.")


# =============================================
# SCENARIO 3: isinstance checks
# =============================================

print("\n=== Scenario 3: isinstance() ===\n")

biryani = Food("Biryani", 300, 450)

print(f"  isinstance(biryani, Food)?     {isinstance(biryani, Food)}")
print(f"  isinstance(biryani, MenuItem)? {isinstance(biryani, MenuItem)}")
print(f"  isinstance(biryani, Beverage)? {isinstance(biryani, Beverage)}")
print()
print("  biryani IS a Food (directly)")
print("  biryani IS a MenuItem (through inheritance)")
print("  biryani is NOT a Beverage")


# =============================================
# SCENARIO 4: Method not overridden
# =============================================

print("\n=== Scenario 4: What if child doesn't override? ===\n")


class Dessert(MenuItem):
    def __init__(self, name, price):
        super().__init__(name, price)
    # No calculate_price() override!


gulab = Dessert("Gulab Jamun", 80)
print(f"  gulab.calculate_price() = {gulab.calculate_price()}")
print("  Dessert has no calculate_price() → MenuItem's version runs (returns base price)")


# =============================================
# SCENARIO 5: super() in overridden method
# =============================================

print("\n=== Scenario 5: super() inside an override ===\n")


class ComboMeal(MenuItem):
    def __init__(self, name, price, items):
        super().__init__(name, price)
        self.items = items

    def calculate_price(self):
        base = super().calculate_price()  # MenuItem's calculate_price()
        discount = base * 0.1             # 10% combo discount
        return base - discount


combo = ComboMeal("Family Combo", 500, ["Biryani", "Naan", "Chai"])
print(f"  combo.calculate_price() = Rs.{combo.calculate_price():.2f}")
print("  super().calculate_price() called MenuItem's version (Rs.500)")
print("  Then ComboMeal applied its own 10% discount")


# =============================================
# QUIZ: Test yourself
# =============================================

print("\n" + "=" * 50)
print("QUIZ: Which method runs?")
print("=" * 50)
print()
print("  class A:")
print("      def greet(self): return 'A'")
print("  class B(A):")
print("      def greet(self): return 'B'")
print("  class C(A):")
print("      pass")
print()

class A:
    def greet(self): return "A"

class B(A):
    def greet(self): return "B"

class C(A):
    pass

print(f"  B().greet() = '{B().greet()}'   ← B overrides, so B's version")
print(f"  C().greet() = '{C().greet()}'   ← C doesn't override, so A's version")
print(f"  A().greet() = '{A().greet()}'   ← A is the original")
