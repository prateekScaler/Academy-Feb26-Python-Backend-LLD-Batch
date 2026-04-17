# LLD-02: OOP-1 — Intro to OOP, Access Modifiers, Constructors

> Last class you learned WHY code structure matters. Now you learn the **first tool** for structuring code — Object-Oriented Programming.

---

## Attributes and Methods — The Vocabulary of OOP

Before we dive in, let's fix the vocabulary. In OOP, we don't say "data and functions." We say:

| Regular Code | Inside a Class |
|---|---|
| Variable | **Attribute** — data that belongs to an object |
| Function | **Method** — a function that belongs to a class and operates on its attributes |

```python
class Dish:
    def __init__(self, name, price):
        self.name = name      # ← Attribute (data)
        self.price = price    # ← Attribute (data)

    def describe(self):       # ← Method (behavior)
        return f"{self.name} costs Rs.{self.price}"
```

**Attributes** = what an object KNOWS (name, price, status)
**Methods** = what an object can DO (describe, calculate, validate)

A class bundles related attributes and methods together. A `Dish` knows its name and price, and can describe itself. The data and behavior that belong together LIVE together.

---

## Programming Paradigms — Different Ways to Think About Code

A **paradigm** is a style of programming — a way of organizing your thoughts and your code. Different paradigms exist because different problems are best solved in different ways.

### The Major Paradigms

| Paradigm | Core Idea | Languages | Think of it as... |
|---|---|---|---|
| **Procedural** | Step-by-step instructions, top to bottom | C, Bash, early Python | A recipe — do step 1, then step 2, then step 3 |
| **Object-Oriented (OOP)** | Model the world as objects that interact | Java, C++, Python, C# | A restaurant — each thing (dish, order, customer) is an object with its own data and behavior |
| **Functional** | Everything is a function, no side effects, data is immutable | Haskell, Erlang, Lisp, Elixir | A math equation — same input always gives same output, nothing changes |
| **Logic/Declarative** | Describe WHAT you want, not HOW to get it | SQL, Prolog, HTML/CSS | An order at a restaurant — "I want butter chicken" not "go to the kitchen, take the pan..." |

Most modern languages support **multiple paradigms**. Python is multi-paradigm — you can write procedural, OOP, and functional code all in the same file. Java forces you into OOP. Haskell forces you into functional.

> **Question:** When you write `SELECT * FROM dishes WHERE price > 200` in SQL, which paradigm is that? You're telling the database WHAT you want, not HOW to find it. That's declarative. When you write a `for` loop in Python to filter the same data, that's procedural.

### Which Paradigm For What?

| Use Case | Best Paradigm | Why |
|---|---|---|
| Small scripts, automation | Procedural | Simple, linear, no overhead |
| Modeling real-world entities (users, orders, payments) | OOP | Objects map naturally to real things |
| Data transformation pipelines | Functional | No side effects, easy to parallelize |
| Database queries | Declarative (SQL) | Express intent, let the engine optimize |
| Safety-critical systems (NASA, medical, aviation) | Procedural with strict rules | Simplicity, auditability, no hidden behavior |

### NASA's Power of 10 Rules

NASA's Jet Propulsion Laboratory has [10 rules for writing safety-critical code](https://en.wikipedia.org/wiki/The_Power_of_10:_Rules_for_Developing_Safety-Critical_Code). Some of them are surprisingly relevant to everyday programming:

- **Rule 1:** No goto, no recursion — keep control flow simple and predictable
- **Rule 2:** All loops must have a fixed upper bound — no infinite loops
- **Rule 6:** Restrict variable scope as much as possible — sound familiar? That's encapsulation!
- **Rule 9:** Limit pointer use — in Python terms: be careful with mutable shared state

NASA chose procedural C over OOP for spacecraft software because in a system controlling a Mars rover, you need to know EXACTLY what every line does. No hidden method calls, no polymorphism surprises, no garbage collector pausing at the wrong moment.

