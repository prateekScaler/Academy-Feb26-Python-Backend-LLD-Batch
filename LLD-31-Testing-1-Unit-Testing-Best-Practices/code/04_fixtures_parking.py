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
Fixtures can also clean up: `yield` the value, and everything AFTER the
yield runs as teardown — even if the test failed.

Run me:
    python3 04_fixtures_parking.py
    pytest -v 04_fixtures_parking.py
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


@pytest.fixture
def audit_log():
    """yield-style fixture: value first, TEARDOWN after the yield."""
    log: list[str] = []
    yield log
    log.clear()          # runs after each test — pass or fail


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


def test_each_test_gets_a_fresh_lot(empty_lot, audit_log):
    # empty_lot is NOT the one previous tests used — no shared state,
    # so tests can run in any order (the I in FIRST: Independent).
    audit_log.append("parking")
    assert empty_lot.free == [0, 1]
    assert audit_log == ["parking"]


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
