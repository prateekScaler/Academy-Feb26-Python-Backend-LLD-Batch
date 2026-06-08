"""
LLD-21 · Example 03 — Splitwise skeleton with three split strategies.

The second-most-asked LLD problem (after Parking Lot) in Indian backend
interviews. The point of this file is NOT a complete Splitwise — it's
the smallest version that shows the patterns you'd reach for:

    - Strategy   : SplitStrategy → EqualSplit / PercentSplit / ShareSplit
    - Protocol   : typing.Protocol, no inheritance forced on implementers
    - dataclass  : for User, Group, Expense

Run:  python3 03_splitwise_skeleton.py
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Protocol


# === Entities ================================================================
@dataclass(frozen=True)
class User:
    user_id: str
    name: str


# === Strategy — the open variable ============================================
class SplitStrategy(Protocol):
    def split(self, amount: float, members: list[User], **kwargs) -> dict[User, float]: ...


class EqualSplit:
    def split(self, amount: float, members: list[User], **kwargs) -> dict[User, float]:
        per = round(amount / len(members), 2)
        return {u: per for u in members}


class PercentSplit:
    """percents = {user_id: percent}. Percents must sum to 100."""

    def split(self, amount: float, members: list[User], **kwargs) -> dict[User, float]:
        percents = kwargs["percents"]
        if abs(sum(percents.values()) - 100.0) > 0.01:
            raise ValueError(f"percents must sum to 100, got {sum(percents.values())}")
        return {u: round(amount * percents[u.user_id] / 100.0, 2) for u in members}


class ShareSplit:
    """shares = {user_id: share_units}. Allocation proportional to shares."""

    def split(self, amount: float, members: list[User], **kwargs) -> dict[User, float]:
        shares = kwargs["shares"]
        total_shares = sum(shares.values())
        return {u: round(amount * shares[u.user_id] / total_shares, 2) for u in members}


@dataclass
class Expense:
    payer: User
    amount: float
    members: list[User]
    strategy: SplitStrategy
    strategy_kwargs: dict = field(default_factory=dict)

    def shares(self) -> dict[User, float]:
        """How much each member OWES the payer for this expense."""
        contributions = self.strategy.split(self.amount, self.members, **self.strategy_kwargs)
        # payer's own share doesn't get owed back to themselves
        out = {u: amt for u, amt in contributions.items() if u != self.payer}
        return out


@dataclass
class Group:
    name: str
    members: list[User] = field(default_factory=list)
    expenses: list[Expense] = field(default_factory=list)

    def add_user(self, u: User) -> None:
        if u not in self.members:
            self.members.append(u)

    def add_expense(self, e: Expense) -> None:
        self.expenses.append(e)

    def balances(self) -> dict[User, float]:
        """Net per user. Positive = others owe them. Negative = they owe."""
        net: dict[User, float] = {u: 0.0 for u in self.members}
        for e in self.expenses:
            for member, owed in e.shares().items():
                net[member] -= owed
                net[e.payer] += owed
        return {u: round(v, 2) for u, v in net.items()}


# === Step 6 — Demo ===========================================================
def demo() -> None:
    print("\n--- Splitwise demo: 3 users, 3 expense types ---")
    ajit = User("u1", "Ajit")
    bhavna = User("u2", "Bhavna")
    chetan = User("u3", "Chetan")

    g = Group("Goa Trip")
    for u in (ajit, bhavna, chetan):
        g.add_user(u)

    # Equal: dinner ₹900, paid by Ajit
    g.add_expense(Expense(ajit, 900, g.members, EqualSplit()))

    # Percent: cab ₹600, paid by Bhavna. Ajit 50, Bhavna 30, Chetan 20
    g.add_expense(
        Expense(
            bhavna, 600, g.members, PercentSplit(),
            strategy_kwargs={"percents": {"u1": 50, "u2": 30, "u3": 20}},
        )
    )

    # Share: shacks ₹450, paid by Chetan. shares: ajit 2, bhavna 1, chetan 0
    # (chetan was driving; only the others ate)
    g.add_expense(
        Expense(
            chetan, 450, g.members, ShareSplit(),
            strategy_kwargs={"shares": {"u1": 2, "u2": 1, "u3": 0}},
        )
    )

    print("\n  Final balances (positive = others owe them):")
    for u, amt in g.balances().items():
        sign = "+" if amt >= 0 else ""
        print(f"    {u.name:<8} {sign}{amt:>8.2f}")

    print("\n  Sanity check: balances should sum to ~0")
    total = sum(g.balances().values())
    print(f"    sum = {total:.2f}")


def step7_tradeoffs() -> None:
    print(
        """
--- Trade-offs (Step 7) ---
  Persistence: All state lives in Python dicts. Production version needs
    a GroupRepository, UserRepository, ExpenseRepository. Domain classes
    stay storage-ignorant.
  Concurrency: Group.add_expense() mutates a list. For concurrent users,
    lock per Group (or use an append-only event log + projection).
  Extensions:
    * New split type (e.g. ExactAmountSplit where each user names a rupee
      amount): one new class implementing SplitStrategy. Zero changes to
      Group, Expense, balances().
    * Settlement / payment graph simplification: add a Settlement event
      type and a simplify() method that minimises the number of edges in
      the debt graph.
    * Multi-currency: Money(amount, currency) dataclass, ExchangeRate
      strategy, settle in user's preferred currency.
"""
    )


if __name__ == "__main__":
    demo()
    step7_tradeoffs()
