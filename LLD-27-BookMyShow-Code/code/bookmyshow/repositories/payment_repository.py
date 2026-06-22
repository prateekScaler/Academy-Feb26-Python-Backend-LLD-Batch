"""PaymentRepository — one Payment per ticket. Same shape as TicketRepository."""

from itertools import count

from ..models import Payment


class PaymentRepository:
    def __init__(self) -> None:
        self._payments: dict[str, Payment] = {}     # keyed by ticket_id
        self._ids = count(1)

    def next_id(self) -> str:
        return f"P-{next(self._ids):04d}"

    def save(self, payment: Payment) -> None:
        self._payments[payment.ticket_id] = payment

    def find_by_ticket(self, ticket_id: str) -> Payment | None:
        return self._payments.get(ticket_id)

    def exists_for(self, ticket_id: str) -> bool:
        return ticket_id in self._payments
