"""
LLD-18 · Adapter · Example 12 — Refactoring the restaurant_project payments
                                view with an Adapter.

Run:  python3 12_django_payments_adapter_refactor.py

This is the lesson the comment in restaurant_project/payments/views.py
promised: "in a later session we'll create a PaymentGateway interface."

This is the later session. The original `views.py` (excerpted in the
class HTML) has three concrete smells:

  1.  razorpay.Client(...) is created at MODULE IMPORT TIME — global state.
  2.  Razorpay-shaped dicts (amount in paise, "payment_link", "notify")
      bleed straight into the view function.
  3.  Razorpay's name appears in MODEL FIELD NAMES (razorpay_payment_link_id)
      and in URLS / handler names (razorpay_webhook, "payment_link.paid").

The refactor below is a runnable, framework-free distillation. The same
shape drops into Django: split `gateways/base.py`, `gateways/razorpay_adapter.py`,
`gateways/stripe_adapter.py`, and a `get_gateway()` factory that reads
`settings.PAYMENT_GATEWAY`.

What this file demonstrates (you can `python3` it):
  - The in-house interface (`PaymentGateway`) — no vendor mention.
  - Two concrete adapters (`RazorpayGateway`, `StripeGateway`) — each
    quarantines its vendor's vocabulary.
  - A factory (`get_gateway`) selects by config string — like
    `settings.PAYMENT_GATEWAY = "razorpay"`.
  - A view-equivalent function (`create_payment_link_view`) that's now
    provider-agnostic — exactly what Django's view should look like
    after the refactor.
  - A FakeGateway used in `test_checkout_flow` — proves the refactor
    makes the checkout unit-testable with no network and no mocks of
    `razorpay.Client`.
"""

from __future__ import annotations

import json
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any


# =====================================================================
# In-house domain types — the rest of the app imports ONLY these.
# Notice: zero vendor names.
# =====================================================================
@dataclass(frozen=True)
class PaymentLink:
    provider_link_id: str          # was: razorpay_payment_link_id
    short_url: str
    amount_paise: int


@dataclass(frozen=True)
class WebhookEvent:
    """Normalised event the rest of the app actually reasons about."""
    kind: str                      # "payment.succeeded" | "payment.failed"
    provider_payment_id: str
    provider_link_id: str
    raw: dict


class PaymentError(Exception):
    pass


# =====================================================================
# Target interface — what the application code knows about.
# =====================================================================
class PaymentGateway(ABC):
    @abstractmethod
    def create_payment_link(
        self,
        *,
        amount_paise: int,
        order_id: str,
        customer_name: str,
        customer_email: str,
        customer_phone: str,
        description: str,
        callback_url: str,
    ) -> PaymentLink: ...

    @abstractmethod
    def verify_webhook(self, payload: bytes, signature: str) -> bool: ...

    @abstractmethod
    def parse_webhook_event(self, payload: bytes) -> WebhookEvent: ...


# =====================================================================
# Adapter 1 — Razorpay (the original vendor, now quarantined)
# =====================================================================
# Simulating the real `import razorpay`. In production you'd
#     import razorpay
# Here we use a stub so the file is runnable.
class _RazorpayClientStub:
    """Pretend this is the official `razorpay.Client`."""
    class _PaymentLinkAPI:
        _counter = 0
        def create(self, payload: dict) -> dict:
            type(self)._counter += 1
            return {"id": f"plink_{type(self)._counter:06d}", "short_url": "https://rzp.io/i/abc"}

    class _Utility:
        def verify_webhook_signature(self, payload: str, sig: str, secret: str) -> None:
            if sig != "good-signature":
                raise ValueError("Signature mismatch")

    def __init__(self, auth: tuple):
        self.api_key, self.api_secret = auth
        self.payment_link = self._PaymentLinkAPI()
        self.utility = self._Utility()


