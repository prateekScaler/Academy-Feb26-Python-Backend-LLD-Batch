"""
LLD-18 · Adapter · Example 6 — Payment Gateway Adapter (UML-friendly).

Run:  python3 06_payment_gateway_adapter.py

This is the real-world scenario from the class notes: our checkout system
expects every gateway to expose `pay(amount, currency)`. We need to plug
in Razorpay, whose SDK exposes `create_order(...)` + `capture_payment(...)`
with amounts in paise (rupees × 100).

The Adapter does three jobs in one class:
   1. Renames methods                    (create_order/capture_payment → pay)
   2. Converts units                     (rupees → paise)
   3. Translates return shapes           (raw dict → PaymentResult)

The class hierarchy is deliberately designed to render cleanly in PyCharm's
UML class-diagram view:

   PaymentGateway (ABC)
        △
        |  (implements)
        |
   ┌────┴──────────┬───────────────┐
   │               │               │
StripeGateway   PayPalGateway  RazorpayAdapter ─── ◇ ─── RazorpayClient
                                                  (adapts/wraps)
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass


# ====================================================================
# 1.  Shared domain types
# ====================================================================
@dataclass(frozen=True)
class PaymentResult:
    success: bool
    txn_id: str
    raw_response: dict


# ====================================================================
# 2.  Target — the interface our checkout system uses
# ====================================================================
class PaymentGateway(ABC):
    @abstractmethod
    def pay(self, amount: float, currency: str) -> PaymentResult: ...


# ====================================================================
# 3.  In-house implementations (no adapter needed)
# ====================================================================
class StripeGateway(PaymentGateway):
    def pay(self, amount: float, currency: str) -> PaymentResult:
        return PaymentResult(
            success=True,
            txn_id=f"stripe_{int(amount * 100)}",
            raw_response={"provider": "stripe", "amount": amount, "currency": currency},
        )


class PayPalGateway(PaymentGateway):
    def pay(self, amount: float, currency: str) -> PaymentResult:
        return PaymentResult(
            success=True,
            txn_id=f"paypal_{int(amount * 100)}",
            raw_response={"provider": "paypal", "amount": amount, "currency": currency},
        )


# ====================================================================
# 4.  Adaptee — the third-party Razorpay SDK we can't change
# ====================================================================
class RazorpayClient:
    """Pretend this came from `pip install razorpay`."""

    def __init__(self, api_key: str, api_secret: str) -> None:
        self.api_key = api_key
        self.api_secret = api_secret
        self._order_counter = 0

    def create_order(self, amount_in_paise: int, receipt_id: str) -> dict:
        self._order_counter += 1
        return {
            "id": f"order_{self._order_counter:06d}",
            "amount": amount_in_paise,
            "receipt": receipt_id,
            "status": "created",
        }

    def capture_payment(self, order_id: str) -> dict:
        return {
            "id": f"pay_{order_id}",
            "order_id": order_id,
            "status": "captured",
        }


# ====================================================================
# 5.  The Adapter
# ====================================================================
class RazorpayAdapter(PaymentGateway):
    """Speaks PaymentGateway outward, RazorpayClient inward."""

    def __init__(self, api_key: str, api_secret: str) -> None:
        # COMPOSITION — the adapter HOLDS a RazorpayClient
        self._client = RazorpayClient(api_key, api_secret)
        self._receipt_counter = 0

    def pay(self, amount: float, currency: str) -> PaymentResult:
        # 1. Unit conversion: rupees → paise
        if currency != "INR":
            raise ValueError("Razorpay only supports INR")
        amount_in_paise = int(round(amount * 100))

        # 2. Method renaming: pay() → create_order() + capture_payment()
        self._receipt_counter += 1
        receipt_id = f"rcpt_{self._receipt_counter:04d}"
        order = self._client.create_order(amount_in_paise, receipt_id)
        result = self._client.capture_payment(order["id"])

        # 3. Return-shape translation: dict → PaymentResult
        return PaymentResult(
            success=result["status"] == "captured",
            txn_id=result["id"],
            raw_response={"order": order, "payment": result},
        )


# ====================================================================
# 6.  Client code — knows ONLY about PaymentGateway
# ====================================================================
def checkout(gateway: PaymentGateway, amount: float, currency: str) -> None:
    result = gateway.pay(amount, currency)
    status = "✓" if result.success else "✗"
    print(f"  [{status}] {gateway.__class__.__name__:>20} → txn_id={result.txn_id}")


if __name__ == "__main__":
    gateways: list[tuple[PaymentGateway, float, str]] = [
        (StripeGateway(),                         59.99,  "USD"),
        (PayPalGateway(),                         29.50,  "USD"),
        (RazorpayAdapter("key_xxx", "sec_xxx"),  499.00,  "INR"),
        (RazorpayAdapter("key_xxx", "sec_xxx"), 1499.50,  "INR"),
    ]

    print("Checkout — all three gateways look identical to the caller:\n")
    for gw, amt, ccy in gateways:
        checkout(gw, amt, ccy)
