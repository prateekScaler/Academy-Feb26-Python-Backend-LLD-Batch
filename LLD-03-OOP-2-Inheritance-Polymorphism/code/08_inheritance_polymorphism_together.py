"""
08 - Inheritance + Polymorphism Together
=========================================
The full picture: a menu system where adding a new
item type requires ZERO changes to existing code.
"""


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


class Beverage(MenuItem):
    def __init__(self, name, price, volume_ml):
        super().__init__(name, price)
        self.volume_ml = volume_ml

    def calculate_price(self):
        return self.price + 10  # Container deposit


def print_bill(items):
    """Works with ANY MenuItem — polymorphism!"""
    print("=" * 40)
    total = 0
    for item in items:
        price = item.calculate_price()
        print(f"  {item.name:.<30} Rs.{price:.2f}")
        total += price
    print("-" * 40)
    print(f"  {'TOTAL':.<30} Rs.{total:.2f}")
    print("=" * 40)


print("=== Original Order ===\n")
order = [Food("Butter Chicken", 350, 450), Food("Naan", 50, 200), Beverage("Chai", 40, 200)]
print_bill(order)


# PM says: "Add Desserts with 12% GST." Changes to existing code: ZERO.
print("\n\n=== After Adding Dessert (zero changes) ===\n")


class Dessert(MenuItem):
    def __init__(self, name, price, is_frozen=False):
        super().__init__(name, price)
        self.is_frozen = is_frozen

    def calculate_price(self):
        return self.price * 1.12  # 12% GST


order2 = [Food("Biryani", 300, 450), Dessert("Gulab Jamun", 80), Beverage("Lassi", 80, 300)]
print_bill(order2)

print("\nOpen for extension, closed for modification.")
