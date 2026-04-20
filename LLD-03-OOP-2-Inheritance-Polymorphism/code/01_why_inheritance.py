"""
Why Inheritance?
================
The PROBLEM: Code duplication.
The SOLUTION: Pull shared code into a parent class.

Run: python 01_why_inheritance.py
"""


# ============================================================
# THE PROBLEM: Duplicated code
# ============================================================
print("=" * 60)
print("THE PROBLEM: Code Duplication")
print("=" * 60)
print()


class Food:
    def __init__(self, name, price, calories):
        self.name = name          # duplicated
        self.price = price        # duplicated
        self.calories = calories  # unique to Food

    def describe(self):           # duplicated
        return f"{self.name} - Rs.{self.price}"

    def nutrition_info(self):     # unique to Food
        return f"{self.calories} cal"


class Beverage:
    def __init__(self, name, price, volume_ml):
        self.name = name          # duplicated
        self.price = price        # duplicated
        self.volume_ml = volume_ml  # unique to Beverage

    def describe(self):           # duplicated
        return f"{self.name} - Rs.{self.price}"

    def pour_info(self):          # unique to Beverage
        return f"{self.volume_ml}ml"


burger = Food("Burger", 199, 450)
cola = Beverage("Cola", 59, 330)

print(f"burger.describe() -> {burger.describe()}")
print(f"cola.describe()   -> {cola.describe()}")
print()

# Count the duplication
print("Duplicated across Food and Beverage:")
print("  - self.name = name          (2 times)")
print("  - self.price = price        (2 times)")
print("  - def describe(self):       (2 times)")
print("  Total: 6 duplicated lines!")
print()
print("Imagine adding Dessert, Combo, Appetizer...")
print("That's 6 x N duplicated lines. Bugs WILL creep in.")
print()


# ============================================================
# THE SOLUTION: Inheritance
# ============================================================
print("=" * 60)
print("THE SOLUTION: A Parent Class")
print("=" * 60)
print()


class MenuItem:
    """Parent class -- holds everything COMMON to all menu items."""

    def __init__(self, name, price):
        self.name = name       # written ONCE
        self.price = price     # written ONCE

    def describe(self):        # written ONCE
        return f"{self.name} - Rs.{self.price}"


class FoodItem(MenuItem):
    """Child class -- inherits name, price, describe() from MenuItem."""

    def __init__(self, name, price, calories):
        super().__init__(name, price)  # let parent handle name & price
        self.calories = calories       # only Food-specific stuff here

    def nutrition_info(self):
        return f"{self.calories} cal"


class BeverageItem(MenuItem):
    """Child class -- also inherits name, price, describe() from MenuItem."""

    def __init__(self, name, price, volume_ml):
        super().__init__(name, price)  # let parent handle name & price
        self.volume_ml = volume_ml     # only Beverage-specific stuff here

    def pour_info(self):
        return f"{self.volume_ml}ml"


burger2 = FoodItem("Burger", 199, 450)
cola2 = BeverageItem("Cola", 59, 330)

print(f"burger2.describe()       -> {burger2.describe()}")
print(f"burger2.nutrition_info() -> {burger2.nutrition_info()}")
print()
print(f"cola2.describe()         -> {cola2.describe()}")
print(f"cola2.pour_info()        -> {cola2.pour_info()}")
print()


# ============================================================
# What gets inherited?
# ============================================================
print("=" * 60)
print("What Gets Inherited?")
print("=" * 60)
print()
print("FoodItem inherits from MenuItem:")
print(f"  burger2.name     -> {burger2.name}     (inherited attribute)")
print(f"  burger2.price    -> {burger2.price}       (inherited attribute)")
print(f"  burger2.describe -> {burger2.describe}  (inherited method)")
print(f"  burger2.calories -> {burger2.calories}       (its OWN attribute)")
print()
print("RULE: A child class gets ALL the parent's attributes and methods,")
print("      plus anything extra it defines itself.")
print()


# ============================================================
# Adding a new type is now easy
# ============================================================
print("=" * 60)
print("Adding a New Type is Easy")
print("=" * 60)
print()


class DessertItem(MenuItem):
    """Just 4 lines to add a whole new menu category!"""

    def __init__(self, name, price, is_frozen):
        super().__init__(name, price)
        self.is_frozen = is_frozen


ice_cream = DessertItem("Ice Cream", 99, True)
print(f"ice_cream.describe()  -> {ice_cream.describe()}")
print(f"ice_cream.is_frozen   -> {ice_cream.is_frozen}")
print()
print("We wrote ZERO duplicate code. describe() just works.")
print("That's the power of inheritance.")
