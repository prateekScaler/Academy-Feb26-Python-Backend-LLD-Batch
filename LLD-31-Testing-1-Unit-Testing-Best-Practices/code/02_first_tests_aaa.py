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
    pytest -v 02_first_tests_aaa.py
    python3 02_first_tests_aaa.py        # same thing — it hands over to pytest

Needs:  pip install pytest
"""


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


if __name__ == "__main__":
    # This file IS a pytest suite — running it directly just hands over to pytest.
    try:
        import pytest
    except ImportError:
        raise SystemExit("This is a pytest test file. Install pytest first:  pip install pytest")
    raise SystemExit(pytest.main([__file__, "-v", "-p", "no:cacheprovider"]))