**Fun trivia:**
- The Mars Curiosity Rover runs on ~2.5 million lines of C. Not a single class.
- Erlang (functional) was built by Ericsson for phone switches — it needs 99.9999999% uptime (that's ~31 milliseconds of downtime per YEAR). Functional programming's "no side effects" rule makes it almost impossible to corrupt shared state.
- SQL was invented in 1974 and is STILL the most widely used declarative language. It outlived every OOP framework ever built.

> **Question:** Your company is building a food delivery app. The order management system has users, restaurants, orders, dishes, payments, delivery drivers. Which paradigm fits best and why? What if you're just writing a one-off script to migrate data from an old database?

---

## The Four Pillars of OOP

OOP rests on four pillars. Today we cover **Abstraction** and **Encapsulation**. Next class: Inheritance and Polymorphism.

```
       THE FOUR PILLARS OF OOP
┌──────────────┬──────────────┬──────────────┬──────────────┐
│ Abstraction  │Encapsulation │ Inheritance  │ Polymorphism │
│  (TODAY)     │   (TODAY)    │  (OOP-2)     │   (OOP-2)    │
│              │              │              │              │
│ Hide         │ Bundle +     │ Reuse +      │ Same         │
│ complexity   │ Protect      │ Extend       │ interface,   │
│              │              │              │ diff behavior│
└──────────────┴──────────────┴──────────────┴──────────────┘
```

---

## Pillar 1: Abstraction — "Show Only What Matters"

### What does "abstraction" even mean?

The word "abstract" means to **pull away details and focus on what's essential.** It appears everywhere, not just programming:

**In art:** An abstract painting of a cat doesn't show every whisker — it shows the ESSENCE of a cat with shapes and colors. You recognize it's a cat without seeing every detail.

**In maps:** A subway map is an abstraction. It doesn't show actual distances or geography — it shows which stations connect to which. That's ALL you need to decide your route.

**In driving:** You press the accelerator and the car speeds up. You don't need to know about fuel injection, spark timing, or crankshaft rotation. The pedal is an **abstraction** — it hides the complexity and gives you a simple interface.

**In programming:** When you call `sorted([3, 1, 2])`, you don't know (or care) whether Python uses quicksort, mergesort, or timsort internally. You just know: give it a list, get back a sorted list. The `sorted()` function is an abstraction.

### Abstraction in OOP

In OOP, abstraction means: **expose WHAT an object can do, hide HOW it does it.**

```python
class PaymentGateway:
    def charge(self, amount):
        """Charge the customer. That's all the caller needs to know."""
        # HOW this works (API calls, authentication, retries) is hidden
        ...

# The caller only knows: "I can call charge(amount)"
# They don't need to know about Razorpay APIs, webhook verification, etc.
```

Think about your phone. You know:
- Tap to open an app (what)
- Swipe to scroll (what)
- Press power to lock (what)

You don't know (and don't need to know):
- How the touchscreen converts finger pressure into coordinates
- How the GPU renders each frame
- How the OS manages memory

That's abstraction. The phone gives you a **simple interface** and hides the **complex implementation**.

> **Question:** When you write `MenuItem.objects.filter(price__gt=200)` in Django, how much do you know about the SQL query Django generates? About database connections? About cursor management? Django's ORM is an abstraction — it lets you think in Python objects, not in SQL.

---

## Pillar 2: Encapsulation — "Bundle and Protect"

### The Capsule Analogy

Think of a medicine capsule:

1. **It holds things together** — the medicine ingredients are bundled inside one shell. They don't float around separately.
2. **It protects from outside** — you can't tamper with the contents. You can't add or remove ingredients from a sealed capsule.
3. **It has a controlled interface** — you swallow the capsule (the one thing you CAN do with it). You don't inject individual ingredients.

**Encapsulation in OOP is the same idea:**

