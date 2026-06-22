"""
LLD-27 · BookMyShow — the complete implementation we code live.

Run:  python3 01_bookmyshow.py          # scripted demos, all assert green

In LLD-26 we DESIGNED this and left one promise: "there are several ways to keep
two users off the same seat — we'll compare them and build the best in LLD-27."
This file keeps that promise.

The model is the one we derived in LLD-26:
  Screen + Seat (physical)            <- FR-1/2  a screen is a grid of typed seats
  Show owns ShowSeats                 <- FR-4  the (seat × show) pairing: status + price
  ShowSeat.status: AVAILABLE/LOCKED/BOOKED   the per-show seat's life
  Ticket (durable) + Payment          <- FR-8  what survives a booking
  no SeatLock entity                  the "hold" is just ShowSeat.status == LOCKED

The headline is CONCURRENCY. The invariant: one show-seat -> one ticket. We make
"check it's free AND take it" a single atomic step with a PER-SHOW LOCK, and we
prove it: the SAME race run under a NaiveLocker double-books, under a PerShowLock
exactly one wins.
"""

from __future__ import annotations

import threading
import time
from abc import ABC, abstractmethod
from contextlib import nullcontext
from dataclasses import dataclass
from enum import Enum
from itertools import count
from typing import Callable, NamedTuple

HOLD_TTL = 300.0   # seconds a LOCKED (unpaid) seat survives before it frees itself
CANCEL_CUTOFF = 3600.0   # FR-10: no cancel within 1 hour of show start


# === Enums — small named sets (straight from the LLD-26 class diagram) ========
class SeatType(Enum):
    GOLD = "gold"
    DIAMOND = "diamond"
    PLATINUM = "platinum"


class SeatStatus(Enum):
    AVAILABLE = "available"
    LOCKED = "locked"      # the third state a bool can't hold — held while paying
    BOOKED = "booked"


class PaymentMode(Enum):
    UPI = "upi"
    CREDIT_CARD = "credit_card"
    NETBANKING = "netbanking"


class TicketStatus(Enum):
    CONFIRMED = "confirmed"
    CANCELLED = "cancelled"


# FR-5's rule as DATA: base price per seat type. A new tier is one entry here.
BASE_PRICE = {SeatType.GOLD: 150.0, SeatType.DIAMOND: 300.0, SeatType.PLATINUM: 450.0}


# === Errors — contract violations only =======================================
class SeatUnavailableError(Exception):
    """One or more requested seats are already LOCKED or BOOKED (the lost race)."""


class HoldExpiredError(Exception):
    """Tried to confirm a hold whose seats had already freed themselves."""


class CutoffPassedError(Exception):
    """Tried to cancel within the no-cancel window before showtime."""


# === Physical layer (shared across all shows) ================================
@dataclass(frozen=True)
class Seat:
    seat_id: str            # "A1"
    seat_type: SeatType


@dataclass(frozen=True)
class Movie:
    movie_id: str
    title: str
    language: str


class Screen:
    """An auditorium — a fixed grid of physical seats."""

    def __init__(self, screen_id: str, name: str, seats: list[Seat]):
        self.screen_id = screen_id
        self.name = name
        self.seats = seats


# === ShowSeat — the (seat × show) pairing: where status + price live ==========
# This is the LLD-26 "association class". The seat is physical and shared; its
# *per-show* state is here. The transient hold is NOT a separate object — it is
# simply status == LOCKED plus a locked_until stamp.
@dataclass
class ShowSeat:
    show_id: str
    seat: Seat
    price: float
    status: SeatStatus = SeatStatus.AVAILABLE
    locked_until: float = 0.0          # meaningful only while LOCKED
    held_by: str | None = None         # the user currently holding it
    ticket_id: str | None = None       # set once BOOKED

    @property
    def seat_id(self) -> str:
        return self.seat.seat_id

    def is_lock_expired(self, now: float) -> bool:
        return self.status is SeatStatus.LOCKED and now >= self.locked_until


