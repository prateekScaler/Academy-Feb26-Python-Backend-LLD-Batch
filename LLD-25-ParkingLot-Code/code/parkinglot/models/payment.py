"""Payment — the second record (FR-9): one per ticket. Frozen, because money
doesn't mutate — a payment is an immutable fact once it happens. `method` is a
field, not a subclass hierarchy: cash/card/UPI don't *behave* differently in our
scope, so they're data."""

from __future__ import annotations

from dataclasses import dataclass

from enums import PaymentMethod


@dataclass(frozen=True)
class Payment:
    payment_id: str
    ticket_id: str
    amount: float
    method: PaymentMethod
    paid_at: float
