"""
05 — Testing errors, and the float trap
=======================================

Two things every backend suite must get right:

1. ERRORS BY DESIGN. When code SHOULD raise (a rule violation), the test
   must assert that it does — and say something about the error:

       with pytest.raises(InsufficientFunds) as excinfo:
           wallet.withdraw(600_00)
       assert "600" in str(excinfo.value)

   Contrast with file 04: a FULL parking lot returns None (an expected
   answer). Exceptions are for violations, not for answers.

2. FLOATS LIE. 0.1 + 0.2 != 0.3 in every IEEE-754 language. For money the
   real fix is integers (paise). When floats are unavoidable (rates,
   averages), compare with pytest.approx — never ==.

Run me:
    python3 05_exceptions_and_floats.py
    pytest -v 05_exceptions_and_floats.py
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


# ── code under test: a wallet with a hard rule ──

class InsufficientFunds(Exception):
    def __init__(self, needed_paise: int, available_paise: int):
        super().__init__(
            f"need {needed_paise} paise, only {available_paise} available")
        self.needed = needed_paise
        self.available = available_paise


class Wallet:
    def __init__(self, balance_paise: int = 0):
        self.balance = balance_paise

    def withdraw(self, amount_paise: int) -> None:
        if amount_paise > self.balance:
            raise InsufficientFunds(amount_paise, self.balance)   # violation
        self.balance -= amount_paise


# ───────────────── testing exceptions by design ─────────────────

def test_overdraw_raises_insufficient_funds():
    wallet = Wallet(balance_paise=500_00)

    with pytest.raises(InsufficientFunds) as excinfo:
        wallet.withdraw(600_00)

    # assert on the ERROR too — it carries information for the caller
    assert excinfo.value.needed == 600_00
    assert excinfo.value.available == 500_00


def test_failed_withdraw_leaves_balance_untouched():
    # error paths must not half-apply their effects
    wallet = Wallet(balance_paise=500_00)

    with pytest.raises(InsufficientFunds):
        wallet.withdraw(600_00)

    assert wallet.balance == 500_00


def test_exact_balance_withdraw_is_allowed_boundary():
    wallet = Wallet(balance_paise=500_00)

    wallet.withdraw(500_00)                     # the == boundary

    assert wallet.balance == 0


# ───────────────────── the float trap ─────────────────────

def test_floats_break_equality_the_famous_example():
    # This is not a Python bug — it is binary floating point (IEEE 754).
    assert 0.1 + 0.2 != 0.3
    assert 0.1 + 0.2 == 0.30000000000000004


def test_approx_is_the_right_tool_when_floats_are_unavoidable():
    average_rating = (4.1 + 4.3 + 4.2) / 3

    assert average_rating == pytest.approx(4.2)             # tolerant compare
    assert 0.1 + 0.2 == pytest.approx(0.3)


def test_money_needs_no_approx_because_paise_are_integers():
    # The stronger fix from LLD-29: never put money in a float at all.
    shares = [3334, 3333, 3333]

    assert sum(shares) == 10_000                # exact. always. no epsilon.


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
