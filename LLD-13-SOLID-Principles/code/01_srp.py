"""
Single Responsibility Principle (SRP)
=====================================
"A class should have one, and only one, reason to change."

Think of it this way: In a restaurant, the chef cooks, the waiter serves,
and the cashier handles payments. You wouldn't want one person doing ALL
of those things — they'd burn out and mistakes would pile up.

Same with code: each class should have ONE job.
"""

print("=" * 60)
print("SINGLE RESPONSIBILITY PRINCIPLE (SRP)")
print("=" * 60)

# ============================================================
# --- BAD: God Class that does EVERYTHING ---
# ============================================================
# This class has MULTIPLE reasons to change:
# 1. If order validation rules change
# 2. If we switch databases
# 3. If we change notification method (SMS -> Email)
# 4. If pricing/discount logic changes

print("\n--- BAD: God Class (OrderProcessor does everything) ---\n")


class OrderProcessorBad:
    """This class violates SRP — it handles validation, storage,
    notification, AND billing all in one place."""

    def __init__(self):
        self.orders = []

    def process_order(self, customer_name, items, discount_percent=0):
        # Responsibility 1: Validation
        if not items:
            print(f"  [ERROR] {customer_name}: No items in order!")
            return None
        for item in items:
            if item["price"] <= 0:
                print(f"  [ERROR] Invalid price for {item['name']}")
                return None

        # Responsibility 2: Calculate total (business logic)
        total = sum(item["price"] * item["qty"] for item in items)
        if discount_percent > 0:
            total = total * (1 - discount_percent / 100)

        # Responsibility 3: Save to database
        order = {
            "customer": customer_name,
            "items": items,
            "total": round(total, 2),
        }
        self.orders.append(order)
        print(f"  [DB] Saved order for {customer_name} to database")

        # Responsibility 4: Send notification
        print(f"  [SMS] Sent to {customer_name}: Your order of Rs.{order['total']} is confirmed!")

        # Responsibility 5: Generate receipt
        print(f"  [RECEIPT] Order #{len(self.orders)}")
        print(f"    Customer: {customer_name}")
        for item in items:
            print(f"    - {item['name']} x{item['qty']} = Rs.{item['price'] * item['qty']}")
        print(f"    Total: Rs.{order['total']}")

        return order


# Run the bad version
bad_processor = OrderProcessorBad()
bad_processor.process_order("Vipul", [
    {"name": "Butter Chicken", "price": 350, "qty": 2},
    {"name": "Naan", "price": 50, "qty": 4},
])


# ============================================================
# --- GOOD: Each class has ONE responsibility ---
# ============================================================
# Now if notification method changes, only NotificationService changes.
# If database changes, only OrderRepository changes.
# Each class has exactly ONE reason to change.

print("\n\n--- GOOD: Separate classes, each with ONE job ---\n")


class OrderValidator:
    """Responsibility: Validate order data. That's it."""

    def validate(self, customer_name, items):
        if not items:
            raise ValueError(f"{customer_name}: No items in order!")
        for item in items:
            if item["price"] <= 0:
                raise ValueError(f"Invalid price for {item['name']}")
        return True


class PriceCalculator:
    """Responsibility: Calculate totals and apply discounts."""

    def calculate_total(self, items, discount_percent=0):
        total = sum(item["price"] * item["qty"] for item in items)
        if discount_percent > 0:
            total = total * (1 - discount_percent / 100)
        return round(total, 2)


class OrderRepository:
    """Responsibility: Persist orders to storage."""

    def __init__(self):
        self.orders = []

    def save(self, order):
        self.orders.append(order)
        print(f"  [DB] Saved order for {order['customer']} to database")
        return len(self.orders)


class NotificationService:
    """Responsibility: Notify the customer."""

    def send_confirmation(self, customer_name, total):
        print(f"  [SMS] Sent to {customer_name}: Your order of Rs.{total} is confirmed!")


class ReceiptGenerator:
    """Responsibility: Format and print receipts."""

    def generate(self, order_id, customer_name, items, total):
        print(f"  [RECEIPT] Order #{order_id}")
        print(f"    Customer: {customer_name}")
        for item in items:
            print(f"    - {item['name']} x{item['qty']} = Rs.{item['price'] * item['qty']}")
        print(f"    Total: Rs.{total}")


class OrderService:
    """Orchestrator — delegates to specialists. Like a restaurant manager
    who doesn't cook or serve but coordinates everyone."""

    def __init__(self, validator, calculator, repository, notifier, receipt_gen):
        self.validator = validator
        self.calculator = calculator
        self.repository = repository
        self.notifier = notifier
        self.receipt_gen = receipt_gen

    def process_order(self, customer_name, items, discount_percent=0):
        # Each step is handled by a specialist
        self.validator.validate(customer_name, items)
        total = self.calculator.calculate_total(items, discount_percent)
        order = {"customer": customer_name, "items": items, "total": total}
        order_id = self.repository.save(order)
        self.notifier.send_confirmation(customer_name, total)
        self.receipt_gen.generate(order_id, customer_name, items, total)
        return order


# Wire up the components (each can be tested/replaced independently!)
service = OrderService(
    validator=OrderValidator(),
    calculator=PriceCalculator(),
    repository=OrderRepository(),
    notifier=NotificationService(),
    receipt_gen=ReceiptGenerator(),
)

service.process_order("Vipul", [
    {"name": "Butter Chicken", "price": 350, "qty": 2},
    {"name": "Naan", "price": 50, "qty": 4},
])

# ============================================================
# WHY THIS MATTERS:
# ============================================================
print("\n" + "=" * 60)
print("WHY SRP MATTERS:")
print("-" * 60)
print("- Want to switch from SMS to Email? Change ONLY NotificationService")
print("- Want to switch from MySQL to MongoDB? Change ONLY OrderRepository")
print("- Want to add GST calculation? Change ONLY PriceCalculator")
print("- Each class is small, testable, and easy to understand")
print("=" * 60)