class RazorpayGateway(PaymentGateway):
    """All Razorpay-isms live inside this file. The rest of the app
       never sees the word 'razorpay' again."""

    def __init__(self, key_id: str, key_secret: str, webhook_secret: str) -> None:
        self._client = _RazorpayClientStub(auth=(key_id, key_secret))   # in prod: razorpay.Client(...)
        self._webhook_secret = webhook_secret

    def create_payment_link(
        self,
        *,
        amount_paise: int,
        order_id: str,
        customer_name: str,
        customer_email: str,
        customer_phone: str,
        description: str,
        callback_url: str,
    ) -> PaymentLink:
        # Translate OUR kwargs into Razorpay's nested dict.
        link = self._client.payment_link.create({
            "amount": amount_paise,
            "currency": "INR",
            "description": description,
            "customer": {
                "name": customer_name,
                "email": customer_email,
                "contact": customer_phone,
            },
            "notify": {"sms": True, "email": True},
            "notes": {"order_id": order_id},
            "callback_url": callback_url,
            "callback_method": "get",
        })
        # Translate Razorpay's response back into OUR PaymentLink.
        return PaymentLink(
            provider_link_id=link["id"],
            short_url=link["short_url"],
            amount_paise=amount_paise,
        )

    def verify_webhook(self, payload: bytes, signature: str) -> bool:
        try:
            self._client.utility.verify_webhook_signature(
                payload.decode("utf-8"), signature, self._webhook_secret
            )
            return True
        except ValueError:
            return False

    def parse_webhook_event(self, payload: bytes) -> WebhookEvent:
        event = json.loads(payload)
        kind_map = {"payment_link.paid": "payment.succeeded",
                    "payment.failed":     "payment.failed"}
        kind = kind_map.get(event["event"], "unknown")
        link  = event["payload"]["payment_link"]["entity"]
        pay   = event["payload"]["payment"]["entity"]
        return WebhookEvent(
            kind=kind,
            provider_payment_id=pay["id"],
            provider_link_id=link["id"],
            raw=event,
        )


# =====================================================================
# Adapter 2 — Stripe (proves the abstraction earns its keep)
# =====================================================================
class _StripeStub:
    """Pretend this is `stripe`. Different SDK style — note the differences
       from Razorpay's payload shape, which is exactly the point."""
    class PaymentLink:
        _counter = 0
        @classmethod
        def create(cls, **params) -> dict:
            cls._counter += 1
            return {"id": f"plink_str_{cls._counter:06d}",
                    "url": "https://buy.stripe.com/xyz"}


class StripeGateway(PaymentGateway):
    def __init__(self, api_key: str, webhook_secret: str) -> None:
        self._stripe = _StripeStub                         # in prod: import stripe
        self._stripe.api_key = api_key                     # set module-level token
        self._webhook_secret = webhook_secret

    def create_payment_link(
        self,
        *,
        amount_paise: int,
        order_id: str,
        customer_name: str,
        customer_email: str,
        customer_phone: str,
        description: str,
        callback_url: str,
    ) -> PaymentLink:
        # Stripe uses kwargs, not a nested dict. Different shape, same intent.
        link = self._stripe.PaymentLink.create(
            line_items=[{"price_data": {"currency": "inr", "unit_amount": amount_paise,
                                        "product_data": {"name": description}},
                         "quantity": 1}],
            metadata={"order_id": order_id, "customer_email": customer_email},
            after_completion={"type": "redirect",
                              "redirect": {"url": callback_url}},
        )
        return PaymentLink(
            provider_link_id=link["id"],
            short_url=link["url"],          # Stripe calls it `url`, Razorpay `short_url`
            amount_paise=amount_paise,
        )

    def verify_webhook(self, payload: bytes, signature: str) -> bool:
        return signature == "good-signature"

    def parse_webhook_event(self, payload: bytes) -> WebhookEvent:
        event = json.loads(payload)
        return WebhookEvent(
            kind="payment.succeeded" if event["type"] == "checkout.session.completed"
                 else "payment.failed",
            provider_payment_id=event["data"]["object"]["payment_intent"],
            provider_link_id=event["data"]["object"]["payment_link"],
            raw=event,
        )


# =====================================================================
# The factory — replaces the module-level razorpay.Client(...) of the old code.
# Reads config, picks the right adapter, returns a PaymentGateway.
# =====================================================================
def get_gateway(settings: dict) -> PaymentGateway:
    name = settings["PAYMENT_GATEWAY"]
    if name == "razorpay":
        return RazorpayGateway(settings["RAZORPAY_KEY_ID"],
                               settings["RAZORPAY_KEY_SECRET"],
                               settings["RAZORPAY_WEBHOOK_SECRET"])
    if name == "stripe":
        return StripeGateway(settings["STRIPE_API_KEY"],
                             settings["STRIPE_WEBHOOK_SECRET"])
    raise ValueError(f"unknown gateway: {name}")


