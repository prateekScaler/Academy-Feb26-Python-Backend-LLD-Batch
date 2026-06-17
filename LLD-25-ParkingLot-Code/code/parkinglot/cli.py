"""cli.py — the parking lot's edge: the CONTROLLER analogue at the console.

Its whole job is the three things a web controller does, minus the HTTP:
  1. parse + validate raw input   (delegated to console.py)
  2. call the service              (ParkingLot — it does the thinking)
  3. format the result, and turn the service's exceptions into friendly lines
     (UnpaidExitError -> "pay first", the same mapping a view does to 402)

The service never imports this file — I/O stays quarantined at the edge, exactly
as FR-8's "render, don't print" boundary became a file boundary in TTT.

A simulated clock (in hours) lets you watch tiered pricing without waiting an hour."""

from __future__ import annotations

from console import ask_choice, ask_enum, ask_int, ask_nonempty, ask_yes_no
from enums import PaymentMethod, SpotSize, VehicleType
from exceptions import AlreadyPaidError, InvalidTicketError, UnpaidExitError
from models.floor import Floor
from models.spot import Spot
from models.vehicle import Vehicle
from service import ParkingLot
from strategies.parking_strategy import FirstFit
from strategies.pricing_strategy import TieredHourly

HOUR = 3600.0


def build_lot() -> ParkingLot:
    """2 floors x (2 small + 3 medium + 1 large) — the same demo lot."""
    def floor(n: int) -> Floor:
        spots = ([Spot(f"F{n}-S{i}", SpotSize.SMALL) for i in range(2)]
                 + [Spot(f"F{n}-M{i}", SpotSize.MEDIUM) for i in range(3)]
                 + [Spot(f"F{n}-L{i}", SpotSize.LARGE) for i in range(1)])
        return Floor(n, spots)
    return ParkingLot([floor(1), floor(2)], FirstFit(), TieredHourly())


def _show(lot: ParkingLot) -> None:
    print("─" * 28)
    print(lot.render())
    print("─" * 28)


def _park(lot: ParkingLot, now: float) -> None:
    plate = ask_nonempty("plate")
    kind = ask_enum("type", VehicleType)
    ticket = lot.park(Vehicle(plate, kind), now)
    if ticket is None:
        print("  lot full for that size — turned away (not an error)")
    else:
        print(f"  parked: {ticket.ticket_id} -> floor {ticket.floor_no}, spot {ticket.spot_id}")


def _due(lot: ParkingLot, now: float) -> None:
    tid = ask_nonempty("ticket id")
    try:
        print(f"  due now: ₹{lot.amount_due(tid, now):.0f}")
    except InvalidTicketError as e:
        print(f"  rejected: {e}")


def _pay(lot: ParkingLot, now: float) -> None:
    tid = ask_nonempty("ticket id")
    method = ask_enum("method", PaymentMethod)
    try:
        payment = lot.pay(tid, method, now)
        print(f"  paid ₹{payment.amount:.0f} by {payment.method.value} ({payment.payment_id})")
    except (InvalidTicketError, AlreadyPaidError) as e:
        print(f"  rejected: {e}")


def _exit(lot: ParkingLot, now: float) -> None:
    tid = ask_nonempty("ticket id")
    try:
        lot.exit_lot(tid, now)
        print(f"  {tid} exited — spot freed")
    except (InvalidTicketError, UnpaidExitError) as e:
        print(f"  rejected: {e}")


def play() -> None:
    print("Parking Lot — 2 floors, sizes s/m/l. The clock is simulated (in hours).")
    lot = build_lot()
    now = 0.0
    _show(lot)
    commands = {"park": _park, "due": _due, "pay": _pay, "exit": _exit}
    while True:
        choice = ask_choice(
            "action — Park / Due / paY / Exit / Show / Tick(+1h) / Quit",
            {"P": "park", "D": "due", "Y": "pay", "E": "exit",
             "S": "show", "T": "tick", "Q": "quit"})
        if choice == "quit":
            break
        elif choice == "show":
            _show(lot)
        elif choice == "tick":
            now += HOUR
            print(f"  clock is now {now / HOUR:.0f}h")
        else:
            commands[choice](lot, now)
    print("bye 👋")
