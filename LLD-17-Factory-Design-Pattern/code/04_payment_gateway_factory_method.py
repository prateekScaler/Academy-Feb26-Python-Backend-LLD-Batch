"""
04 - Payment Gateway Factory Method (a second example)
======================================================

Same pattern as 02_factory_method.py, applied to a domain you'll
likely build for real: switching between payment providers without
modifying business code.

Pattern:
  - PaymentGateway: abstract product
  - StripeGateway, PayPalGateway, RazorpayGateway: concrete products
  - PaymentService: abstract creator with create_gateway() factory method
  - StripeService / PayPalService / RazorpayService: concrete creators

Adding Square later? Just a new pair of classes - existing services unchanged.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass


# ---------------------------------------------------------------------------
# Products
# ---------------------------------------------------------------------------

class PaymentGateway(ABC):
    @abstractmethod
    def charge(self, amount_cents: int) -> dict: ...

    @abstractmethod
    def refund(self, txn_id: str) -> dict: ...


class StripeGateway(PaymentGateway):
    def __init__(self, api_key: str):
        self.api_key = api_key

    def charge(self, amount_cents):
        return {"provider": "stripe", "amount": amount_cents, "status": "captured"}

    def refund(self, txn_id):
        return {"provider": "stripe", "txn": txn_id, "status": "refunded"}


class PayPalGateway(PaymentGateway):
    def __init__(self, client_id: str, secret: str):
        self.client_id = client_id
        self.secret = secret

    def charge(self, amount_cents):
        return {"provider": "paypal", "amount": amount_cents, "status": "captured"}

    def refund(self, txn_id):
        return {"provider": "paypal", "txn": txn_id, "status": "refunded"}


class RazorpayGateway(PaymentGateway):
    def __init__(self, key_id: str, key_secret: str):
        self.key_id = key_id
        self.key_secret = key_secret

    def charge(self, amount_cents):
        return {"provider": "razorpay", "amount": amount_cents, "status": "captured"}

    def refund(self, txn_id):
        return {"provider": "razorpay", "txn": txn_id, "status": "refunded"}


# ---------------------------------------------------------------------------
# Creators
# ---------------------------------------------------------------------------

class PaymentService(ABC):
    """Abstract creator. Has a template method (process_order) that uses
    the factory method (create_gateway) internally."""

    @abstractmethod
    def create_gateway(self) -> PaymentGateway: ...

    def process_order(self, order_id: str, amount_cents: int) -> dict:
        gateway = self.create_gateway()
        result = gateway.charge(amount_cents)
        print(f"[order {order_id}] {result}")
        return result


class StripeService(PaymentService):
    def __init__(self, api_key: str):
        self.api_key = api_key

    def create_gateway(self):
        return StripeGateway(api_key=self.api_key)


class PayPalService(PaymentService):
    def __init__(self, client_id: str, secret: str):
        self.client_id, self.secret = client_id, secret

    def create_gateway(self):
        return PayPalGateway(client_id=self.client_id, secret=self.secret)


class RazorpayService(PaymentService):
    def __init__(self, key_id: str, key_secret: str):
        self.key_id, self.key_secret = key_id, key_secret

    def create_gateway(self):
        return RazorpayGateway(key_id=self.key_id, key_secret=self.key_secret)


# ---------------------------------------------------------------------------
# Demo - same orders, three different gateways, zero business-code changes
# ---------------------------------------------------------------------------

def demo():
    services = [
        StripeService(api_key="sk_test_xxx"),
        PayPalService(client_id="paypal_id", secret="paypal_secret"),
        RazorpayService(key_id="rzp_key", key_secret="rzp_secret"),
    ]

    for svc in services:
        svc.process_order(order_id="ord-001", amount_cents=9_99)

    # Adding a new gateway (e.g. SquareService) would be a new class -
    # the demo above doesn't need to change.


if __name__ == "__main__":
    demo()
