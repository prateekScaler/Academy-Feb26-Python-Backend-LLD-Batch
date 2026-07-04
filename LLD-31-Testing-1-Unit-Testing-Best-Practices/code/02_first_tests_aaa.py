"""
02 — Your first real tests: AAA and naming
==========================================

Anatomy of a good unit test:

    def test_<the_behaviour_in_plain_english>():
        # Arrange  — set the world up
        # Act      — do the ONE thing this test is about
        # Assert   — check the ONE outcome you care about

Three rules that make suites pleasant to live with:
  1. AAA — every test reads top-to-bottom as Arrange / Act / Assert.
  2. The NAME states the behaviour — a failing name should tell you
     what broke without opening the file.
  3. ONE behaviour per test — when it fails, you know exactly what died.

Run me:
    python3 02_first_tests_aaa.py
    pytest -v 02_first_tests_aaa.py
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


# ── the code under test: a miniature Splitwise group ──

class ExpenseGroup:
    """Tiny slice of LLD-29: add expenses, read net balances (in paise)."""

    def __init__(self, members: list[str]):
        self.members = list(members)
        self.balance = {m: 0 for m in members}     # +ve ⇒ others owe you

    def add_expense(self, paid_by: str, total_paise: int) -> None:
        base, rem = divmod(total_paise, len(self.members))
        for i, m in enumerate(self.members):
            share = base + 1 if i < rem else base
            if m == paid_by:
                self.balance[m] += total_paise - share
            else:
                self.balance[m] -= share


# ─────────────────────────── the tests ───────────────────────────

def test_payer_is_owed_the_others_shares():
    # Arrange — three friends, empty slate
    group = ExpenseGroup(["asha", "bala", "chen"])

    # Act — asha pays ₹300.00 for dinner
    group.add_expense("asha", 30_000)

    # Assert — asha is owed the two other ₹100 shares
    assert group.balance["asha"] == 20_000


def test_non_payers_each_owe_one_equal_share():
    group = ExpenseGroup(["asha", "bala", "chen"])

    group.add_expense("asha", 30_000)

    assert group.balance["bala"] == -10_000
    assert group.balance["chen"] == -10_000


def test_balances_always_sum_to_zero():
    # The conservation property again — debts and credits must cancel.
    group = ExpenseGroup(["asha", "bala", "chen"])

    group.add_expense("asha", 30_000)
    group.add_expense("bala", 10_001)          # awkward remainder on purpose

    assert sum(group.balance.values()) == 0


def test_two_expenses_net_against_each_other():
    group = ExpenseGroup(["asha", "bala"])

    group.add_expense("asha", 10_000)          # bala owes 5 000
    group.add_expense("bala", 10_000)          # asha owes 5 000 back

    assert group.balance == {"asha": 0, "bala": 0}


# ── ANTI-EXAMPLE (kept as a comment — do NOT write this test) ──
#
#  def test_group():                       # name says nothing
#      g = ExpenseGroup(["a", "b"])
#      g.add_expense("a", 100)
#      assert g.balance["a"] == 50         # behaviour 1
#      g.add_expense("b", 300)             # re-Arranging mid-test!
#      assert g.balance["b"] == 100        # behaviour 2
#      assert len(g.members) == 2          # behaviour 3, unrelated
#
#  When this fails, WHICH behaviour broke? You cannot tell from the name,
#  and the first failing assert hides the ones after it.


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
