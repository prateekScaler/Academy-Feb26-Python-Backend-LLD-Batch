"""CLI — the interactive booking shell (`python3 main.py play`). It wires a real
wall-clock into the service (the demos inject `now`; here it's `time.time()`),
renders the seat map, and walks one user through hold -> pay -> confirm."""

from __future__ import annotations

import time

from . import console
from .enums import PaymentMode, SeatStatus, SeatType
from .exceptions import HoldExpiredError, SeatUnavailableError
from .models import Movie, Screen, Seat, User
from .service import BookingService

_GLYPH = {SeatStatus.AVAILABLE: ".", SeatStatus.LOCKED: "L", SeatStatus.BOOKED: "X"}
_ROWS = [("A", SeatType.GOLD), ("B", SeatType.DIAMOND), ("C", SeatType.PLATINUM)]


def _demo_show(svc: BookingService):
    seats = [Seat(f"{row}{i}", stype) for row, stype in _ROWS for i in range(1, 6)]
    screen = Screen("SCR-1", "Audi 1", seats)
    return svc.create_show("SHOW-1", Movie("M-1", "Inception", "English"),
                           screen, start_time=time.time() + 86_400)


def _print_map(show) -> None:
    print(f"\n  {show.movie.title} — {show.screen.name}    [ . available   L locked   X booked ]")
    for row, stype in _ROWS:
        cells = "  ".join(f"{row}{i}:{_GLYPH[show.show_seat(f'{row}{i}').status]}"
                          for i in range(1, 6))
        price = show.show_seat(f"{row}1").price
        print(f"    {stype.value:<9} ₹{price:<5.0f} {cells}")
    print()


def play() -> None:
    svc = BookingService()
    show = _demo_show(svc)
    print("=" * 62)
    print(" BookMyShow — interactive booking")
    print(" Hold seats, then pay before the hold expires (one seat, one ticket).")
    print("=" * 62)

    while True:
        _print_map(show)
        action = console.ask_choice("Action", ["book", "map", "quit"])
        if action == "quit":
            print("bye!")
            return
        if action == "map":
            continue

        name = console.ask_nonempty("Your name: ")
        user = User(f"u-{name.lower()}", name)
        wanted = console.ask_seats("Seats (e.g. A1 B2): ")
        try:
            hold = svc.hold(show, wanted, user, now=time.time())
        except (SeatUnavailableError, KeyError) as exc:
            print(f"  ✗ couldn't hold: {exc}")
            continue

        due = svc.amount_due(hold)
        print(f"  held {list(hold.seat_ids)} — amount due ₹{due:.0f}")
        if console.ask_choice("Pay now?", ["yes", "no"]) == "no":
            print("  (the hold will expire on its own; the seats free up then)")
            continue
        mode = PaymentMode(console.ask_choice("Mode", ["upi", "credit_card", "netbanking"]))
        try:
            ticket = svc.confirm(hold, mode, now=time.time())
            print(f"  ✔ booked {ticket.ticket_id}: {list(ticket.seat_ids)} for ₹{ticket.amount:.0f}")
        except HoldExpiredError as exc:
            print(f"  ✗ {exc}")
