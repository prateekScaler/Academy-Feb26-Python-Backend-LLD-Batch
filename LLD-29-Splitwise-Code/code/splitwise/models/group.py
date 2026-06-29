import itertools
from dataclasses import dataclass, field

from .user import User

_ids = itertools.count(1)


@dataclass
class Group:
    name: str
    created_by: User            # the permissions FR: only the creator edits members
    members: list = field(default_factory=list)
    id: int = field(default_factory=lambda: next(_ids))

    def has(self, user) -> bool:
        return user in self.members
