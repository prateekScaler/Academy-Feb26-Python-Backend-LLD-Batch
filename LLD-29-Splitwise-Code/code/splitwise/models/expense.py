import itertools
from dataclasses import dataclass, field

_ids = itertools.count(1)


@dataclass
class Expense:
    description: str
    amount: int                 # total, in paise
    paid_by: dict               # {User: paise paid}  — "who paid what"
    splits: list                # [Split]             — "who owes what"
    group: object = None        # optional
    id: int = field(default_factory=lambda: next(_ids))
