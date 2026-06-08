"""
LLD-21 · Example 01 — Parking Lot, the 90-minute walkthrough.

Run:  python3 01_parking_lot_walkthrough.py

This is the version we build live in class, on the clock. It follows the
7-step playbook exactly:

    Step 1 — Clarify        (assumed, see comments at top)
    Step 2 — Requirements   (FR + NFR pinned in this docstring)
    Step 3 — Entities       (the classes below)
    Step 4 — APIs           (signatures defined before bodies, scroll down)
    Step 5 — Code           (happy path first, then 3 edge cases)
    Step 6 — Demo           (the if __name__ == "__main__" block at the bottom)
    Step 7 — Trade-offs     (printed at the end of the demo)

# === Step 1 — Clarify (questions the interviewer answered) ====================
#   Q: Vehicle types?          A: Car, Bike, Truck.
#   Q: Multiple floors?        A: Yes, 1 lot, N floors — let's say 2 floors.
#   Q: Pricing?                A: Flat hourly per vehicle type.
#   Q: Persistence?            A: In-memory only.
#   Q: Concurrent users?       A: Single-threaded for now.
#   Q: Slot mismatch?          A: A bike can't park in a car slot. Lot-full = reject.

# === Step 2 — Requirements ===================================================
#   FR:  park(vehicle) -> Ticket | None
#        unpark(ticket, time_out) -> charge: float
#        available_slots(VehicleType) -> int
#   NFR: in-memory, single-threaded, <=200 slots, INR only.

# === Step 3 — Entities & relationships =======================================
#   ParkingLot — orchestrator
#     ◇ many Floor          (aggregation; floors outlive the lot logically)
#     uses ParkingStrategy  (Strategy)
#     uses PricingStrategy  (Strategy)
#   Floor
#     ◆ many Slot           (composition; kill the floor, kill its slots)
#   Slot
#     kind: VehicleType
#     occupied: bool
#   Vehicle  (Car / Bike / Truck via VehicleType enum)
#   Ticket   (just an id + reference to slot + time_in)
"""

from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum
from typing import Protocol
import time


# ===== Step 4 — APIs (signatures only first; bodies come below) ===============
class VehicleType(Enum):
    CAR = "car"
    BIKE = "bike"
    TRUCK = "truck"


@dataclass(frozen=True)
class Vehicle:
    plate: str
    kind: VehicleType


@dataclass
class Slot:
    slot_id: str
    kind: VehicleType
    occupied: bool = False


@dataclass
class Floor:
    floor_id: str
    slots: list[Slot] = field(default_factory=list)

    def free_slots(self, kind: VehicleType) -> list[Slot]:
        return [s for s in self.slots if not s.occupied and s.kind == kind]


@dataclass
class Ticket:
    ticket_id: str
    slot: Slot
    floor: Floor
    time_in: float


# ===== Strategy: where to put the car ========================================
class ParkingStrategy(Protocol):
    def pick(self, floors: list[Floor], kind: VehicleType) -> tuple[Floor, Slot] | None: ...


class FirstFit:
    """Take the first free slot on the lowest-numbered floor."""

    def pick(self, floors: list[Floor], kind: VehicleType):
        for f in floors:
            free = f.free_slots(kind)
            if free:
                return f, free[0]
        return None


class LeastCrowded:
    """Pick the floor with the most free slots of that kind. Spreads load."""

    def pick(self, floors: list[Floor], kind: VehicleType):
        ranked = sorted(floors, key=lambda f: -len(f.free_slots(kind)))
        for f in ranked:
            free = f.free_slots(kind)
            if free:
                return f, free[0]
        return None


# ===== Strategy: pricing =====================================================
class PricingStrategy(Protocol):
    def charge(self, kind: VehicleType, seconds: float) -> float: ...


class FlatHourly:
    RATES = {VehicleType.CAR: 40, VehicleType.BIKE: 20, VehicleType.TRUCK: 80}

    def charge(self, kind: VehicleType, seconds: float) -> float:
        hours = max(1.0, seconds / 3600.0)  # min 1 hour billing
        return self.RATES[kind] * hours


