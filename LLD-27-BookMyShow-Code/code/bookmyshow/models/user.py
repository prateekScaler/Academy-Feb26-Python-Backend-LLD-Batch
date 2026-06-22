"""User — books & cancels; holds tickets."""

from dataclasses import dataclass


@dataclass(frozen=True)
class User:
    user_id: str
    name: str
