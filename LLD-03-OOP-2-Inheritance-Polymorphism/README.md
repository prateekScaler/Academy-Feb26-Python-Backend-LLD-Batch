# LLD-03: OOP-2 — Inheritance and Polymorphism

> Last class you learned to build classes with constructors, access modifiers, and encapsulation. Now you learn how to **reuse those classes and make them flexible** — without copy-pasting code.

---

## Quick Recap Quiz

Before we move forward, let's check what stuck from OOP-1. Try to answer without looking back.

**Q1:** What is `self` in Python? When you write `c1.increment()`, what does Python actually call behind the scenes?

<details>
<summary>Answer</summary>

`self` refers to the specific object the method is being called on. Python translates `c1.increment()` into `Counter.increment(c1)` — so `self = c1`.

</details>

**Q2:** What's the difference between a parameterized and non-parameterized constructor? Why is this bad?

```python
dish = Dish()
dish.name = "Biryani"
dish.price = 300
```

<details>
<summary>Answer</summary>

A non-parameterized constructor takes no arguments (except `self`). A parameterized one requires data upfront: `Dish("Biryani", 300)`. The bad example creates an incomplete object — if someone forgets to set `name`, calling `dish.describe()` would crash. An object should be **ready to use the moment it's created.**

</details>

**Q3:** What does `@property` do? Why is it better than making `balance` a public attribute?

<details>
<summary>Answer</summary>

`@property` lets you run validation code behind what looks like simple attribute access. `account.balance` can trigger a getter, and `account.balance = -500` can trigger a setter that rejects invalid values. Without it, anyone can set `account.balance = -99999` and break everything.

</details>

**Q4:** What's the difference between `_name` (single underscore) and `__name` (double underscore)?

<details>
<summary>Answer</summary>

`_name` is a convention meaning "this is internal, please don't touch." Python doesn't enforce it. `__name` triggers **name mangling** — Python renames it to `_ClassName__name`, making accidental access nearly impossible. Neither is truly private — Python trusts developers ("we're all consenting adults").

</details>

---

## Inheritance — "Reuse and Extend"

### The Real-World Idea

Think about vehicles. Every vehicle has some things in common — it has a make, a model, a speed, and it can start and stop. But a Car has doors and seats, a Motorcycle has handlebars, a Truck has cargo capacity.

You wouldn't design a Car from scratch, then design a Truck from scratch, then copy-paste the common parts. You'd start with a general **Vehicle** concept and then **specialize** it.

That's inheritance. A **child class** gets everything from the **parent class** and then adds or changes what's specific to it.

```
        Vehicle (parent)
       /    |    \
     Car  Truck  Motorcycle (children)
```

In a restaurant system:

```
        MenuItem (parent)
       /    |    \
    Food  Beverage  Dessert (children)
```

Every menu item has a name, a price, and a description. But Food has `is_vegetarian`, Beverage has `size` and `is_cold`, Dessert has `allergens`. Inheritance lets us define the common stuff ONCE.

---

### The Duplication Problem — Why Copy-Pasting Code is Bad

Let's say your restaurant app needs classes for different menu item types.

**Without inheritance (the copy-paste approach):**

```python
class Food:
    def __init__(self, name, price, description, is_vegetarian):
        self.name = name
        self.price = price
        self.description = description
        self.is_vegetarian = is_vegetarian

    def get_summary(self):
        return f"{self.name} - Rs.{self.price}"

    def apply_discount(self, percent):
        self.price = self.price * (1 - percent / 100)


class Beverage:
    def __init__(self, name, price, description, size, is_cold):
        self.name = name               # ← Duplicated
        self.price = price             # ← Duplicated
        self.description = description # ← Duplicated
        self.size = size
        self.is_cold = is_cold

    def get_summary(self):             # ← Duplicated
        return f"{self.name} - Rs.{self.price}"

    def apply_discount(self, percent): # ← Duplicated
        self.price = self.price * (1 - percent / 100)


class Dessert:
    def __init__(self, name, price, description, allergens):
        self.name = name               # ← Duplicated again!
        self.price = price             # ← Duplicated again!
        self.description = description # ← Duplicated again!
        self.allergens = allergens

    def get_summary(self):             # ← Duplicated again!
        return f"{self.name} - Rs.{self.price}"

    def apply_discount(self, percent): # ← Duplicated again!
        self.price = self.price * (1 - percent / 100)
```

**Three classes. The same code is written three times.** Now imagine:

