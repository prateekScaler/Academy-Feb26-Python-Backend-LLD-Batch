"""
LLD-25 · Parking Lot — the complete implementation we code live.

Run:  python3 01_parking_lot.py        # scripted demos, all assert green

Every line traces back to an LLD-24 decision:
  VehicleType + SpotSize + SPOT_SIZE_FOR  <- FR-2 — two concepts, one mapping (policy as DATA)
  Spot (size + SpotStatus, can_fit)       <- FR-2/6 — the Cell analogue, with a third state
  Floor (identity + free-counts)          <- FR-1/7 — earns class-hood, unlike TTT's rows
  Ticket (the record)                     <- FR-3 — parking's Move: billing, audit, replay
  park() -> Ticket | None                 <- FR-4 — lot-full is EXPECTED flow, not exceptional
  pay-once-then-exit, 3 exceptions        <- FR-9 — contract violations DO raise
  ParkingStrategy / PricingStrategy       <- FR-8 — two open variables from minute one
"""

from __future__ import annotations

import math
from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum
from itertools import count


# === Enums — three small named sets =========================================
class VehicleType(Enum):
    BIKE = "bike"
    CAR = "car"
    TRUCK = "truck"


class SpotSize(Enum):
    SMALL = "small"
    MEDIUM = "medium"
    LARGE = "large"


class SpotStatus(Enum):
    FREE = "free"
    OCCUPIED = "occupied"
    OUT_OF_ORDER = "out_of_order"    # the third state a bool cannot hold


class PaymentMethod(Enum):
    CASH = "cash"
    CARD = "card"
    UPI = "upi"


# FR-2's rule as DATA: "can a bike take a car spot?" is now a one-line policy
# change here — not an edit to any class. Adding SCOOTER/BUS is one entry each.
SPOT_SIZE_FOR = {
    VehicleType.BIKE: SpotSize.SMALL,
    VehicleType.CAR: SpotSize.MEDIUM,
    VehicleType.TRUCK: SpotSize.LARGE,
}


# === Errors — only for contract violations (FR-4 returns None instead) ======
class InvalidTicketError(Exception):
    """Unknown or already-used ticket — unlike a full lot, this IS exceptional."""


class AlreadyPaidError(Exception):
    """A ticket is paid exactly once (FR-9)."""


class UnpaidExitError(Exception):
    """The gate opens only for a paid ticket (FR-9)."""


@dataclass(frozen=True)
class Vehicle:
    plate: str
    kind: VehicleType


# === Spot — the Cell analogue: two facts + the rules relating them ===========
@dataclass
class Spot:
    spot_id: str
    size: SpotSize
    status: SpotStatus = SpotStatus.FREE

    def is_free(self) -> bool:
        return self.status is SpotStatus.FREE

    def can_fit(self, vehicle: Vehicle) -> bool:
        return self.is_free() and self.size == SPOT_SIZE_FOR[vehicle.kind]

    def occupy(self) -> None:
        self.status = SpotStatus.OCCUPIED

    def free(self) -> None:
        self.status = SpotStatus.FREE


# === Floor — identity + its own queries (FR-7) ===============================
class Floor:
    def __init__(self, number: int, spots: list[Spot]):
        self.number = number
        self.spots = spots

    def free_spots(self, size: SpotSize) -> list[Spot]:
        return [s for s in self.spots if s.is_free() and s.size == size]

    def free_count(self, size: SpotSize) -> int:
        return len(self.free_spots(size))


# === Ticket & Payment — the records (parking's Move) =========================
@dataclass
class Ticket:
    ticket_id: str
    vehicle: Vehicle
    floor_no: int
    spot_id: str
    entry_time: float
    exit_time: float | None = None


@dataclass(frozen=True)
class Payment:
    payment_id: str
    ticket_id: str
    amount: float
    method: PaymentMethod
    paid_at: float


# === Strategy 1: where to put the vehicle (FR-8) =============================
class ParkingStrategy(ABC):
    @abstractmethod
    def pick(self, floors: list[Floor], vehicle: Vehicle) -> tuple[Floor, Spot] | None: ...


class FirstFit(ParkingStrategy):
    """First free spot of the right size on the lowest floor — minimises walking."""

    def pick(self, floors: list[Floor], vehicle: Vehicle) -> tuple[Floor, Spot] | None:
        for floor in floors:
            for spot in floor.spots:
                if spot.can_fit(vehicle):
                    return floor, spot
        return None


class LeastCrowded(ParkingStrategy):
    """Floor with the most free spots of that size — spreads congestion."""

    def pick(self, floors: list[Floor], vehicle: Vehicle) -> tuple[Floor, Spot] | None:
        size = SPOT_SIZE_FOR[vehicle.kind]
        best = max(floors, key=lambda f: f.free_count(size), default=None)
        if best is None or best.free_count(size) == 0:
            return None
        return best, best.free_spots(size)[0]


