"""
04 - Abstraction: Show WHAT, Hide HOW
=======================================
Abstraction means exposing a simple interface
and hiding the complex implementation details.
"""


# =============================================
# Example 1: sorted() is an abstraction
# =============================================

print("=== sorted() — you don't know the algorithm ===")
numbers = [64, 25, 12, 22, 11]
result = sorted(numbers)
print(f"Input:  {numbers}")
print(f"Output: {result}")
print("You didn't specify quicksort, mergesort, or timsort.")
print("Python chose for you. That's abstraction.\n")


# =============================================
# Example 2: A simple payment gateway abstraction
# =============================================

print("=== Payment Gateway — caller doesn't know the details ===\n")


class PaymentGateway:
    """
    The caller only knows: call charge(amount) and get a result.
    They don't know about API keys, HTTP calls, retries, webhooks.
    """

    def __init__(self, gateway_name):
        self.__gateway_name = gateway_name
        self.__api_key = "sk_secret_12345"  # Hidden detail

    def charge(self, amount, currency="INR"):
        """Simple interface — WHAT you can do."""
        # Complex implementation hidden inside — HOW it works
        self.__validate_amount(amount)
        self.__connect_to_api()
        transaction_id = self.__send_charge_request(amount, currency)
        self.__log_transaction(transaction_id, amount)
        return transaction_id

    # All these are hidden implementation details
    def __validate_amount(self, amount):
        if amount <= 0:
            raise ValueError("Amount must be positive")
        print(f"  [internal] Validating amount: {amount}")

    def __connect_to_api(self):
        print(f"  [internal] Connecting to {self.__gateway_name} API...")

    def __send_charge_request(self, amount, currency):
        print(f"  [internal] Sending charge: {currency} {amount}")
        return "txn_abc123"

    def __log_transaction(self, txn_id, amount):
        print(f"  [internal] Logged: {txn_id} for {amount}")


# The CALLER sees only this — simple and clean:
gateway = PaymentGateway("Razorpay")
txn = gateway.charge(500)
print(f"\nTransaction ID: {txn}")
print("\nThe caller wrote ONE line: gateway.charge(500)")
print("But 4 complex steps happened behind the scenes.")
print("That's abstraction — simple outside, complex inside.")


# =============================================
# Example 3: Real-world — you abstract every day
# =============================================

print("\n=== Abstractions you already use ===")
examples = [
    ("print('hello')", "You don't manage stdout buffers, encoding, or terminal control codes"),
    ("requests.get(url)", "You don't manage TCP sockets, DNS resolution, TLS handshakes"),
    ("MenuItem.objects.all()", "You don't write SQL, manage connections, or parse result sets"),
    ("car.accelerate()", "You don't manage fuel injection, spark timing, or torque distribution"),
]

for api, hidden in examples:
    print(f"  {api}")
    print(f"    Hidden: {hidden}\n")
