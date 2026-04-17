"""
09 - @property: Pythonic Encapsulation
=======================================
Step-by-step: from ugly Java-style to clean Python @property.

@property lets you add validation to attributes
WITHOUT changing how they're used from outside.
"""


# =============================================
# THE PROBLEM: You want validation on an attribute
# =============================================

print("=== The Problem ===\n")


class DishNoValidation:
    def __init__(self, name, price):
        self.name = name
        self.price = price


dish = DishNoValidation("Biryani", 300)
dish.price = -50  # Oops! No one stops this.
print(f"dish.price = {dish.price}")  # -50 — broken!
print("No validation. Anyone can set price to anything.\n")


# =============================================
# STEP 1: The Java Way (ugly but works)
# =============================================

print("=== Step 1: Java-style Getters/Setters ===\n")


class DishJavaStyle:
    def __init__(self, name, price):
        self.__name = name
        self.__price = price

    def get_price(self):
        return self.__price

    def set_price(self, value):
        if value < 0:
            raise ValueError("Price can't be negative")
        self.__price = value


d = DishJavaStyle("Biryani", 300)
print(f"d.get_price() = {d.get_price()}")   # Works but verbose
d.set_price(350)                              # Works but verbose
print(f"d.get_price() = {d.get_price()}")

try:
    d.set_price(-50)
except ValueError as e:
    print(f"d.set_price(-50) → {e}")

print()
print("Problems:")
print("  - d.get_price() instead of just d.price (ugly)")
print("  - Must remember 'is it .price or .get_price()?' everywhere")
print("  - If you start with .price and LATER need validation,")
print("    you have to change EVERY place that uses .price")


# =============================================
# STEP 2: The Python Way — @property
# =============================================

print("\n=== Step 2: @property (the Python way) ===\n")


class DishPythonic:
    def __init__(self, name, price):
        self.name = name
        self.price = price    # NOTE: This calls the @price.setter below!

    @property                  # When someone READS dish.price → call this
    def price(self):
        return self.__price

    @price.setter              # When someone WRITES dish.price = X → call this
    def price(self, value):
        if value < 0:
            raise ValueError("Price can't be negative")
        self.__price = value


d = DishPythonic("Biryani", 300)

# LOOKS like simple attribute access...
print(f"d.price = {d.price}")        # calls the @property getter
d.price = 350                         # calls the @price.setter
print(f"d.price = {d.price}")

# ...but validation runs behind the scenes!
try:
    d.price = -50
except ValueError as e:
    print(f"d.price = -50 → {e}")

print()
print("The magic:")
print("  d.price     → LOOKS like reading an attribute")
print("               → ACTUALLY calls the @property getter")
print("  d.price = X → LOOKS like a simple assignment")
print("               → ACTUALLY calls the setter with validation")
print("  Clean syntax AND protection!")


# =============================================
# REAL EXAMPLE: Order Status
# =============================================

print("\n=== Real Example: Order Status ===\n")


class Order:
    VALID_STATUSES = ["pending", "confirmed", "preparing", "delivered", "cancelled"]

    def __init__(self, customer, items):
        self.customer = customer
        self.items = items
        self.__status = "pending"

    @property
    def status(self):
        return self.__status

    @status.setter
    def status(self, new_status):
        if new_status not in self.VALID_STATUSES:
            raise ValueError(f"Invalid status '{new_status}'. Valid: {self.VALID_STATUSES}")
        if self.__status == "delivered":
            raise ValueError("Cannot change status of delivered order")
        if self.__status == "cancelled":
            raise ValueError("Cannot change status of cancelled order")
        old = self.__status
        self.__status = new_status
        print(f"  {old} → {new_status}")


order = Order("Rahul", ["Butter Chicken", "Naan"])
print(f"Initial: {order.status}")

# Valid transitions
order.status = "confirmed"
order.status = "preparing"
order.status = "delivered"

# Blocked: can't change delivered order
try:
    order.status = "pending"
except ValueError as e:
    print(f"  BLOCKED: {e}")

# Typo caught immediately!
order2 = Order("Priya", ["Biryani"])
try:
    order2.status = "delievered"  # Typo!
except ValueError as e:
    print(f"\n  TYPO CAUGHT: {e}")

print()
print("Without @property:")
print("  order.status = 'delievered' → stored silently, order stuck forever")
print("With @property:")
print("  order.status = 'delievered' → ValueError immediately, bug caught NOW")
