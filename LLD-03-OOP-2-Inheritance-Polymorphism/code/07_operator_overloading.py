"""
Operator Overloading -- Making Operators Work with Your Classes
================================================================
Special "dunder" (double underscore) methods let you define what
+, ==, len(), print(), etc. do for YOUR custom objects.

- __str__  -> what print() shows
- __add__  -> what + does
- __len__  -> what len() returns
- __eq__   -> what == checks

Run: python 07_operator_overloading.py
"""


# ============================================================
# 1. __str__ -- what print() shows
# ============================================================
print("=" * 60)
print("1. __str__ -- Custom Print Output")
print("=" * 60)
print()


class Dish:
    def __init__(self, name, price):
        self.name = name
        self.price = price


class DishWithStr:
    def __init__(self, name, price):
        self.name = name
        self.price = price

    def __str__(self):
        return f"{self.name} (Rs.{self.price})"


# Without __str__
plain = Dish("Burger", 199)
print(f"Without __str__: {plain}")

# With __str__
nice = DishWithStr("Burger", 199)
print(f"With __str__:    {nice}")
print()
print("print() automatically calls __str__() on your object.")
print("Without it, you get an ugly <__main__.Dish object at 0x...> message.")
print()


# ============================================================
# 2. __add__ -- what + does
# ============================================================
print("=" * 60)
print("2. __add__ -- Custom + Operator (Money Example)")
print("=" * 60)
print()


class Money:
    def __init__(self, amount, currency="INR"):
        self.amount = amount
        self.currency = currency

    def __add__(self, other):
        if self.currency != other.currency:
            raise ValueError(f"Cannot add {self.currency} and {other.currency}")
        return Money(self.amount + other.amount, self.currency)

    def __str__(self):
        return f"Rs.{self.amount}"


price1 = Money(199)
price2 = Money(149)
total = price1 + price2   # calls price1.__add__(price2)

print(f"  {price1} + {price2} = {total}")
print()

# Chaining works too
price3 = Money(99)
grand_total = price1 + price2 + price3
print(f"  {price1} + {price2} + {price3} = {grand_total}")
print()

# Different currencies
usd = Money(10, "USD")
try:
    result = price1 + usd
except ValueError as e:
    print(f"  Rs.199 + $10 -> ValueError: {e}")
print()


# ============================================================
# 3. __len__ -- what len() returns
# ============================================================
print("=" * 60)
print("3. __len__ -- Custom len() (Cart Example)")
print("=" * 60)
print()


class Cart:
    def __init__(self):
        self.items = []

    def add(self, item_name):
        self.items.append(item_name)

    def __len__(self):
        return len(self.items)

    def __str__(self):
        return f"Cart with {len(self)} items: {', '.join(self.items)}"


cart = Cart()
print(f"  Empty cart: len(cart) = {len(cart)}")

cart.add("Burger")
cart.add("Fries")
cart.add("Cola")
print(f"  After adding 3 items: len(cart) = {len(cart)}")
print(f"  {cart}")
print()

# __len__ also makes bool() work!
empty_cart = Cart()
full_cart = Cart()
full_cart.add("Pizza")

print(f"  bool(empty_cart) = {bool(empty_cart)}  (len=0 is falsy)")
print(f"  bool(full_cart)  = {bool(full_cart)}  (len>0 is truthy)")
print()


# ============================================================
# 4. __eq__ -- what == checks
# ============================================================
print("=" * 60)
print("4. __eq__ -- Custom Equality (MenuItem Example)")
print("=" * 60)
print()


class MenuItem:
    def __init__(self, name, price):
        self.name = name
        self.price = price

    def __eq__(self, other):
        if not isinstance(other, MenuItem):
            return False
        return self.name == other.name and self.price == other.price

    def __str__(self):
        return f"{self.name} (Rs.{self.price})"


item_a = MenuItem("Burger", 199)
item_b = MenuItem("Burger", 199)
item_c = MenuItem("Burger", 249)

print(f"  {item_a} == {item_b} -> {item_a == item_b}   (same name, same price)")
print(f"  {item_a} == {item_c} -> {item_a == item_c}  (same name, different price)")
print()

# Without __eq__, Python compares by memory address (identity)
plain_a = Dish("Burger", 199)
plain_b = Dish("Burger", 199)
print(f"  Without __eq__: Dish('Burger', 199) == Dish('Burger', 199) -> {plain_a == plain_b}")
print("  (False! Because Python compares memory addresses by default)")
print()


# ============================================================
# 5. All the common dunder methods at a glance
# ============================================================
print("=" * 60)
print("5. Common Dunder Methods -- Reference")
print("=" * 60)
print()
print("  Method         Triggered by       Example")
print("  -----------    ----------------   -------------------")
print("  __str__        print(obj), str()  print(dish)")
print("  __repr__       repr(obj), REPL    >>> dish")
print("  __add__        obj + other        money1 + money2")
print("  __sub__        obj - other        money1 - money2")
print("  __mul__        obj * other        price * 3")
print("  __len__        len(obj)           len(cart)")
print("  __eq__         obj == other       item_a == item_b")
print("  __lt__         obj < other        item_a < item_b")
print("  __getitem__    obj[key]           cart[0]")
print("  __contains__   x in obj           'Burger' in cart")
print()
print("You don't need to memorize all of these.")
print("Just know: if an operator doesn't work on your class,")
print("there's probably a dunder method you can define to make it work.")
