"""service.py — ParkingLot, the SERVICE layer: business rules and orchestration,
no HTTP and (now) no storage details. It holds two Strategies (the open
variables) and two Repositories (the storage seam), and coordinates them.

Read the command trio top to bottom — each is "guard -> act -> record":
  park     : ask the strategy -> mark the spot -> write the ticket
  pay       : guard pay-once   -> price it     -> write the payment
  exit_lot  : guard paid       -> free the spot -> retire the ticket

The single-file version kept `_active`/`_payments` dicts inline; here they are
injected repositories, so the exact same logic now runs one step closer to the
layered backend the engine ultimately slots into."""

from __future__ import annotations

from enums import SpotSize, SpotStatus, PaymentMethod
from exceptions import AlreadyPaidError, InvalidTicketError, UnpaidExitError
from models.floor import Floor
from models.payment import Payment
from models.spot import Spot
from models.ticket import Ticket
from models.vehicle import Vehicle
from repositories.payment_repository import PaymentRepository
from repositories.ticket_repository import TicketRepository
from strategies.parking_strategy import ParkingStrategy
from strategies.pricing_strategy import PricingStrategy


class ParkingLot:
    def __init__(self, floors: list[Floor],
                 parking: ParkingStrategy, pricing: PricingStrategy,
                 tickets: TicketRepository | None = None,
                 payments: PaymentRepository | None = None):
        self.floors = floors
        self.parking = parking
        self.pricing = pricing
        self.tickets = tickets or TicketRepository()
        self.payments = payments or PaymentRepository()

    # --- commands ---------------------------------------------------------
    def park(self, vehicle: Vehicle, now: float) -> Ticket | None:
        """None when no suitable spot exists — expected flow, not an error."""
        picked = self.parking.pick(self.floors, vehicle)
        if picked is None:
            return None
        floor, spot = picked
        spot.occupy()
        ticket = Ticket(self.tickets.next_id(), vehicle,
                        floor.number, spot.spot_id, entry_time=now)
        self.tickets.save(ticket)
        return ticket

    def pay(self, ticket_id: str, method: PaymentMethod, now: float) -> Payment:
        ticket = self._require_active(ticket_id)
        if self.payments.exists(ticket_id):
            raise AlreadyPaidError(f"{ticket_id} is already paid (FR-9: pay exactly once)")
        amount = self.pricing.fee(self._spot_of(ticket).size, now - ticket.entry_time)
        payment = Payment(self.payments.next_id(), ticket_id, amount, method, now)
        self.payments.save(payment)
        return payment

    def exit_lot(self, ticket_id: str, now: float) -> Ticket:
        ticket = self._require_active(ticket_id)
        if not self.payments.exists(ticket_id):
            raise UnpaidExitError(f"{ticket_id} is unpaid — the gate stays down")
        self._spot_of(ticket).free()             # FR-6: free the moment it leaves
        ticket.exit_time = now
        self.tickets.delete(ticket_id)
        return ticket

    # --- queries (FR-7) ---------------------------------------------------
    def amount_due(self, ticket_id: str, now: float) -> float:
        """What the booth display shows — a read, no mutation."""
        ticket = self._require_active(ticket_id)
        return self.pricing.fee(self._spot_of(ticket).size, now - ticket.entry_time)

    def available(self, size: SpotSize) -> int:
        return sum(f.free_count(size) for f in self.floors)

    def per_floor(self, size: SpotSize) -> dict[int, int]:
        return {f.number: f.free_count(size) for f in self.floors}

    def render(self) -> str:
        marks = {SpotStatus.FREE: " {} ", SpotStatus.OCCUPIED: "[{}]",
                 SpotStatus.OUT_OF_ORDER: " # "}
        return "\n".join(
            f"F{f.number}: " + " ".join(
                marks[s.status].format(s.size.value[0]) for s in f.spots)
            for f in self.floors)

    # --- internals --------------------------------------------------------
    def _require_active(self, ticket_id: str) -> Ticket:
        ticket = self.tickets.find(ticket_id)
        if ticket is None:
            raise InvalidTicketError(f"unknown or already-used ticket: {ticket_id}")
        return ticket

    def _spot_of(self, ticket: Ticket) -> Spot:
        floor = next(f for f in self.floors if f.number == ticket.floor_no)
        return next(s for s in floor.spots if s.spot_id == ticket.spot_id)
