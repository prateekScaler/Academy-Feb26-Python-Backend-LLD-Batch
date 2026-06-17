"""PaymentRepository — the REPOSITORY layer for payments, keyed by ticket id.

`exists(ticket_id)` is the pay-once guard expressed as a query: the service asks
"has this ticket already paid?" without knowing whether the answer comes from a
dict or a `SELECT 1 FROM payments WHERE ticket_id = ?`. In a database the same
invariant is a `UNIQUE(ticket_id)` constraint — the schema enforces what this
method enforces in memory."""

from __future__ import annotations

from itertools import count

from models.payment import Payment


class PaymentRepository:
    def __init__(self):
        self._payments: dict[str, Payment] = {}
        self._ids = count(1)

    def next_id(self) -> str:
        return f"P-{next(self._ids):04d}"

    def save(self, payment: Payment) -> None:
        self._payments[payment.ticket_id] = payment

    def exists(self, ticket_id: str) -> bool:
        return ticket_id in self._payments

    def find(self, ticket_id: str) -> Payment | None:
        return self._payments.get(ticket_id)
