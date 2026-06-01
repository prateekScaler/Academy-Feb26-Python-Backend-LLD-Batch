"""
LLD-18 · Adapter + Factory · Example 9 — Two patterns composed.

Run:  python3 09_adapter_with_factory.py

Real production code rarely uses a pattern in isolation. The canonical
"Adapter playing with Factory" arrangement:

   - Factory hides WHICH concrete object to make.
   - Adapter hides HOW one of those objects' weird SDK fits in.

The caller sees one uniform `PaymentGateway`. It has no idea that
"stripe" returns a native implementation while "razorpay" returns a
class that's actually wrapping a vendor SDK with a totally different
shape. That's the point — the architecture is plug-and-play, and
swapping or adding a vendor touches exactly one file (the adapter).

Bonus: this file also demonstrates the production convention of
translating vendor exceptions into your own at the adapter boundary —
so the rest of the codebase only catches your exception types,
never the vendor's.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass


# ====================================================================
# 1.  Our domain types + exception hierarchy
#     (callers ONLY ever import these — never the vendor exceptions)
# ====================================================================
@dataclass(frozen=True)
class PaymentResult:
    success: bool
    txn_id: str
    raw_response: dict


class PaymentError(Exception):
    """Base for every payment failure we surface to the caller."""


class AuthFailed(PaymentError):
    """Bad API key, signature mismatch, etc."""


class InsufficientFunds(PaymentError):
    """Card declined, balance too low, etc."""


class PaymentNetworkError(PaymentError):
    """Vendor unreachable, timeout, etc."""


# ====================================================================
# 2.  Target interface
# ====================================================================
class PaymentGateway(ABC):
    @abstractmethod
    def pay(self, amount: float, currency: str) -> PaymentResult: ...


# ====================================================================
# 3a.  Native implementation — no adapter, no SDK
# ====================================================================
class StripeGateway(PaymentGateway):
    """Pretend we wrote this in-house; it implements PaymentGateway directly."""

    def pay(self, amount: float, currency: str) -> PaymentResult:
        if amount <= 0:
            raise InsufficientFunds(f"amount={amount}")
        return PaymentResult(
            success=True,
            txn_id=f"stripe_{int(amount * 100)}",
            raw_response={"provider": "stripe", "amount": amount, "currency": currency},
        )


# ====================================================================
# 3b.  Vendor SDK we DON'T control (pretend it's pip-installed)
# ====================================================================
class _RazorpaySDKError(Exception):
    """Pretend this is razorpay.errors.RazorpayError"""


class _RazorpaySignatureError(_RazorpaySDKError):
    """Pretend this is razorpay.errors.SignatureVerificationError"""


class _RazorpayBadRequest(_RazorpaySDKError):
    """Pretend this is razorpay.errors.BadRequestError"""


class RazorpayClient:
    """Pretend SDK with the 'wrong' interface."""

    def __init__(self, api_key: str, api_secret: str) -> None:
        self.api_key = api_key
        self.api_secret = api_secret
        self._counter = 0

    def create_order(self, amount_in_paise: int, receipt_id: str) -> dict:
        if not self.api_key.startswith("key_"):
            raise _RazorpaySignatureError("invalid api key prefix")
        if amount_in_paise <= 0:
            raise _RazorpayBadRequest(f"amount_in_paise={amount_in_paise}")
        self._counter += 1
        return {"id": f"order_{self._counter:06d}", "amount": amount_in_paise, "receipt": receipt_id}

    def capture_payment(self, order_id: str) -> dict:
        return {"id": f"pay_{order_id}", "order_id": order_id, "status": "captured"}


# ====================================================================
# 3c.  ADAPTER — wraps the vendor SDK behind PaymentGateway,
#      and translates exceptions to our hierarchy.
# ====================================================================
class RazorpayAdapter(PaymentGateway):
    def __init__(self, api_key: str, api_secret: str) -> None:
        self._client = RazorpayClient(api_key, api_secret)
        self._receipt_counter = 0

    def pay(self, amount: float, currency: str) -> PaymentResult:
        if currency != "INR":
            raise PaymentError(f"Razorpay only supports INR, got {currency}")

        amount_in_paise = int(round(amount * 100))
        self._receipt_counter += 1
        receipt = f"rcpt_{self._receipt_counter:04d}"

        try:
            order = self._client.create_order(amount_in_paise, receipt)
            result = self._client.capture_payment(order["id"])
        except _RazorpaySignatureError as e:
            raise AuthFailed(str(e)) from e             # vendor → ours
        except _RazorpayBadRequest as e:
            raise InsufficientFunds(str(e)) from e
        except _RazorpaySDKError as e:
            raise PaymentNetworkError(str(e)) from e

        return PaymentResult(
            success=result["status"] == "captured",
            txn_id=result["id"],
            raw_response={"order": order, "payment": result},
        )


# ====================================================================
# 4.  FACTORY — hides which concrete one to hand out
# ====================================================================
class PaymentGatewayFactory:
    """Caller picks by name; factory decides native vs adapter."""

    @staticmethod
    def create(kind: str) -> PaymentGateway:
        if kind == "stripe":
            return StripeGateway()                       # native impl
        if kind == "razorpay":
            return RazorpayAdapter("key_xxx", "sec_xxx") # SDK behind adapter
        raise ValueError(f"unknown payment provider: {kind}")


# ====================================================================
# 5.  Client code — Adapter and Factory are both invisible
# ====================================================================
def checkout(provider: str, amount: float, currency: str) -> None:
    gateway = PaymentGatewayFactory.create(provider)    # ← Factory
    try:
        result = gateway.pay(amount, currency)          # ← maybe Adapter
        print(f"  ✓ [{provider:>8}] txn_id={result.txn_id}")
    except AuthFailed as e:
        print(f"  ✗ [{provider:>8}] auth failed: {e}")
    except InsufficientFunds as e:
        print(f"  ✗ [{provider:>8}] insufficient funds: {e}")
    except PaymentError as e:
        print(f"  ✗ [{provider:>8}] payment error: {e}")


if __name__ == "__main__":
    print("--- Happy path: both providers look identical to the caller ---")
    checkout("stripe",   59.99,  "USD")
    checkout("razorpay", 499.00, "INR")

    print("\n--- Adapter-translated exceptions: caller only catches OUR types ---")
    checkout("razorpay", -100, "INR")   # underlying vendor raises BadRequest → InsufficientFunds
    checkout("razorpay", 100,  "USD")   # adapter rejects upfront

    print("\nNote: the caller has zero `import razorpay` anywhere.")
    print("Adapter contains the SDK; Factory selects the gateway; Caller stays clean.")
