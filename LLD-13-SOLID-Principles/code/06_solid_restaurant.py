"""
Complete Restaurant Ordering System — ALL 5 SOLID Principles
=============================================================
This is a mini restaurant system that demonstrates how all SOLID principles
work TOGETHER in a real design.

- SRP: Separate classes for validation, pricing, persistence, notification
- OCP: Strategy pattern for discounts — add new ones without changing existing code
- LSP: All MenuItem subclasses (VegDish, NonVegDish, Beverage) are substitutable
- ISP: Small focused interfaces (IDatabase, INotifier, IPayment)
- DIP: OrderService depends on abstractions, not concrete implementations
"""

from abc import ABC, abstractmethod
from datetime import datetime

print("=" * 60)
print("SOLID RESTAURANT ORDERING SYSTEM")
print("=" * 60)


# ============================================================
# MENU ITEMS (LSP) — All subclasses honor the MenuItem contract
# ============================================================

class MenuItem(ABC):
    """Abstract base for all menu items.
    LSP: Any code using MenuItem must work with ALL subclasses."""

    def __init__(self, name: str, base_price: float):
        self.name = name
        self.base_price = base_price

    @abstractmethod
    def get_price(self) -> float:
        """Must return a valid positive price."""
        pass

    @abstractmethod
    def get_category(self) -> str:
        pass

    def __repr__(self):
        return f"{self.name} (Rs.{self.get_price():.0f})"


class VegDish(MenuItem):
    def get_price(self) -> float:
        return self.base_price

    def get_category(self) -> str:
        return "VEG"


class NonVegDish(MenuItem):
    def get_price(self) -> float:
        return self.base_price * 1.05  # 5% non-veg surcharge

    def get_category(self) -> str:
        return "NON-VEG"


class Beverage(MenuItem):
    def __init__(self, name: str, base_price: float, is_alcoholic: bool = False):
        super().__init__(name, base_price)
        self.is_alcoholic = is_alcoholic

    def get_price(self) -> float:
        if self.is_alcoholic:
            return self.base_price * 1.20  # 20% sin tax
        return self.base_price

    def get_category(self) -> str:
        return "BEVERAGE"


# ============================================================
# DISCOUNT STRATEGIES (OCP) — Add new discounts without modifying existing code
# ============================================================

class DiscountStrategy(ABC):
    """OCP: New discount types extend this, no existing code changes."""

    @abstractmethod
    def calculate(self, total: float) -> float:
        """Return discount amount."""
        pass

    @abstractmethod
    def name(self) -> str:
        pass


class NoDiscount(DiscountStrategy):
    def calculate(self, total: float) -> float:
        return 0.0

    def name(self) -> str:
        return "No discount"


class PercentageDiscount(DiscountStrategy):
    def __init__(self, percent: float):
        self.percent = percent

    def calculate(self, total: float) -> float:
        return total * (self.percent / 100)

    def name(self) -> str:
        return f"{self.percent}% off"


class FlatDiscount(DiscountStrategy):
    def __init__(self, amount: float):
        self.amount = amount

    def calculate(self, total: float) -> float:
        return min(self.amount, total)

    def name(self) -> str:
        return f"Flat Rs.{self.amount} off"


class FirstOrderDiscount(DiscountStrategy):
    """20% off for first-time customers, max Rs.150."""

    def calculate(self, total: float) -> float:
        return min(total * 0.20, 150)

    def name(self) -> str:
        return "First order (20% off, max Rs.150)"


# ============================================================
# INTERFACES (ISP + DIP) — Small focused abstractions
# ============================================================

class IDatabase(ABC):
    """ISP: Only database operations. DIP: Abstraction for persistence."""

    @abstractmethod
    def save_order(self, order: dict) -> int:
        pass

    @abstractmethod
    def get_order(self, order_id: int) -> dict:
        pass


class INotifier(ABC):
    """ISP: Only notification. DIP: Abstraction for messaging."""

    @abstractmethod
    def send(self, recipient: str, message: str) -> None:
        pass


class IPaymentProcessor(ABC):
    """ISP: Only payment. DIP: Abstraction for payment processing."""

    @abstractmethod
    def process(self, amount: float, customer: str) -> bool:
        pass


# ============================================================
# CONCRETE IMPLEMENTATIONS (can be swapped via DIP)
# ============================================================