1. **Bundle** related data (attributes) and behavior (methods) inside one class
2. **Protect** internal state from direct external access
3. **Provide a controlled interface** — methods that are the ONLY way to interact with the data

### Without Encapsulation

```python
# Data and functions are separate — no capsule
customer_balance = 5000

def withdraw(amount):
    global customer_balance
    customer_balance -= amount

# Anyone can do this:
customer_balance = -99999  # No capsule, no protection
```

### With Encapsulation

```python
# Data and behavior are bundled inside a capsule (class)
class BankAccount:
    def __init__(self, balance):
        self.__balance = balance  # Protected inside the capsule

    def withdraw(self, amount):  # Controlled interface
        if amount > self.__balance:
            raise ValueError("Insufficient funds")
        self.__balance -= amount

    def get_balance(self):       # Controlled interface
        return self.__balance

account = BankAccount(5000)
account.withdraw(1000)     # Must use the interface
# account.__balance = -99999  → Can't break into the capsule
```

**Abstraction says:** "You can withdraw money" (WHAT)
**Encapsulation says:** "But you must go through the `withdraw()` method, and I'll validate the amount" (HOW access is controlled)

They work together: abstraction decides what's visible, encapsulation enforces the boundary.

> **Question:** Think of an ATM. The abstraction is: you see a screen with "Withdraw", "Check Balance", "Transfer." The encapsulation is: you can't open the ATM and grab cash directly. You MUST go through the interface. What happens to a bank if ATMs had no encapsulation — anyone could open them?

---

## Classes and Objects

### The Blueprint Analogy

A **class** is a blueprint. An **object** is a thing built from that blueprint.

```python
# Class = Blueprint (defines the structure)
class Dish:
    def __init__(self, name, price, is_vegetarian):
        self.name = name              # Attribute
        self.price = price            # Attribute
        self.is_vegetarian = is_vegetarian  # Attribute

    def describe(self):               # Method
        veg = "Veg" if self.is_vegetarian else "Non-Veg"
        return f"{self.name} - Rs.{self.price} ({veg})"

# Objects = Specific instances built from the blueprint
butter_chicken = Dish("Butter Chicken", 350, False)
paneer_tikka = Dish("Paneer Tikka", 280, True)

print(butter_chicken.describe())  # "Butter Chicken - Rs.350 (Non-Veg)"
print(paneer_tikka.describe())    # "Paneer Tikka - Rs.280 (Veg)"
```

- One class → many objects
- Each object has its OWN attributes (butter chicken's price ≠ paneer tikka's price)
- All objects SHARE the same methods (both can call `describe()`)

> **Question:** In your Django project, `MenuItem` is a class. Every row in the database is an object. When you write `MenuItem.objects.get(id=1)`, Django returns an object. How many objects of `MenuItem` exist in your restaurant project?

---

## Constructors — Building Objects Right

### What is a constructor?

A constructor is the method that runs **automatically** when you create an object. It sets up the object's initial state.

### Step 1: Non-Parameterized Constructor

The simplest constructor takes no arguments (except `self`):

```python
class Counter:
    def __init__(self):
        self.count = 0
        self.created_at = datetime.now()

c1 = Counter()  # count = 0
c2 = Counter()  # count = 0, independent from c1
```

Every Counter starts at 0. No customization. This is useful when every object starts in the same state.

**But is this good practice?** It depends. If every object truly should start the same way, it's fine. But usually, objects need to be created with specific data — which is where parameterized constructors come in.

### Step 2: Parameterized Constructor (and Why)

```python
class Dish:
    def __init__(self, name, price):
        self.name = name
        self.price = price

# Each object is created with specific data
biryani = Dish("Biryani", 300)
dosa = Dish("Dosa", 120)
```

**Why parameterized?** Because a Dish without a name and price is meaningless. The constructor forces you to provide the essential data. **An object should be READY TO USE the moment it's created.**

