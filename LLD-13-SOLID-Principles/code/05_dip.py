"""
Dependency Inversion Principle (DIP)
=====================================
"High-level modules should not depend on low-level modules.
Both should depend on abstractions."

Restaurant analogy: The restaurant MANAGER doesn't personally go to
a specific farm to get tomatoes. Instead, they depend on the CONCEPT of
a "supplier" — any supplier who meets the contract works. Want to switch
from Farm A to Farm B? The manager's workflow doesn't change at all.

In code: Your business logic (OrderService) shouldn't directly import
MySQLDatabase or TwilioSMS. Instead, it should depend on abstract
interfaces (Database, Notifier). Then you can swap implementations
freely — real DB for production, fake DB for testing.
"""

print("=" * 60)
print("DEPENDENCY INVERSION PRINCIPLE (DIP)")
print("=" * 60)

from abc import ABC, abstractmethod

# ============================================================
# --- BAD: High-level module directly depends on low-level modules ---
# ============================================================
# OrderServiceBad is TIGHTLY COUPLED to specific implementations.
# Want to switch from MySQL to PostgreSQL? Must modify OrderServiceBad.
# Want to test without sending real SMS? Can't — it's hardcoded!

print("\n--- BAD: Tight coupling (can't swap, can't test) ---\n")


class MySQLDatabase:
    """Low-level module: specific database implementation."""

    def save_order(self, order_data: dict):
        print(f"  [MySQL] INSERT INTO orders VALUES ({order_data['customer']}, Rs.{order_data['total']})")
        return 101  # fake order ID


class TwilioSMSService:
    """Low-level module: specific SMS provider."""

    def send_sms(self, phone: str, message: str):
        print(f"  [Twilio SMS] To {phone}: {message}")


class RazorpayPayment:
    """Low-level module: specific payment gateway."""

    def charge(self, amount: float, customer: str):
        print(f"  [Razorpay] Charged Rs.{amount} to {customer}")
        return True


class OrderServiceBad:
    """HIGH-LEVEL module that's tightly coupled to LOW-LEVEL modules.

    Problems:
    1. Can't switch MySQL to PostgreSQL without changing THIS class
    2. Can't switch Twilio to SendGrid without changing THIS class
    3. Can't test without hitting real MySQL/Twilio/Razorpay!
    """

    def __init__(self):
        # Direct dependencies on concrete implementations — BAD!
        self.db = MySQLDatabase()
        self.sms = TwilioSMSService()
        self.payment = RazorpayPayment()

    def place_order(self, customer: str, phone: str, items: list):
        total = sum(item["price"] for item in items)

        # Tightly coupled to Razorpay
        self.payment.charge(total, customer)

        # Tightly coupled to MySQL
        order_id = self.db.save_order({"customer": customer, "total": total})

        # Tightly coupled to Twilio
        self.sms.send_sms(phone, f"Order #{order_id} confirmed! Total: Rs.{total}")

        return order_id


# Works but is rigid — can't swap anything!
bad_service = OrderServiceBad()
bad_service.place_order("Vipul", "+91-9876543210", [
    {"name": "Biryani", "price": 350},
    {"name": "Raita", "price": 50},
])


# ============================================================
# --- GOOD: Depend on abstractions, inject implementations ---
# ============================================================

print("\n\n--- GOOD: Abstractions + Dependency Injection ---\n")


# Step 1: Define ABSTRACTIONS (interfaces/contracts)

class Database(ABC):
    """Abstract interface for any database."""

    @abstractmethod
    def save_order(self, order_data: dict) -> int:
        pass

    @abstractmethod
    def get_order(self, order_id: int) -> dict:
        pass


class Notifier(ABC):
    """Abstract interface for any notification method."""

    @abstractmethod
    def notify(self, recipient: str, message: str) -> None:
        pass


class PaymentGateway(ABC):
    """Abstract interface for any payment processor."""

    @abstractmethod
    def charge(self, amount: float, customer: str) -> bool:
        pass


# Step 2: Create CONCRETE implementations of the abstractions

class PostgreSQLDatabase(Database):
    """One concrete implementation of Database."""

    def __init__(self):
        self.orders = {}
        self.next_id = 1

    def save_order(self, order_data: dict) -> int:
        order_id = self.next_id
        self.orders[order_id] = order_data
        self.next_id += 1
        print(f"  [PostgreSQL] Saved order #{order_id} for {order_data['customer']}")
        return order_id

    def get_order(self, order_id: int) -> dict:
        return self.orders.get(order_id, {})


class EmailNotifier(Notifier):
    """Sends notifications via email."""

    def notify(self, recipient: str, message: str) -> None:
        print(f"  [Email] To {recipient}: {message}")


class WhatsAppNotifier(Notifier):
    """Sends notifications via WhatsApp."""

    def notify(self, recipient: str, message: str) -> None:
        print(f"  [WhatsApp] To {recipient}: {message}")


class StripePayment(PaymentGateway):
    """Payment via Stripe."""

    def charge(self, amount: float, customer: str) -> bool:
        print(f"  [Stripe] Charged Rs.{amount} to {customer}")
        return True


