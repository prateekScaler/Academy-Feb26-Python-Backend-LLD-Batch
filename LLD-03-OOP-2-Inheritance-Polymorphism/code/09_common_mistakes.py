"""
09 - Common Mistakes with Inheritance
======================================
What NOT to do.
"""


# =============================================
# MISTAKE 1: Too-deep hierarchies
# =============================================

print("=== Mistake 1: Too-deep hierarchies ===\n")


class Animal:
    def __init__(self, name):
        self.name = name


class Mammal(Animal):
    def __init__(self, name, fur_color):
        super().__init__(name)
        self.fur_color = fur_color


class Pet(Mammal):
    def __init__(self, name, fur_color, owner):
        super().__init__(name, fur_color)
        self.owner = owner


class Dog(Pet):
    def __init__(self, name, fur_color, owner, breed):
        super().__init__(name, fur_color, owner)
        self.breed = breed


class GuideDog(Dog):
    def __init__(self, name, fur_color, owner, breed, handler):
        super().__init__(name, fur_color, owner, breed)
        self.handler = handler


# 5 levels deep! Each __init__ passes args up the chain.
# Where does 'name' come from? You have to trace 5 files.
buddy = GuideDog("Buddy", "golden", "Rahul", "Labrador", "Service Center")
print(f"  {buddy.name} - {buddy.breed} - handler: {buddy.handler}")
print(f"  Hierarchy: GuideDog -> Dog -> Pet -> Mammal -> Animal")
print(f"  5 levels deep. Don't do this. Keep it to 2-3 max.\n")


# =============================================
# MISTAKE 2: Forgetting super().__init__()
# =============================================

print("=== Mistake 2: Forgetting super().__init__() ===\n")


class MenuItem:
    def __init__(self, name, price):
        self.name = name
        self.price = price


class BrokenFood(MenuItem):
    def __init__(self, name, price, calories):
        # FORGOT: super().__init__(name, price)
        self.calories = calories


broken = BrokenFood("Biryani", 300, 450)
print(f"  broken.calories = {broken.calories}")  # Works

try:
    print(f"  broken.name = {broken.name}")
except AttributeError as e:
    print(f"  broken.name -> AttributeError: {e}")
    print("  Parent's __init__ never ran, so name was never set!")


# The fix:
class FixedFood(MenuItem):
    def __init__(self, name, price, calories):
        super().__init__(name, price)  # Don't forget this!
        self.calories = calories


fixed = FixedFood("Biryani", 300, 450)
print(f"\n  fixed.name = {fixed.name}")  # Works now!
print(f"  fixed.price = {fixed.price}")
print(f"  fixed.calories = {fixed.calories}")


# =============================================
# MISTAKE 3: "Is-a" vs "Has-a" confusion
# =============================================

print("\n=== Mistake 3: Inheritance when composition is better ===\n")

# BAD: Order IS a list? No! Order HAS a list.
# class Order(list):  # Don't do this!

# GOOD: Order HAS items (composition)
class Order:
    def __init__(self, customer):
        self.customer = customer
        self.items = []  # HAS a list, not IS a list

    def add_item(self, item):
        self.items.append(item)

    def total(self):
        return sum(item.price for item in self.items)


print("  Ask yourself:")
print("    Dog IS an Animal?       -> Yes, use inheritance")
print("    Car IS an Engine?       -> No! Car HAS an engine -> composition")
print("    PremiumUser IS a User?  -> Yes, use inheritance")
print("    Order IS a list?        -> No! Order HAS items -> composition")
