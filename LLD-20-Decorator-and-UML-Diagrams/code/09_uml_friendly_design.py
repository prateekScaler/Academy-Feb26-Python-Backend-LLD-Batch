"""
LLD-20 · UML · Example 9 — Code structured to render cleanly in PyCharm UML.

Run:  python3 09_uml_friendly_design.py

This file demonstrates a small e-commerce ordering domain that
shows EVERY relationship type from the UML class-diagram lesson:

    Inheritance       — SavingsAccount IS-A Account
    Realisation       — RazorpayGateway IMPLEMENTS PaymentGateway
    Composition       — Order OWNS OrderLines (filled diamond)
    Aggregation       — Cart HAS Products (open diamond)
    Dependency        — OrderService USES PaymentGateway briefly

Open this file in PyCharm:
    Right-click → Diagrams → Show Diagram… → Python Class Diagram

Every arrow on PyCharm's auto-generated diagram corresponds to
one of the five relationship types in the LLD-20 UML section.
"""

from __future__ import annotations
from abc import ABC, abstractmethod
from dataclasses import dataclass, field


# =====================================================================
# Inheritance  (open triangle, solid line)
# Account ←──── SavingsAccount / CheckingAccount
# =====================================================================
class Account:
    def __init__(self, account_id: str, balance: float) -> None:
        self.account_id = account_id
        self.balance = balance

    def deposit(self, amount: float) -> None:
        self.balance += amount

    def withdraw(self, amount: float) -> bool:
        if self.balance < amount:
            return False
        self.balance -= amount
        return True


class SavingsAccount(Account):
    """SavingsAccount IS-A Account, plus interest accrual."""
    def __init__(self, account_id: str, balance: float, interest_rate: float) -> None:
        super().__init__(account_id, balance)
        self.interest_rate = interest_rate

    def accrue_interest(self) -> None:
        self.balance *= 1 + self.interest_rate


class CheckingAccount(Account):
    """CheckingAccount IS-A Account, plus an overdraft limit."""
    def __init__(self, account_id: str, balance: float, overdraft: float) -> None:
        super().__init__(account_id, balance)
        self.overdraft = overdraft

    def withdraw(self, amount: float) -> bool:
        if self.balance + self.overdraft < amount:
            return False
        self.balance -= amount
        return True


# =====================================================================
# Realisation (dashed line, open triangle)
# PaymentGateway ←- - - RazorpayGateway / StripeGateway
# =====================================================================
class PaymentGateway(ABC):
    @abstractmethod
    def pay(self, amount: float, currency: str) -> str: ...


class RazorpayGateway(PaymentGateway):
    def pay(self, amount: float, currency: str) -> str:
        return f"razorpay_txn_{int(amount * 100)}"


class StripeGateway(PaymentGateway):
    def pay(self, amount: float, currency: str) -> str:
        return f"stripe_ch_{int(amount * 100)}"


# =====================================================================
# Composition (filled diamond)
# Order ♦──── OrderLine    (OrderLines cannot exist without the Order)
# =====================================================================
@dataclass
class OrderLine:
    sku: str
    qty: int
    unit_price: float


@dataclass
class Order:
    order_id: str
    customer_id: str
    lines: list[OrderLine] = field(default_factory=list)

    def add_line(self, sku: str, qty: int, unit_price: float) -> None:
        # The OrderLine is created INSIDE Order — it exists only as a part of Order
        self.lines.append(OrderLine(sku, qty, unit_price))

    @property
    def total(self) -> float:
        return sum(line.qty * line.unit_price for line in self.lines)


# =====================================================================
# Aggregation (open diamond)
# Cart ◇──── Product   (Products exist before, after, and outside the Cart)
# =====================================================================
@dataclass
class Product:
    sku: str
    name: str
    price: float


class Cart:
    """The cart HOLDS references to Products that exist independently."""
    def __init__(self, cart_id: str) -> None:
        self.cart_id = cart_id
        self._items: list[tuple[Product, int]] = []     # (product, qty)

    def add_product(self, product: Product, qty: int = 1) -> None:
        # We HOLD the existing Product, we don't OWN it.
        self._items.append((product, qty))


# =====================================================================
# Dependency (dashed arrow)
# OrderService - - -> PaymentGateway   (uses transiently in one method)
# =====================================================================
class OrderService:
    """Placing an order USES a PaymentGateway briefly — the service
       doesn't hold a long-lived reference to one."""

    def __init__(self, repo: "OrderRepository") -> None:
        self._repo = repo   # composition — service owns the repo

    def place_order(self, order: Order, gateway: PaymentGateway) -> str:
        # The PaymentGateway parameter is the dependency: used during
        # this method, then forgotten.
        txn_id = gateway.pay(order.total, "INR")
        self._repo.save(order)
        return txn_id


class OrderRepository:
    def __init__(self) -> None:
        self._db: dict[str, Order] = {}

    def save(self, order: Order) -> None:
        self._db[order.order_id] = order


# =====================================================================
# Demo
# =====================================================================
def main() -> None:
    # Aggregation: products exist on their own
    laptop = Product(sku="LP-01", name="MacBook", price=1199.0)
    book   = Product(sku="BK-01", name="Python LLD", price=49.0)

    cart = Cart(cart_id="cart_42")
    cart.add_product(laptop, qty=1)
    cart.add_product(book, qty=2)

    # Composition: OrderLines created INSIDE the Order
    order = Order(order_id="ORD-001", customer_id="cust_42")
    order.add_line(laptop.sku, 1, laptop.price)
    order.add_line(book.sku,   2, book.price)
    print(f"Order total: ${order.total:.2f}")

    # Inheritance: SavingsAccount IS-A Account, has extra behaviour
    savings = SavingsAccount("ACC-100", balance=1000.0, interest_rate=0.04)
    savings.accrue_interest()
    print(f"Savings balance after interest: ${savings.balance:.2f}")

    # Realisation: RazorpayGateway IMPLEMENTS PaymentGateway interface
    # Dependency: OrderService USES a PaymentGateway transiently
    service = OrderService(OrderRepository())
    txn = service.place_order(order, gateway=RazorpayGateway())
    print(f"Order placed, payment ref: {txn}")

    print("\nOpen this file in PyCharm and view its UML diagram —")
    print("each arrow you see maps to exactly one of:")
    print("  - Inheritance (solid + open triangle)")
    print("  - Realisation (dashed + open triangle)")
    print("  - Composition (filled diamond)")
    print("  - Aggregation (open diamond)")
    print("  - Dependency (dashed arrow)")


if __name__ == "__main__":
    main()
