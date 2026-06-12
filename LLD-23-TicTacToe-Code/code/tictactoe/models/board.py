"""Board — geometry + occupancy, nothing else. No turns, no rules, no I/O."""

from __future__ import annotations

from enums import Symbol
from exceptions import InvalidMoveError
from models.cell import Cell

BOARD_SIZE = 3


class Board:
    def __init__(self, n: int = BOARD_SIZE):
        self.n = n
        self._grid = [[Cell() for _ in range(n)] for _ in range(n)]

    def cell(self, row: int, col: int) -> Cell:
        if not (0 <= row < self.n and 0 <= col < self.n):
            raise InvalidMoveError(f"({row}, {col}) is out of bounds")
        return self._grid[row][col]

    def symbol_at(self, row: int, col: int) -> Symbol | None:
        return self.cell(row, col).symbol

    def place(self, row: int, col: int, sym: Symbol) -> None:
        # Hint: when squares gain a second fact — say, BLOCKED cells that
        # nobody may play — Cell grows `blocked` plus a can_place() rule,
        # and THIS check asks the cell. One class changes; nothing else here.
        cell = self.cell(row, col)
        if not cell.is_empty():
            raise InvalidMoveError(f"cell ({row}, {col}) is occupied")
        cell.symbol = sym

    def is_full(self) -> bool:
        return not any(c.is_empty() for row in self._grid for c in row)

    def render(self) -> str:
        return "\n".join(" ".join(c.symbol.value if c.symbol else "." for c in row)
                         for row in self._grid)