- A bug in `apply_discount` — you fix it in `Food` but forget `Beverage`. Now one works, the other doesn't.
- The PM says "add a `category` field to all menu items" — you update three constructors, three tests, three places to make mistakes.
- You add a fourth type (Combo) — you copy-paste a fourth time.

This violates **DRY (Don't Repeat Yourself)** — one of the most fundamental principles in programming.

> **Question:** You have 6 types of menu items and a bug in `apply_discount`. How many files do you check? How many do you forget to update? What happens when a customer gets a wrong bill because one item type calculates discounts differently?

---

### Basic Syntax — `class Child(Parent)`

Inheritance in Python is one pair of parentheses:

```python
class MenuItem:
    """Parent class — everything common to all menu items."""
    def __init__(self, name, price, description):
        self.name = name
        self.price = price
        self.description = description

    def get_summary(self):
        return f"{self.name} - Rs.{self.price}"

    def apply_discount(self, percent):
        self.price = self.price * (1 - percent / 100)


class Food(MenuItem):
    """Child class — inherits from MenuItem, adds food-specific stuff."""
    def __init__(self, name, price, description, is_vegetarian):
        super().__init__(name, price, description)  # Call parent's constructor
        self.is_vegetarian = is_vegetarian


class Beverage(MenuItem):
    """Child class — inherits from MenuItem, adds beverage-specific stuff."""
    def __init__(self, name, price, description, size, is_cold):
        super().__init__(name, price, description)  # Call parent's constructor
        self.size = size
        self.is_cold = is_cold


class Dessert(MenuItem):
    """Child class — inherits from MenuItem, adds dessert-specific stuff."""
    def __init__(self, name, price, description, allergens):
        super().__init__(name, price, description)  # Call parent's constructor
        self.allergens = allergens
```

Now `get_summary()` and `apply_discount()` exist in ONE place. Bug fix? Fix it once in `MenuItem`. Add a field? Add it once. Add a new type (Combo)? Just inherit from `MenuItem`.

```python
# All of these work — the child inherits the parent's methods
butter_chicken = Food("Butter Chicken", 350, "Creamy tomato gravy", False)
lassi = Beverage("Mango Lassi", 120, "Sweet yogurt drink", "Large", True)

print(butter_chicken.get_summary())  # "Butter Chicken - Rs.350"
print(lassi.get_summary())           # "Mango Lassi - Rs.120"

butter_chicken.apply_discount(10)
print(butter_chicken.price)           # 315.0
```

---

### What Gets Inherited

When a child class inherits from a parent, it gets:

| Inherited | Not Inherited |
|---|---|
| All public methods | `__init__` is NOT automatically called (you must use `super()`) |
| All public attributes | Private attributes (double underscore) — name-mangled to parent |
| All protected methods/attributes (`_name`) | Nothing is "blocked" — but private attrs need the parent's name to access |

```python
class MenuItem:
    def __init__(self, name, price):
        self.name = name           # Public — inherited
        self._category = "general" # Protected — inherited
        self.__id = id(self)       # Private — name-mangled

class Food(MenuItem):
    def __init__(self, name, price, is_veg):
        super().__init__(name, price)
        self.is_veg = is_veg

    def show_info(self):
        print(self.name)       # Works — public, inherited
        print(self._category)  # Works — protected, inherited
        # print(self.__id)     # AttributeError! It's _MenuItem__id
```

---

### `super().__init__()` — Calling the Parent Constructor

This is the most important line in inheritance. Let's connect it to what you learned about constructors in OOP-1.

Remember: a constructor sets up the object's initial state. When a child class has its OWN constructor, it **overrides** the parent's. If you don't call `super().__init__()`, the parent's setup code never runs.

**What happens when you forget `super().__init__()`:**

```python
class MenuItem:
    def __init__(self, name, price):
        self.name = name
        self.price = price

class Food(MenuItem):
    def __init__(self, name, price, is_vegetarian):
        # Forgot to call super().__init__()!
        self.is_vegetarian = is_vegetarian

biryani = Food("Biryani", 300, False)
print(biryani.is_vegetarian)  # False ✓
print(biryani.name)            # AttributeError! name was never set
```

The parent's constructor never ran, so `name` and `price` were never assigned. The object is **incomplete** — exactly the problem we warned about in OOP-1.

**The correct way:**

```python
class Food(MenuItem):
    def __init__(self, name, price, is_vegetarian):
        super().__init__(name, price)   # ← Let the parent set up its part
        self.is_vegetarian = is_vegetarian  # ← Then set up the child's part
```

Think of it like building a house. The parent lays the foundation (name, price). The child builds the extra rooms (is_vegetarian). If you skip the foundation, the extra rooms have nothing to stand on.

> **Question:** In OOP-1, we said "an object should be ready to use the moment it's created." If `Food` forgets `super().__init__()`, is the object ready to use? What breaks?

---

### Method Overriding — Child Changes Parent's Behavior

A child class can **override** (replace) a method from the parent. The child provides its own version.

```python
class MenuItem:
    def __init__(self, name, price):
        self.name = name
        self.price = price

    def get_summary(self):
        return f"{self.name} - Rs.{self.price}"


class Food(MenuItem):
    def __init__(self, name, price, is_vegetarian):
        super().__init__(name, price)
        self.is_vegetarian = is_vegetarian

    def get_summary(self):  # ← Overrides parent's get_summary
        veg = "Veg" if self.is_vegetarian else "Non-Veg"
        return f"{self.name} - Rs.{self.price} ({veg})"


class Beverage(MenuItem):
    def __init__(self, name, price, size):
        super().__init__(name, price)
        self.size = size

    def get_summary(self):  # ← Different override
        return f"{self.name} ({self.size}) - Rs.{self.price}"


# Same method name, different behavior
bc = Food("Butter Chicken", 350, False)
lassi = Beverage("Lassi", 80, "Large")

print(bc.get_summary())     # "Butter Chicken - Rs.350 (Non-Veg)"
print(lassi.get_summary())  # "Lassi (Large) - Rs.80"
```

The parent defines the DEFAULT behavior. The child can keep it or replace it. If the child doesn't override, it uses the parent's version.

---

### `isinstance()` and `issubclass()`

These let you check relationships at runtime.

```python
bc = Food("Butter Chicken", 350, False)

# isinstance — "Is this object of this type?"
print(isinstance(bc, Food))      # True — bc IS a Food
print(isinstance(bc, MenuItem))  # True — bc is ALSO a MenuItem (via inheritance)
print(isinstance(bc, Beverage))  # False — bc is NOT a Beverage

# issubclass — "Is this class a child of that class?"
print(issubclass(Food, MenuItem))      # True — Food inherits from MenuItem
print(issubclass(MenuItem, Food))      # False — MenuItem does NOT inherit from Food
print(issubclass(Food, Food))          # True — a class is a subclass of itself
```

**Key insight:** A `Food` object IS a `MenuItem`. This is the "is-a" relationship. "Butter Chicken IS a MenuItem." This "is-a" test is how you decide whether inheritance makes sense.

> **Question:** Does "Customer IS a Order" make sense? No. A customer HAS orders. That's not inheritance — that's composition (we'll cover this later). Always ask: "Is [Child] a type of [Parent]?"

---

### Types of Inheritance

#### Single Inheritance

One parent, one child. The most common and simplest form.

```python
class MenuItem:
    pass

class Food(MenuItem):  # Food inherits from MenuItem
    pass
```

```
MenuItem → Food
```

#### Multilevel Inheritance

A chain: grandparent → parent → child.

```python
class MenuItem:
    def __init__(self, name, price):
        self.name = name
        self.price = price

class Food(MenuItem):
    def __init__(self, name, price, is_vegetarian):
        super().__init__(name, price)
        self.is_vegetarian = is_vegetarian

class IndianFood(Food):
    def __init__(self, name, price, is_vegetarian, spice_level):
        super().__init__(name, price, is_vegetarian)
        self.spice_level = spice_level
```

```
MenuItem → Food → IndianFood
```

`IndianFood` inherits from `Food`, which inherits from `MenuItem`. So `IndianFood` has everything: `name`, `price`, `is_vegetarian`, AND `spice_level`.

```python
biryani = IndianFood("Biryani", 300, False, "Medium")
print(biryani.name)         # From MenuItem (grandparent)
print(biryani.is_vegetarian) # From Food (parent)
print(biryani.spice_level)   # From IndianFood (itself)
print(biryani.get_summary()) # From MenuItem (grandparent) — if not overridden
```

#### Multiple Inheritance

A class inherits from MORE than one parent. Python supports this; Java does not.

```python
class Discountable:
    def apply_discount(self, percent):
        self.price = self.price * (1 - percent / 100)

class Taxable:
    def apply_tax(self, percent):
        self.price = self.price * (1 + percent / 100)

class Food(MenuItem, Discountable, Taxable):  # Multiple parents
    pass

biryani = Food("Biryani", 300)
biryani.apply_discount(10)  # From Discountable
biryani.apply_tax(5)        # From Taxable
```

**Warning:** Multiple inheritance can get confusing fast. What if two parents define the same method? Which one wins? That's where MRO comes in.

#### MRO — Method Resolution Order

When multiple parents have the same method, Python follows a specific order to decide which one to use. This is called the **Method Resolution Order (MRO)**.

```python
class A:
    def greet(self):
        return "Hello from A"

class B(A):
    def greet(self):
        return "Hello from B"

class C(A):
    def greet(self):
        return "Hello from C"

class D(B, C):  # Inherits from both B and C
    pass

d = D()
print(d.greet())  # "Hello from B" — B comes before C in the parent list

# You can see the full MRO:
print(D.__mro__)
# (<class 'D'>, <class 'B'>, <class 'C'>, <class 'A'>, <class 'object'>)
```

Python uses the **C3 Linearization** algorithm. The simple rule: it goes left to right in the parent list, depth-first, but avoids visiting a class before all its children are visited.

For this module, the key takeaway is: **prefer single inheritance. Use multiple inheritance only for simple "mixin" classes** (like `Discountable` and `Taxable` above) that add a single behavior.

---

### When to Use Inheritance vs When NOT To

**Use inheritance when there is a clear "is-a" relationship:**
- Food IS a MenuItem
- Dog IS an Animal
- SavingsAccount IS a BankAccount

**Don't use inheritance when the relationship is "has-a":**
- Customer HAS orders (not "Customer IS an Order")
- Car HAS an engine (not "Car IS an Engine")
- Restaurant HAS a menu (not "Restaurant IS a Menu")

"Has-a" relationships use **composition** — an object CONTAINS another object as an attribute.

```python
# Inheritance (is-a) — Food IS a MenuItem
class Food(MenuItem):
    pass

# Composition (has-a) — Restaurant HAS a menu
class Restaurant:
    def __init__(self, name):
        self.name = name
        self.menu = []  # Restaurant CONTAINS menu items

    def add_item(self, item):
        self.menu.append(item)
```

We'll explore composition more in upcoming classes. For now, the rule of thumb is: **favor composition over inheritance when in doubt.** Inheritance creates tight coupling — changes to the parent affect all children.

> **Question:** "ElectricCar IS a Car" — inheritance makes sense. "Car IS a Battery" — obviously wrong. But what about "ElectricCar IS a ChargingDevice"? That feels weird. A better model: ElectricCar HAS a Battery and HAS a ChargingSystem. How do you decide?

---

### MRO — How Python Differs From Java

| | Python | Java |
|---|---|---|
| **Multiple class inheritance** | Allowed | NOT allowed |
| **Conflict resolution** | C3 Linearization (MRO) | Not needed (no multiple inheritance) |
| **Check the order** | `ClassName.__mro__` or `ClassName.mro()` | N/A |
| **Philosophy** | "We trust the developer" | "Prevent ambiguity at the language level" |

**Can you bypass MRO?** You can call a specific parent's method directly: `B.greet(self)` instead of `super().greet()`. But this breaks cooperative inheritance and is almost always a bad idea.

### `super` vs `super()`

```python
# super   → the built-in class itself (a type object)
# super() → a PROXY OBJECT that follows MRO to find the next class

class Child(Parent):
    def greet(self):
        # super().greet()   → follows MRO, calls Parent.greet(self) ✓
        # super.greet(self) → TypeError! super is a class, not an instance ✗
        return super().greet() + " + Child"
```

**Rule: Always use `super()` with parentheses.** `super` without `()` is the class itself, not a usable proxy. You'll almost never need bare `super`.

---

## Polymorphism — "Same Interface, Different Behavior"

### The Word Itself

**Poly** = many. **Morph** = forms. Polymorphism means "many forms."

The same action takes different forms depending on WHO does it.

### Real-World Analogy

Think about the action "drive." You get in a Car — you turn the steering wheel, press pedals, use an automatic gearbox. You get on a Motorcycle — you twist the handlebars, use foot pedals, shift gears manually. You drive a Truck — same steering concept, but with air brakes and 18 gears.

**Same action** ("drive"), **different behavior** depending on the vehicle type. That's polymorphism.

In a restaurant: "prepare an order" means something different for the kitchen (cook the food), the bar (mix the drinks), and the dessert station (plate the sweets). The **action** is the same — the **execution** differs.

---

### Method Overriding IS Polymorphism

You've already seen polymorphism! When `Food.get_summary()` and `Beverage.get_summary()` do different things — that's polymorphism.

```python
class MenuItem:
    def __init__(self, name, price):
        self.name = name
        self.price = price

    def get_summary(self):
        return f"{self.name} - Rs.{self.price}"

class Food(MenuItem):
    def __init__(self, name, price, is_vegetarian):
        super().__init__(name, price)
        self.is_vegetarian = is_vegetarian

    def get_summary(self):
        veg = "Veg" if self.is_vegetarian else "Non-Veg"
        return f"{self.name} - Rs.{self.price} ({veg})"

class Beverage(MenuItem):
    def __init__(self, name, price, size):
        super().__init__(name, price)
        self.size = size

    def get_summary(self):
        return f"{self.name} ({self.size}) - Rs.{self.price}"
```

**The power of polymorphism — write code that doesn't care about the specific type:**

```python
def print_menu(items):
    """This function doesn't know or CARE if items are Food, Beverage, or Dessert."""
    for item in items:
        print(item.get_summary())  # Calls the RIGHT version automatically

menu = [
    Food("Butter Chicken", 350, False),
    Beverage("Mango Lassi", 120, "Large"),
    Food("Paneer Tikka", 280, True),
    Beverage("Masala Chai", 60, "Small"),
]

print_menu(menu)
# Butter Chicken - Rs.350 (Non-Veg)   ← Food's version
# Mango Lassi (Large) - Rs.120         ← Beverage's version
# Paneer Tikka - Rs.280 (Veg)          ← Food's version
# Masala Chai (Small) - Rs.60           ← Beverage's version
```

`print_menu` doesn't have a single `if isinstance(item, Food)` check. It just calls `get_summary()` and **trusts** that each object knows how to summarize itself. This is polymorphism in action.

> **Question:** Tomorrow the PM says "add Combo items to the menu." With polymorphism, do you change `print_menu`? No. You just create a `Combo` class with its own `get_summary()`. Zero changes to existing code. What would happen WITHOUT polymorphism — with a giant `if/elif` chain checking item types?

---

### Duck Typing — "If It Quacks Like a Duck"

Python doesn't care about the TYPE of an object. It cares about whether the object has the METHOD you're trying to call. This is called **duck typing**.

> "If it walks like a duck and quacks like a duck, then it's a duck."

```python
class Food:
    def get_summary(self):
        return "Butter Chicken - Rs.350"

class Coupon:
    def get_summary(self):
        return "10% OFF on orders above Rs.500"

class DailySpecial:
    def get_summary(self):
        return "Today's Special: Chef's Surprise - Rs.250"


def print_items(items):
    for item in items:
        print(item.get_summary())  # Python doesn't check the TYPE
                                    # It only checks: "does this object have get_summary()?"

# These are COMPLETELY unrelated classes — no inheritance!
print_items([Food(), Coupon(), DailySpecial()])
# All three work because they all have get_summary()
```

`Food`, `Coupon`, and `DailySpecial` have no common parent. They aren't related by inheritance at all. But they all have `get_summary()`, so `print_items` works with all of them.

**In Java**, you'd need an interface or shared parent class. **In Python**, you just need the right method. That's duck typing.

This is powerful but comes with a tradeoff: if you pass an object that DOESN'T have `get_summary()`, you get a runtime error, not a compile-time error. Python trusts you — but if you break that trust, errors appear at runtime.

---

### Operator Overloading — Briefly

Python lets you define what operators (`+`, `-`, `==`, `len()`) do for YOUR classes using **dunder methods** (double-underscore methods).

```python
class CartItem:
    def __init__(self, name, price, quantity):
        self.name = name
        self.price = price
        self.quantity = quantity

    def __str__(self):
        """What print() shows."""
        return f"{self.name} x{self.quantity} = Rs.{self.price * self.quantity}"

    def __add__(self, other):
        """What + does."""
        return self.price * self.quantity + other.price * other.quantity

    def __eq__(self, other):
        """What == does."""
        return self.name == other.name and self.price == other.price

    def __len__(self):
        """What len() does."""
        return self.quantity


item1 = CartItem("Biryani", 300, 2)
item2 = CartItem("Naan", 40, 4)

print(item1)             # "Biryani x2 = Rs.600"  ← __str__
print(item1 + item2)     # 760                     ← __add__
print(item1 == item2)    # False                    ← __eq__
print(len(item1))        # 2                        ← __len__
```

This is polymorphism too! The `+` operator does different things depending on the type: for integers it adds, for strings it concatenates, for your `CartItem` it totals the cost. Same operator, different behavior = polymorphism.

Common dunder methods:

| Method | Operator/Function | Example |
|---|---|---|
| `__str__` | `print()`, `str()` | Human-readable representation |
| `__repr__` | `repr()`, debugger | Developer-readable representation |
| `__add__` | `+` | Adding two objects |
| `__eq__` | `==` | Comparing two objects |
| `__lt__` | `<` | Less-than comparison |
| `__len__` | `len()` | Length of an object |

---

### Real Example — Notification System

Different notification types, same interface.

```python
class Notification:
    def __init__(self, recipient, message):
        self.recipient = recipient
        self.message = message

    def send(self):
        raise NotImplementedError("Subclasses must implement send()")


class EmailNotification(Notification):
    def send(self):
        print(f"Sending EMAIL to {self.recipient}: {self.message}")
        # In real code: use SMTP, SendGrid, etc.


class SMSNotification(Notification):
    def send(self):
        print(f"Sending SMS to {self.recipient}: {self.message}")
        # In real code: use Twilio, AWS SNS, etc.


class PushNotification(Notification):
    def send(self):
        print(f"Sending PUSH to {self.recipient}: {self.message}")
        # In real code: use Firebase, APNs, etc.


# The function doesn't care WHICH type of notification
def send_all(notifications):
    for n in notifications:
        n.send()

notifications = [
    EmailNotification("rahul@email.com", "Your order is confirmed!"),
    SMSNotification("+91-9876543210", "Your order is confirmed!"),
    PushNotification("device_token_abc", "Your order is confirmed!"),
]

send_all(notifications)
# Sending EMAIL to rahul@email.com: Your order is confirmed!
# Sending SMS to +91-9876543210: Your order is confirmed!
# Sending PUSH to device_token_abc: Your order is confirmed!
```

Tomorrow, the business says "add WhatsApp notifications." You create `WhatsAppNotification` with a `send()` method. `send_all` works without any changes.

> **Question:** What does `raise NotImplementedError` in the parent's `send()` do? It forces every child class to provide its own implementation. If someone creates a new notification type and forgets to implement `send()`, they get a clear error instead of silent failure. (In OOP-3, we'll see a stricter way to enforce this with Abstract Base Classes.)

---

### Method Overloading — Does Python Support It?

**Short answer: No.** In Java, you can have multiple methods with the same name but different parameter counts. In Python, the second definition **replaces** the first:

```python
class Calculator:
    def add(self, a, b):
        return a + b

    def add(self, a, b, c):  # This REPLACES the version above!
        return a + b + c

calc = Calculator()
calc.add(1, 2, 3)  # Works — 6
calc.add(1, 2)      # TypeError! The 2-param version is GONE
```

**The Pythonic way — default parameters and *args:**

```python
class Calculator:
    def add(self, *args):  # Accept any number of arguments
        return sum(args)

calc = Calculator()
calc.add(1, 2)         # 3
calc.add(1, 2, 3)      # 6
calc.add(1, 2, 3, 4)   # 10
```

**Why doesn't Python need overloading?** Python is dynamically typed. One method handles any type: `add(1, 2)` → 3, `add("hi", "!")` → "hi!". Java needs overloading because it's statically typed.

> **Question:** You define `def calculate(self, a, b)` and then `def calculate(self, a, b, c)` in the same class. A colleague calls `obj.calculate(1, 2)`. What happens? Why?

---

### Which Method Gets Called? — Scenarios

This is the question that trips up beginners. **The OBJECT's type decides which method runs, not the variable's type.**

```python
class MenuItem:
    def calculate_price(self): return self.price
    def describe(self): return f"{self.name} - Rs.{self.price}"

class Food(MenuItem):
    def calculate_price(self): return self.price * 1.05
    def describe(self): return f"{self.name} ({self.calories} cal)"

class Beverage(MenuItem):
    def calculate_price(self): return self.price + 10
    # No describe() override — uses MenuItem's

class Dessert(MenuItem):
    pass  # No overrides at all
```

**Scenario 1:** `biryani = Food("Biryani", 300, 450)` → `biryani.describe()` → **Food's describe()** runs (Food overrides it)

**Scenario 2:** `chai = Beverage("Chai", 40, 200)` → `chai.describe()` → **MenuItem's describe()** runs (Beverage doesn't override it, Python goes up to parent)

