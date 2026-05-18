# LLD-13: SOLID Principles

> Five principles that separate code that survives from code that rots.

---

## Recap — Exception Handling

> **Q:** try/except/else/finally — when does `else` run?
<details><summary>Answer</summary>
`else` runs ONLY if no exception was raised in `try`. It's for code that should run on success.
</details>

> **Q:** What is EAFP?
<details><summary>Answer</summary>
Easier to Ask Forgiveness than Permission — try it first, handle exception if it fails. The Pythonic way.
</details>

---

## Why SOLID?

You've written code that works. But 6 months later:
- Adding one feature breaks 3 others
- A "simple change" takes 2 weeks because everything is coupled
- Nobody wants to touch that 800-line god class

SOLID gives you 5 rules to prevent this rot:

| Letter | Principle | One-liner |
|---|---|---|
| **S** | Single Responsibility | A class should have only ONE reason to change |
| **O** | Open/Closed | Open for extension, closed for modification |
| **L** | Liskov Substitution | Subtypes must be substitutable for their base types |
| **I** | Interface Segregation | No client should be forced to depend on methods it doesn't use |
| **D** | Dependency Inversion | Depend on abstractions, not concretions |

---

## S — Single Responsibility Principle (SRP)

**"A class should have only ONE reason to change."**

### The Problem

```python
# BAD: This class has 5 reasons to change
class OrderProcessor:
    def validate_order(self, order): ...
    def save_to_database(self, order): ...
    def send_confirmation_email(self, order): ...
    def generate_invoice(self, order): ...
    def update_inventory(self, order): ...
```

If email format changes → you edit OrderProcessor.
If database schema changes → you edit OrderProcessor.
If invoice template changes → you edit OrderProcessor.
One class, FIVE reasons to change. That's the problem.

### The Fix

```python
# GOOD: Each class has ONE reason to change
class OrderValidator:
    def validate(self, order): ...

class OrderRepository:
    def save(self, order): ...

class EmailNotifier:
    def send_confirmation(self, order): ...

class InvoiceGenerator:
    def generate(self, order): ...

class InventoryService:
    def update_stock(self, order): ...
```

### How to Spot SRP Violations

If you describe what a class does and use the word **"AND"**, it probably does too much:
- "This class validates orders AND saves them AND sends emails" ← violation
- "This class validates orders" ← single responsibility ✓

---

## O — Open/Closed Principle (OCP)

**"Open for extension, closed for modification."**

### The Problem

```python
# BAD: Every new discount type = modify this function
class DiscountCalculator:
    def calculate(self, order, discount_type):
        if discount_type == "student":
            return order.total * 0.10
        elif discount_type == "premium":
            return order.total * 0.25
        elif discount_type == "employee":
            return order.total * 0.40
        elif discount_type == "festival":
            return order.total * 0.15
        # Adding "loyalty" means editing this working code...
```

### The Fix

```python
# GOOD: New discount = new class, existing code untouched
from abc import ABC, abstractmethod

class DiscountStrategy(ABC):
    @abstractmethod
    def calculate(self, order) -> float:
        pass

class StudentDiscount(DiscountStrategy):
    def calculate(self, order):
        return order.total * 0.10

class PremiumDiscount(DiscountStrategy):
    def calculate(self, order):
        return order.total * 0.25

class FestivalDiscount(DiscountStrategy):
    def calculate(self, order):
        return order.total * 0.15

# Adding LoyaltyDiscount = create a new class. ZERO changes to existing code.
class LoyaltyDiscount(DiscountStrategy):
    def calculate(self, order):
        return order.total * 0.20

# Usage:
def apply_discount(order, strategy: DiscountStrategy):
    return strategy.calculate(order)
```

### How to Spot OCP Violations

If adding a new feature requires **modifying existing working code** (especially if/elif chains), OCP is violated.

---

## L — Liskov Substitution Principle (LSP)

**"Subtypes must be substitutable for their base types."**

If code works with a `MenuItem`, it must also work with `VegDish(MenuItem)` and `NonVegDish(MenuItem)` without breaking.

### The Problem

```python
# BAD: Square "is a" Rectangle, but breaks substitution
class Rectangle:
    def __init__(self, width, height):
        self.width = width
        self.height = height

    def set_width(self, w):
        self.width = w

    def set_height(self, h):
        self.height = h

    def area(self):
        return self.width * self.height

class Square(Rectangle):
    def set_width(self, w):
        self.width = w
        self.height = w  # forced to keep square!

    def set_height(self, h):
        self.width = h
        self.height = h

# This function works for Rectangle but BREAKS for Square:
def resize(shape: Rectangle):
    shape.set_width(5)
    shape.set_height(10)
    assert shape.area() == 50  # Fails for Square! area = 100
```

### The Fix

Don't make Square inherit from Rectangle. Use a common Shape base with `area()`.

### How to Spot LSP Violations

- You check `isinstance()` before calling a method
- A subclass raises `NotImplementedError` for a parent's method
- A subclass silently ignores or overrides parent behavior in unexpected ways

---

## I — Interface Segregation Principle (ISP)

**"No client should be forced to depend on methods it doesn't use."**

### The Problem