# =====================================================================
# View-equivalent — what the post-refactor Django view looks like.
# Notice there's no `razorpay` (or `stripe`) anywhere here.
# =====================================================================
def create_payment_link_view(settings: dict, order: dict) -> dict:
    gateway = get_gateway(settings)
    link = gateway.create_payment_link(
        amount_paise=int(order["total_rupees"] * 100),
        order_id=order["id"],
        customer_name=order["customer_name"],
        customer_email=order["customer_email"],
        customer_phone=order["customer_phone"],
        description=f"Payment for Order #{order['id']}",
        callback_url=settings["BASE_URL"] + "/payments/callback/",
    )
    # The model field is named provider_link_id, NOT razorpay_payment_link_id.
    # Switching providers tomorrow doesn't require a DB migration.
    return {
        "provider_link_id": link.provider_link_id,
        "short_url": link.short_url,
        "amount_paise": link.amount_paise,
    }


def payment_webhook_view(settings: dict, payload: bytes, signature: str) -> str:
    gateway = get_gateway(settings)
    if not gateway.verify_webhook(payload, signature):
        return "401 Invalid signature"
    event = gateway.parse_webhook_event(payload)
    if event.kind == "payment.succeeded":
        return f"Marked payment {event.provider_payment_id} as PAID"
    if event.kind == "payment.failed":
        return f"Marked payment {event.provider_payment_id} as FAILED"
    return "200 ignored"


# =====================================================================
# Test — the whole point of the refactor.
# Notice this is a UNIT test: no Django, no network, no mock of razorpay.Client.
# We swap the entire gateway with a FakeGateway in 3 lines.
# =====================================================================
class FakeGateway(PaymentGateway):
    def __init__(self) -> None:
        self.created_links: list[dict] = []

    def create_payment_link(self, **kwargs) -> PaymentLink:
        self.created_links.append(kwargs)
        return PaymentLink(provider_link_id="fake_001",
                           short_url="https://fake/abc",
                           amount_paise=kwargs["amount_paise"])

    def verify_webhook(self, payload: bytes, signature: str) -> bool:
        return signature == "good-signature"

    def parse_webhook_event(self, payload: bytes) -> WebhookEvent:
        return WebhookEvent(kind="payment.succeeded", provider_payment_id="pay_001",
                            provider_link_id="fake_001", raw={})


def test_checkout_flow() -> None:
    """A real unit test — would pass with no network in any CI."""
    fake = FakeGateway()
    settings = {"PAYMENT_GATEWAY": "fake", "BASE_URL": "http://localhost"}

    # Monkey-patching the factory is the seam that makes the whole flow testable.
    # In Django you'd dependency-inject the gateway into the view instead.
    import sys; this = sys.modules[__name__]
    this.get_gateway = lambda s: fake

    order = {"id": "ORD-42", "total_rupees": 499.0,
             "customer_name": "Test User", "customer_email": "t@example.com",
             "customer_phone": "9999999999"}
    response = create_payment_link_view(settings, order)

    assert response["provider_link_id"] == "fake_001"
    assert fake.created_links[0]["amount_paise"] == 49900
    assert fake.created_links[0]["order_id"] == "ORD-42"
    print("test_checkout_flow ✓  (no Razorpay, no Stripe, no network)")


# =====================================================================
# Demo
# =====================================================================
def demo() -> None:
    order = {"id": "ORD-1234", "total_rupees": 499.0,
             "customer_name": "Ada Lovelace", "customer_email": "ada@scaler.com",
             "customer_phone": "9999999999"}

    print("--- Settings: PAYMENT_GATEWAY = razorpay ---")
    settings = {"PAYMENT_GATEWAY": "razorpay",
                "RAZORPAY_KEY_ID": "key_xxx",
                "RAZORPAY_KEY_SECRET": "sec_xxx",
                "RAZORPAY_WEBHOOK_SECRET": "wh_xxx",
                "BASE_URL": "https://restaurant.com"}
    print(" ", create_payment_link_view(settings, order))

    print("\n--- Settings: PAYMENT_GATEWAY = stripe   (one line of config changed) ---")
    settings = {"PAYMENT_GATEWAY": "stripe",
                "STRIPE_API_KEY": "sk_test_xxx",
                "STRIPE_WEBHOOK_SECRET": "whsec_xxx",
                "BASE_URL": "https://restaurant.com"}
    print(" ", create_payment_link_view(settings, order))

    print("\n--- The unit test the original code couldn't have written ---")


if __name__ == "__main__":
    demo()
    test_checkout_flow()
