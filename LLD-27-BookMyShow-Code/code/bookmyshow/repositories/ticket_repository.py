"""TicketRepository — the durable tickets store. In-memory dict today; the
interface (save/find/exists/next_id) is what a SQL/NoSQL impl would honour."""

from itertools import count

from ..models import Ticket


class TicketRepository:
    def __init__(self) -> None:
        self._tickets: dict[str, Ticket] = {}
        self._ids = count(1)

    def next_id(self) -> str:
        return f"T-{next(self._ids):04d}"

    def save(self, ticket: Ticket) -> None:
        self._tickets[ticket.ticket_id] = ticket

    def find(self, ticket_id: str) -> Ticket | None:
        return self._tickets.get(ticket_id)

    def exists(self, ticket_id: str) -> bool:
        return ticket_id in self._tickets

    def all(self) -> list[Ticket]:
        return list(self._tickets.values())
