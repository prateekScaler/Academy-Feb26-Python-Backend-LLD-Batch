"""
Open/Closed Principle (OCP)
============================
"Software entities should be open for extension, but closed for modification."

Restaurant analogy: Your menu card is PRINTED. To add a new dish, you don't
reprint the entire menu — you add a new page/insert. The existing menu stays
untouched (closed for modification), but you can always add new dishes
(open for extension).

In code: When you need new behavior, you should ADD new code, not CHANGE
existing working code. Every time you modify existing code, you risk
breaking something that already works.
"""

print("=" * 60)
print("OPEN/CLOSED PRINCIPLE (OCP)")
print("=" * 60)

# ============================================================
# --- BAD: Must modify existing code for every new discount type ---
# ============================================================
# Every time marketing invents a new discount, a developer must
# open this class and add another elif. Risk of bugs in existing logic!

print("\n--- BAD: if/elif chain that grows forever ---\n")


class DiscountCalculatorBad:
    """Violates OCP: Adding a new discount type requires modifying this class."""

    def calculate_discount(self, order_total, discount_type, customer_name):
        if discount_type == "percentage":
            # 10% off
            discount = order_total * 0.10
        elif discount_type == "flat":
            # Flat Rs.50 off
            discount = 50
        elif discount_type == "buy_one_get_one":
            # 50% off (approximation)
            discount = order_total * 0.50
        elif discount_type == "loyalty":
            # 15% off for loyal customers
            discount = order_total * 0.15
        # PROBLEM: Every new discount type = modify this method
        # elif discount_type == "festival":  <- must edit existing code!
        # elif discount_type == "student":   <- must edit existing code!
        else:
            discount = 0

        final = order_total - discount
        print(f"  {customer_name}: Rs.{order_total} - Rs.{discount:.0f} ({discount_type}) = Rs.{final:.0f}")
        return final


bad_calc = DiscountCalculatorBad()
bad_calc.calculate_discount(500, "percentage", "Vipul")
bad_calc.calculate_discount(500, "flat", "Kaarthik")
bad_calc.calculate_discount(500, "loyalty", "Ajit")


# ============================================================
# --- GOOD: Strategy Pattern — open for extension, closed for modification ---
# ============================================================
# To add a new discount, just create a NEW class. No existing code changes!

print("\n\n--- GOOD: Strategy Pattern (add new discounts without changing existing code) ---\n")

from abc import ABC, abstractmethod


class DiscountStrategy(ABC):
    """Abstract base — defines the contract for all discount strategies."""

    @abstractmethod
    def calculate(self, order_total: float) -> float:
        """Return the discount amount."""
        pass

    @abstractmethod
    def description(self) -> str:
        pass


class PercentageDiscount(DiscountStrategy):
    def __init__(self, percent: float):
        self.percent = percent

    def calculate(self, order_total: float) -> float:
        return order_total * (self.percent / 100)

    def description(self) -> str:
        return f"{self.percent}% off"


class FlatDiscount(DiscountStrategy):
    def __init__(self, amount: float):
        self.amount = amount

    def calculate(self, order_total: float) -> float:
        return min(self.amount, order_total)  # Can't discount more than total

    def description(self) -> str:
        return f"Flat Rs.{self.amount} off"


class LoyaltyDiscount(DiscountStrategy):
    """15% off for loyal customers who've ordered 10+ times."""

    def calculate(self, order_total: float) -> float:
        return order_total * 0.15

    def description(self) -> str:
        return "15% loyalty reward"


class DiscountCalculatorGood:
    """This class is CLOSED for modification — we never need to touch it again.
    New discount types are added by creating new Strategy classes."""

    def apply_discount(self, order_total: float, strategy: DiscountStrategy, customer_name: str) -> float:
        discount = strategy.calculate(order_total)
        final = order_total - discount
        print(f"  {customer_name}: Rs.{order_total} - Rs.{discount:.0f} ({strategy.description()}) = Rs.{final:.0f}")
        return final


# Using the good version
calc = DiscountCalculatorGood()
calc.apply_discount(500, PercentageDiscount(10), "Vipul")
calc.apply_discount(500, FlatDiscount(50), "Kaarthik")
calc.apply_discount(500, LoyaltyDiscount(), "Ajit")


# ============================================================
# NOW: Adding a new discount type WITHOUT changing any existing code!
# ============================================================

print("\n--- Adding NEW discount types (no existing code modified!) ---\n")


class FestivalDiscount(DiscountStrategy):
    """Diwali special: 25% off, max Rs.200."""

    def calculate(self, order_total: float) -> float:
        discount = order_total * 0.25
        return min(discount, 200)  # Cap at Rs.200

    def description(self) -> str:
        return "Diwali Special (25% off, max Rs.200)"


class StudentDiscount(DiscountStrategy):
    """Students get 20% off on orders above Rs.300."""

    def __init__(self, student_id: str):
        self.student_id = student_id

    def calculate(self, order_total: float) -> float:
        if order_total >= 300:
            return order_total * 0.20
        return 0

    def description(self) -> str:
        return f"Student discount (20% off, min order Rs.300)"


# We added two new discount types and NEVER touched DiscountCalculatorGood!
calc.apply_discount(800, FestivalDiscount(), "Vipul")
calc.apply_discount(500, StudentDiscount("STU-2024-001"), "Kaarthik")
calc.apply_discount(200, StudentDiscount("STU-2024-002"), "Ajit")  # Below minimum


# ============================================================
# WHY THIS MATTERS:
# ============================================================
print("\n" + "=" * 60)
print("WHY OCP MATTERS:")
print("-" * 60)
print("- BAD version: Adding 'FestivalDiscount' means editing DiscountCalculatorBad")
print("  -> Risk breaking existing percentage/flat/loyalty logic")
print("  -> Must re-test ALL discount types")
print("")
print("- GOOD version: Adding 'FestivalDiscount' means creating a NEW file/class")
print("  -> Existing code untouched, existing tests still pass")
print("  -> Only need to test the NEW discount class")
print("  -> Can even be done by a different developer!")
print("=" * 60)
