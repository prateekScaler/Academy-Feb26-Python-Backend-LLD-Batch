"""
06 — Testing time: inject the clock
===================================

Code that calls datetime.now() DIRECTLY is untestable: the answer changes
every run, and you cannot test "what happens at 09:00 tomorrow" without
waiting until 09:00 tomorrow.

The fix is the LLD-30 pattern — DEPEND ON A CLOCK, not on the wall:

    class Clock:      now() -> real aware-UTC time      (production)
    class FakeClock:  now() -> whatever the test says   (tests)

Now "time travel" is just constructing a FakeClock — no sleeping, no
patching the OS, no flaky midnight failures.
(Same trick for randomness: inject random.Random(seed), not the module.)

Run me:
    pytest -v 06_testing_time.py
    python3 06_testing_time.py        # same thing — it hands over to pytest

Needs:  pip install pytest
"""


from datetime import datetime, timedelta, timezone


# ── the clocks ──

class Clock:
    """Production: real, aware, UTC."""
    def now(self) -> datetime:
        return datetime.now(timezone.utc)


class FakeClock:
    """Tests: frozen — and advanceable — time."""
    def __init__(self, t: datetime):
        self.t = t
    def now(self) -> datetime:
        return self.t
    def advance(self, **kw) -> None:
        self.t += timedelta(**kw)


# ── code under test: LLD-30's reminder, done testably ──

class Reminder:
    def __init__(self, event_start: datetime, minutes_before: int):
        self.fire_at = event_start - timedelta(minutes=minutes_before)

    def is_due(self, clock) -> bool:
        return clock.now() >= self.fire_at


TOKEN_LEEWAY = timedelta(seconds=60)     # the skew lesson from the time quiz

def token_expired(expiry: datetime, clock) -> bool:
    return clock.now() > expiry + TOKEN_LEEWAY


# ─────────────────────────── the tests ───────────────────────────

MEETING = datetime(2026, 7, 6, 10, 0, tzinfo=timezone.utc)   # Mon 10:00


def test_reminder_is_not_due_before_its_fire_time():
    reminder = Reminder(MEETING, minutes_before=15)
    clock = FakeClock(datetime(2026, 7, 6, 9, 30, tzinfo=timezone.utc))

    assert not reminder.is_due(clock)


def test_reminder_fires_exactly_at_minutes_before_boundary():
    reminder = Reminder(MEETING, minutes_before=15)
    clock = FakeClock(datetime(2026, 7, 6, 9, 45, tzinfo=timezone.utc))

    assert reminder.is_due(clock)               # >= : the boundary fires


def test_advancing_the_fake_clock_is_time_travel():
    reminder = Reminder(MEETING, minutes_before=15)
    clock = FakeClock(datetime(2026, 7, 6, 9, 0, tzinfo=timezone.utc))

    assert not reminder.is_due(clock)
    clock.advance(minutes=45)                   # no sleep(2700)!
    assert reminder.is_due(clock)


def test_token_within_leeway_is_still_accepted():
    expiry = datetime(2026, 7, 6, 12, 0, tzinfo=timezone.utc)
    clock = FakeClock(expiry + timedelta(seconds=30))    # 30s past expiry

    assert not token_expired(expiry, clock)     # inside the 60s leeway


def test_token_past_leeway_is_rejected():
    expiry = datetime(2026, 7, 6, 12, 0, tzinfo=timezone.utc)
    clock = FakeClock(expiry + timedelta(seconds=61))

    assert token_expired(expiry, clock)


def test_seeded_randomness_makes_flaky_tests_deterministic():
    import random
    # Inject a SEEDED generator the same way we inject the clock.
    rng = random.Random(42)
    rolls = [rng.randint(1, 6) for _ in range(5)]

    assert rolls == [6, 1, 1, 6, 3]             # same seed ⇒ same "random"


if __name__ == "__main__":
    # This file IS a pytest suite — running it directly just hands over to pytest.
    try:
        import pytest
    except ImportError:
        raise SystemExit("This is a pytest test file. Install pytest first:  pip install pytest")
    raise SystemExit(pytest.main([__file__, "-v", "-p", "no:cacheprovider"]))
