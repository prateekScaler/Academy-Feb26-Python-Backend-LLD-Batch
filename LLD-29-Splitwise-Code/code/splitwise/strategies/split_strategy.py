from abc import ABC, abstractmethod

from ..models import Split
from ..exceptions import SplitError


class SplitStrategy(ABC):
    """The open variable. Contract: one Split per participant, summing to `amount`."""

    @abstractmethod
    def split(self, amount: int, participants: list, args=None) -> list:
        ...


class EqualSplit(SplitStrategy):
    def split(self, amount, participants, args=None):
        n = len(participants)
        base, remainder = divmod(amount, n)          # the leftover paise
        # the first `remainder` participants absorb one extra paisa each
        return [Split(u, base + (1 if i < remainder else 0))
                for i, u in enumerate(participants)]


class ExactSplit(SplitStrategy):
    def split(self, amount, participants, args):     # args: {User: paise}
        if sum(args.values()) != amount:
            raise SplitError("exact shares must sum to the total")
        return [Split(u, args[u]) for u in participants]


class PercentSplit(SplitStrategy):
    def split(self, amount, participants, args):     # args: {User: percent (int)}
        if sum(args.values()) != 100:
            raise SplitError("percentages must sum to 100")
        splits, allocated, last = [], 0, len(participants) - 1
        for i, u in enumerate(participants):
            if i < last:
                share = amount * args[u] // 100
                allocated += share
            else:
                share = amount - allocated            # last one absorbs the rounding
            splits.append(Split(u, share))
        return splits