# === Show — owns its ShowSeats + the lock that guards them ====================
class Show:
    def __init__(self, show_id: str, movie: Movie, screen: Screen,
                 start_time: float, pricing: "PricingStrategy"):
        self.show_id = show_id
        self.movie = movie
        self.screen = screen
        self.start_time = start_time
        # FR-4: one ShowSeat per physical seat, price baked in at creation.
        self.show_seats: dict[str, ShowSeat] = {
            s.seat_id: ShowSeat(show_id, s, pricing.price(s)) for s in screen.seats
        }
        self.lock = threading.Lock()   # the per-show concurrency boundary

    def show_seat(self, seat_id: str) -> ShowSeat:
        return self.show_seats[seat_id]


# === Records =================================================================
@dataclass(frozen=True)
class User:
    user_id: str
    name: str


@dataclass
class Ticket:
    ticket_id: str
    show_id: str
    seat_ids: tuple[str, ...]
    user_id: str
    amount: float
    status: TicketStatus = TicketStatus.CONFIRMED


@dataclass(frozen=True)
class Payment:
    payment_id: str
    ticket_id: str
    amount: float
    mode: PaymentMode
    paid_at: float


# A Hold is a transient RECEIPT returned by hold() — NOT stored anywhere. The
# source of truth is each ShowSeat's status; this just lets confirm() find them.
class Hold(NamedTuple):
    show: "Show"
    seat_ids: tuple[str, ...]
    user_id: str
    expires_at: float


# === Strategy: what to charge (FR-5) =========================================
class PricingStrategy(ABC):
    @abstractmethod
    def price(self, seat: Seat) -> float: ...


class TierPricing(PricingStrategy):
    """Base price by seat type."""

    def price(self, seat: Seat) -> float:
        return BASE_PRICE[seat.seat_type]


class WeekendSurge(PricingStrategy):
    """Same seats, +20% — FR-5's 'price varies by day' axis, swapped in."""

    def price(self, seat: Seat) -> float:
        return BASE_PRICE[seat.seat_type] * 1.2


# === SeatLocker — THE approach we are comparing (the LLD-26 promise) ==========
# In LLD-26 we listed several ways to enforce "one seat, one ticket". Here they
# are as a pluggable strategy so we can run the SAME race under each and watch
# what happens. The realistic in-memory choice is PerShowLock.
class SeatLocker(ABC):
    @abstractmethod
    def guard(self, show: Show):
        """A context manager held around the check-and-set on this show."""


class PerShowLock(SeatLocker):
    """Our choice: one mutex per show. Different shows never contend, so this
    scales fine and stays simple. Maps to `SELECT ... FOR UPDATE` on the row in a DB."""

    def guard(self, show: Show):
        return show.lock


class NaiveLocker(SeatLocker):
    """No mutual exclusion — only here to DEMONSTRATE the race. check-then-act is
    two steps, so two threads both pass the check and both 'win'. Never ship this."""

    def guard(self, show: Show):
        return nullcontext()


