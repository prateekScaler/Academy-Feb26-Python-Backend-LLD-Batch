"""
Liskov Substitution Principle (LSP)
====================================
"Objects of a superclass should be replaceable with objects of a subclass
without breaking the program."

Restaurant analogy: If your menu says "Any pizza can be customized with
extra toppings", then EVERY pizza (Margherita, Pepperoni, Farmhouse) must
support that. You can't have a "Frozen Pizza" subclass that throws an error
when someone tries to add toppings — that would surprise the customer!

In code: If function works with base class, it MUST work correctly with
any subclass. Subclasses should EXTEND behavior, not break expectations.
"""

print("=" * 60)
print("LISKOV SUBSTITUTION PRINCIPLE (LSP)")
print("=" * 60)

# ============================================================
# --- BAD: Classic Rectangle/Square violation ---
# ============================================================
# Mathematically, a square IS a rectangle. But in code, substituting
# Square for Rectangle breaks expectations.

print("\n--- BAD: Rectangle/Square violation ---\n")


class Rectangle:
    def __init__(self, width, height):
        self._width = width
        self._height = height

    def set_width(self, width):
        self._width = width

    def set_height(self, height):
        self._height = height

    def area(self):
        return self._width * self._height


class Square(Rectangle):
    """A square IS-A rectangle mathematically, but this violates LSP!"""

    def __init__(self, side):
        super().__init__(side, side)

    def set_width(self, width):
        # Must keep it square, so we change BOTH dimensions
        self._width = width
        self._height = width  # Surprise! Setting width also changes height

    def set_height(self, height):
        self._width = height  # Surprise! Setting height also changes width
        self._height = height


def print_area_after_resize(shape: Rectangle, new_width, new_height):
    """This function expects Rectangle behavior.
    It sets width and height INDEPENDENTLY."""
    shape.set_width(new_width)
    shape.set_height(new_height)
    expected = new_width * new_height
    actual = shape.area()
    status = "OK" if actual == expected else "BUG!"
    print(f"  Set width={new_width}, height={new_height}")
    print(f"  Expected area: {expected}, Got: {actual} [{status}]")


print("Rectangle (works correctly):")
rect = Rectangle(5, 5)
print_area_after_resize(rect, 10, 5)

print("\nSquare substituted for Rectangle (BREAKS!):")
sq = Square(5)
print_area_after_resize(sq, 10, 5)
# Expected 50, but got 25 because set_height(5) also set width to 5!


# ============================================================
# --- BAD: Restaurant example violating LSP ---
# ============================================================

print("\n\n--- BAD: MenuItem with a subclass that breaks the contract ---\n")


class MenuItemBad:
    def __init__(self, name, price):
        self.name = name
        self.price = price

    def get_price(self):
        return self.price

    def prepare(self):
        return f"Preparing {self.name}..."

    def customize(self, extras):
        """All menu items should support customization."""
        return f"{self.name} with {', '.join(extras)}"


class ComboMealBad(MenuItemBad):
    """Violates LSP: customize() doesn't work as expected!"""

    def __init__(self, name, price, items):
        super().__init__(name, price)
        self.items = items

    def customize(self, extras):
        # VIOLATION: Raises exception instead of working like parent!
        raise NotImplementedError("Combo meals cannot be customized!")


def process_order(item: MenuItemBad, customer_name: str):
    """This function trusts the MenuItem interface."""
    try:
        result = item.customize(["extra cheese", "no onion"])
        print(f"  {customer_name} ordered: {result} -> Rs.{item.get_price()}")
    except NotImplementedError as e:
        print(f"  {customer_name}: CRASHED! {e}")


print("Regular item (works):")
biryani = MenuItemBad("Hyderabadi Biryani", 300)
process_order(biryani, "Vipul")

print("\nCombo meal substituted (BREAKS!):")
combo = ComboMealBad("Family Combo", 999, ["Pizza", "Pasta", "Garlic Bread"])
process_order(combo, "Kaarthik")


# ============================================================
# --- GOOD: Proper restaurant example following LSP ---
# ============================================================

print("\n\n--- GOOD: All subclasses honor the MenuItem contract ---\n")

