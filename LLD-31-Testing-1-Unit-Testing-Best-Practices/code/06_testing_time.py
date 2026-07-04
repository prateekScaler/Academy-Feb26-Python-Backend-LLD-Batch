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
    python3 06_testing_time.py
    pytest -v 06_testing_time.py
"""

# ────────────────────────── run-anywhere shim ──────────────────────────
# In class we use the real `pytest`. This tiny stand-in only exists so the
# file also runs with plain `python3` on a machine without pytest. Skip it.
try:
    import pytest
except ImportError:
    class _Raises:
        def __init__(self, exc): self.exc = exc
        def __enter__(self): return self
        def __exit__(self, t, v, tb):
            assert t is not None and issubclass(t, self.exc), \
                f"expected {self.exc.__name__}, got {t.__name__ if t else 'no error'}"
            self.value = v
            return True
    class _Approx:
        def __init__(self, v, tol): self.v, self.tol = v, tol
        def __eq__(self, o): return abs(o - self.v) <= self.tol
        def __repr__(self): return f"approx({self.v})"
    class _Mark:
        @staticmethod
        def parametrize(names, cases):
            def deco(fn): fn._params = (names, cases); return fn
            return deco
    class pytest:
        mark = _Mark
        @staticmethod
        def raises(exc): return _Raises(exc)
        @staticmethod
        def approx(v, rel=None, abs=None):
            tol = abs if abs is not None else (rel if rel is not None else 1e-6) * max(1.0, v if v >= 0 else -v)
            return _Approx(v, tol)
        @staticmethod
        def fixture(fn=None, **kw):
            def deco(f): f._fixture = True; return f
            return deco(fn) if fn else deco
# ───────────────────────── end shim · lesson begins ─────────────────────


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


# ───────────────── standalone runner (python3 file.py) ─────────────────

def _run_standalone():
    import inspect
    g = dict(globals())
    fixtures = {n: f for n, f in g.items() if getattr(f, "_fixture", False)}
    passed = failed = 0
    for name, fn in sorted(g.items()):
        if not (name.startswith("test_") and callable(fn)):
            continue
        names, cases = getattr(fn, "_params", (None, [None]))
        for case in cases:
            kwargs, label, gens = {}, name, []
            if names:
                vals = case if isinstance(case, tuple) else (case,)
                kwargs = dict(zip([s.strip() for s in names.split(",")], vals))
                label = f"{name}[{', '.join(map(repr, vals))}]"
            for p in inspect.signature(fn).parameters:
                if p not in kwargs and p in fixtures:
                    r = fixtures[p]()
                    if inspect.isgenerator(r):
                        gens.append(r); r = next(r)
                    kwargs[p] = r
            try:
                fn(**kwargs); print(f"  PASS  {label}"); passed += 1
            except Exception as e:                              # noqa: BLE001
                print(f"  FAIL  {label}  ->  {e}"); failed += 1
            for gen in gens:
                try: next(gen)
                except StopIteration: pass
    print(f"\n{passed} passed, {failed} failed")
    return failed


if __name__ == "__main__":
    import sys
    print(__doc__.strip().splitlines()[0])
    print()
    if hasattr(pytest, "main"):
        sys.exit(pytest.main([__file__, "-v", "-p", "no:cacheprovider"]))
    sys.exit(_run_standalone())