# === BookingService — the orchestrator =======================================
class BookingService:
    def __init__(self, locker: SeatLocker | None = None,
                 pricing: PricingStrategy | None = None,
                 _race_window: Callable[[], None] | None = None):
        self.locker = locker or PerShowLock()
        self.pricing = pricing or TierPricing()
        self._tickets: dict[str, Ticket] = {}
        self._payments: dict[str, Payment] = {}
        self._ids = count(1)
        # test hook: a no-op in real life; the race demo injects a tiny sleep here
        # to force two threads to interleave *between* the check and the set.
        self._race_window = _race_window or (lambda: None)

    # --- internals --------------------------------------------------------
    def _free_expired(self, show: Show, now: float) -> None:
        """Lazy expiry: a LOCKED seat past its TTL frees itself on next access."""
        for ss in show.show_seats.values():
            if ss.is_lock_expired(now):
                ss.status = SeatStatus.AVAILABLE
                ss.held_by = None

    # --- commands ---------------------------------------------------------
    def hold(self, show: Show, seat_ids: list[str], user: User, now: float) -> Hold:
        """FR-4 + FR-9. Under the locker's guard, check ('all AVAILABLE') and act
        ('set LOCKED') are ONE atomic step — two callers can't both pass the check."""
        with self.locker.guard(show):
            self._free_expired(show, now)
            taken = [s for s in seat_ids
                     if show.show_seat(s).status is not SeatStatus.AVAILABLE]
            self._race_window()                      # (test hook — no-op normally)
            if taken:
                raise SeatUnavailableError(f"unavailable: {taken}")
            expires = now + HOLD_TTL
            for s in seat_ids:
                ss = show.show_seat(s)
                ss.status = SeatStatus.LOCKED
                ss.locked_until = expires
                ss.held_by = user.user_id
            return Hold(show, tuple(seat_ids), user.user_id, expires)

    def amount_due(self, hold: Hold) -> float:
        """A read — the booking-page total (prices are already on each ShowSeat)."""
        return sum(hold.show.show_seat(s).price for s in hold.seat_ids)

    def confirm(self, hold: Hold, mode: PaymentMode, now: float) -> Ticket:
        """FR-8. Pay while still LOCKED-by-you -> LOCKED becomes BOOKED and a
        Ticket + Payment are born. If the seats freed themselves first -> raise."""
        show = hold.show
        with self.locker.guard(show):
            self._free_expired(show, now)
            for s in hold.seat_ids:
                ss = show.show_seat(s)
                if ss.status is not SeatStatus.LOCKED or ss.held_by != hold.user_id:
                    raise HoldExpiredError(f"hold on {s} is gone")
            amount = self.amount_due(hold)
            ticket = Ticket(f"T-{next(self._ids):04d}", show.show_id,
                            hold.seat_ids, hold.user_id, amount)
            payment = Payment(f"P-{next(self._ids):04d}", ticket.ticket_id,
                              amount, mode, now)
            for s in hold.seat_ids:
                ss = show.show_seat(s)
                ss.status = SeatStatus.BOOKED
                ss.ticket_id = ticket.ticket_id
                ss.held_by = None
            self._tickets[ticket.ticket_id] = ticket
            self._payments[ticket.ticket_id] = payment
            return ticket

    def cancel(self, show: Show, ticket: Ticket, now: float) -> None:
        """FR-10. Free the seats and mark the ticket CANCELLED — but not inside
        the cutoff window before showtime."""
        if now >= show.start_time - CANCEL_CUTOFF:
            raise CutoffPassedError("too close to showtime to cancel")
        with self.locker.guard(show):
            for s in ticket.seat_ids:
                ss = show.show_seat(s)
                ss.status = SeatStatus.AVAILABLE
                ss.ticket_id = None
            ticket.status = TicketStatus.CANCELLED

    # --- queries (FR-7) ---------------------------------------------------
    def available_seats(self, show: Show, now: float) -> list[str]:
        with self.locker.guard(show):
            self._free_expired(show, now)
            return sorted(s for s, ss in show.show_seats.items()
                          if ss.status is SeatStatus.AVAILABLE)


# === Demo helpers ============================================================
def build_show(pricing: PricingStrategy, start_time: float = 100_000.0) -> Show:
    """One screen: rows A (gold), B (diamond), C (platinum), 5 seats each."""
    seats = ([Seat(f"A{i}", SeatType.GOLD) for i in range(1, 6)]
             + [Seat(f"B{i}", SeatType.DIAMOND) for i in range(1, 6)]
             + [Seat(f"C{i}", SeatType.PLATINUM) for i in range(1, 6)])
    screen = Screen("SCR-1", "Audi 1", seats)
    movie = Movie("M-1", "Inception", "English")
    return Show("SHOW-1", movie, screen, start_time, pricing)


def _race(locker: SeatLocker) -> int:
    """Run the SAME race under a given locker; return how many users 'won' A3.
    A tiny sleep inside hold() (between the check and the set) forces the
    interleave so the outcome is deterministic, not luck."""
    svc = BookingService(locker=locker, _race_window=lambda: time.sleep(0.02))
    show = build_show(TierPricing())
    ananya, rahul = User("u1", "ananya"), User("u2", "rahul")
    winners: list[str] = []
    wl = threading.Lock()
    barrier = threading.Barrier(2)

    def grab(user: User) -> None:
        barrier.wait()                                  # both reach hold() together
        try:
            h = svc.hold(show, ["A3"], user, now=0.0)
            svc.confirm(h, PaymentMode.UPI, now=1.0)
            with wl:
                winners.append(user.name)
        except SeatUnavailableError:
            pass

    ts = [threading.Thread(target=grab, args=(u,)) for u in (ananya, rahul)]
    for t in ts:
        t.start()
    for t in ts:
        t.join()
    return len(winners)


