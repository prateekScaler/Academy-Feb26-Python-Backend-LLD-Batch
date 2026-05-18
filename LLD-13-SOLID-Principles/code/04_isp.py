"""
Interface Segregation Principle (ISP)
======================================
"Clients should not be forced to depend on interfaces they do not use."

Restaurant analogy: A waiter's job description shouldn't include
"must know how to repair the tandoor oven." A chef's job description
shouldn't include "must know how to process UPI payments."

Each role should only be required to implement skills relevant to THEIR job.
Fat interfaces force classes to implement methods they don't need,
leading to empty methods, NotImplementedError, or dummy returns.
"""

print("=" * 60)
print("INTERFACE SEGREGATION PRINCIPLE (ISP)")
print("=" * 60)

from abc import ABC, abstractmethod

# ============================================================
# --- BAD: One fat interface that forces everyone to implement everything ---
# ============================================================

print("\n--- BAD: Fat IRestaurantWorker interface ---\n")


class IRestaurantWorkerBad(ABC):
    """This interface is TOO broad. Not every worker does all of these!"""

    @abstractmethod
    def cook_food(self, dish_name: str) -> str:
        pass

    @abstractmethod
    def serve_table(self, table_number: int) -> str:
        pass

    @abstractmethod
    def take_order(self, table_number: int) -> str:
        pass

    @abstractmethod
    def clean_table(self, table_number: int) -> str:
        pass

    @abstractmethod
    def manage_inventory(self, item: str, qty: int) -> str:
        pass

    @abstractmethod
    def process_payment(self, amount: float) -> str:
        pass


class WaiterBad(IRestaurantWorkerBad):
    """Vipul is a waiter. He should NOT need to implement cook_food or manage_inventory!"""

    def __init__(self, name: str):
        self.name = name

    def take_order(self, table_number: int) -> str:
        return f"{self.name} took order from table {table_number}"

    def serve_table(self, table_number: int) -> str:
        return f"{self.name} served food to table {table_number}"

    def clean_table(self, table_number: int) -> str:
        return f"{self.name} cleaned table {table_number}"

    # FORCED to implement these even though a waiter doesn't do them!
    def cook_food(self, dish_name: str) -> str:
        raise NotImplementedError("I'm a waiter, not a chef!")  # Smell!

    def manage_inventory(self, item: str, qty: int) -> str:
        raise NotImplementedError("I'm a waiter, not a manager!")  # Smell!

    def process_payment(self, amount: float) -> str:
        raise NotImplementedError("I'm a waiter, not a cashier!")  # Smell!


class ChefBad(IRestaurantWorkerBad):
    """Kaarthik is a chef. He should NOT need to implement serve_table or process_payment!"""

    def __init__(self, name: str):
        self.name = name

    def cook_food(self, dish_name: str) -> str:
        return f"{self.name} cooked {dish_name}"

    def manage_inventory(self, item: str, qty: int) -> str:
        return f"{self.name} updated inventory: {item} = {qty}"

    # FORCED to implement these even though a chef doesn't do them!
    def serve_table(self, table_number: int) -> str:
        raise NotImplementedError("I'm a chef, not a waiter!")  # Smell!

    def take_order(self, table_number: int) -> str:
        raise NotImplementedError("I'm a chef, not a waiter!")  # Smell!

    def clean_table(self, table_number: int) -> str:
        raise NotImplementedError("I'm a chef, not a cleaner!")  # Smell!

    def process_payment(self, amount: float) -> str:
        raise NotImplementedError("I'm a chef, not a cashier!")  # Smell!


# Demonstrate the problem
waiter = WaiterBad("Vipul")
chef = ChefBad("Kaarthik")

print(f"  {waiter.take_order(3)}")
print(f"  {chef.cook_food('Biryani')}")

print("\n  Now watch what happens with methods they shouldn't have:")
try:
    waiter.cook_food("Pasta")
except NotImplementedError as e:
    print(f"  CRASH! Waiter.cook_food() -> {e}")

try:
    chef.serve_table(5)
except NotImplementedError as e:
    print(f"  CRASH! Chef.serve_table() -> {e}")


# ============================================================
# --- GOOD: Small, focused interfaces (one per responsibility) ---
# ============================================================

print("\n\n--- GOOD: Small focused interfaces ---\n")


class ICook(ABC):
    """Only for roles that cook."""

    @abstractmethod
    def cook_food(self, dish_name: str) -> str:
        pass


