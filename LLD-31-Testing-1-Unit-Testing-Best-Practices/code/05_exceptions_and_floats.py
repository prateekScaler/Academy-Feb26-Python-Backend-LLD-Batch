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
    pytest -v 05_exceptions_and_floats.py
    python3 05_exceptions_and_floats.py        # same thing — it hands over to pytest

Needs:  pip install pytest
"""

import pytest


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


if __name__ == "__main__":
    # This file IS a pytest suite — running it directly just hands over to pytest.
    try:
        import pytest
    except ImportError:
        raise SystemExit("This is a pytest test file. Install pytest first:  pip install pytest")
    raise SystemExit(pytest.main([__file__, "-v", "-p", "no:cacheprovider"]))