Bad:
```python
# Non-parameterized — object is created incomplete
dish = Dish()
dish.name = "Biryani"  # What if someone forgets this?
dish.price = 300       # What if they set price but not name?
# dish.describe() → crashes because name was never set
```

Good:
```python
# Parameterized — object is complete from the start
dish = Dish("Biryani", 300)  # Can't forget name or price
dish.describe()  # Always works
```

### Step 3: Defaults + Validation

```python
class Restaurant:
    def __init__(self, name, cuisine, rating=0.0, is_open=True):
        if not name:
            raise ValueError("Restaurant must have a name")
        if not 0 <= rating <= 5:
            raise ValueError(f"Rating must be 0-5, got {rating}")
        self.name = name
        self.cuisine = cuisine
        self.rating = rating
        self.is_open = is_open

# Required params first, optional with defaults after
r = Restaurant("Biryani House", "Indian")           # rating=0.0, is_open=True
r = Restaurant("Sushi Bar", "Japanese", rating=4.5)  # is_open=True
r = Restaurant("", "Indian")                          # ValueError!
```

**Good practice summary:**
1. Required parameters for essential data — don't let incomplete objects exist
2. Default values for optional data — `rating=0.0`
3. Validation in the constructor — bad objects should never be created

> **Question:** You're building a `PaymentTransaction` class. What should be required (can't create without it)? What should have defaults? What should be auto-set (like `created_at`)? What happens if you allow creating a transaction with `amount = -500`?

---

## Access Modifiers — Public, Protected, Private

### The Three Levels

```python
class BankAccount:
    def __init__(self, owner, balance):
        self.owner = owner              # Public — anyone can read/write
        self._account_type = "savings"  # Protected — convention: "internal use"
        self.__balance = balance        # Private — name mangling

account = BankAccount("Rahul", 5000)

print(account.owner)             # "Rahul" — works
print(account._account_type)     # "savings" — works, but signals "don't touch"
print(account.__balance)         # AttributeError! Can't access directly
```

| Modifier | Syntax | Who Should Access | Python Enforcement |
|---|---|---|---|
| **Public** | `self.name` | Anyone | None — fully open |
| **Protected** | `self._name` | Class + subclasses | Convention — linters warn |
| **Private** | `self.__name` | Class only | Name mangling |

---

## Name Mangling — Why Python Lets You Access "Private" Attributes

Here's something that surprises people: Python's "private" isn't truly private.

```python
class Secret:
    def __init__(self):
        self.__password = "hunter2"

s = Secret()
print(s.__password)                # AttributeError ✗
print(s._Secret__password)         # "hunter2" ✓  — Wait, what?!
```

**What is name mangling?**

When you write `self.__name`, Python doesn't make it invisible. It RENAMES it to `_ClassName__name`. That's all. It's called "name mangling" because Python mangles (rewrites) the name.

**Why not truly private like Java/C++?**

Python's philosophy is **"we're all consenting adults here."** The language trusts developers. The underscore conventions say:
- `_name` → "I'm internal, please don't touch"
- `__name` → "I REALLY don't want you to touch this, so I'm making it inconvenient"

Name mangling exists primarily to prevent **accidental name collisions in inheritance** (when a parent and child class both have `__balance`). It's a namespacing tool, not a security tool.

**The real protection in Python comes from:**
1. Convention — developers respect the underscore
2. `@property` — controlled access with validation
3. Code review — team culture enforces boundaries

> **Question:** If Python's private isn't truly private, why bother with `__`? Because it prevents ACCIDENTS, not attacks. A developer won't accidentally type `account._BankAccount__balance`. But they might type `account.balance` or `account._balance`. The double underscore makes accidental access nearly impossible while keeping intentional access available for debugging and testing.

---

## Encapsulation in Practice — `@property`

Now let's combine encapsulation with Python's `@property` decorator. Instead of Java-style `get_balance()` / `set_balance()`, Python lets you do this:

```python
class Temperature:
    def __init__(self, celsius):
        self.__celsius = celsius

    @property
    def celsius(self):
        return self.__celsius

    @celsius.setter
    def celsius(self, value):
        if value < -273.15:
            raise ValueError("Below absolute zero!")
        self.__celsius = value

    @property
    def fahrenheit(self):
        return self.__celsius * 9/5 + 32

# Looks like simple attribute access...
temp = Temperature(25)
print(temp.celsius)      # 25 — but this calls the getter!
print(temp.fahrenheit)   # 77.0 — computed on the fly!
temp.celsius = 30        # Calls the setter → validation runs
temp.celsius = -300      # ValueError: Below absolute zero!
```

**The beauty:** From the outside, `temp.celsius` looks like reading a regular attribute. But behind the scenes, it runs your validation code. Clean syntax AND protection.

### Real Example — Order Status

```python
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
            raise ValueError(f"Invalid status: {new_status}")
        if self.__status == "delivered":
            raise ValueError("Cannot change status of delivered order")
        self.__status = new_status

order = Order("Rahul", ["Butter Chicken", "Naan"])
order.status = "confirmed"    # ✓ Works
order.status = "delivered"    # ✓ Works
order.status = "pending"      # ✗ ValueError: Cannot change delivered order
order.status = "delievered"   # ✗ ValueError: Invalid status (typo caught!)
```

Without `@property`, someone types `order.status = "delievered"` (typo) and the order sits in a state no code recognizes. With `@property`, the typo is caught immediately.

> **Question:** You're building an e-commerce system. The `Product` class has a `price` attribute. Should it be public or use `@property`? What if someone sets `product.price = -50`? What if a business rule says "price can never decrease by more than 20%"? How would you enforce that?

---

## `self` — What It Actually Is

Every method receives `self` as its first parameter. It refers to **this specific object**.

```python
class Counter:
    def __init__(self):
        self.count = 0

    def increment(self):
        self.count += 1

c1 = Counter()
c2 = Counter()
c1.increment()
c1.increment()

print(c1.count)  # 2
print(c2.count)  # 0 — independent!

# What Python actually does:
# c1.increment() → Counter.increment(c1)  — self = c1
# c2.increment() → Counter.increment(c2)  — self = c2
```

**The #1 OOP bug in Python:** forgetting `self`

```python
class BrokenCounter:
    def __init__(self):
        self.count = 0

    def increment(self):
        count += 1  # BUG! This is a local variable, not self.count

c = BrokenCounter()
c.increment()  # UnboundLocalError!
```

---

## Connecting to What's Next

| Today | Next Class (OOP-2) | Later |
|---|---|---|
| **Classes & Objects** | Inheritance — classes that extend other classes | Factory Pattern creates objects |
| **Constructors** | `super().__init__()` — calling parent constructors | Builder Pattern for complex construction |
| **Access Modifiers** | Protected members become key with inheritance | SOLID principles build on encapsulation |
| **Abstraction** | Abstract Base Classes — enforcing abstraction | Strategy, Observer patterns |
| **Encapsulation & @property** | Polymorphism — same property, different behavior | Used in every design pattern |

---

## Resources

- [Scaler Python Topics — OOP](https://www.scaler.com/topics/python/python-classes-and-objects/) — Classes, objects, constructors basics
- [NASA Power of 10 Rules](https://en.wikipedia.org/wiki/The_Power_of_10:_Rules_for_Developing_Safety-Critical_Code) — Safety-critical coding guidelines
- [Python OOP Tutorial — Corey Schafer](https://www.youtube.com/watch?v=ZDa-Z5JzLYM) — Part 1: Classes and Instances
- [Real Python — OOP in Python](https://realpython.com/python3-object-oriented-programming/) — Comprehensive guide
- [Python @property — Real Python](https://realpython.com/python-property/) — Deep dive into property decorators
