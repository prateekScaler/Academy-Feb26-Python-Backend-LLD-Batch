"""Player ABC + BotPlayer. (HumanPlayer lives in cli.py — it's the input
adapter, and models never touch a console.)"""

from __future__ import annotations

from abc import ABC, abstractmethod

from enums import Difficulty, Symbol
from models.board import Board
from strategies.move_strategy import RandomMove


class Player(ABC):
    def __init__(self, name: str, symbol: Symbol):
        self.name = name
        self.symbol = symbol

    @abstractmethod
    def choose_move(self, board: Board) -> tuple[int, int]: ...


class BotPlayer(Player):
    STRATEGIES = {Difficulty.EASY: RandomMove}   # add HARD: MinimaxMove and the CLI menu grows itself

    def __init__(self, name: str, symbol: Symbol, difficulty: Difficulty = Difficulty.EASY):
        super().__init__(name, symbol)
        self.difficulty = difficulty
        self._strategy = self.STRATEGIES[difficulty]()

    def choose_move(self, board: Board) -> tuple[int, int]:
        return self._strategy.choose(board)
