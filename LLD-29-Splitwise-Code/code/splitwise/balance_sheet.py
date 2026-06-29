from collections import defaultdict


class BalanceSheet:
    """The running net of who owes whom.

    balances[a][b] = paise that a owes b. Kept **net** — we never store both
    a->b and b->a at the same time, so opposite debts cancel.
    """

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

    def apply(self, expense):
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
        """+ve = user is owed overall; -ve = user owes."""
        owed_to_user = sum(self.balances[x][user] for x in self.balances)
        user_owes = sum(self.balances[user].values())
        return owed_to_user - user_owes

    def edges(self):
        return [(a, b, amt) for a in self.balances for b, amt in self.balances[a].items()]
