"""
04 — Fixtures: Arrange once, reuse everywhere
=============================================

Every test in file 02 began `group = ExpenseGroup([...])` — the same
Arrange, copy-pasted. A FIXTURE extracts that setup:

    @pytest.fixture
    def empty_lot():
        return ParkingLot(spots=2)

    def test_park(empty_lot):        # ← ask for it BY NAME as a parameter
        ...

pytest sees the parameter name, calls the fixture, and hands you the value.
Fixtures can also build on each other — `full_lot` composes the same
lot class, pre-filled — so each test just names the world it needs.

Run me:
    pytest -v 04_fixtures_parking.py
    python3 04_fixtures_parking.py        # same thing — it hands over to pytest

Needs:  pip install pytest
"""

import pytest


# ── code under test: a miniature LLD-24/25 parking lot ──

class Ticket:
    def __init__(self, spot: int, plate: str):
        self.spot, self.plate = spot, plate


class ParkingLot:
    def __init__(self, spots: int):
        self.free = list(range(spots))
        self.occupied: dict[int, str] = {}

    def park(self, plate: str) -> Ticket | None:
        """A full lot is an EXPECTED outcome → return None, don't raise.
        (The LLD-24 lesson: exceptions are for rule violations, not
        for answers the caller asked about.)"""
        if not self.free:
            return None
        spot = self.free.pop(0)
        self.occupied[spot] = plate
        return Ticket(spot, plate)

    def unpark(self, ticket: Ticket) -> None:
        del self.occupied[ticket.spot]
        self.free.append(ticket.spot)


# ─────────────────────────── fixtures ───────────────────────────

@pytest.fixture
def empty_lot():
    """A fresh 2-spot lot for every test that asks for one."""
    return ParkingLot(spots=2)


@pytest.fixture
def full_lot():
    """Fixtures compose: build on the same idea, pre-filled."""
    lot = ParkingLot(spots=2)
    lot.park("KA-01-AA-1111")
    lot.park("KA-01-BB-2222")
    return lot


# ─────────────────────────── the tests ───────────────────────────

def test_parking_assigns_the_first_free_spot(empty_lot):
    ticket = empty_lot.park("KA-01-AA-1111")

    assert ticket is not None
    assert ticket.spot == 0


def test_full_lot_returns_none_not_an_exception(full_lot):
    ticket = full_lot.park("KA-01-CC-3333")

    assert ticket is None                    # expected outcome, not an error


def test_unparking_frees_the_spot_for_reuse(full_lot):
    # Arrange (extra): pull out one of the parked cars' tickets
    spot0_plate = full_lot.occupied[0]
    ticket = Ticket(0, spot0_plate)

    full_lot.unpark(ticket)
    new_ticket = full_lot.park("KA-01-DD-4444")

    assert new_ticket is not None
    assert new_ticket.spot == 0              # the freed spot is reused


def test_each_test_gets_a_fresh_lot(empty_lot):
    # empty_lot is NOT the one previous tests used — no shared state,
    # so tests can run in any order (the I in FIRST: Independent).
    assert empty_lot.free == [0, 1]


if __name__ == "__main__":
    # This file IS a pytest suite — running it directly just hands over to pytest.
    try:
        import pytest
    except ImportError:
        raise SystemExit("This is a pytest test file. Install pytest first:  pip install pytest")
    raise SystemExit(pytest.main([__file__, "-v", "-p", "no:cacheprovider"]))