# ===== The orchestrator ======================================================
class ParkingLot:
    def __init__(
        self,
        floors: list[Floor],
        parking: ParkingStrategy,
        pricing: PricingStrategy,
    ):
        self.floors = floors
        self.parking = parking
        self.pricing = pricing
        self.active: dict[str, Ticket] = {}

    def park(self, vehicle: Vehicle, time_in: float | None = None) -> Ticket | None:
        time_in = time.time() if time_in is None else time_in
        choice = self.parking.pick(self.floors, vehicle.kind)
        if choice is None:
            return None
        floor, slot = choice
        slot.occupied = True
        ticket = Ticket(
            ticket_id=f"T-{vehicle.plate}-{int(time_in)}",
            slot=slot,
            floor=floor,
            time_in=time_in,
        )
        self.active[ticket.ticket_id] = ticket
        return ticket

    def unpark(self, ticket_id: str, time_out: float | None = None) -> float:
        time_out = time.time() if time_out is None else time_out
        if ticket_id not in self.active:
            raise KeyError(f"unknown ticket: {ticket_id}")
        ticket = self.active.pop(ticket_id)
        ticket.slot.occupied = False
        return self.pricing.charge(ticket.slot.kind, time_out - ticket.time_in)

    def available(self, kind: VehicleType) -> int:
        return sum(len(f.free_slots(kind)) for f in self.floors)


# ===== Step 5 + 6 — Demo (happy path, 3 edges) ===============================
def build_demo_lot() -> ParkingLot:
    """A small lot: 2 floors × (3 car, 2 bike, 1 truck) slots each."""
    floors = []
    for fid in range(1, 3):
        slots = (
            [Slot(f"F{fid}-C{i}", VehicleType.CAR) for i in range(3)]
            + [Slot(f"F{fid}-B{i}", VehicleType.BIKE) for i in range(2)]
            + [Slot(f"F{fid}-T{i}", VehicleType.TRUCK) for i in range(1)]
        )
        floors.append(Floor(f"F{fid}", slots))
    return ParkingLot(floors, FirstFit(), FlatHourly())


def demo_happy_path():
    print("\n--- Happy path: park a car, leave 2 hours, unpark, charge ---")
    lot = build_demo_lot()
    t_in = 1_000_000.0
    ticket = lot.park(Vehicle("KA-01-9876", VehicleType.CAR), time_in=t_in)
    assert ticket is not None
    print(f"  parked: ticket={ticket.ticket_id}  slot={ticket.slot.slot_id}")
    charge = lot.unpark(ticket.ticket_id, time_out=t_in + 2 * 3600)
    print(f"  unparked. charge = INR {charge:.0f}  (expected 80)")


def demo_edge_lot_full():
    print("\n--- Edge case 1: lot is full for trucks ---")
    lot = build_demo_lot()  # only 2 truck slots total
    lot.park(Vehicle("TRK-1", VehicleType.TRUCK), time_in=1)
    lot.park(Vehicle("TRK-2", VehicleType.TRUCK), time_in=2)
    third = lot.park(Vehicle("TRK-3", VehicleType.TRUCK), time_in=3)
    print(f"  third truck parked? {third is not None}  (expected False)")
    print(f"  available trucks now: {lot.available(VehicleType.TRUCK)} (expected 0)")


def demo_edge_unknown_ticket():
    print("\n--- Edge case 2: unparking with an unknown ticket id ---")
    lot = build_demo_lot()
    try:
        lot.unpark("NOPE")
    except KeyError as e:
        print(f"  got expected KeyError: {e}")


def demo_edge_swap_strategy():
    print("\n--- Edge case 3: swap the placement strategy at runtime ---")
    floors = build_demo_lot().floors  # reuse the lot layout
    lot = ParkingLot(floors, LeastCrowded(), FlatHourly())  # new strategy
    for plate in ["A", "B", "C"]:
        lot.park(Vehicle(plate, VehicleType.CAR), time_in=1)
    by_floor = {f.floor_id: sum(s.occupied for s in f.slots) for f in floors}
    print(f"  cars per floor with LeastCrowded: {by_floor}  (expected spread)")


def step7_tradeoffs():
    print(
        """
--- Step 7 — Trade-offs you would say out loud ---
  Persistence: ParkingLot state is dict-in-memory. To persist:
    * SlotRepository / FloorRepository per aggregate
    * load floors at boot, persist Slot.occupied transitions
  Concurrency: ParkingLot is single-threaded. For concurrent users:
    * lock per Floor (most contention is within a floor)
    * OR: serialize park/unpark through a single queue
    * (DO NOT use a global ParkingLot-level lock — it serialises everything)
  Extensions:
    * Reserved EV slots: new VehicleType.EV + a new ParkingStrategy that
      prefers EV slots when an EV arrives, falls back otherwise.
    * Dynamic pricing: new PricingStrategy class. Zero changes elsewhere.
    * Multi-lot: introduce ParkingLotRegistry that picks a lot by location.
"""
    )


if __name__ == "__main__":
    demo_happy_path()
    demo_edge_lot_full()
    demo_edge_unknown_ticket()
    demo_edge_swap_strategy()
    step7_tradeoffs()
