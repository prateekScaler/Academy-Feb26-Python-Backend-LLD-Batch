"""
OOP-1 Recap Quiz
=================
Quick refresher on the concepts from the previous class:
- What is `self`?
- Instance vs local variables
- Public vs private attributes
- @property with validation

Run: python 00_recap_quiz_oop1.py
"""


# ============================================================
# Question 1: What is `self`?
# ============================================================
print("=" * 60)
print("Q1: What is `self`?")
print("=" * 60)


class Order:
    def __init__(self, item_name, quantity):
        self.item_name = item_name   # self = the specific order being created
        self.quantity = quantity

    def summary(self):
        # self lets us access THIS order's data
        return f"{self.quantity}x {self.item_name}"


order_a = Order("Burger", 2)
order_b = Order("Pizza", 1)

print(f"order_a.summary() -> {order_a.summary()}")
print(f"order_b.summary() -> {order_b.summary()}")
print()
print("ANSWER: `self` refers to the specific object calling the method.")
print("        order_a.summary() -- self is order_a")
print("        order_b.summary() -- self is order_b")
print()


# ============================================================
# Question 2: What happens if you forget self.count vs count?
# ============================================================
print("=" * 60)
print("Q2: self.count vs count -- what's the difference?")
print("=" * 60)


class Kitchen:
    def __init__(self):
        self.dishes_prepared = 0   # stored ON the object (persists)

    def prepare_dish(self):
        local_counter = 1          # local variable (lost after method ends)
        self.dishes_prepared += 1  # updates the object's attribute

    def status(self):
        return f"Total dishes prepared: {self.dishes_prepared}"


kitchen = Kitchen()
kitchen.prepare_dish()
kitchen.prepare_dish()
kitchen.prepare_dish()
print(kitchen.status())
print()
print("ANSWER: self.dishes_prepared lives on the object -- it persists.")
print("        local_counter is a local variable -- it disappears after")
print("        the method finishes. If you wrote `dishes_prepared += 1`")
print("        without self, Python would look for a local variable and crash.")
print()


# ============================================================
# Question 3: Public vs private attribute access
# ============================================================
print("=" * 60)
print("Q3: Public vs Private attributes")
print("=" * 60)


class Restaurant:
    def __init__(self, name, secret_recipe):
        self.name = name                  # public -- anyone can read/write
        self.__secret_recipe = secret_recipe  # private -- name-mangled

    def reveal_recipe(self):
        # The class itself CAN access its own private attribute
        return f"Recipe: {self.__secret_recipe}"


r = Restaurant("Scaler Bites", "Add extra cheese at the end")

print(f"r.name           -> {r.name}")           # works fine
print(f"r.reveal_recipe() -> {r.reveal_recipe()}")  # works fine

try:
    print(r.__secret_recipe)
except AttributeError as e:
    print(f"r.__secret_recipe -> AttributeError: {e}")

# Python doesn't truly hide it -- just name-mangles it
print(f"r._Restaurant__secret_recipe -> {r._Restaurant__secret_recipe}")
print()
print("ANSWER: __attribute becomes _ClassName__attribute (name mangling).")
print("        It's a CONVENTION, not true security. Don't rely on it for secrets.")
print()


# ============================================================
# Question 4: @property with validation
# ============================================================
print("=" * 60)
print("Q4: @property with validation")
print("=" * 60)


class Dish:
    def __init__(self, name, price):
        self.name = name
        self.price = price   # this calls the @price.setter below

    @property
    def price(self):
        return self._price

    @price.setter
    def price(self, value):
        if value < 0:
            raise ValueError(f"Price cannot be negative! Got {value}")
        self._price = value


dish = Dish("Pasta", 250)
print(f"dish.price = {dish.price}")

dish.price = 300   # uses the setter -- validation runs
print(f"After dish.price = 300 -> {dish.price}")

try:
    dish.price = -50
except ValueError as e:
    print(f"dish.price = -50 -> ValueError: {e}")

print()
print("ANSWER: @property lets you add validation while keeping the")
print("        simple `obj.attribute = value` syntax. No need for")
print("        get_price() / set_price() Java-style methods.")
print()


# ============================================================
# Summary
# ============================================================
print("=" * 60)
print("RECAP COMPLETE")
print("=" * 60)
print("  1. self = the specific object calling the method")
print("  2. self.x persists on the object; x alone is local and temporary")
print("  3. __attr is name-mangled, not truly private")
print("  4. @property = controlled access with clean syntax")
print()
print("Now let's learn INHERITANCE and POLYMORPHISM!")
