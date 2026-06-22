"""BookingService — the booking engine.

The whole thing is three steps a user walks through:

    1. hold(seats)     reserve seats for a few minutes   AVAILABLE -> LOCKED
    2. confirm(hold)   pay; the reservation becomes a ticket   LOCKED -> BOOKED
    3. cancel(ticket)  give the seats back                BOOKED -> AVAILABLE

The one rule that must never break: a seat is BOOKED by at most one user. We keep
it by doing every seat change *inside the show's lock* (`with self.locker.guard(show)`),
so only one booking touches a given show at a time.

The lock, the pricing and the two stores are injected, so each can be swapped
without touching this class. `now` is passed in (not read from the clock) so tests
can fast-forward time.
"""

from __future__ import annotations

from .config import CANCEL_CUTOFF, HOLD_TTL
from .enums import PaymentMode, SeatStatus, TicketStatus
from .exceptions import CutoffPassedError, HoldExpiredError, SeatUnavailableError
from .models import Hold, Movie, Payment, Screen, Show, ShowSeat, Ticket, User
from .repositories import PaymentRepository, TicketRepository
from .strategies import PerShowLock, PricingStrategy, SeatLocker, TierPricing


class BookingService:
    def __init__(self, locker: SeatLocker | None = None,
                 pricing: PricingStrategy | None = None,
                 tickets: TicketRepository | None = None,
                 payments: PaymentRepository | None = None):
        self.locker = locker or PerShowLock()        # keeps two users off one seat
        self.pricing = pricing or TierPricing()      # what a seat costs
        self.tickets = tickets or TicketRepository()  # where booked tickets live
        self.payments = payments or PaymentRepository()

    # === set up a show =======================================================
    def create_show(self, show_id: str, movie: Movie, screen: Screen,
                    start_time: float) -> Show:
        """One ShowSeat (its own status + price) per physical seat in the screen."""
        show_seats = {seat.seat_id: ShowSeat(show_id, seat, self.pricing.price(seat))
                      for seat in screen.seats}
        return Show(show_id, movie, screen, start_time, show_seats)

    # === step 1 · hold the seats =============================================
    def hold(self, show: Show, seat_ids: list[str], user: User, now: float) -> Hold:
        """Reserve seats for this user for a few minutes. Raises if any is taken."""
        with self.locker.guard(show):                       # one booking per show at a time
            self._free_expired(show, now)                   # let lapsed holds go first

            # 1. are ALL the wanted seats free right now?
            taken = [sid for sid in seat_ids
                     if show.show_seat(sid).status is not SeatStatus.AVAILABLE]
            if taken:
                raise SeatUnavailableError(f"already taken: {taken}")

            # 2. mark each one LOCKED by this user, with an expiry time
            for sid in seat_ids:
                seat = show.show_seat(sid)
                seat.status = SeatStatus.LOCKED
                seat.held_by = user.user_id
                seat.locked_until = now + HOLD_TTL

            # 3. give back a receipt the user can pay with
            return Hold(show, tuple(seat_ids), user.user_id, now + HOLD_TTL)

    def amount_due(self, hold: Hold) -> float:
        """What the user owes — the price already sits on each ShowSeat."""
        return sum(hold.show.show_seat(sid).price for sid in hold.seat_ids)

    # === step 2 · pay and confirm ============================================
    def confirm(self, hold: Hold, mode: PaymentMode, now: float) -> Ticket:
        """Pay for a still-valid hold; the seats become BOOKED and a Ticket is born."""
        show = hold.show
        with self.locker.guard(show):
            self._free_expired(show, now)

            # 1. is the hold still ours (and not expired)?
            for sid in hold.seat_ids:
                seat = show.show_seat(sid)
                if seat.status is not SeatStatus.LOCKED or seat.held_by != hold.user_id:
                    raise HoldExpiredError(f"the hold on {sid} is gone")

            # 2. take the money and write the records
            amount = self.amount_due(hold)
            ticket = Ticket(self.tickets.next_id(), show.show_id,
                            hold.seat_ids, hold.user_id, amount)
            payment = Payment(self.payments.next_id(), ticket.ticket_id, amount, mode, now)
            self.tickets.save(ticket)
            self.payments.save(payment)

            # 3. flip the seats to BOOKED and tie them to the ticket
            for sid in hold.seat_ids:
                seat = show.show_seat(sid)
                seat.status = SeatStatus.BOOKED
                seat.ticket_id = ticket.ticket_id
                seat.held_by = None

            return ticket

    # === step 3 · cancel =====================================================
    def cancel(self, show: Show, ticket: Ticket, now: float) -> None:
        """Give the seats back — unless we're inside the no-cancel window."""
        if now >= show.start_time - CANCEL_CUTOFF:
            raise CutoffPassedError("too close to showtime to cancel")
        with self.locker.guard(show):
            for sid in ticket.seat_ids:
                seat = show.show_seat(sid)
                seat.status = SeatStatus.AVAILABLE
                seat.ticket_id = None
            ticket.status = TicketStatus.CANCELLED

    # === read · which seats are free =========================================
    def available_seats(self, show: Show, now: float) -> list[str]:
        with self.locker.guard(show):
            self._free_expired(show, now)
            return sorted(sid for sid, seat in show.show_seats.items()
                          if seat.status is SeatStatus.AVAILABLE)

    # === helper · an unpaid hold past its time frees itself ==================
    def _free_expired(self, show: Show, now: float) -> None:
        for seat in show.show_seats.values():
            if seat.is_lock_expired(now):
                seat.status = SeatStatus.AVAILABLE
                seat.held_by = None
