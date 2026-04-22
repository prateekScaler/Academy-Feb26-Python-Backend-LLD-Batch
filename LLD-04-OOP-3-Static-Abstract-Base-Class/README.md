
# LLD-04: OOP-3 — Static Methods, Class Methods, and Abstract Base Classes

> Last class you learned to reuse code with inheritance and make it flexible with polymorphism. Now you learn how to **organize utility functions inside classes** and **enforce contracts** so that broken implementations get caught early.

---

## Quick Recap Quiz

Before we move forward, let's check what stuck from OOP-2. Try to answer without looking back.

**Q1:** What does `super().__init__()` do? What happens if a child class forgets to call it?

<details>
<summary>Answer</summary>

`super().__init__()` calls the parent class's constructor, setting up the parent's attributes (like `name` and `price`). If you forget it, the parent's setup code never runs — the object is incomplete. Accessing `self.name` would raise `AttributeError` because the attribute was never created.

</details>

**Q2:** In `class D(B, C)` where both `B` and `C` define `greet()`, which version runs when you call `D().greet()`?

<details>
<summary>Answer</summary>

`B`'s version runs. Python follows the Method Resolution Order (MRO), which goes left to right in the parent list. Since `B` is listed before `C`, `B.greet()` wins. You can check with `D.__mro__`.

</details>

**Q3:** What's the difference between **replacing** and **extending** a parent method?

<details>
<summary>Answer</summary>

**Replacing** means the child writes a completely new version — the parent's code never runs. **Extending** means the child calls `super().method()` first (or last) and then adds its own logic. Extending keeps the parent's behavior and builds on top of it.

</details>

**Q4:** Does Python support method overloading? What happens if you define two methods with the same name in a class?

<details>
<summary>Answer</summary>

No. The second definition **replaces** the first entirely. If you define `add(self, a, b)` and then `add(self, a, b, c)`, only the 3-parameter version exists. The Pythonic approach is to use default parameters or `*args`.

</details>

**Q5:** What does `_protected` vs `__private` mean for child classes?

<details>
<summary>Answer</summary>

`_protected` is a naming convention — child classes CAN access it directly, but it signals "this is internal." `__private` triggers name mangling — Python renames it to `_ParentClass__private`, so child classes can't access it by the original name. It's effectively hidden from children.

</details>

---

## Instance Methods vs Static Methods vs Class Methods

### Instance Methods — What You Already Know

Every method you've written so far is an instance method. It takes `self` as the first parameter and operates on a specific object's data.

```python
class Dish:
    def __init__(self, name, price):
        self.name = name
        self.price = price

    def describe(self):
        """Instance method — needs self to access this dish's name and price."""
        return f"{self.name} costs Rs.{self.price}"


biryani = Dish("Biryani", 300)
biryani.describe()  # "Biryani costs Rs.300"
```

`describe()` makes no sense without a specific `Dish` object. It needs `self.name` and `self.price`. That's why it's an instance method.

---

### The Problem — Where Do Utility Functions Live?

Your restaurant app needs a function to validate prices. A price must be a positive number, not negative, not zero.

```python
# This works, but where does it live?
def is_valid_price(price):
    return isinstance(price, (int, float)) and price > 0


class Dish:
    def __init__(self, name, price):
        if not is_valid_price(price):  # Calling a floating function
            raise ValueError(f"Invalid price: {price}")
        self.name = name
        self.price = price
```

`is_valid_price` doesn't need a `Dish` object — it just checks a number. But it's clearly related to `Dish`. It's floating outside the class like an orphan. If someone reads your codebase, they have no idea this function is related to dishes.

Now imagine 50 such utility functions scattered across the file. Which class do they belong to? Nobody knows.

> **Question:** You have `is_valid_price()`, `is_valid_name()`, `format_currency()`, and `calculate_tax()` — all related to `Dish` but none needing a `Dish` object. Where do they live? In a separate `utils.py`? At the top of the file? Inside the class somehow?

---

### Static Methods — `@staticmethod`

A **static method** is a regular function that lives inside a class for organizational purposes. It doesn't get `self` (no instance) and doesn't get `cls` (no class). It's just a function with a class address.

