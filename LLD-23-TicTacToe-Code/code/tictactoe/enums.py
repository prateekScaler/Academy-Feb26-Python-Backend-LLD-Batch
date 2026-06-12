"""The shared vocabulary — imports nothing, everything imports it."""

from enum import Enum


class Symbol(Enum):
    X = "X"
    O = "O"


class GameStatus(Enum):
    IN_PROGRESS = "in_progress"
    WON = "won"
    DRAW = "draw"


class Difficulty(Enum):
    EASY = "easy"
    HARD = "hard"