# === Strategy 2: what to charge (FR-5 + FR-8) ================================
class PricingStrategy(ABC):
    @abstractmethod
    def fee(self, size: SpotSize, seconds: float) -> float:
        """You pay for the spot you occupied, not the vehicle you drove."""


class TieredHourly(PricingStrategy):
    """First hour at one rate, every extra hour at another — per spot size."""

    RATES = {  # size: (first_hour, each_extra_hour)
        SpotSize.SMALL: (50, 80),
        SpotSize.MEDIUM: (80, 100),
        SpotSize.LARGE: (100, 120),
    }

    def fee(self, size: SpotSize, seconds: float) -> float:
        hours = max(1, math.ceil(seconds / 3600))   # minimum 1 hour, round up
        first, extra = self.RATES[size]
        return first + (hours - 1) * extra


class WeekendFlat(PricingStrategy):
    """Flat ticket regardless of duration — mall promo."""

    def fee(self, size: SpotSize, seconds: float) -> float:
        return 100.0


# === ParkingLot — the orchestrator ===========================================
class ParkingLot:
    def __init__(self, floors: list[Floor],
                 parking: ParkingStrategy, pricing: PricingStrategy):
        self.floors = floors
        self.parking = parking
        self.pricing = pricing
        self._active: dict[str, Ticket] = {}
        self._payments: dict[str, Payment] = {}
        self._ids = count(1)

    # --- commands ---------------------------------------------------------
    def park(self, vehicle: Vehicle, now: float) -> Ticket | None:
        """None when no suitable spot exists — expected flow, not an error."""
        picked = self.parking.pick(self.floors, vehicle)
        if picked is None:
            return None
        floor, spot = picked
        spot.occupy()
        ticket = Ticket(f"T-{next(self._ids):04d}", vehicle,
                        floor.number, spot.spot_id, entry_time=now)
        self._active[ticket.ticket_id] = ticket
        return ticket

    def pay(self, ticket_id: str, method: PaymentMethod, now: float) -> Payment:
        ticket = self._require_active(ticket_id)
        if ticket_id in self._payments:
            raise AlreadyPaidError(f"{ticket_id} is already paid (FR-9: pay exactly once)")
        amount = self.pricing.fee(self._spot_of(ticket).size, now - ticket.entry_time)
        payment = Payment(f"P-{next(self._ids):04d}", ticket_id, amount, method, now)
        self._payments[ticket_id] = payment
        return payment

    def exit_lot(self, ticket_id: str, now: float) -> Ticket:
        ticket = self._require_active(ticket_id)
        if ticket_id not in self._payments:
            raise UnpaidExitError(f"{ticket_id} is unpaid — the gate stays down")
        self._spot_of(ticket).free()             # FR-6: free the moment it leaves
        ticket.exit_time = now
        del self._active[ticket_id]
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
        ticket = self._active.get(ticket_id)
        if ticket is None:
            raise InvalidTicketError(f"unknown or already-used ticket: {ticket_id}")
        return ticket

    def _spot_of(self, ticket: Ticket) -> Spot:
        floor = next(f for f in self.floors if f.number == ticket.floor_no)
        return next(s for s in floor.spots if s.spot_id == ticket.spot_id)


# === Demo helpers ============================================================
def build_lot(parking: ParkingStrategy | None = None,
              pricing: PricingStrategy | None = None) -> ParkingLot:
    """2 floors x (2 small + 3 medium + 1 large)."""
    def floor(n: int) -> Floor:
        spots = ([Spot(f"F{n}-S{i}", SpotSize.SMALL) for i in range(2)]
                 + [Spot(f"F{n}-M{i}", SpotSize.MEDIUM) for i in range(3)]
                 + [Spot(f"F{n}-L{i}", SpotSize.LARGE) for i in range(1)])
        return Floor(n, spots)
    return ParkingLot([floor(1), floor(2)],
                      parking or FirstFit(), pricing or TieredHourly())


def banner(t: str) -> None:
    print(f"\n--- {t} ---")


HOUR = 3600.0


