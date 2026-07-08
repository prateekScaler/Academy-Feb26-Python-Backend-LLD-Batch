"""
08 — HOMEWORK: you write the tests
==================================

The code under test is COMPLETE and CORRECT — your job is only to test it.
Every exercise below is a `pytest.skip(...)` stub: delete the skip line and
write the real test. Start with everything skipped:

    pytest -v 08_homework.py        ->  s s s s s s s s s s s s  (12 skips)

…and finish with everything green:

    pytest -v 08_homework.py        ->  ............            (all PASSED)

Rules of the game (today's class):
  * AAA           — Arrange / Act / Assert, one behaviour per test
  * Naming        — test_<the_behaviour_in_plain_english>
  * parametrize   — boundary tables, not copy-paste     (model: file 03)
  * fixtures      — extract the shared Arrange          (model: file 04)
  * raises        — rule violations raise; expected outcomes return values
                                                        (model: files 04, 05)
  * money         — integer paise, exact equality        (model: file 05)
  * time          — inject the clock, never date/datetime.now()
                                                        (model: file 06)

Needs:  pip install pytest
"""

import pytest
from datetime import datetime, time, timedelta, timezone


# ═══════════════════════ the code under test ═══════════════════════
# A cinema's booking backend — four small, correct units.


def refund_percent(hours_before_show: float) -> int:
    """Cancellation policy: 100% refund if more than 24h before the show,
    50% if between 2h and 24h (inclusive), 0% if less than 2h."""
    if hours_before_show > 24:
        return 100
    if hours_before_show >= 2:
        return 50
    return 0


class InsufficientBalance(Exception):
    def __init__(self, needed_paise: int, available_paise: int):
        super().__init__(f"need {needed_paise}, have {available_paise}")
        self.needed = needed_paise
        self.available = available_paise


class GiftCard:
    """Stored value in integer paise. Spending more than the balance is a
    RULE VIOLATION -> raises. A failed spend must not change the balance."""

    def __init__(self, balance_paise: int = 0):
        self.balance = balance_paise

    def spend(self, amount_paise: int) -> None:
        if amount_paise > self.balance:
            raise InsufficientBalance(amount_paise, self.balance)
        self.balance -= amount_paise


class ScreenSeats:
    """Seat allocation for one screen. A sold-out screen is an EXPECTED
    OUTCOME -> book() returns None (not an exception)."""

    def __init__(self, seats: int):
        self.free = list(range(1, seats + 1))
        self.taken: dict[int, str] = {}

    def book(self, customer: str) -> int | None:
        if not self.free:
            return None
        seat = self.free.pop(0)
        self.taken[seat] = customer
        return seat

    def release(self, seat: int) -> None:
        del self.taken[seat]
        self.free.append(seat)


MATINEE_START = time(12, 0)   # matinee pricing applies 12:00–14:59 UTC
MATINEE_END = time(15, 0)     # (end exclusive)

def is_matinee(clock) -> bool:
    """Matinee discount window. Depends on an injected clock — the code
    never calls datetime.now() itself (the file-06 pattern)."""
    now = clock.now()
    return MATINEE_START <= now.time() < MATINEE_END


class FakeClock:
    """Your time machine for exercises 10–12 (same as file 06)."""
    def __init__(self, t: datetime):
        self.t = t
    def now(self) -> datetime:
        return self.t
    def advance(self, **kw) -> None:
        self.t += timedelta(**kw)


# ═════════════════════════ the exercises ═════════════════════════
# Delete each `pytest.skip(...)` line and write the test it describes.


# ── Part 1 · AAA & naming (model: file 02) ──────────────────────────

def test_ex01_spending_reduces_the_balance():
    # Write the happy path for GiftCard.spend as clean AAA:
    #   Arrange a card with ₹500 (50_000 paise), Act: spend ₹120,
    #   Assert the balance is exactly ₹380 — in paise, exact equality.
    pytest.skip("TODO ex01: write me")


def test_ex02_rename_me_to_state_the_behaviour():
    # This test is written for you — but its NAME is useless.
    # Rename the function so a 2 AM CI failure explains itself.
    pytest.skip("TODO ex02: delete this line AND rename the test")
    card = GiftCard(balance_paise=10_000)
    card.spend(10_000)
    assert card.balance == 0        # spending the exact balance is allowed