from abc import ABC, abstractmethod


class MenuItem(ABC):
    """Base class with a clear contract that ALL subclasses must honor."""

    def __init__(self, name: str, base_price: float):
        self.name = name
        self.base_price = base_price

    @abstractmethod
    def get_price(self) -> float:
        """Must return a valid positive price."""
        pass

    @abstractmethod
    def get_preparation_time(self) -> int:
        """Must return preparation time in minutes."""
        pass

    def get_description(self) -> str:
        """Can be overridden, but must always return a valid string."""
        return self.name


class VegDish(MenuItem):
    """Vegetarian dish — follows the contract perfectly."""

    def __init__(self, name: str, base_price: float, is_jain: bool = False):
        super().__init__(name, base_price)
        self.is_jain = is_jain

    def get_price(self) -> float:
        return self.base_price  # Veg dishes: no surcharge

    def get_preparation_time(self) -> int:
        return 15  # Veg dishes: 15 minutes

    def get_description(self) -> str:
        jain_tag = " [Jain]" if self.is_jain else ""
        return f"[VEG] {self.name}{jain_tag}"


class NonVegDish(MenuItem):
    """Non-vegetarian dish — follows the contract, adds appropriate behavior."""

    def __init__(self, name: str, base_price: float, spice_level: str = "medium"):
        super().__init__(name, base_price)
        self.spice_level = spice_level

    def get_price(self) -> float:
        # Non-veg has a 10% surcharge (valid positive price - contract honored!)
        return self.base_price * 1.10

    def get_preparation_time(self) -> int:
        return 25  # Non-veg takes longer (still returns valid int - contract honored!)

    def get_description(self) -> str:
        return f"[NON-VEG] {self.name} ({self.spice_level} spice)"


class ComboMeal(MenuItem):
    """Combo meal — ALSO follows the contract. No surprises!"""

    def __init__(self, name: str, items: list):
        # Combo price is sum of items with 10% combo discount
        total = sum(item.get_price() for item in items)
        super().__init__(name, total * 0.90)
        self.items = items

    def get_price(self) -> float:
        return self.base_price  # Valid price, contract honored!

    def get_preparation_time(self) -> int:
        # Longest item determines combo prep time
        return max(item.get_preparation_time() for item in self.items)

    def get_description(self) -> str:
        item_names = ", ".join(item.name for item in self.items)
        return f"[COMBO] {self.name}: ({item_names})"


def place_order(items: list, customer_name: str):
    """This function works with ANY MenuItem subclass — no surprises, no crashes."""
    print(f"  Order for {customer_name}:")
    total_price = 0
    max_time = 0
    for item in items:
        # LSP guarantee: all these calls work correctly for ANY subclass
        price = item.get_price()
        time = item.get_preparation_time()
        desc = item.get_description()
        total_price += price
        max_time = max(max_time, time)
        print(f"    {desc} - Rs.{price:.0f} ({time} min)")
    print(f"  Total: Rs.{total_price:.0f} | Ready in: {max_time} min")
    print()


# Create items of different types
paneer = VegDish("Paneer Tikka", 250)
dal = VegDish("Dal Makhani", 200, is_jain=True)
chicken = NonVegDish("Chicken Tikka", 350, spice_level="hot")
mutton = NonVegDish("Mutton Rogan Josh", 450)
combo = ComboMeal("Ajit's Special Combo", [paneer, chicken])

# ALL types work perfectly when substituted — LSP satisfied!
place_order([paneer, dal], "Vipul")
place_order([chicken, mutton], "Kaarthik")
place_order([combo, dal], "Ajit")


# ============================================================
# WHY THIS MATTERS:
# ============================================================
print("=" * 60)
print("WHY LSP MATTERS:")
print("-" * 60)
print("- Code that uses the base type should NEVER need to check")
print("  'is this actually a Square?' or 'is this a Combo?'")
print("- If you find yourself writing isinstance() checks, you")
print("  probably have an LSP violation")
print("- Subclasses must STRENGTHEN guarantees, never weaken them")
print("- If parent promises 'returns a price', child can't raise an error")
print("=" * 60)