```python
# BAD: One fat interface — Waiter forced to implement cook()??
from abc import ABC, abstractmethod

class IRestaurantWorker(ABC):
    @abstractmethod
    def cook(self): pass

    @abstractmethod
    def serve(self): pass

    @abstractmethod
    def clean(self): pass

    @abstractmethod
    def manage_inventory(self): pass

class Waiter(IRestaurantWorker):
    def cook(self):
        raise NotImplementedError("Waiters don't cook!")  # ← forced to implement!

    def serve(self):
        return "Serving food"

    def clean(self):
        return "Cleaning table"

    def manage_inventory(self):
        raise NotImplementedError("Waiters don't manage inventory!")
```

### The Fix

```python
# GOOD: Small, focused interfaces
class ICook(ABC):
    @abstractmethod
    def cook(self): pass

class IServer(ABC):
    @abstractmethod
    def serve(self): pass

class ICleaner(ABC):
    @abstractmethod
    def clean(self): pass

# Each role implements only what it needs:
class Waiter(IServer, ICleaner):
    def serve(self):
        return "Serving food"
    def clean(self):
        return "Cleaning table"

class Chef(ICook, ICleaner):
    def cook(self):
        return "Cooking food"
    def clean(self):
        return "Cleaning kitchen"
```

### How to Spot ISP Violations

- Classes with methods that raise `NotImplementedError`
- Methods that just `pass` or `return None` because they don't apply
- "This class doesn't need half of these methods"

---

## D — Dependency Inversion Principle (DIP)

**"High-level modules should not depend on low-level modules. Both should depend on abstractions."**

### The Problem

```python
# BAD: OrderService is TIGHTLY COUPLED to specific implementations
class OrderService:
    def __init__(self):
        self.db = MySQLDatabase()       # hardcoded!
        self.notifier = SMSNotifier()   # hardcoded!

    def place_order(self, order):
        self.db.save(order)
        self.notifier.send(f"Order {order.id} placed")
```

Want to switch to PostgreSQL? Edit OrderService.
Want to add email notifications? Edit OrderService.
Want to test without a real DB? Can't.

### The Fix

```python
# GOOD: Depend on abstractions, inject implementations
from abc import ABC, abstractmethod

class Database(ABC):
    @abstractmethod
    def save(self, entity): pass

class Notifier(ABC):
    @abstractmethod
    def send(self, message): pass

class OrderService:
    def __init__(self, db: Database, notifier: Notifier):
        self.db = db              # injected!
        self.notifier = notifier  # injected!

    def place_order(self, order):
        self.db.save(order)
        self.notifier.send(f"Order {order.id} placed")

# Usage — easy to swap implementations:
service = OrderService(
    db=PostgreSQLDatabase(),
    notifier=EmailNotifier()
)

# Testing — inject mocks:
service = OrderService(
    db=MockDatabase(),
    notifier=MockNotifier()
)
```

### How to Spot DIP Violations

- A class creates its own dependencies with `SomeClass()` inside `__init__`
- Changing a database/email/SMS provider requires editing business logic
- You can't test a class without a real database/network

---

## SOLID Summary

| Principle | What It Says | Violation Smell | Fix |
|---|---|---|---|
| **SRP** | One reason to change | Class does X AND Y AND Z | Split into focused classes |
| **OCP** | Extend, don't modify | if/elif chain grows with each feature | Strategy pattern, polymorphism |
| **LSP** | Subtypes = substitutable | isinstance() checks, NotImplementedError | Fix hierarchy, use composition |
| **ISP** | Small interfaces | Classes with unused methods | Split into role-specific interfaces |
| **DIP** | Depend on abstractions | Hardcoded `SomeClass()` in __init__ | Inject dependencies, use ABC |

---

## Code Files

| File | What It Demonstrates |
|---|---|
| `01_srp.py` | Single Responsibility — before/after restaurant example |
| `02_ocp.py` | Open/Closed — discount strategies |
| `03_lsp.py` | Liskov Substitution — shape and menu item examples |
| `04_isp.py` | Interface Segregation — restaurant worker roles |
| `05_dip.py` | Dependency Inversion — injected dependencies |
| `06_solid_restaurant.py` | Full restaurant system following all 5 SOLID principles |

---

## Key Takeaways

1. **SRP** — One class, one job. If it does X AND Y, split it.
2. **OCP** — New feature = new code, not editing old code. Use polymorphism.
3. **LSP** — Subclass must work everywhere parent works. No surprises.
4. **ISP** — Small interfaces > fat interfaces. Don't force unused methods.
5. **DIP** — Depend on abstractions. Inject dependencies. Testable code.
6. **SOLID is not dogma** — it's a compass. Real code involves trade-offs. Apply where the pain is.

**Next class:** Design Patterns (Strategy, Observer, Factory, Singleton)

---

## Resources

- [SOLID Principles (Wikipedia)](https://en.wikipedia.org/wiki/SOLID)
- [Real Python — SOLID Principles](https://realpython.com/solid-principles-python/)
- [Python docs — ABC](https://docs.python.org/3/library/abc.html)
- [Robert C. Martin — Clean Architecture](https://blog.cleancoder.com/uncle-bob/2012/08/13/the-clean-architecture.html)
