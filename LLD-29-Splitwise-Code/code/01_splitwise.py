"""LLD-29 — Splitwise: Code (Part 2)  —  the whole engine in one file.

Run:  python3 01_splitwise.py        (every demo asserts green)

Design notes (from LLD-28):
  * Money is integer **paise** everywhere — no float drift, and the penny problem
    becomes a clean integer-remainder rule.
  * The **split strategy** is the open variable (EQUAL / EXACT / PERCENT); a new
    way to split is one new class.
  * "who paid what" and "who owes what" are two sides of one expense; the
    BalanceSheet keeps the **net** debt between every pair.
  * **Debt simplification** settles a group in the fewest payments (greedy
    net-and-match — the standard, practical answer; the exact minimum is NP-hard).
"""
from __future__ import annotations
from abc import ABC, abstractmethod
from collections import defaultdict
from dataclasses import dataclass, field
from enum import Enum
import itertools

# ───────────────────────── money helpers ─────────────────────────
def rupees(r: float) -> int:            # ₹ -> paise
    return int(round(r * 100))
def fmt(paise: int) -> str:             # paise -> "₹x.xx"
    return f"₹{paise / 100:.2f}"

# ───────────────────────── enums ─────────────────────────
class SplitType(Enum):
    EQUAL = "EQUAL"
    EXACT = "EXACT"
    PERCENT = "PERCENT"

# ───────────────────────── domain models ─────────────────────────
_ids = itertools.count(1)

@dataclass
class User:
    name: str
    phone: str
    id: int = field(default_factory=lambda: next(_ids))
    def __hash__(self): return self.id
    def __eq__(self, o): return isinstance(o, User) and o.id == self.id
    def __repr__(self): return self.name

@dataclass
class Group:
    name: str
    created_by: "User"
    members: list = field(default_factory=list)
    id: int = field(default_factory=lambda: next(_ids))
    def has(self, u): return u in self.members

@dataclass
class Split:
    """One side of an expense: how much `user` OWES on it. (The association
    class — persists as a UserExpense row of type OWED.)"""
    user: "User"
    amount: int

@dataclass
class Expense:
    description: str
    amount: int                 # total, in paise
    paid_by: dict               # {User: paise paid}  ("who paid what")
    splits: list                # [Split]             ("who owes what")
    group: "Group" = None
    id: int = field(default_factory=lambda: next(_ids))

@dataclass
class Payment:
    frm: "User"
    to: "User"
    amount: int
    def __repr__(self): return f"{self.frm} → {self.to} {fmt(self.amount)}"

# ───────────────────────── split strategies (the open variable) ─────────────────────────
class SplitStrategy(ABC):
    """Contract: produce one Split per participant, summing to `amount`."""
    @abstractmethod
    def split(self, amount: int, participants: list, args=None) -> list: ...

class EqualSplit(SplitStrategy):
    def split(self, amount, participants, args=None):
        n = len(participants)
        base, remainder = divmod(amount, n)       # the leftover paise
        # the first `remainder` participants absorb one extra paisa each
        return [Split(u, base + (1 if i < remainder else 0))
                for i, u in enumerate(participants)]

class ExactSplit(SplitStrategy):
    def split(self, amount, participants, args):  # args: {User: paise}
        if sum(args.values()) != amount:
            raise ValueError("exact shares must sum to the total")
        return [Split(u, args[u]) for u in participants]

class PercentSplit(SplitStrategy):
    def split(self, amount, participants, args):  # args: {User: percent (int)}
        if sum(args.values()) != 100:
            raise ValueError("percentages must sum to 100")
        splits, allocated = [], 0
        for i, u in enumerate(participants):
            if i < len(participants) - 1:
                share = amount * args[u] // 100
                allocated += share
            else:
                share = amount - allocated         # last one absorbs the rounding
            splits.append(Split(u, share))
        return splits