**Scenario 3:** `items: list[MenuItem] = [Food(...), Beverage(...)]` → `item.calculate_price()` → **Depends on the actual object.** For Food → Food's version. For Beverage → Beverage's version. The type hint `list[MenuItem]` is just documentation — Python ignores it at runtime. **This IS polymorphism.**

**Scenario 4:** `gulab = Dessert("Gulab Jamun", 80)` → `gulab.calculate_price()` → **MenuItem's version** (Dessert has no overrides)

> **Question:** If `Food` overrides `describe()` but NOT `calculate_price()`, which `calculate_price()` runs when you call `biryani.calculate_price()`? Answer: Food's — wait, Food DOES override it. But if it didn't? Then MenuItem's would run. The rule: Python starts at the object's class and walks UP the inheritance chain until it finds the method.

---

## Inheritance + Polymorphism Together

This is where the two concepts combine into something genuinely powerful. Let's build a complete example.

### Restaurant Menu — Different Pricing Logic

```python
class MenuItem:
    def __init__(self, name, base_price):
        self.name = name
        self.base_price = base_price

    def calculate_price(self):
        """Default: just return the base price."""
        return self.base_price

    def display(self):
        return f"{self.name}: Rs.{self.calculate_price()}"


class Food(MenuItem):
    def __init__(self, name, base_price, is_vegetarian):
        super().__init__(name, base_price)
        self.is_vegetarian = is_vegetarian

    def calculate_price(self):
        """Food: 5% packaging charge."""
        return round(self.base_price * 1.05, 2)

    def display(self):
        veg = "[V]" if self.is_vegetarian else "[NV]"
        return f"{veg} {self.name}: Rs.{self.calculate_price()}"


class Beverage(MenuItem):
    SIZES = {"Small": 1.0, "Medium": 1.3, "Large": 1.6}

    def __init__(self, name, base_price, size):
        super().__init__(name, base_price)
        self.size = size

    def calculate_price(self):
        """Beverages: price depends on size."""
        multiplier = self.SIZES.get(self.size, 1.0)
        return round(self.base_price * multiplier, 2)

    def display(self):
        return f"{self.name} ({self.size}): Rs.{self.calculate_price()}"


class Dessert(MenuItem):
    def __init__(self, name, base_price, allergens=None):
        super().__init__(name, base_price)
        self.allergens = allergens or []

    def calculate_price(self):
        """Desserts: 18% GST included."""
        return round(self.base_price * 1.18, 2)

    def display(self):
        allergen_info = f" ⚠ Contains: {', '.join(self.allergens)}" if self.allergens else ""
        return f"{self.name}: Rs.{self.calculate_price()}{allergen_info}"
```

