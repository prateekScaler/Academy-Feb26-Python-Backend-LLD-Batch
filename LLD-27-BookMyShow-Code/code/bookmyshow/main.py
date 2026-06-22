"""Entry point for the layered package.

    cd code/bookmyshow && python3 main.py         # acceptance — all assert green
    cd code/bookmyshow && python3 main.py play     # interactive booking shell

Run as a script (not `-m`); the sys.path shim lets `from bookmyshow...` resolve
whether you launch from inside the package dir or its parent."""

from __future__ import annotations

import os
import sys
import threading

# Allow `python3 main.py` from inside the package dir: put the PARENT on the path
# so `import bookmyshow` works, exactly like the carried-over package layout.
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from bookmyshow.enums import PaymentMode, SeatStatus, SeatType, TicketStatus    # noqa: E402
from bookmyshow.exceptions import (                                            # noqa: E402
    CutoffPassedError,
    HoldExpiredError,
    SeatUnavailableError,
)
from bookmyshow.models import Movie, Screen, Seat, User                        # noqa: E402
from bookmyshow.service import BookingService                                  # noqa: E402
from bookmyshow.strategies import WeekendSurge                                 # noqa: E402


def build_show(svc: BookingService, start_time: float = 100_000.0):
    """One screen: rows A (gold), B (diamond), C (platinum), 5 seats each."""
    seats = ([Seat(f"A{i}", SeatType.GOLD) for i in range(1, 6)]
             + [Seat(f"B{i}", SeatType.DIAMOND) for i in range(1, 6)]
             + [Seat(f"C{i}", SeatType.PLATINUM) for i in range(1, 6)])
    screen = Screen("SCR-1", "Audi 1", seats)
    return svc.create_show("SHOW-1", Movie("M-1", "Inception", "English"),
                           screen, start_time)


def _race() -> int:
    """Two threads grab the same seat at once; return how many got a ticket.
    The per-show lock serialises them, so exactly one wins. (The full naive-vs-locked
    comparison lives in code/02_concurrency_demo.py.)"""
    svc = BookingService()
    show = build_show(svc)
    ananya, rahul = User("u1", "ananya"), User("u2", "rahul")
    winners: list[str] = []
    wl = threading.Lock()
    barrier = threading.Barrier(2)

    def grab(user: User) -> None:
        barrier.wait()
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
    show = build_show(svc)
    ananya, rahul = User("u1", "ananya"), User("u2", "rahul")

    h = svc.hold(show, ["A1", "B1"], ananya, now=0.0)
    assert svc.amount_due(h) == 150.0 + 300.0
    ticket = svc.confirm(h, PaymentMode.UPI, now=60.0)
    assert ticket.amount == 450.0 and ticket.status is TicketStatus.CONFIRMED
    assert show.show_seat("A1").status is SeatStatus.BOOKED
    assert svc.payments.exists_for(ticket.ticket_id)
    print("happy   hold -> due -> pay -> confirm; seats BOOKED          ✔")

    try:
        svc.hold(show, ["A1"], rahul, now=70.0)
        raise AssertionError("should have raised")
    except SeatUnavailableError:
        pass
    print("FR-9    booked seat can't be re-held                         ✔")

    svc2 = BookingService()
    show2 = build_show(svc2)
    svc2.hold(show2, ["C1"], ananya, now=0.0)
    assert show2.show_seat("C1").status is SeatStatus.LOCKED
    assert "C1" in svc2.available_seats(show2, now=400.0)
    later = svc2.hold(show2, ["C1"], rahul, now=400.0)
    assert svc2.confirm(later, PaymentMode.CREDIT_CARD, now=410.0).user_id == "u2"
    print("FR-4    unpaid LOCKED seat expires, frees itself             ✔")

    svc3 = BookingService()
    show3 = build_show(svc3)
    stale = svc3.hold(show3, ["A2"], ananya, now=0.0)
    try:
        svc3.confirm(stale, PaymentMode.UPI, now=999.0)
        raise AssertionError("should have raised")
    except HoldExpiredError:
        pass
    print("FR-8    confirming an expired hold raises                    ✔")

    svc4 = BookingService()
    show4 = build_show(svc4, start_time=100_000.0)
    tkt4 = svc4.confirm(svc4.hold(show4, ["B2"], ananya, now=0.0), PaymentMode.UPI, now=10.0)
    svc4.cancel(show4, tkt4, now=10.0)
    assert tkt4.status is TicketStatus.CANCELLED
    assert "B2" in svc4.available_seats(show4, now=20.0)
    tkt4b = svc4.confirm(svc4.hold(show4, ["B3"], ananya, now=20.0), PaymentMode.UPI, now=30.0)
    try:
        svc4.cancel(show4, tkt4b, now=100_000.0 - 60.0)
        raise AssertionError("should have raised")
    except CutoffPassedError:
        pass
    print("FR-10   cancel frees seats; refuses inside the cutoff        ✔")

    surge = BookingService(pricing=WeekendSurge())
    s5 = build_show(surge)
    h5 = surge.hold(s5, ["C2"], ananya, now=0.0)
    assert surge.amount_due(h5) == 540.0
    print("FR-5    WeekendSurge: platinum ₹450 -> ₹540, no engine edits  ✔")

    winners = _race()
    assert winners == 1, f"two users, one seat: exactly one should win, got {winners}"
    print(f"RACE    two users race one seat: exactly one wins ({winners} ticket)        ✔")

    print("\nacceptance: all green ✔")


def main() -> None:
    if len(sys.argv) > 1 and sys.argv[1] == "play":
        from bookmyshow.cli import play
        play()
    else:
        acceptance()


if __name__ == "__main__":
    main()
