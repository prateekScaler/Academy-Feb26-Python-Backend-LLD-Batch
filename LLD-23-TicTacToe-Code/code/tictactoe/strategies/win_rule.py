"""WinRule — the FR-5 Strategy. Gomoku = KInARowRule(k) on a bigger Board."""

from __future__ import annotations

from abc import ABC, abstractmethod

from enums import Symbol
from models.board import Board

WIN_LEN = 3


class WinRule(ABC):
    @abstractmethod
    def winner(self, board: Board) -> Symbol | None: ...


class KInARowRule(WinRule):
    def __init__(self, k: int = WIN_LEN):
        self.k = k

    def winner(self, board: Board) -> Symbol | None:
        n, k = board.n, self.k
        directions = [(0, 1), (1, 0), (1, 1), (1, -1)]
        for r in range(n):
            for c in range(n):
                start = board.symbol_at(r, c)
                if start is None:
                    continue
                for dr, dc in directions:
                    end_r, end_c = r + (k - 1) * dr, c + (k - 1) * dc
                    if not (0 <= end_r < n and 0 <= end_c < n):
                        continue
                    if all(board.symbol_at(r + i * dr, c + i * dc) == start for i in range(k)):
                        return start
        return None
