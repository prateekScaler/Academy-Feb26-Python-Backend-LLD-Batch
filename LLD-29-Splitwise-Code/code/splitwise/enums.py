from enum import Enum


class SplitType(Enum):
    """How an expense divides — the open variable (one type ⇒ one strategy)."""
    EQUAL = "EQUAL"
    EXACT = "EXACT"
    PERCENT = "PERCENT"