# ───────────────────────── the balance sheet (who owes whom) ─────────────────────────
class BalanceSheet:
    """Net pairwise debts. balances[a][b] = paise that a owes b. Kept net, so we
    never store both a->b and b->a at the same time."""
    def __init__(self):
        self.balances = defaultdict(lambda: defaultdict(int))

    def add_debt(self, debtor, creditor, amount):
        if debtor == creditor or amount <= 0:
            return
        reverse = self.balances[creditor][debtor]      # does creditor already owe debtor?
        if reverse >= amount:
            self.balances[creditor][debtor] = reverse - amount
        else:
            if reverse:
                self.balances[creditor][debtor] = 0
            self.balances[debtor][creditor] += amount - reverse
        self._prune()

    def _prune(self):
        for a in list(self.balances):
            for b in list(self.balances[a]):
                if self.balances[a][b] == 0:
                    del self.balances[a][b]
            if not self.balances[a]:
                del self.balances[a]

    def apply(self, expense: Expense):
        """Each ower owes each payer, proportional to what that payer paid."""
        total_paid = sum(expense.paid_by.values())
        for s in expense.splits:
            for payer, paid in expense.paid_by.items():
                if s.user == payer:
                    continue
                self.add_debt(s.user, payer, s.amount * paid // total_paid)

    def owes(self, debtor, creditor) -> int:
        return self.balances[debtor][creditor]

    def net(self, user) -> int:
        """+ve = user is owed money overall; -ve = user owes."""
        owed_to_user = sum(self.balances[x][user] for x in self.balances)
        user_owes = sum(self.balances[user].values())
        return owed_to_user - user_owes

    def edges(self):
        return [(a, b, amt) for a in self.balances for b, amt in self.balances[a].items()]

# ───────────────────────── debt simplification (fewest payments) ─────────────────────────
class DebtSimplifier:
    @staticmethod
    def minimal_payments(nets: dict) -> list:
        """Greedy net-and-match: repeatedly settle the biggest creditor against
        the biggest debtor. Standard practical answer (exact min is NP-hard)."""
        creditors = [[u, n] for u, n in nets.items() if n > 0]
        debtors = [[u, -n] for u, n in nets.items() if n < 0]
        payments = []
        while creditors and debtors:
            creditors.sort(key=lambda x: -x[1])
            debtors.sort(key=lambda x: -x[1])
            c, d = creditors[0], debtors[0]
            pay = min(c[1], d[1])
            payments.append(Payment(d[0], c[0], pay))
            c[1] -= pay
            d[1] -= pay
            if c[1] == 0: creditors.pop(0)
            if d[1] == 0: debtors.pop(0)
        return payments

# ───────────────────────── the orchestrator ─────────────────────────
class ExpenseService:
    def __init__(self):
        self.users, self.groups, self.expenses = {}, {}, []
        self.sheet = BalanceSheet()
        self.strategies = {SplitType.EQUAL: EqualSplit(),
                           SplitType.EXACT: ExactSplit(),
                           SplitType.PERCENT: PercentSplit()}

    # -- users & groups --
    def register(self, name, phone):
        u = User(name, phone); self.users[u.id] = u; return u

    def create_group(self, name, creator, members=()):
        roster = [creator] + [m for m in members if m != creator]
        g = Group(name, creator, roster); self.groups[g.id] = g; return g

    def add_member(self, group, actor, new_member):
        if actor != group.created_by:                       # the permission check (server-side)
            raise PermissionError("only the group's creator can add or remove members")
        if new_member not in group.members:
            group.members.append(new_member)

    # -- expenses --
    def add_expense(self, description, paid_by, participants, split_type, args=None, group=None):
        amount = sum(paid_by.values())
        splits = self.strategies[split_type].split(amount, participants, args)
        if sum(s.amount for s in splits) != amount:          # FR-invariant: splits sum to total
            raise ValueError("splits must sum to the total")
        exp = Expense(description, amount, dict(paid_by), splits, group)
        self.expenses.append(exp)
        self.sheet.apply(exp)
        return exp

    # -- views --
    def balance_of(self, user) -> int:
        return self.sheet.net(user)

    def show_balances(self):
        return self.sheet.edges()

    # -- settle up --
    def settle_up_user(self, user):
        """Personal: the transactions that leave `user` owing/owed nothing."""
        return [Payment(a, b, amt) for a, b, amt in self.sheet.edges()
                if user in (a, b)]

    def simplify_group(self, group):
        """Group: fewest payments to settle everyone, using only this group's expenses."""
        scoped = BalanceSheet()
        for e in self.expenses:
            if e.group is group:
                scoped.apply(e)
        nets = {u: scoped.net(u) for u in group.members}
        return DebtSimplifier.minimal_payments(nets)


# ═════════════════════════ demos (all assert green) ═════════════════════════
def demo_penny():
    print("1) Penny problem — ₹100 split equally 3 ways")
    a = User("A", "1"); b = User("B", "2"); c = User("C", "3")
    splits = EqualSplit().split(rupees(100), [a, b, c])
    amounts = [s.amount for s in splits]
    print("   shares:", [fmt(x) for x in amounts], "→ sum", fmt(sum(amounts)))
    assert amounts == [3334, 3333, 3333]
    assert sum(amounts) == rupees(100)          # no paisa created or lost

def demo_balances():
    print("2) Add expense → balances")
    s = ExpenseService()
    a = s.register("Ananya", "1"); b = s.register("Bharat", "2")
    c = s.register("Chetan", "3"); d = s.register("Divya", "4")
    s.add_expense("Dinner", {a: rupees(1200)}, [a, b, c, d], SplitType.EQUAL)
    for u in (b, c, d):
        assert s.sheet.owes(u, a) == rupees(300)
    assert s.balance_of(a) == rupees(900)        # owed 300 by each of 3
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
    s.add_expense("hotel",   {a: rupees(3000)}, [a, b, c], SplitType.EQUAL, group=g)
    s.add_expense("petrol",  {b: rupees(1500)}, [b, c],    SplitType.EQUAL, group=g)
    payments = s.simplify_group(g)
    print("   nets:", {u.name: fmt(s.sheet.net(u)) for u in (a, b, c)})
    print("   payments:", payments)
    assert len(payments) == 2
    paid_to_a = sum(p.amount for p in payments if p.to == a)
    assert paid_to_a == rupees(2000)             # A is made whole
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
        assert False, "should reject shares that don't sum to total"
    except ValueError:
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
        s.add_member(g, b, c)                     # B is not the creator
        assert False, "non-creator must not add members"
    except PermissionError:
        pass
    s.add_member(g, a, c)                         # creator can
    assert g.has(c)
    print("   creator added C ✓ · non-creator blocked ✓")

if __name__ == "__main__":
    for demo in (demo_penny, demo_balances, demo_netting,
                 demo_simplify, demo_strategies, demo_permissions):
        demo()
    print("\nAll demos green ✅")
