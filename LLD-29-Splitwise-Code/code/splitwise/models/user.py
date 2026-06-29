import itertools
from dataclasses import dataclass, field

_ids = itertools.count(1)


@dataclass
class User:
    name: str
    phone: str
    id: int = field(default_factory=lambda: next(_ids))

    def __hash__(self):
        return self.id

    def __eq__(self, other):
        return isinstance(other, User) and other.id == self.id

    def __repr__(self):
        return self.name