```python
class Dish:
    def __init__(self, name, price):
        if not Dish.is_valid_price(price):
            raise ValueError(f"Invalid price: {price}")
        self.name = name
        self.price = price

    def describe(self):
        """Instance method — needs self."""
        return f"{self.name} costs Rs.{self.price}"

    @staticmethod
    def is_valid_price(price):
        """Static method — no self, no cls. Just a utility function."""
        return isinstance(price, (int, float)) and price > 0

    @staticmethod
    def format_currency(amount):
        """Static method — formats any number as currency."""
        return f"Rs.{amount:,.2f}"
```

```python
# Can call on the class — no object needed
print(Dish.is_valid_price(300))      # True
print(Dish.is_valid_price(-50))      # False
print(Dish.format_currency(1299.5))  # "Rs.1,299.50"

# Can also call on an instance — same result
biryani = Dish("Biryani", 300)
print(biryani.is_valid_price(300))   # True — works, but less common
```

**When to use `@staticmethod`:**
- The function is related to the class but doesn't need instance data (`self`) or class data (`cls`)
- It's a utility/helper function: validation, conversion, formatting
- You want to group related functions together for organization

**More examples:**

```python
class Temperature:
    def __init__(self, celsius):
        self.celsius = celsius

    @staticmethod
    def celsius_to_fahrenheit(c):
        return (c * 9/5) + 32

    @staticmethod
    def fahrenheit_to_celsius(f):
        return (f - 32) * 5/9


# No Temperature object needed
print(Temperature.celsius_to_fahrenheit(100))  # 212.0
print(Temperature.fahrenheit_to_celsius(32))   # 0.0
```

> **Question:** Could you write `celsius_to_fahrenheit` as a regular function outside the class? Yes. Would the code still work? Yes. So why put it inside the class? Because when someone sees `Temperature.celsius_to_fahrenheit()`, they immediately know this function is related to temperature. Organization matters as codebases grow.

---

### Class Methods — `@classmethod`

A **class method** gets `cls` (the class itself) as the first parameter, instead of `self` (an instance). It can access and modify class-level data, and — most importantly — it can create new instances of the class.

```python
class MenuItem:
    restaurant_name = "Spice Garden"  # Class-level attribute — shared by all instances

    def __init__(self, name, price, is_available=True):
        self.name = name
        self.price = price
        self.is_available = is_available

    def describe(self):
        """Instance method — needs self."""
        return f"{self.name} - Rs.{self.price}"

    @classmethod
    def from_dict(cls, data):
        """Class method — creates a MenuItem from a dictionary."""
        return cls(
            name=data["name"],
            price=data["price"],
            is_available=data.get("is_available", True)
        )

    @classmethod
    def from_csv_line(cls, line):
        """Class method — creates a MenuItem from a CSV string."""
        parts = line.split(",")
        return cls(name=parts[0], price=float(parts[1]))

    @classmethod
    def get_restaurant_name(cls):
        """Class method — accesses class-level data."""
        return cls.restaurant_name
```

```python
# Normal constructor
biryani = MenuItem("Biryani", 300)

# Alternative constructor — from a dictionary (e.g., from a JSON API)
data = {"name": "Butter Chicken", "price": 350, "is_available": True}
bc = MenuItem.from_dict(data)
print(bc.describe())  # "Butter Chicken - Rs.350"

# Alternative constructor — from a CSV line (e.g., from a file import)
naan = MenuItem.from_csv_line("Garlic Naan,60")
print(naan.describe())  # "Garlic Naan - Rs.60.0"

# Accessing class-level data
print(MenuItem.get_restaurant_name())  # "Spice Garden"
```

**The key use case: alternative constructors (factory methods).** The regular `__init__` takes `name` and `price` directly. But real data comes in many formats — dictionaries from APIs, CSV lines from files, database rows, XML. Class methods let you create objects from any format without stuffing all that parsing logic into `__init__`.

**Real Python examples you've already seen:**

```python
from datetime import datetime

# Normal constructor
dt = datetime(2026, 4, 20, 14, 30)

# Class method constructors — alternative ways to create a datetime
now = datetime.now()                              # From the system clock
ts = datetime.fromtimestamp(1745150400)            # From a Unix timestamp
parsed = datetime.strptime("2026-04-20", "%Y-%m-%d")  # From a string
```

These are all `@classmethod` calls. The `datetime` class has one `__init__` but multiple ways to create instances.

