"""Custom exceptions — build your own exception hierarchy."""


# --- Why custom exceptions? ---
# Generic exceptions tell you WHAT went wrong, not WHY.
# Custom exceptions encode business logic.

# BAD:
# raise ValueError("Insufficient stock")  ← can't programmatically distinguish
# raise ValueError("Invalid email")       ← from this one

# GOOD:
# raise InsufficientStockError(available=5, requested=10)
# raise InvalidEmailError("missing @")


# --- Step 1: Basic custom exception ---
class PaymentError(Exception):
    """Base exception for all payment-related errors."""
    pass


class InsufficientFundsError(PaymentError):
    def __init__(self, balance: float, amount: float):
        self.balance = balance
        self.amount = amount
        self.deficit = amount - balance
        super().__init__(
            f"Cannot pay ₹{amount}: only ₹{balance} available (short by ₹{self.deficit})"
        )


class PaymentGatewayError(PaymentError):
    def __init__(self, gateway: str, status_code: int):
        self.gateway = gateway
        self.status_code = status_code
        super().__init__(f"{gateway} returned status {status_code}")


class CardExpiredError(PaymentError):
    pass


# --- Step 2: Use them ---
def process_payment(amount: float, balance: float) -> str:
    if balance < amount:
        raise InsufficientFundsError(balance, amount)
    return f"Paid ₹{amount}. Remaining: ₹{balance - amount}"


# Catch specific exception
try:
    result = process_payment(1000, 500)
except InsufficientFundsError as e:
    print(f"Payment failed: {e}")
    print(f"  Balance: ₹{e.balance}")
    print(f"  Requested: ₹{e.amount}")
    print(f"  Short by: ₹{e.deficit}")


# --- Step 3: Catch parent = catches all children ---
print("\nCatching parent PaymentError:")
for error in [InsufficientFundsError(500, 1000), PaymentGatewayError("Razorpay", 502), CardExpiredError()]:
    try:
        raise error
    except PaymentError as e:
        print(f"  {type(e).__name__}: {e}")


# --- Step 4: Exception hierarchy pattern ---
# AppError (base)
# ├── AuthError
# │   ├── InvalidCredentialsError
# │   └── TokenExpiredError
# ├── PaymentError
# │   ├── InsufficientFundsError
# │   └── PaymentGatewayError
# └── ValidationError
#     ├── InvalidEmailError
#     └── InvalidPhoneError

print("\n--- Best practices ---")
print("  1. Inherit from Exception (or a custom base), never BaseException")
print("  2. Create a base error for your app/module (AppError, PaymentError)")
print("  3. Store useful data as attributes (balance, amount, deficit)")
print("  4. super().__init__(message) for readable str(error)")
print("  5. Catch specific exceptions, not generic Exception")
print("  6. Use hierarchy: except PaymentError catches all payment errors")
