from dataclasses import dataclass

from .user import User


@dataclass
class Split:
    """The association class: how much `user` OWES on one expense.
    Persists as a UserExpense row of type OWED."""
    user: User
    amount: int     # paise
