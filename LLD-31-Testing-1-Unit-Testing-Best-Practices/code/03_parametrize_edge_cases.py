"""
03 — parametrize: one test, a table of edge cases
=================================================

Copy-pasting a test six times with different numbers is a smell.
`@pytest.mark.parametrize` turns the test into a TABLE:

    @pytest.mark.parametrize("total, n, expected", [ ...cases... ])
    def test_split(total, n, expected): ...

Each row runs (and fails!) independently — you see exactly which case broke.

Where do the rows come from? BOUNDARIES. For any numeric input think:
  0 · 1 · the typical value · the value where behaviour changes · the max.
For a split: remainder 0, remainder 1, remainder n-1, n = 1, total = 0.

Run me:
    python3 03_parametrize_edge_cases.py
    pytest -v 03_parametrize_edge_cases.py
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


# ── code under test #1: the paise split from file 01 ──

def split_equal_paise(total_paise: int, n: int) -> list[int]:
    base, rem = divmod(total_paise, n)
    return [base + 1 if i < rem else base for i in range(n)]


@pytest.mark.parametrize("total, n", [
    (10_000, 3),      # the classic ₹100 / 3
    (10_000, 1),      # n = 1 → one person pays everything
    (0,      4),      # zero rupees → all shares zero
    (1,      3),      # 1 paisa among 3 → someone pays it, sum still 1
    (9_999,  2),      # odd remainder
    (7,      7),      # total == n → everyone pays exactly 1
    (6,      7),      # total < n → some pay 1, some pay 0
])
def test_split_conserves_total_for_every_boundary(total, n):
    assert sum(split_equal_paise(total, n)) == total


@pytest.mark.parametrize("total, n", [(10_000, 3), (1, 3), (6, 7)])
def test_split_is_fair_shares_differ_by_at_most_one(total, n):
    shares = split_equal_paise(total, n)
    assert max(shares) - min(shares) <= 1


# ── code under test #2: the LLD-23 winner check ──

def winner(board: list[list[str]]) -> str | None:
    """3×3 tic-tac-toe. Returns 'X', 'O', or None."""
    lines = (
        board                                              # 3 rows
        + [list(col) for col in zip(*board)]               # 3 columns
        + [[board[i][i] for i in range(3)],                # main diagonal
           [board[i][2 - i] for i in range(3)]]            # anti-diagonal
    )
    for line in lines:
        if line[0] and line == [line[0]] * 3:
            return line[0]
    return None


X, O, _ = "X", "O", ""

@pytest.mark.parametrize("board, expected", [
    ([[X, X, X], [_, O, _], [O, _, _]], X),     # top row
    ([[O, _, X], [O, X, _], [O, _, X]], O),     # left column
    ([[X, O, _], [O, X, _], [_, _, X]], X),     # main diagonal
    ([[_, O, X], [O, X, _], [X, _, _]], X),     # anti-diagonal
    ([[X, O, X], [X, O, O], [O, X, X]], None),  # full board, draw
    ([[_, _, _], [_, _, _], [_, _, _]], None),  # empty board
])
def test_winner_detects_every_line_and_no_false_positives(board, expected):
    assert winner(board) == expected


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
