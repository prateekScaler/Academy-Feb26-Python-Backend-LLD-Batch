from .models import User, Group, Expense, Payment
from .strategies import EqualSplit, ExactSplit, PercentSplit
from .balance_sheet import BalanceSheet
from .debt_simplifier import DebtSimplifier
from .enums import SplitType
from .exceptions import SplitError, PermissionDenied


class ExpenseService:
    """The orchestrator: register users, add expenses (via a split strategy),
    view balances, settle up, and simplify a group's debts."""

    def __init__(self):
        self.users = {}
        self.groups = {}
        self.expenses = []
        self.sheet = BalanceSheet()
        self.strategies = {
            SplitType.EQUAL: EqualSplit(),
            SplitType.EXACT: ExactSplit(),
            SplitType.PERCENT: PercentSplit(),
        }

    # ---- users & groups ----
    def register(self, name, phone):
        u = User(name, phone)
        self.users[u.id] = u
        return u

    def create_group(self, name, creator, members=()):
        roster = [creator] + [m for m in members if m != creator]
        g = Group(name, creator, roster)
        self.groups[g.id] = g
        return g

    def add_member(self, group, actor, new_member):
        if actor != group.created_by:                       # server-side authorisation check
            raise PermissionDenied("only the group's creator can add or remove members")
        if new_member not in group.members:
            group.members.append(new_member)

    # ---- expenses ----
    def add_expense(self, description, paid_by, participants, split_type, args=None, group=None):
        amount = sum(paid_by.values())
        splits = self.strategies[split_type].split(amount, participants, args)
        if sum(s.amount for s in splits) != amount:          # invariant: splits sum to total
            raise SplitError("splits must sum to the total")
        exp = Expense(description, amount, dict(paid_by), splits, group)
        self.expenses.append(exp)
        self.sheet.apply(exp)
        return exp

    # ---- views ----
    def balance_of(self, user) -> int:
        return self.sheet.net(user)

    def show_balances(self):
        return self.sheet.edges()

    # ---- settle up ----
    def settle_up_user(self, user):
        """Personal: the transactions that leave `user` owing/owed nothing."""
        return [Payment(a, b, amt) for a, b, amt in self.sheet.edges() if user in (a, b)]

    def simplify_group(self, group):
        """Group: fewest payments to settle everyone, using only this group's expenses."""
        scoped = BalanceSheet()
        for e in self.expenses:
            if e.group is group:
                scoped.apply(e)
        nets = {u: scoped.net(u) for u in group.members}
        return DebtSimplifier.minimal_payments(nets)
