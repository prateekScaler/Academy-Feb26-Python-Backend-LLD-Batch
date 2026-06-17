"""Entry point — write this file FIRST in the interview, as TODOs.

Run:  python3 main.py          # acceptance run: every FR asserted green
      python3 main.py play     # interactive booth (simulated clock)

This is the SAME engine as code/01_parking_lot.py — diff the class bodies and
they barely change. What the package buys you is the tree: domain (models/),
the two open variables (strategies/), the storage seam (repositories/), the
service (service.py) and the I/O edge (cli.py + console.py). The acceptance below
drives every FR the single-file demos drove."""

from __future__ import annotations

import sys

from enums import PaymentMethod, SpotSize, SpotStatus, VehicleType
from exceptions import AlreadyPaidError, InvalidTicketError, UnpaidExitError
from models.floor import Floor
from models.spot import Spot
from models.vehicle import Vehicle
from service import ParkingLot
from strategies.parking_strategy import FirstFit, LeastCrowded
from strategies.pricing_strategy import TieredHourly, WeekendFlat

HOUR = 3600.0


def build_lot(parking=None, pricing=None) -> ParkingLot:
    """2 floors x (2 small + 3 medium + 1 large)."""
    def floor(n: int) -> Floor:
        spots = ([Spot(f"F{n}-S{i}", SpotSize.SMALL) for i in range(2)]
                 + [Spot(f"F{n}-M{i}", SpotSize.MEDIUM) for i in range(3)]
                 + [Spot(f"F{n}-L{i}", SpotSize.LARGE) for i in range(1)])
        return Floor(n, spots)
    return ParkingLot([floor(1), floor(2)],
                      parking or FirstFit(), pricing or TieredHourly())


def acceptance() -> None:
    # FR happy path: park 2h -> due -> pay -> exit; spot frees (car = MEDIUM: 80 + 100)
    lot = build_lot()
    t = lot.park(Vehicle("KA-01-1234", VehicleType.CAR), now=0.0)
    assert t is not None
    assert lot.amount_due(t.ticket_id, now=2 * HOUR) == 180.0
    p = lot.pay(t.ticket_id, PaymentMethod.UPI, now=2 * HOUR)
    assert p.amount == 180.0
    lot.exit_lot(t.ticket_id, now=2 * HOUR)
    assert lot.available(SpotSize.MEDIUM) == 6          # freed (FR-6)
    print("happy  park -> due -> pay -> exit; spot freed            ✔")

    # FR-4: lot full -> None (expected flow, NOT an exception)
    lot = build_lot()
    trucks = [lot.park(Vehicle(f"TRK-{i}", VehicleType.TRUCK), now=0) for i in range(3)]
    assert trucks[0] and trucks[1] and trucks[2] is None
    print("FR-4   third truck turned away with None, no exception   ✔")

    # FR-9: the three exceptions guard the CONTRACT (contrast FR-4)
    lot = build_lot()
    t = lot.park(Vehicle("KA-03-9", VehicleType.CAR), now=0)
    for attempt, exc in [
        (lambda: lot.exit_lot(t.ticket_id, HOUR), UnpaidExitError),       # exit unpaid
        (lambda: lot.pay("T-9999", PaymentMethod.CASH, HOUR), InvalidTicketError),
    ]:
        try:
            attempt(); raise AssertionError("should have raised")
        except exc:
            pass
    lot.pay(t.ticket_id, PaymentMethod.CARD, now=HOUR)
    try:
        lot.pay(t.ticket_id, PaymentMethod.CASH, now=HOUR)                # pay twice
        raise AssertionError("should have raised")
    except AlreadyPaidError:
        pass
    lot.exit_lot(t.ticket_id, now=HOUR)
    try:
        lot.exit_lot(t.ticket_id, now=HOUR)                              # reuse ticket
        raise AssertionError("should have raised")
    except InvalidTicketError:
        pass
    print("FR-9   unpaid / unknown / double-pay / reuse all raised  ✔")

    # SpotStatus's third state: OUT_OF_ORDER (a bool can't say this)
    lot = build_lot()
    lot.floors[0].spots[2].status = SpotStatus.OUT_OF_ORDER   # F1-M0 leaks oil
    t = lot.park(Vehicle("KA-04-1", VehicleType.CAR), now=0)
    assert t.spot_id != "F1-M0"
    assert lot.available(SpotSize.MEDIUM) == 4                # 6 - 1 broken - 1 taken
    print("State  OUT_OF_ORDER spot skipped; availability correct   ✔")

    # FR-7: availability per size, per floor and total
    lot = build_lot()
    for i in range(4):
        lot.park(Vehicle(f"CAR-{i}", VehicleType.CAR), now=0)
    assert lot.per_floor(SpotSize.MEDIUM) == {1: 0, 2: 2}
    assert lot.available(SpotSize.MEDIUM) == 2
    print("FR-7   per-floor and total availability reported         ✔")

    # FR-8a: swap the parking strategy -> different placement, zero edits
    first = build_lot(parking=FirstFit())
    spread = build_lot(parking=LeastCrowded())
    for lot in (first, spread):
        for i in range(4):
            lot.park(Vehicle(f"V{i}", VehicleType.CAR), now=0)
    assert first.per_floor(SpotSize.MEDIUM)[1] == 0           # floor 1 exhausted first
    assert spread.per_floor(SpotSize.MEDIUM) == {1: 1, 2: 1}  # spread alternates
    print("FR-8a  FirstFit vs LeastCrowded — placement swapped      ✔")

    # FR-8b: swap pricing -> same stay, different bill
    tiered = build_lot(pricing=TieredHourly())
    flat = build_lot(pricing=WeekendFlat())
    bike = lambda: Vehicle("KA-02-7", VehicleType.BIKE)
    tt = tiered.park(bike(), now=0)
    ff = flat.park(bike(), now=0)
    assert tiered.amount_due(tt.ticket_id, 3 * HOUR) == 210   # 50 + 2*80
    assert flat.amount_due(ff.ticket_id, 3 * HOUR) == 100
    print("FR-8b  TieredHourly ₹210 vs WeekendFlat ₹100, same stay  ✔")

    # Repository seam: the service talks to a contract, not a dict
    lot = build_lot()
    t = lot.park(Vehicle("KA-09-1", VehicleType.BIKE), now=0)
    assert lot.tickets.find(t.ticket_id) is t                # save/find round-trips
    assert lot.payments.exists(t.ticket_id) is False         # pay-once query
    print("Repo   service reads tickets/payments via repositories   ✔")

    print("\nacceptance: all green ✔")


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "play":
        from cli import play
        play()
    else:
        acceptance()
