"""WinRule — the FR-5 Strategy. Gomoku = KInARowRule(k) on a bigger Board."""

from __future__ import annotations

from abc import ABC, abstractmethod

from enums import Symbol
from models.board import Board

WIN_LEN = 3
DIRECTIONS = ((0, 1), (1, 0), (1, 1), (1, -1))


class WinRule(ABC):
    @abstractmethod
    def winner(self, board: Board, row: int, col: int) -> Symbol | None: ...


class KInARowRule(WinRule):
    """Full-board scan — O(N² × K). Keeps the original strategy name."""

    def __init__(self, k: int = WIN_LEN):
        self.k = k

    def winner(self, board: Board, row: int, col: int) -> Symbol | None:
        n, k = board.n, self.k
        for r in range(n):
            for c in range(n):
                start = board.symbol_at(r, c)
                if start is None:
                    continue
                for dr, dc in DIRECTIONS:
                    end_r, end_c = r + (k - 1) * dr, c + (k - 1) * dc
                    if not (0 <= end_r < n and 0 <= end_c < n):
                        continue
                    if all(board.symbol_at(r + i * dr, c + i * dc) == start for i in range(k)):
                        return start
        return None


FullBoardScanRule = KInARowRule


class LastMoveWinRule(WinRule):
    """Checks only lines through the last move — O(K)."""

    def __init__(self, k: int = WIN_LEN):
        self.k = k

    def winner(self, board: Board, row: int, col: int) -> Symbol | None:
        sym = board.symbol_at(row, col)
        if sym is None:
            return None

        n, k = board.n, self.k
        for dr, dc in DIRECTIONS:
            count = 1
            r, c = row + dr, col + dc
            while 0 <= r < n and 0 <= c < n and board.symbol_at(r, c) == sym:
                count += 1
                r += dr
                c += dc
            r, c = row - dr, col - dc
            while 0 <= r < n and 0 <= c < n and board.symbol_at(r, c) == sym:
                count += 1
                r -= dr
                c -= dc
            if count >= k:
                return sym
        return None
