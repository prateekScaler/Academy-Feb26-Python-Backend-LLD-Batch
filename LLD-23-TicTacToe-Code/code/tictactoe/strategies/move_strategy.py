"""MoveStrategy — how a bot thinks. Difficulty maps to one of these, no if-tree."""

from __future__ import annotations

import random
from abc import ABC, abstractmethod

from models.board import Board


class MoveStrategy(ABC):
    @abstractmethod
    def choose(self, board: Board) -> tuple[int, int]: ...


class RandomMove(MoveStrategy):
    def choose(self, board: Board) -> tuple[int, int]:
        options = [(r, c) for r in range(board.n) for c in range(board.n)
                   if board.symbol_at(r, c) is None]
        return random.choice(options)