def acceptance() -> None:
    svc = BookingService()
    show = build_show(TierPricing())
    ananya, rahul = User("u1", "ananya"), User("u2", "rahul")

    # FR-4/8: hold -> due -> pay -> confirm; ShowSeats become BOOKED
    h = svc.hold(show, ["A1", "B1"], ananya, now=0.0)
    assert svc.amount_due(h) == 150.0 + 300.0                 # gold + diamond
    ticket = svc.confirm(h, PaymentMode.UPI, now=60.0)
    assert ticket.amount == 450.0 and ticket.status is TicketStatus.CONFIRMED
    assert show.show_seat("A1").status is SeatStatus.BOOKED
    assert show.show_seat("A1").ticket_id == ticket.ticket_id
    print("happy   hold -> due -> pay -> confirm; seats BOOKED          ✔")

    # FR-9: a booked seat can't be held again
    try:
        svc.hold(show, ["A1"], rahul, now=70.0)
        raise AssertionError("should have raised")
    except SeatUnavailableError:
        pass
    print("FR-9    booked seat can't be re-held                         ✔")

    # FR-4: a LOCKED seat past its TTL frees itself
    svc2 = BookingService()
    show2 = build_show(TierPricing())
    svc2.hold(show2, ["C1"], ananya, now=0.0)
    assert show2.show_seat("C1").status is SeatStatus.LOCKED
    assert "C1" in svc2.available_seats(show2, now=400.0)     # expired -> available
    later = svc2.hold(show2, ["C1"], rahul, now=400.0)
    assert svc2.confirm(later, PaymentMode.CREDIT_CARD, now=410.0).user_id == "u2"
    print("FR-4    unpaid LOCKED seat expires, frees itself             ✔")

    # FR-8: confirming an expired hold raises
    svc3 = BookingService()
    show3 = build_show(TierPricing())
    stale = svc3.hold(show3, ["A2"], ananya, now=0.0)
    try:
        svc3.confirm(stale, PaymentMode.UPI, now=999.0)
        raise AssertionError("should have raised")
    except HoldExpiredError:
        pass
    print("FR-8    confirming an expired hold raises                    ✔")

    # FR-10: cancel frees the seats; inside the cutoff it refuses
    svc4 = BookingService()
    show4 = build_show(TierPricing(), start_time=100_000.0)
    h4 = svc4.hold(show4, ["B2"], ananya, now=0.0)
    tkt4 = svc4.confirm(h4, PaymentMode.UPI, now=10.0)
    svc4.cancel(show4, tkt4, now=10.0)
    assert tkt4.status is TicketStatus.CANCELLED
    assert "B2" in svc4.available_seats(show4, now=20.0)
    h4b = svc4.hold(show4, ["B3"], ananya, now=20.0)
    tkt4b = svc4.confirm(h4b, PaymentMode.UPI, now=30.0)
    try:
        svc4.cancel(show4, tkt4b, now=100_000.0 - 60.0)       # 1 min before show
        raise AssertionError("should have raised")
    except CutoffPassedError:
        pass
    print("FR-10   cancel frees seats; refuses inside the cutoff        ✔")

    # FR-5: swap pricing -> same seats, different total, zero engine edits
    surge = BookingService(pricing=WeekendSurge())
    s5 = build_show(WeekendSurge())
    h5 = surge.hold(s5, ["C2"], ananya, now=0.0)              # platinum 450 * 1.2
    assert surge.amount_due(h5) == 540.0
    print("FR-5    WeekendSurge: platinum ₹450 -> ₹540, no engine edits  ✔")

    # === THE HEADLINE: compare the approaches on the SAME race ===============
    naive_winners = _race(NaiveLocker())
    locked_winners = _race(PerShowLock())
    assert naive_winners == 2, f"naive should double-book, got {naive_winners}"
    assert locked_winners == 1, f"per-show lock: exactly one should win, got {locked_winners}"
    print(f"RACE    NaiveLocker -> {naive_winners} tickets for one seat (the BUG)     ✔")
    print(f"RACE    PerShowLock -> {locked_winners} ticket  (exactly one wins)        ✔")

    print("\nacceptance: all green ✔")


if __name__ == "__main__":
    acceptance()
