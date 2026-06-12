"""Cell — FR-1: the smallest class in the build."""

from __future__ import annotations

from dataclasses import dataclass

from enums import Symbol


@dataclass
class Cell:
    """One fact today (symbol). Tomorrow's facts — blocked? bonus? trap? —
    land HERE, which is why the final design keeps it a class and not a
    bare Symbol|None value."""

    symbol: Symbol | None = None

    def is_empty(self) -> bool:
        return self.symbol is None