def demo_happy_path() -> None:
    banner("happy path: park 2h -> pay -> exit (car = MEDIUM: 80 + 100)")
    lot = build_lot()
    t = lot.park(Vehicle("KA-01-1234", VehicleType.CAR), now=0.0)
    assert t is not None
    print(f"parked: {t.ticket_id} -> floor {t.floor_no}, spot {t.spot_id}")
    print(f"due at 2h: ₹{lot.amount_due(t.ticket_id, now=2 * HOUR):.0f}")
    p = lot.pay(t.ticket_id, PaymentMethod.UPI, now=2 * HOUR)
    lot.exit_lot(t.ticket_id, now=2 * HOUR)
    print(f"paid ₹{p.amount:.0f} by {p.method.value}; exited")
    assert p.amount == 180.0
    assert lot.available(SpotSize.MEDIUM) == 6      # spot freed (FR-6)


def demo_lot_full() -> None:
    banner("FR-4: lot full -> None (expected flow, no exception)")
    lot = build_lot()
    trucks = [lot.park(Vehicle(f"TRK-{i}", VehicleType.TRUCK), now=0) for i in range(3)]
    print("results:", [t.ticket_id if t else None for t in trucks])
    assert trucks[0] and trucks[1] and trucks[2] is None
    print("third truck politely turned away ✔")


def demo_contract_violations() -> None:
    banner("FR-9: the exceptions guard the CONTRACT (contrast FR-4)")
    lot = build_lot()
    t = lot.park(Vehicle("KA-03-9", VehicleType.CAR), now=0)
    for attempt, exc in [
        (lambda: lot.exit_lot(t.ticket_id, HOUR), UnpaidExitError),       # exit unpaid
        (lambda: lot.pay("T-9999", PaymentMethod.CASH, HOUR), InvalidTicketError),
    ]:
        try:
            attempt()
        except exc as e:
            print(f"rejected ({exc.__name__}): {e}")
    lot.pay(t.ticket_id, PaymentMethod.CARD, now=HOUR)
    try:
        lot.pay(t.ticket_id, PaymentMethod.CASH, now=HOUR)                # pay twice
    except AlreadyPaidError as e:
        print(f"rejected (AlreadyPaidError): {e}")
    lot.exit_lot(t.ticket_id, now=HOUR)
    try:
        lot.exit_lot(t.ticket_id, now=HOUR)                               # reuse ticket
    except InvalidTicketError as e:
        print(f"rejected (InvalidTicketError): {e}")


def demo_out_of_order() -> None:
    banner("SpotStatus's third state: OUT_OF_ORDER (a bool can't say this)")
    lot = build_lot()
    lot.floors[0].spots[2].status = SpotStatus.OUT_OF_ORDER   # F1-M0 leaks oil
    t = lot.park(Vehicle("KA-04-1", VehicleType.CAR), now=0)
    print(lot.render())
    print(f"car skipped the broken spot -> {t.spot_id}")
    assert t.spot_id != "F1-M0"
    assert lot.available(SpotSize.MEDIUM) == 4     # 6 - 1 broken - 1 taken


def demo_per_floor() -> None:
    banner("FR-7: availability per size, per floor and total")
    lot = build_lot()
    for i in range(4):
        lot.park(Vehicle(f"CAR-{i}", VehicleType.CAR), now=0)
    print(lot.render())
    print(f"medium spots per floor: { {f: c for f, c in lot.per_floor(SpotSize.MEDIUM).items()} }"
          f"  total: {lot.available(SpotSize.MEDIUM)}")
    assert lot.available(SpotSize.MEDIUM) == 2


def demo_strategy_swap() -> None:
    banner("FR-8a: swap the parking strategy -> different placement, zero edits")
    first = build_lot(parking=FirstFit())
    spread = build_lot(parking=LeastCrowded())
    for lot, name in [(first, "FirstFit"), (spread, "LeastCrowded")]:
        placed = [lot.park(Vehicle(f"V{i}", VehicleType.CAR), now=0).floor_no for i in range(4)]
        print(f"{name:13s}: cars went to floors {placed}")
    assert first.per_floor(SpotSize.MEDIUM)[1] == 0           # floor 1 exhausted first
    assert spread.per_floor(SpotSize.MEDIUM) == {1: 1, 2: 1}  # spread alternates


def demo_pricing_swap() -> None:
    banner("FR-8b: swap pricing -> same stay, different bill")
    for pricing, label in [(TieredHourly(), "TieredHourly"), (WeekendFlat(), "WeekendFlat")]:
        lot = build_lot(pricing=pricing)
        t = lot.park(Vehicle("KA-02-7", VehicleType.BIKE), now=0)
        print(f"{label:12s}: 3h bike (SMALL) -> ₹{lot.amount_due(t.ticket_id, 3 * HOUR):.0f}")


if __name__ == "__main__":
    demo_happy_path()
    demo_lot_full()
    demo_contract_violations()
    demo_out_of_order()
    demo_per_floor()
    demo_strategy_swap()
    demo_pricing_swap()
    print("\nall demos passed ✔")
