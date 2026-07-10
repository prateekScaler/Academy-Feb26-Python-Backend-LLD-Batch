"""
01 — Why mock: the awkward dependency
=====================================

Some collaborators can't be called in a unit test:
  * SLOW    — an HTTPS round-trip to a payment gateway (~800ms)
  * PAID    — real money actually moves
  * FLAKY   — the network fails 1% of the time
  * NON-DETERMINISTIC — an LLM, or the clock, or randomness

The cure is a TEST DOUBLE: a stand-in that behaves how the test needs.
The cleanest way to slot one in is the move you already know from
LLD-31's Clock — DEPENDENCY INJECTION: pass the collaborator in, so a
test can pass a fake instead of the real thing.

Needs:  pip install pytest
"""

import pytest


class PaymentError(Exception):
    pass


class StripeGateway:
    """The real thing — DO NOT call this in a test."""
    def charge(self, amount_paise: int, token: str) -> str:
        raise RuntimeError("this would hit the real network and move real money")


class Checkout:
    def __init__(self, gateway):          # <- dependency injection: the seam
        self.gateway = gateway

    def pay(self, amount_paise: int, token: str) -> dict:
        receipt = self.gateway.charge(amount_paise, token)
        return {"status": "PAID", "receipt": receipt}


class FakeGateway:
    """A hand-written double: behaves like a gateway, records what it saw."""
    def __init__(self, receipt: str = "rcpt_1"):
        self.receipt = receipt
        self.charges: list[tuple[int, str]] = []

    def charge(self, amount_paise: int, token: str) -> str:
        self.charges.append((amount_paise, token))
        return self.receipt


def test_pay_returns_a_receipt_from_the_gateway():
    checkout = Checkout(FakeGateway(receipt="rcpt_42"))     # inject the double
    assert checkout.pay(500_00, "tok_visa") == {"status": "PAID", "receipt": "rcpt_42"}


def test_pay_forwards_the_exact_amount_and_token():
    fake = FakeGateway()
    Checkout(fake).pay(500_00, "tok_visa")
    assert fake.charges == [(500_00, "tok_visa")]           # the fake also spies


if __name__ == "__main__":
    try:
        import pytest as _pt
    except ImportError:
        raise SystemExit("This is a pytest test file. Install pytest first:  pip install pytest")
    raise SystemExit(_pt.main([__file__, "-v", "-p", "no:cacheprovider"]))
