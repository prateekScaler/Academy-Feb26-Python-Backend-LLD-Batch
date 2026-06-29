"""Runnable demos against the layered package.

Run from the `code/` directory:   python3 -m splitwise.main
(every demo asserts green)
"""
from splitwise.money import rupees, fmt
from splitwise.enums import SplitType
from splitwise.service import ExpenseService
from splitwise.strategies import EqualSplit, ExactSplit, PercentSplit
from splitwise.exceptions import SplitError, PermissionDenied


def demo_penny():
    print("1) Penny problem — ₹100 split equally 3 ways")
    from splitwise.models import User
    a, b, c = User("A", "1"), User("B", "2"), User("C", "3")
    shares = [s.amount for s in EqualSplit().split(rupees(100), [a, b, c])]
    print("   shares:", [fmt(x) for x in shares], "→ sum", fmt(sum(shares)))
    assert shares == [3334, 3333, 3333]
    assert sum(shares) == rupees(100)


def demo_balances():
    print("2) Add expense → balances")
    s = ExpenseService()
    a = s.register("Ananya", "1"); b = s.register("Bharat", "2")
    c = s.register("Chetan", "3"); d = s.register("Divya", "4")
    s.add_expense("Dinner", {a: rupees(1200)}, [a, b, c, d], SplitType.EQUAL)
    for u in (b, c, d):
        assert s.sheet.owes(u, a) == rupees(300)
    assert s.balance_of(a) == rupees(900)
    print("   B/C/D each owe A", fmt(rupees(300)), "· A net", fmt(s.balance_of(a)))


def demo_netting():
    print("3) Opposite debts net out")
    s = ExpenseService()
    a = s.register("A", "1"); b = s.register("B", "2")
    s.add_expense("lunch", {a: rupees(100)}, [a, b], SplitType.EQUAL)   # B owes A 50
    s.add_expense("cab",   {b: rupees(60)},  [a, b], SplitType.EQUAL)   # A owes B 30
    assert s.sheet.owes(b, a) == rupees(20) and s.sheet.owes(a, b) == 0
    print("   net: B owes A", fmt(s.sheet.owes(b, a)))


def demo_simplify():
    print("4) Debt simplification — 3 edges → 2 payments")
    s = ExpenseService()
    a = s.register("A", "1"); b = s.register("B", "2"); c = s.register("C", "3")
    g = s.create_group("Trip", a, [b, c])
    s.add_expense("hotel",  {a: rupees(3000)}, [a, b, c], SplitType.EQUAL, group=g)
    s.add_expense("petrol", {b: rupees(1500)}, [b, c],    SplitType.EQUAL, group=g)
    payments = s.simplify_group(g)
    print("   nets:", {u.name: fmt(s.sheet.net(u)) for u in (a, b, c)})
    print("   payments:", payments)
    assert len(payments) == 2
    assert sum(p.amount for p in payments if p.to == a) == rupees(2000)
    assert {p.amount for p in payments} == {rupees(1750), rupees(250)}


def demo_strategies():
    print("5) Exact & percent splits validate")
    s = ExpenseService()
    a = s.register("A", "1"); b = s.register("B", "2")
    s.add_expense("groceries", {a: rupees(1000)}, [a, b], SplitType.EXACT,
                  args={a: rupees(400), b: rupees(600)})
    assert s.sheet.owes(b, a) == rupees(600)
    try:
        ExactSplit().split(rupees(1000), [a, b], {a: rupees(400), b: rupees(500)})
        assert False
    except SplitError:
        pass
    pct = PercentSplit().split(rupees(1000), [a, b], {a: 30, b: 70})
    assert sum(x.amount for x in pct) == rupees(1000)
    print("   exact ok · percent sums to total ✓")


def demo_permissions():
    print("6) Only the creator edits members")
    s = ExpenseService()
    a = s.register("A", "1"); b = s.register("B", "2"); c = s.register("C", "3")
    g = s.create_group("Flat", a, [b])
    try:
        s.add_member(g, b, c)
        assert False
    except PermissionDenied:
        pass
    s.add_member(g, a, c)
    assert g.has(c)
    print("   creator added C ✓ · non-creator blocked ✓")


def main():
    for demo in (demo_penny, demo_balances, demo_netting,
                 demo_simplify, demo_strategies, demo_permissions):
        demo()
    print("\nAll demos green ✅")


if __name__ == "__main__":
    main()