# ── Part 2 · parametrize & boundaries (model: file 03) ──────────────

def test_ex03_refund_bands_parametrized():
    # Rewrite this as ONE parametrized test over a boundary table.
    #   @pytest.mark.parametrize("hours, expected", [...])
    # Pick the rows the way q-boundary taught you: both sides of each
    # cutoff (25/24/23 and 3/2/1) — think hard about what 24 and 2
    # should return, straight from the docstring.
    pytest.skip("TODO ex03: replace me with a @pytest.mark.parametrize test")


def test_ex04_zero_hours_is_a_boundary_too():
    # What does refund_percent(0) mean (cancelling as the show starts),
    # and what about a negative value (cancelling AFTER it started)?
    # Assert the current behaviour for both — sometimes writing the test
    # is how you DISCOVER the spec gap. Leave a one-line comment: is the
    # negative-hours behaviour a bug or a feature?
    pytest.skip("TODO ex04: write me")


# ── Part 3 · fixtures (model: file 04) ──────────────────────────────
# Write the two fixtures the next three tests need:
#
# @pytest.fixture
# def two_seat_screen():   -> a fresh ScreenSeats(seats=2)
#
# @pytest.fixture
# def sold_out_screen():   -> a ScreenSeats(seats=2) with both seats booked


def test_ex05_booking_assigns_the_lowest_free_seat():
    # Use the two_seat_screen fixture (ask for it by parameter name!).
    # Book once; assert the customer got seat 1.
    pytest.skip("TODO ex05: write me (and the two_seat_screen fixture)")


def test_ex06_sold_out_screen_returns_none_not_an_exception():
    # Use the sold_out_screen fixture. Booking a third customer must
    # return None — an expected outcome, not an error (the LLD-24 line).
    pytest.skip("TODO ex06: write me (and the sold_out_screen fixture)")


def test_ex07_released_seat_is_booked_again():
    # Use sold_out_screen: release seat 1, book a new customer,
    # assert they got seat 1. (Fixture gives you the same fresh world
    # no matter what ex06 did — that's Independence.)
    pytest.skip("TODO ex07: write me")


# ── Part 4 · errors by design (model: file 05) ──────────────────────

def test_ex08_overspending_raises_insufficient_balance():
    # Use `with pytest.raises(InsufficientBalance) as excinfo:` and then
    # assert on the error object: .needed and .available carry the numbers.
    pytest.skip("TODO ex08: write me")


def test_ex09_failed_spend_leaves_the_balance_untouched():
    # The other half of ex08: after the raise, the balance must be
    # exactly what it was. Error paths must not half-apply.
    pytest.skip("TODO ex09: write me")


# ── Part 5 · testing time (model: file 06) ──────────────────────────

def test_ex10_noon_is_matinee():
    # Freeze a FakeClock at exactly 12:00 UTC on any date and assert
    # is_matinee(clock) — 12:00 is the inclusive lower boundary.
    pytest.skip("TODO ex10: write me")


def test_ex11_three_pm_is_not_matinee():
    # Freeze at exactly 15:00 UTC — the EXCLUSIVE upper boundary.
    # (If you're tempted by 14:59 or 15:01 instead: which bug would
    # each of the three instants catch?)
    pytest.skip("TODO ex11: write me")


def test_ex12_advance_crosses_into_matinee():
    # Start the clock at 11:00, assert not matinee; advance(hours=1),
    # assert matinee. No sleep() — that's the whole point.
    pytest.skip("TODO ex12: write me")


# ── Stretch (no stub): your own code from this course ────────────────
# Pick your LLD-29 Splitwise engine (or LLD-25 ParkingLot) and write its
# first five tests in a new file: one conservation property, one
# parametrized boundary table, one fixture, one raises, one value-return.
# That file is the real homework — this one was the warm-up.


if __name__ == "__main__":
    try:
        import pytest as _pt
    except ImportError:
        raise SystemExit("This is a pytest test file. Install pytest first:  pip install pytest")
    raise SystemExit(_pt.main([__file__, "-v", "-p", "no:cacheprovider"]))