class InMemoryDatabase(IDatabase):
    def __init__(self):
        self.orders = {}
        self.next_id = 1

    def save_order(self, order: dict) -> int:
        order_id = self.next_id
        order["id"] = order_id
        order["created_at"] = datetime.now().strftime("%H:%M:%S")
        self.orders[order_id] = order
        self.next_id += 1
        return order_id

    def get_order(self, order_id: int) -> dict:
        return self.orders.get(order_id, {})


class ConsoleNotifier(INotifier):
    def send(self, recipient: str, message: str) -> None:
        print(f"    [NOTIFY] {recipient}: {message}")


class SMSNotifier(INotifier):
    def send(self, recipient: str, message: str) -> None:
        print(f"    [SMS -> {recipient}] {message}")


class SimulatedPayment(IPaymentProcessor):
    def process(self, amount: float, customer: str) -> bool:
        print(f"    [PAYMENT] Rs.{amount:.0f} charged to {customer}'s account")
        return True


# ============================================================
# SINGLE RESPONSIBILITY CLASSES (SRP)
# ============================================================

class OrderValidator:
    """SRP: Only validates orders. Nothing else."""

    def validate(self, customer: str, items: list) -> bool:
        if not customer or not customer.strip():
            raise ValueError("Customer name is required")
        if not items:
            raise ValueError("Order must have at least one item")
        for item in items:
            if not isinstance(item, MenuItem):
                raise ValueError(f"Invalid item: {item}")
        return True


class PriceCalculator:
    """SRP: Only calculates prices. Handles subtotals, tax, discounts."""

    TAX_RATE = 0.05  # 5% GST

    def calculate(self, items: list, discount_strategy: DiscountStrategy) -> dict:
        subtotal = sum(item.get_price() for item in items)
        discount = discount_strategy.calculate(subtotal)
        after_discount = subtotal - discount
        tax = after_discount * self.TAX_RATE
        total = after_discount + tax

        return {
            "subtotal": round(subtotal, 2),
            "discount": round(discount, 2),
            "discount_name": discount_strategy.name(),
            "tax": round(tax, 2),
            "total": round(total, 2),
        }


class ReceiptPrinter:
    """SRP: Only formats and prints receipts."""

    def print_receipt(self, order_id: int, customer: str, items: list, pricing: dict):
        print(f"\n    {'=' * 40}")
        print(f"    RECEIPT - Order #{order_id}")
        print(f"    Customer: {customer}")
        print(f"    {'-' * 40}")
        for item in items:
            print(f"    [{item.get_category()}] {item.name:.<25} Rs.{item.get_price():.0f}")
        print(f"    {'-' * 40}")
        print(f"    Subtotal:{'':.<23} Rs.{pricing['subtotal']:.0f}")
        if pricing["discount"] > 0:
            print(f"    Discount ({pricing['discount_name']}): -Rs.{pricing['discount']:.0f}")
        print(f"    GST (5%):{'':.<23} Rs.{pricing['tax']:.0f}")
        print(f"    {'=' * 40}")
        print(f"    TOTAL:{'':.<26} Rs.{pricing['total']:.0f}")
        print(f"    {'=' * 40}")


# ============================================================
# ORDER SERVICE — The orchestrator (depends on abstractions via DIP)
# ============================================================

class OrderService:
    """Orchestrates the order flow.

    - SRP: Only coordinates, delegates actual work to specialists
    - DIP: Depends on abstractions (IDatabase, INotifier, IPaymentProcessor)
    - OCP: Discount strategy is passed in, not hardcoded
    """

    def __init__(
        self,
        db: IDatabase,
        notifier: INotifier,
        payment: IPaymentProcessor,
        validator: OrderValidator,
        calculator: PriceCalculator,
        receipt: ReceiptPrinter,
    ):
        self.db = db
        self.notifier = notifier
        self.payment = payment
        self.validator = validator
        self.calculator = calculator
        self.receipt = receipt

    def place_order(
        self,
        customer: str,
        contact: str,
        items: list,
        discount: DiscountStrategy = None,
    ) -> int:
        if discount is None:
            discount = NoDiscount()

        # Validate (SRP: validator handles this)
        self.validator.validate(customer, items)

        # Calculate pricing (SRP: calculator handles this)
        pricing = self.calculator.calculate(items, discount)

        # Process payment (DIP: abstraction, any implementation works)
        success = self.payment.process(pricing["total"], customer)
        if not success:
            raise RuntimeError("Payment failed!")

        # Persist order (DIP: abstraction, any DB works)
        order_data = {
            "customer": customer,
            "contact": contact,
            "items": [{"name": item.name, "price": item.get_price()} for item in items],
            "pricing": pricing,
        }
        order_id = self.db.save_order(order_data)

        # Notify customer (DIP: abstraction, any notifier works)
        self.notifier.send(
            contact,
            f"Order #{order_id} confirmed! Total: Rs.{pricing['total']:.0f}",
        )

        # Print receipt (SRP: receipt printer handles this)
        self.receipt.print_receipt(order_id, customer, items, pricing)

        return order_id