---

### Why `cls` Instead of Hardcoding the Class Name?

This is the subtle but important part. Watch what happens with inheritance:

```python
class MenuItem:
    def __init__(self, name, price):
        self.name = name
        self.price = price

    @classmethod
    def from_dict(cls, data):
        # cls is whatever class called this method!
        return cls(name=data["name"], price=data["price"])


class Food(MenuItem):
    def __init__(self, name, price, is_vegetarian=False):
        super().__init__(name, price)
        self.is_vegetarian = is_vegetarian


# When called on Food, cls = Food, NOT MenuItem
data = {"name": "Paneer Tikka", "price": 280}
item = Food.from_dict(data)
print(type(item))  # <class 'Food'> — NOT MenuItem!
```

If we had written `return MenuItem(...)` instead of `return cls(...)`, calling `Food.from_dict()` would return a `MenuItem` object, not a `Food` object. That would be a bug. `cls` ensures the method works correctly with inheritance.

> **Question:** You have `MenuItem.from_dict()` using `cls`. A new child class `Beverage(MenuItem)` calls `Beverage.from_dict(data)`. What is `cls` inside `from_dict`? What type of object gets created?

---

### Comparison Table

| | Instance Method | Static Method | Class Method |
|---|---|---|---|
| **First param** | `self` (the instance) | none | `cls` (the class) |
| **Access instance data?** | Yes | No | No |
| **Access class data?** | Yes (via `self.__class__` or directly) | No | Yes (via `cls`) |
| **Call syntax** | `obj.method()` | `Class.method()` or `obj.method()` | `Class.method()` or `obj.method()` |
| **Decorator** | none needed | `@staticmethod` | `@classmethod` |
| **Use case** | Operate on object data | Utility functions | Alternative constructors, class-level operations |

> **Question:** You need to write a method that counts the total number of `MenuItem` objects ever created. Should it be an instance method, static method, or class method? (Hint: you need a class-level counter that `cls` can access.)

<details>
<summary>Answer</summary>

A `@classmethod`. You'd keep a class-level counter `MenuItem.count = 0`, increment it in `__init__`, and read it via `cls.count` in the class method.

```python
class MenuItem:
    count = 0

    def __init__(self, name, price):
        self.name = name
        self.price = price
        MenuItem.count += 1

    @classmethod
    def get_total_count(cls):
        return cls.count
```

</details>

---

## Abstract Base Classes (ABC)

### The Problem — Duck Typing's Weakness

Remember duck typing from OOP-2? "If it has a `send()` method, we can use it." This function works with any object that has `send()`:

```python
def notify_all(notifiers, message):
    for notifier in notifiers:
        notifier.send(message)
```

Beautiful. Flexible. But what happens when someone writes this?

```python
class EmailNotification:
    def send(self, message):
        print(f"Email: {message}")


class SMSNotification:
    def send(self, message):
        print(f"SMS: {message}")


class BrokenNotification:
    # Oops — forgot to implement send()!
    def receive(self, message):
        print(f"Received: {message}")


# This works fine...
notify_all([EmailNotification(), SMSNotification()], "Order confirmed!")

# This CRASHES at runtime!
notify_all([BrokenNotification()], "Order confirmed!")
# AttributeError: 'BrokenNotification' object has no attribute 'send'
```

The `BrokenNotification` object was **created successfully**. Nobody complained. It sat there in your system, a ticking time bomb, until someone actually tried to call `send()` on it — maybe in production, at 2 AM, with real customer orders.

The crash happens at **runtime** (when the method is called), not at **creation time** (when the object is made). That's the problem.

> **Question:** You're building a payment system. Your `PaymentGateway` base class has a `charge()` method. A new developer joins, creates `NewGateway`, and forgets to implement `charge()`. With duck typing, when does the system break — during testing or when a customer tries to pay?

---

### The Solution — ABC Enforces the Contract

Python's `abc` module lets you define **Abstract Base Classes** — classes that act as contracts. They say: "If you inherit from me, you MUST implement these methods. No exceptions."

