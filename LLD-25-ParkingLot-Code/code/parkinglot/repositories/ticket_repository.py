"""TicketRepository — the REPOSITORY layer for active tickets.

In `01_parking_lot.py` this was a bare `dict` living inside the service. Pulling
it behind a class is the one real step the package takes toward the backend
stack: the service now depends on a *contract* (save / find / delete / all), not
on "a dict". Swap this class for a `DjangoTicketRepository` backed by a table and
the service never notices — that is the entire repository pattern.

Holds only ACTIVE tickets: a ticket is removed on exit, so a reused id `find()`s
to None and the service raises InvalidTicketError. (A persistent DB repo would
soft-delete — set a status — instead of dropping the row; see the persistence
trade-off.) It also mints ticket ids, because id allocation is a storage concern."""

from __future__ import annotations

from itertools import count

from models.ticket import Ticket


class TicketRepository:
    def __init__(self):
        self._tickets: dict[str, Ticket] = {}
        self._ids = count(1)

    def next_id(self) -> str:
        return f"T-{next(self._ids):04d}"

    def save(self, ticket: Ticket) -> None:
        self._tickets[ticket.ticket_id] = ticket

    def find(self, ticket_id: str) -> Ticket | None:
        return self._tickets.get(ticket_id)

    def delete(self, ticket_id: str) -> None:
        self._tickets.pop(ticket_id, None)

    def all_active(self) -> list[Ticket]:
        return list(self._tickets.values())