class IServer(ABC):
    """Only for roles that serve customers."""

    @abstractmethod
    def take_order(self, table_number: int) -> str:
        pass

    @abstractmethod
    def serve_table(self, table_number: int) -> str:
        pass


class ICleaner(ABC):
    """Only for roles that clean."""

    @abstractmethod
    def clean_table(self, table_number: int) -> str:
        pass


class IInventoryManager(ABC):
    """Only for roles that manage inventory."""

    @abstractmethod
    def manage_inventory(self, item: str, qty: int) -> str:
        pass


class ICashier(ABC):
    """Only for roles that handle payments."""

    @abstractmethod
    def process_payment(self, amount: float) -> str:
        pass


# Now each role implements ONLY what it actually does!

class Waiter(IServer, ICleaner):
    """Vipul is a waiter: takes orders, serves food, cleans tables.
    Does NOT cook, manage inventory, or process payments."""

    def __init__(self, name: str):
        self.name = name

    def take_order(self, table_number: int) -> str:
        return f"{self.name} took order from table {table_number}"

    def serve_table(self, table_number: int) -> str:
        return f"{self.name} served food to table {table_number}"

    def clean_table(self, table_number: int) -> str:
        return f"{self.name} cleaned table {table_number}"


class Chef(ICook, IInventoryManager):
    """Kaarthik is a chef: cooks food and manages ingredient inventory.
    Does NOT serve tables or process payments."""

    def __init__(self, name: str):
        self.name = name

    def cook_food(self, dish_name: str) -> str:
        return f"{self.name} cooked {dish_name}"

    def manage_inventory(self, item: str, qty: int) -> str:
        return f"{self.name} updated inventory: {item} = {qty}"


class Cashier(ICashier):
    """Ajit is a cashier: processes payments.
    Does NOT cook, serve, or clean."""

    def __init__(self, name: str):
        self.name = name

    def process_payment(self, amount: float) -> str:
        return f"{self.name} processed payment of Rs.{amount}"


class HeadWaiter(IServer, ICleaner, ICashier):
    """A head waiter does serving AND can handle payments.
    Multiple interfaces = composable roles!"""

    def __init__(self, name: str):
        self.name = name

    def take_order(self, table_number: int) -> str:
        return f"{self.name} (Head Waiter) took order from table {table_number}"

    def serve_table(self, table_number: int) -> str:
        return f"{self.name} (Head Waiter) served table {table_number}"

    def clean_table(self, table_number: int) -> str:
        return f"{self.name} (Head Waiter) cleaned table {table_number}"

    def process_payment(self, amount: float) -> str:
        return f"{self.name} (Head Waiter) processed payment of Rs.{amount}"


# Demonstrate — each role only has what it needs
vipul = Waiter("Vipul")
kaarthik = Chef("Kaarthik")
ajit = Cashier("Ajit")
head_waiter = HeadWaiter("Vipul Sr.")

print("Waiter (Vipul) — only serving & cleaning:")
print(f"  {vipul.take_order(3)}")
print(f"  {vipul.serve_table(3)}")
print(f"  {vipul.clean_table(3)}")
# vipul.cook_food() <- This doesn't even exist! No crash, just not available.

print("\nChef (Kaarthik) — only cooking & inventory:")
print(f"  {kaarthik.cook_food('Butter Chicken')}")
print(f"  {kaarthik.manage_inventory('Chicken', 50)}")

print("\nCashier (Ajit) — only payments:")
print(f"  {ajit.process_payment(750)}")

print("\nHead Waiter — serving + cleaning + payments (composed!):")
print(f"  {head_waiter.take_order(1)}")
print(f"  {head_waiter.process_payment(500)}")


# Type-safe function that only needs specific capability
def serve_all_tables(server: IServer, tables: list):
    """This function only needs IServer — doesn't care about cooking or payments."""
    print(f"\n  Serving tables {tables}:")
    for t in tables:
        print(f"    {server.serve_table(t)}")


# Both Waiter and HeadWaiter satisfy IServer!
serve_all_tables(vipul, [1, 2, 3])
serve_all_tables(head_waiter, [4, 5])


# ============================================================
# WHY THIS MATTERS:
# ============================================================
print("\n" + "=" * 60)
print("WHY ISP MATTERS:")
print("-" * 60)
print("- No more NotImplementedError or pass-only methods")
print("- Each class only implements what it genuinely does")
print("- Functions can declare exactly what capability they need")
print("- New roles (HeadWaiter) compose interfaces like building blocks")
print("- Easier to test: mock only the small interface you need")
print("=" * 60)