**Now the magic — a function that works with ALL types:**

```python
def generate_bill(items):
    """Works with ANY MenuItem subclass — past, present, or future."""
    print("=" * 40)
    print("        RESTAURANT BILL")
    print("=" * 40)
    total = 0
    for item in items:
        print(item.display())              # Polymorphism — each type displays differently
        total += item.calculate_price()    # Polymorphism — each type calculates differently
    print("-" * 40)
    print(f"TOTAL: Rs.{round(total, 2)}")
    print("=" * 40)


order = [
    Food("Butter Chicken", 350, False),
    Food("Dal Makhani", 250, True),
    Beverage("Mango Lassi", 100, "Large"),
    Dessert("Gulab Jamun", 150, ["dairy", "gluten"]),
]

generate_bill(order)
```

Output:
```
========================================
        RESTAURANT BILL
========================================
[NV] Butter Chicken: Rs.367.5
[V] Dal Makhani: Rs.262.5
Mango Lassi (Large): Rs.160.0
Gulab Jamun: Rs.177.0
----------------------------------------
TOTAL: Rs.967.0
========================================
```

### Adding a New Type — ZERO Changes to Existing Code

The PM says: "We're adding Combo meals. A combo is 15% cheaper than the sum of its items."

```python
class Combo(MenuItem):
    def __init__(self, name, items):
        total_base = sum(item.base_price for item in items)
        super().__init__(name, total_base)
        self.items = items

    def calculate_price(self):
        """Combos: 15% discount on combined price."""
        return round(self.base_price * 0.85, 2)

    def display(self):
        item_names = " + ".join(item.name for item in self.items)
        return f"COMBO: {self.name} ({item_names}): Rs.{self.calculate_price()}"
```