```python
from abc import ABC, abstractmethod


class Notification(ABC):
    """Abstract class — cannot be instantiated directly.
    Any child MUST implement send()."""

    @abstractmethod
    def send(self, message):
        """Every notification type must define how to send."""
        pass


class EmailNotification(Notification):
    def send(self, message):
        print(f"Email: {message}")


class SMSNotification(Notification):
    def send(self, message):
        print(f"SMS: {message}")


class BrokenNotification(Notification):
    pass  # Forgot to implement send()!
```

Now watch what happens:

```python
email = EmailNotification()        # Works fine
sms = SMSNotification()            # Works fine

broken = BrokenNotification()      # TypeError!
# TypeError: Can't instantiate abstract class BrokenNotification
#            with abstract method send
```

The error happens at **creation time** — the moment you try to create a `BrokenNotification` object. Not when you call `send()`. Not in production. Not at 2 AM. **Right here, right now, during development.**

This is the key difference:

| | Duck Typing | ABC |
|---|---|---|
| When does the error happen? | When the method is called (runtime) | When the object is created (creation time) |
| Where in production? | During customer checkout | During deployment/testing |
| Error message | `AttributeError: no attribute 'send'` | `TypeError: Can't instantiate abstract class` |
| Who catches it? | Probably a customer | Probably you, the developer |

---

### Real Example — Payment Gateway

A payment system where every gateway MUST support `charge()` and `refund()`:

```python
from abc import ABC, abstractmethod


class PaymentGateway(ABC):
    """Abstract base class — defines the contract for all payment gateways."""

    @abstractmethod
    def charge(self, amount, currency="INR"):
        """Process a payment. Must return a transaction ID."""
        pass

    @abstractmethod
    def refund(self, transaction_id, amount):
        """Refund a payment. Must return True/False."""
        pass

    def log_transaction(self, action, amount):
        """Concrete method — shared by all gateways. NOT abstract."""
        print(f"[LOG] {self.__class__.__name__}: {action} Rs.{amount}")


class RazorpayGateway(PaymentGateway):
    def charge(self, amount, currency="INR"):
        self.log_transaction("CHARGE", amount)
        # In real code: call Razorpay API
        return "rzp_txn_123456"

    def refund(self, transaction_id, amount):
        self.log_transaction("REFUND", amount)
        # In real code: call Razorpay refund API
        return True


class StripeGateway(PaymentGateway):
    def charge(self, amount, currency="INR"):
        self.log_transaction("CHARGE", amount)
        # In real code: call Stripe API
        return "stripe_pi_789"

    def refund(self, transaction_id, amount):
        self.log_transaction("REFUND", amount)
        return True


class BrokenGateway(PaymentGateway):
    def charge(self, amount, currency="INR"):
        return "broken_txn"
    # Forgot to implement refund()!
```

```python
razorpay = RazorpayGateway()   # Works
stripe = StripeGateway()       # Works

broken = BrokenGateway()       # TypeError!
# TypeError: Can't instantiate abstract class BrokenGateway
#            with abstract method refund
```

Notice: `log_transaction()` is a **concrete method** (not abstract). It has a real implementation that all gateways share. Abstract classes can have a mix of abstract methods (must be overridden) and concrete methods (shared as-is).

> **Question:** Can you create an instance of `PaymentGateway` directly? Try `gateway = PaymentGateway()`. What happens and why?

<details>
<summary>Answer</summary>

`TypeError: Can't instantiate abstract class PaymentGateway with abstract methods charge, refund`. You can NEVER instantiate an abstract class directly. It's a contract, not a concrete thing. You must create a child class that implements ALL abstract methods.

</details>

---

### Abstract Properties

You can also make properties abstract. Every child class MUST provide that property.

```python
from abc import ABC, abstractmethod


class MenuItem(ABC):
    def __init__(self, name, price):
        self.name = name
        self.price = price

    @property
    @abstractmethod
    def category(self):
        """Every menu item must declare its category."""
        pass

    def display(self):
        return f"[{self.category}] {self.name} - Rs.{self.price}"


class Food(MenuItem):
    @property
    def category(self):
        return "Food"


class Beverage(MenuItem):
    @property
    def category(self):
        return "Beverage"


class MysteryItem(MenuItem):
    pass  # Forgot to define category!
```

```python
biryani = Food("Biryani", 300)
print(biryani.display())  # "[Food] Biryani - Rs.300"

chai = Beverage("Masala Chai", 60)
print(chai.display())     # "[Beverage] Masala Chai - Rs.60"

mystery = MysteryItem("???", 100)  # TypeError! Missing abstract property 'category'
```