# ============================================================
# PUTTING IT ALL TOGETHER
# ============================================================

print("\n--- Setting up the restaurant system ---\n")

# Wire up dependencies (DIP: all injected, easily swappable)
db = InMemoryDatabase()
notifier = ConsoleNotifier()
payment = SimulatedPayment()

order_service = OrderService(
    db=db,
    notifier=notifier,
    payment=payment,
    validator=OrderValidator(),
    calculator=PriceCalculator(),
    receipt=ReceiptPrinter(),
)

# Create menu items (LSP: all work interchangeably)
menu = {
    "paneer_tikka": VegDish("Paneer Tikka", 280),
    "dal_makhani": VegDish("Dal Makhani", 220),
    "butter_chicken": NonVegDish("Butter Chicken", 380),
    "fish_fry": NonVegDish("Fish Fry", 320),
    "lassi": Beverage("Mango Lassi", 90),
    "beer": Beverage("Kingfisher", 250, is_alcoholic=True),
}

# --- Order 1: Vipul (regular order, no discount) ---
print("\n--- Order 1: Vipul (no discount) ---")
order_service.place_order(
    customer="Vipul",
    contact="vipul@email.com",
    items=[menu["paneer_tikka"], menu["dal_makhani"], menu["lassi"]],
)

# --- Order 2: Kaarthik (first-time customer discount — OCP!) ---
print("\n--- Order 2: Kaarthik (first order discount) ---")
order_service.place_order(
    customer="Kaarthik",
    contact="+91-9876543210",
    items=[menu["butter_chicken"], menu["fish_fry"], menu["beer"]],
    discount=FirstOrderDiscount(),  # OCP: new discount, no code changes
)

# --- Order 3: Ajit (flat discount) ---
print("\n--- Order 3: Ajit (flat Rs.100 off) ---")
order_service.place_order(
    customer="Ajit",
    contact="ajit@email.com",
    items=[menu["paneer_tikka"], menu["butter_chicken"], menu["lassi"]],
    discount=FlatDiscount(100),
)

# --- Demonstrate swappability (DIP) ---
print("\n\n--- Swapping notifier to SMS (DIP in action) ---")
sms_service = OrderService(
    db=db,
    notifier=SMSNotifier(),  # Swapped! Zero changes to OrderService
    payment=payment,
    validator=OrderValidator(),
    calculator=PriceCalculator(),
    receipt=ReceiptPrinter(),
)

sms_service.place_order(
    customer="Vipul",
    contact="+91-9999999999",
    items=[menu["dal_makhani"], menu["lassi"]],
    discount=PercentageDiscount(10),
)

# --- Show all orders in database ---
print("\n\n--- All orders stored in database ---")
for oid in range(1, db.next_id):
    order = db.get_order(oid)
    print(f"  Order #{oid}: {order['customer']} — Rs.{order['pricing']['total']:.0f} ({order['created_at']})")


# ============================================================
# SOLID SUMMARY
# ============================================================
print("\n" + "=" * 60)
print("HOW ALL 5 SOLID PRINCIPLES WORK TOGETHER:")
print("=" * 60)
print("""
  S - Single Responsibility:
      OrderValidator, PriceCalculator, ReceiptPrinter, OrderService
      each have ONE job.

  O - Open/Closed:
      Add FestivalDiscount, StudentDiscount, BulkDiscount...
      without touching OrderService or PriceCalculator.

  L - Liskov Substitution:
      VegDish, NonVegDish, Beverage all work wherever MenuItem is expected.
      No isinstance() checks, no surprises.

  I - Interface Segregation:
      IDatabase, INotifier, IPaymentProcessor — small and focused.
      OrderService doesn't force a database to know about notifications.

  D - Dependency Inversion:
      OrderService depends on IDatabase/INotifier/IPaymentProcessor.
      Swap InMemoryDB -> PostgreSQL, ConsoleNotifier -> WhatsApp
      without changing a single line in OrderService.
""")
print("=" * 60)
