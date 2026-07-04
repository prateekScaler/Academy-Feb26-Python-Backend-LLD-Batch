"""
01 — The bug a test catches
===========================

The motivating story. In LLD-29 we fixed the *penny problem*: split money in
integer paise with divmod, so ₹100 / 3 sums back to exactly ₹100.

Months later a well-meaning teammate "simplifies" the code to use floats.
Nothing crashes. Every screen still renders. The app looks fine.

    ₹100.00 split 3 ways → ₹33.33 + ₹33.33 + ₹33.33 = ₹99.99   (a paisa vanished)

Nobody notices — unless a TEST pins the behaviour down. That is what tests
are for: not proving the code works today, but *keeping* it working tomorrow.

Run me:
    python3 01_the_bug_a_test_catches.py          # no install needed
    pytest -v 01_the_bug_a_test_catches.py        # if you have pytest
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


# ── The GOOD implementation (LLD-29's penny fix): integer paise + divmod ──

def split_equal_paise(total_paise: int, n: int) -> list[int]:
    """Split `total_paise` into n integer shares that sum back EXACTLY.

    divmod gives the base share and the remainder; the first `remainder`
    people pay one extra paisa. ₹100.00 / 3 → [3334, 3333, 3333].
    """
    base, remainder = divmod(total_paise, n)
    return [base + 1 if i < remainder else base for i in range(n)]


# ── The "simplified" refactor (the bug): floats + per-share rounding ──

def split_equal_float(total_rupees: float, n: int) -> list[float]:
    """What the teammate wrote. Looks reasonable. Loses money."""
    share = round(total_rupees / n, 2)      # ₹33.33
    return [share] * n                       # 3 × 33.33 = 99.99 ≠ 100.00


# ─────────────────────────── the tests ───────────────────────────
# One property nails the bug forever: WHATEVER we split, the shares
# must sum back to the exact total. This is called *conservation*.

def test_paise_split_conserves_the_total():
    shares = split_equal_paise(10_000, 3)          # ₹100.00 in paise
    assert sum(shares) == 10_000                   # not one paisa lost
    assert shares == [3334, 3333, 3333]


def test_paise_split_shares_differ_by_at_most_one_paisa():
    shares = split_equal_paise(10_000, 3)
    assert max(shares) - min(shares) <= 1          # fair split


def test_float_split_loses_money_which_is_why_we_never_do_it():
    # This test *documents the pitfall*: the float version violates
    # conservation. If someone "simplifies" back to floats, the suite
    # above goes red and the refactor is caught in seconds — not in
    # production, three weeks later, by an angry finance team.
    shares = split_equal_float(100.00, 3)
    assert sum(shares) != 100.00                   # money vanished!
    assert sum(shares) == pytest.approx(99.99)


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
    # the demo: watch the paisa vanish
    f = split_equal_float(100.00, 3)
    p = split_equal_paise(10_000, 3)
    print(f"  float  split of ₹100/3 → {f}  → sum = ₹{sum(f):.2f}   (lost a paisa!)")
    print(f"  paise  split of ₹100/3 → {p} → sum = {sum(p)} paise = ₹100.00 ✓")
    print()
    if hasattr(pytest, "main"):
        sys.exit(pytest.main([__file__, "-v", "-p", "no:cacheprovider"]))
    sys.exit(_run_standalone())