Notice the decorator order: `@property` goes on top of `@abstractmethod`. The child class implements it as a regular `@property`.

---

### When to Use ABC vs Duck Typing

Both are valid approaches. The choice depends on context:

| Situation | Use |
|---|---|
| Small script, personal project | Duck typing — keep it simple |
| Internal code, small team | Duck typing — everyone knows the convention |
| Large team, many developers | ABC — new developers can't accidentally skip methods |
| Public library/API | ABC — users need a clear contract |
| Payment, auth, critical systems | ABC — bugs here cost money or security |

**ABC = documentation + enforcement in one.** When someone reads an abstract class, they immediately see: "To create a new gateway, I need `charge()` and `refund()`." No guessing, no reading through documentation, no hunting through existing implementations.

> **Question:** You're building a plugin system where third-party developers write plugins for your app. Each plugin must have `activate()`, `deactivate()`, and `get_info()` methods. Would you use duck typing or ABC? Why?

---

## Combining Everything — Static + Class + Abstract

Let's build a complete example that uses all three concepts together:

```python
from abc import ABC, abstractmethod


class MenuItem(ABC):
    """Abstract base class for all menu items.
    - Abstract method: calculate_price() — each type prices differently
    - Class method: from_dict() — alternative constructor
    - Static method: is_valid_price() — utility validation
    """

    def __init__(self, name, base_price):
        if not MenuItem.is_valid_price(base_price):
            raise ValueError(f"Invalid price: {base_price}")
        self.name = name
        self.base_price = base_price

    @abstractmethod
    def calculate_price(self):
        """Each menu item type calculates final price differently."""
        pass

    @classmethod
    def from_dict(cls, data):
        """Alternative constructor — create from a dictionary."""
        return cls(name=data["name"], base_price=data["base_price"])

    @staticmethod
    def is_valid_price(price):
        """Utility — check if a price value is valid."""
        return isinstance(price, (int, float)) and price > 0

    def display(self):
        """Concrete method — shared by all items."""
        return f"{self.name}: Rs.{self.calculate_price()}"


class Food(MenuItem):
    """Food items — 5% packaging charge added."""

    def __init__(self, name, base_price, is_vegetarian=False):
        super().__init__(name, base_price)
        self.is_vegetarian = is_vegetarian

    def calculate_price(self):
        return round(self.base_price * 1.05, 2)

    @classmethod
    def from_dict(cls, data):
        """Override from_dict to handle is_vegetarian."""
        return cls(
            name=data["name"],
            base_price=data["base_price"],
            is_vegetarian=data.get("is_vegetarian", False)
        )

    def display(self):
        veg = "[V]" if self.is_vegetarian else "[NV]"
        return f"{veg} {self.name}: Rs.{self.calculate_price()}"


class Beverage(MenuItem):
    """Beverages — price depends on size."""
    SIZE_MULTIPLIERS = {"Small": 1.0, "Medium": 1.3, "Large": 1.6}

    def __init__(self, name, base_price, size="Medium"):
        super().__init__(name, base_price)
        self.size = size

    def calculate_price(self):
        multiplier = self.SIZE_MULTIPLIERS.get(self.size, 1.0)
        return round(self.base_price * multiplier, 2)

    def display(self):
        return f"{self.name} ({self.size}): Rs.{self.calculate_price()}"
```

```python
# Static method — no object needed
print(MenuItem.is_valid_price(300))   # True
print(MenuItem.is_valid_price(-50))   # False

# Class method — create from dictionary
food_data = {"name": "Paneer Tikka", "base_price": 280, "is_vegetarian": True}
paneer = Food.from_dict(food_data)
print(paneer.display())  # "[V] Paneer Tikka: Rs.294.0"

# Regular constructor
chai = Beverage("Masala Chai", 50, "Large")
print(chai.display())  # "Masala Chai (Large): Rs.80.0"

# Abstract class can't be instantiated
# item = MenuItem("Test", 100)  # TypeError! Can't instantiate abstract class

# Polymorphism still works
menu = [paneer, chai, Food("Biryani", 300)]
for item in menu:
    print(item.display())  # Each type displays differently
```

