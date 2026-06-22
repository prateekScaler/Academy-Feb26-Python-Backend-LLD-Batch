"""Ticket — the *durable* record (LLD-26: what survives a booking). Born when
payment succeeds; ties the user to the show-seats + amount. Stores ids, not refs."""

from dataclasses import dataclass

from ..enums import TicketStatus


@dataclass
class Ticket:
    ticket_id: str
    show_id: str
    seat_ids: tuple[str, ...]
    user_id: str
    amount: float
    status: TicketStatus = TicketStatus.CONFIRMED
