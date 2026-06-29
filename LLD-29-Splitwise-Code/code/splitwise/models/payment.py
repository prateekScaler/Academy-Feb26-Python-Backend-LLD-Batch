from dataclasses import dataclass

from .user import User
from ..money import fmt


@dataclass
class Payment:
    """A settle-up transfer in the plan (from -> to)."""
    frm: User
    to: User
    amount: int

    def __repr__(self):
        return f"{self.frm} → {self.to} {fmt(self.amount)}"