# Step 3: High-level module depends ONLY on abstractions

class OrderServiceGood:
    """HIGH-LEVEL module that depends on ABSTRACTIONS, not concrete classes.

    It doesn't know or care whether it's using PostgreSQL or MongoDB,
    Email or WhatsApp, Stripe or Razorpay. It just uses the interface.
    """

    def __init__(self, db: Database, notifier: Notifier, payment: PaymentGateway):
        # Dependencies are INJECTED — we accept interfaces, not create concretes
        self.db = db
        self.notifier = notifier
        self.payment = payment

    def place_order(self, customer: str, contact: str, items: list):
        total = sum(item["price"] for item in items)

        # Uses abstract interface — works with ANY payment gateway
        self.payment.charge(total, customer)

        # Uses abstract interface — works with ANY database
        order_id = self.db.save_order({"customer": customer, "total": total, "items": items})

        # Uses abstract interface — works with ANY notifier
        self.notifier.notify(contact, f"Order #{order_id} confirmed! Total: Rs.{total}")

        return order_id


# Use with PostgreSQL + Email + Stripe
print("Configuration 1: PostgreSQL + Email + Stripe")
service1 = OrderServiceGood(
    db=PostgreSQLDatabase(),
    notifier=EmailNotifier(),
    payment=StripePayment(),
)
service1.place_order("Vipul", "vipul@email.com", [
    {"name": "Biryani", "price": 350},
    {"name": "Raita", "price": 50},
])

# Swap to WhatsApp notifications — ZERO changes to OrderServiceGood!
print("\nConfiguration 2: Same DB + WhatsApp + Stripe")
service2 = OrderServiceGood(
    db=PostgreSQLDatabase(),
    notifier=WhatsAppNotifier(),  # Swapped! No code changes needed.
    payment=StripePayment(),
)
service2.place_order("Kaarthik", "+91-9876543210", [
    {"name": "Dosa", "price": 150},
    {"name": "Filter Coffee", "price": 80},
])


# ============================================================
# The REAL power: Testing with mocks!
# ============================================================

print("\n\n--- BONUS: Easy testing with mock/fake implementations ---\n")


class FakeDatabase(Database):
    """In-memory fake for testing — no real DB needed!"""

    def __init__(self):
        self.saved_orders = []

    def save_order(self, order_data: dict) -> int:
        self.saved_orders.append(order_data)
        print(f"  [FakeDB] Stored order in memory (for testing)")
        return len(self.saved_orders)

    def get_order(self, order_id: int) -> dict:
        return self.saved_orders[order_id - 1] if order_id <= len(self.saved_orders) else {}


class FakeNotifier(Notifier):
    """Captures notifications for assertions — no real emails sent!"""

    def __init__(self):
        self.sent_messages = []

    def notify(self, recipient: str, message: str) -> None:
        self.sent_messages.append((recipient, message))
        print(f"  [FakeNotifier] Captured: {recipient} -> {message}")


class FakePayment(PaymentGateway):
    """Always succeeds — no real charges!"""

    def __init__(self):
        self.charges = []

    def charge(self, amount: float, customer: str) -> bool:
        self.charges.append((amount, customer))
        print(f"  [FakePayment] Recorded charge: Rs.{amount} to {customer}")
        return True


# Test without any real infrastructure!
fake_db = FakeDatabase()
fake_notifier = FakeNotifier()
fake_payment = FakePayment()

test_service = OrderServiceGood(
    db=fake_db,
    notifier=fake_notifier,
    payment=fake_payment,
)

print("Running test order with ALL fakes:")
test_service.place_order("Ajit", "ajit@test.com", [
    {"name": "Paneer Tikka", "price": 280},
])

# Verify behavior without hitting real services!
print(f"\n  Assertions:")
print(f"    Orders saved: {len(fake_db.saved_orders)} (expected 1) {'PASS' if len(fake_db.saved_orders) == 1 else 'FAIL'}")
print(f"    Notifications sent: {len(fake_notifier.sent_messages)} (expected 1) {'PASS' if len(fake_notifier.sent_messages) == 1 else 'FAIL'}")
print(f"    Payments charged: {len(fake_payment.charges)} (expected 1) {'PASS' if len(fake_payment.charges) == 1 else 'FAIL'}")
print(f"    Amount charged: Rs.{fake_payment.charges[0][0]} (expected 280) {'PASS' if fake_payment.charges[0][0] == 280 else 'FAIL'}")


# ============================================================
# WHY THIS MATTERS:
# ============================================================
print("\n" + "=" * 60)
print("WHY DIP MATTERS:")
print("-" * 60)
print("- Switch databases without touching business logic")
print("- Switch notification providers in one line")
print("- Test WITHOUT real databases, APIs, or payment gateways")
print("- Different environments can use different implementations:")
print("  - Dev: FakeDB + ConsoleNotifier + FakePayment")
print("  - Prod: PostgreSQL + WhatsApp + Stripe")
print("- The high-level policy (OrderService) is PROTECTED from")
print("  low-level implementation changes")
print("=" * 60)
