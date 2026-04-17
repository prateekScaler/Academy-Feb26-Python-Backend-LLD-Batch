"""
02 - Attributes and Methods
============================
Attributes = what an object KNOWS (data)
Methods = what an object can DO (behavior)
"""


class Dish:
    """A dish on a restaurant menu."""

    def __init__(self, name, price, is_vegetarian):
        # Attributes — what this dish KNOWS
        self.name = name
        self.price = price
        self.is_vegetarian = is_vegetarian

    # Methods — what this dish can DO
    def describe(self):
        veg = "Veg" if self.is_vegetarian else "Non-Veg"
        return f"{self.name} - Rs.{self.price} ({veg})"

    def apply_discount(self, percent):
        discounted = self.price * (1 - percent / 100)
        return round(discounted, 2)

    def is_expensive(self, threshold=300):
        return self.price > threshold


# Creating objects (instances) from the class (blueprint)
butter_chicken = Dish("Butter Chicken", 350, False)
paneer_tikka = Dish("Paneer Tikka", 280, True)
dal_makhani = Dish("Dal Makhani", 220, True)

# Using attributes — accessing what the object KNOWS
print(f"Name: {butter_chicken.name}")
print(f"Price: Rs.{butter_chicken.price}")
print(f"Is Veg: {butter_chicken.is_vegetarian}")

print()

# Using methods — asking the object to DO something
print(butter_chicken.describe())
print(paneer_tikka.describe())
print(dal_makhani.describe())

print()

# Methods can take parameters and return values
print(f"Butter Chicken with 20% off: Rs.{butter_chicken.apply_discount(20)}")
print(f"Is Butter Chicken expensive? {butter_chicken.is_expensive()}")
print(f"Is Dal Makhani expensive? {dal_makhani.is_expensive()}")

print()

# Each object has its OWN attributes — independent data
print("--- Each object is independent ---")
butter_chicken.price = 400  # Only changes butter_chicken
print(f"Butter Chicken price: Rs.{butter_chicken.price}")
print(f"Paneer Tikka price: Rs.{paneer_tikka.price}")  # Unchanged!