That's it. `generate_bill` works with `Combo` without a single change. No `if isinstance(item, Combo)`. No modifications anywhere.

```python
combo = Combo("Family Pack", [
    Food("Butter Chicken", 350, False),
    Food("Naan", 60, True),
    Beverage("Lassi", 100, "Large"),
])

generate_bill([combo])
# COMBO: Family Pack (Butter Chicken + Naan + Lassi): Rs.433.5
```

**This is the Open/Closed Principle from SOLID in action** — the code is OPEN for extension (add new types) but CLOSED for modification (don't change existing code). We'll cover SOLID formally later, but you're already seeing it.

> **Question:** How many lines of existing code did we change to add `Combo`? Zero. How many lines would we change with a giant `if/elif` approach checking types? Every function that handles menu items.

---

## Common Mistakes

### 1. Deep Inheritance Hierarchies

```python
# BAD — too many levels
class Entity:
    pass

class LivingThing(Entity):
    pass

class Animal(LivingThing):
    pass

class Mammal(Animal):
    pass

class DomesticAnimal(Mammal):
    pass

class Dog(DomesticAnimal):
    pass

class GoldenRetriever(Dog):
    pass
```

Seven levels deep. To understand `GoldenRetriever`, you need to read 6 other classes. A change in `Entity` ripples through everything. Debugging becomes "which level overrode which method?"

**Rule of thumb:** Keep inheritance to 2-3 levels max. If you need more, use composition instead.

```python
# BETTER — flat and composed
class Dog:
    def __init__(self, breed, temperament):
        self.breed = breed
        self.temperament = temperament  # Composition — Dog HAS a temperament
```

### 2. Using Inheritance When Composition Is Better

```python
# BAD — a Stack is NOT a list
class Stack(list):
    def push(self, item):
        self.append(item)

s = Stack()
s.push(1)
s.push(2)
s.insert(0, "oops")  # A stack shouldn't allow this! But list does.
```

`Stack` inherits ALL of `list`'s methods — including `insert`, `sort`, `reverse` — none of which make sense for a stack. You've inherited too much.

```python
# GOOD — Stack HAS a list (composition)
class Stack:
    def __init__(self):
        self._items = []  # Internal list — hidden

    def push(self, item):
        self._items.append(item)

    def pop(self):
        if not self._items:
            raise IndexError("Stack is empty")
        return self._items.pop()

    def peek(self):
        if not self._items:
            raise IndexError("Stack is empty")
        return self._items[-1]

# Only push, pop, peek are available. No insert, no sort. Clean.
```

### 3. Forgetting `super().__init__()`

We covered this above, but it bears repeating because it's the most common bug with inheritance.

```python
class Food(MenuItem):
    def __init__(self, name, price, is_veg):
        # If you forget this line, name and price are never set!
        super().__init__(name, price)
        self.is_veg = is_veg
```

**Every time you write `__init__` in a child class, ask yourself:** "Did I call `super().__init__()`?"

---

## Connecting to What's Next

| Today (OOP-2) | Next Class (OOP-3) | Later (SOLID & Patterns) |
|---|---|---|
| **Inheritance** — reuse and extend | **Abstract Base Classes** — enforce that children implement methods | **Liskov Substitution Principle** — proper inheritance rules |
| `raise NotImplementedError` | `@abstractmethod` — stricter, fails at object creation, not at method call | **Factory Pattern** — use polymorphism to create objects |
| **Polymorphism** — same interface, diff behavior | **Static methods** — methods that belong to the class, not the object | **Strategy Pattern** — polymorphism as a design pattern |
| **Method overriding** | ABCs formalize the "contract" | **Observer Pattern** — uses inheritance + interfaces |
| **Duck typing** | Type hints make duck typing safer | Design patterns combine all OOP concepts |

In OOP-3, we'll answer the question: "How do I FORCE every child class to implement `send()` or `calculate_price()`?" Right now, if someone forgets, they get an error only when the method is called. Abstract Base Classes catch that error **when the object is created** — much earlier and safer.

---

## Resources

- [Python OOP Tutorial — Corey Schafer (YouTube)](https://www.youtube.com/watch?v=RSl87lqOXDE) — Part 4: Inheritance
- [Real Python — Inheritance and Composition](https://realpython.com/inheritance-composition-python/) — When to use which, with practical examples
- [Real Python — Operator and Function Overloading](https://realpython.com/operator-function-overloading/) — Deep dive into dunder methods
- [Python super() — Real Python](https://realpython.com/python-super/) — Understanding super() in single and multiple inheritance
- [Python MRO — Method Resolution Order](https://www.python.org/download/releases/2.3/mro/) — Technical details on C3 linearization