Notice how all three work together:
- **`@abstractmethod`** forces every child to implement `calculate_price()` — the contract
- **`@classmethod from_dict()`** provides alternative construction — with `cls` for proper inheritance
- **`@staticmethod is_valid_price()`** validates data — no instance or class needed

---

## Common Mistakes

### 1. Making Everything Static

```python
# BAD — if you need self, it's NOT a static method
class Order:
    def __init__(self, items):
        self.items = items

    @staticmethod
    def get_total(items):  # Why pass items when it's already in self?
        return sum(item.price for item in items)

order = Order([item1, item2])
order.get_total(order.items)  # Awkward! You're passing what the object already has.
```

```python
# GOOD — this needs self, so it's an instance method
class Order:
    def __init__(self, items):
        self.items = items

    def get_total(self):
        return sum(item.price for item in self.items)

order = Order([item1, item2])
order.get_total()  # Clean — the object knows its own items
```

**Rule of thumb:** If the method needs `self`, it's an instance method. If it needs `cls`, it's a class method. If it needs neither, it's a static method. Don't force-fit.

### 2. Forgetting `@abstractmethod` Without ABC

```python
# BAD — @abstractmethod does nothing without ABC as parent!
class Notification:  # Not inheriting from ABC
    @abstractmethod
    def send(self, message):
        pass

broken = Notification()  # No error! The decorator is ignored.
```

```python
# GOOD — inherit from ABC for @abstractmethod to work
from abc import ABC, abstractmethod

class Notification(ABC):  # ABC parent is required
    @abstractmethod
    def send(self, message):
        pass

broken = Notification()  # TypeError! Correctly enforced.
```

### 3. Abstract Class With No Abstract Methods

```python
# POINTLESS — if nothing is abstract, why use ABC?
from abc import ABC

class MenuItem(ABC):
    def describe(self):
        return "I'm a menu item"

item = MenuItem()  # Works fine — no abstract methods to enforce
```

If your class inherits from `ABC` but has zero `@abstractmethod` decorators, it can be instantiated normally. The `ABC` parent does nothing without abstract methods. Either add abstract methods or don't use `ABC`.

### 4. Using `@staticmethod` When You Need `cls`

```python
# BAD — this breaks with inheritance
class MenuItem:
    @staticmethod
    def create_default():
        return MenuItem("Default Item", 0)  # Hardcoded class name!

class Food(MenuItem):
    pass

item = Food.create_default()
print(type(item))  # <class 'MenuItem'> — should be Food!
```

```python
# GOOD — use @classmethod when you need to create instances
class MenuItem:
    @classmethod
    def create_default(cls):
        return cls("Default Item", 0)  # cls = whatever class called this

class Food(MenuItem):
    pass

item = Food.create_default()
print(type(item))  # <class 'Food'> — correct!
```

**If the method creates an instance of the class, use `@classmethod`.** If it's a pure utility function that doesn't need `cls` or `self`, use `@staticmethod`.

---

## Connecting to What's Next

| Today (OOP-3) | Concurrency Module | Design Patterns |
|---|---|---|
| **Static methods** | Thread-safe utility functions | **Singleton pattern** uses `@classmethod` |
| **ABC / `@abstractmethod`** | -- | **Strategy pattern**: ABC defines the interface, children are strategies |
| **Abstract + child implementations** | -- | **Factory pattern**: ABC defines the product, children are concrete products |
| **Class methods** | -- | **Factory method pattern**: `@classmethod` as the factory |

The patterns you're learning now are the **building blocks** of design patterns. When we reach the design patterns module, you won't be learning new Python features — you'll be learning how to COMBINE the features you already know (`ABC`, `@classmethod`, inheritance, polymorphism) into proven architectural solutions.

---

## Resources

- [Scaler Topics — Python OOP](https://www.scaler.com/topics/python/) — Scaler's own Python learning path
- [Real Python — Abstract Base Classes](https://realpython.com/python-interface/#using-abstract-method-declaration) — When and how to use ABCs
- [Corey Schafer — Static and Class Methods (YouTube)](https://www.youtube.com/watch?v=rq8cL2XMM5M) — Clear 15-minute walkthrough with examples
- [Python docs — abc module](https://docs.python.org/3/library/abc.html) — Official documentation for Abstract Base Classes
