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
    pytest -v 03_parametrize_edge_cases.py
    python3 03_parametrize_edge_cases.py        # same thing — it hands over to pytest

Needs:  pip install pytest
"""

import pytest


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


if __name__ == "__main__":
    # This file IS a pytest suite — running it directly just hands over to pytest.
    try:
        import pytest
    except ImportError:
        raise SystemExit("This is a pytest test file. Install pytest first:  pip install pytest")
    raise SystemExit(pytest.main([__file__, "-v", "-p", "no:cacheprovider"]))
