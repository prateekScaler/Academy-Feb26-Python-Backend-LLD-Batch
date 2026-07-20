"""
LLD-22 · Example 02 — Tic-Tac-Toe skeleton (Step-4 output). YOUR HOMEWORK.

Run:  python3 02_tictactoe_skeleton.py   (passes once you fill in the bodies)

This file is exactly what you'd have on screen at minute 25 of the
interview: signatures, docstrings, constants — no bodies. Fill them in
before LLD-23, where we'll code it live and compare.

Rules of the homework:
  - Don't change the signatures (they're the contract we designed).
  - Make `demo()` at the bottom pass.
  - Stretch goal: change BOARD_SIZE/WIN_LEN to 5 and confirm Gomoku works.
"""

from __future__ import annotations
from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum

BOARD_SIZE = 3
WIN_LEN = 3


class Symbol(Enum):
    X = "X"
    O = "O"


class GameStatus(Enum):
    IN_PROGRESS = "in_progress"
    WON = "won"
    DRAW = "draw"


@dataclass
class Cell:
    """One square. Two facts + the rules that relate them (obstacle variant)."""
    symbol: Symbol | None = None
    blocked: bool = False

    def is_empty(self) -> bool:
        """True when there is no symbol AND the cell is not blocked."""
        raise NotImplementedError("homework")

    def can_place(self) -> bool:
        raise NotImplementedError("homework")


# NOTE: the full LLD-22 design makes Player an ABC with choose_move(board),
# implemented by HumanPlayer (reads input) and BotPlayer (difficulty -> MoveStrategy).
# The homework keeps the dataclass so you focus on Board/WinRule/Game logic;
# we build the Player family live in LLD-23.
@dataclass(frozen=True)
class Player:
    name: str
    symbol: Symbol


class InvalidMoveError(Exception):
    """Raised for: occupied cell, out-of-bounds, or move after game over."""


class Board:
    def __init__(self, n: int = BOARD_SIZE, blocked: set[tuple[int, int]] = frozenset()):
        """Create an n×n grid of Cells; cells listed in `blocked` start blocked."""
        raise NotImplementedError("homework")

    def cell(self, row: int, col: int) -> Cell:
        """The Cell object at (row, col)."""
        raise NotImplementedError("homework")

    def place(self, row: int, col: int, sym: Symbol) -> None:
        """Put `sym` at (row, col).

        Raises InvalidMoveError if (row, col) is outside the board or
        the cell is already occupied. MUST NOT silently overwrite.
        """
        raise NotImplementedError("homework")

    def at(self, row: int, col: int) -> Symbol | None:
        """Return the symbol at (row, col), or None if empty."""
        raise NotImplementedError("homework")

    def is_full(self) -> bool:
        """True when no PLAYABLE cell remains (blocked cells never count)."""
        raise NotImplementedError("homework")

    def render(self) -> str:
        """A printable picture of the grid. Presentation ONLY — no logic."""
        raise NotImplementedError("homework")


class WinRule(ABC):
    @abstractmethod
    def winner(self, board: Board) -> Symbol | None:
        """Return the winning symbol, or None if nobody has won yet."""


class KInARowRule(WinRule):
    def __init__(self, k: int = WIN_LEN):
        self.k = k

    def winner(self, board: Board) -> Symbol | None:
        """Scan rows, columns, and both diagonal directions for k in a row."""
        raise NotImplementedError("homework")


class Game:
    def __init__(self, players: list[Player], board: Board, rule: WinRule):
        """Validate: at least 2 players, all symbols distinct (FR-2!)."""
        raise NotImplementedError("homework")

    def make_move(self, row: int, col: int) -> None:
        """Current player places at (row, col).

        Order of operations (from the LLD-22 edge-case table):
          1. refuse if the game is already over        (InvalidMoveError)
          2. delegate placement to Board.place()        (it validates bounds/occupied)
          3. check win BEFORE checking full              (a winning move can fill the board)
          4. flip the turn ONLY if the move was legal and the game continues
        """
        raise NotImplementedError("homework")

    def status(self) -> GameStatus:
        raise NotImplementedError("homework")

    def winner(self) -> Player | None:
        """Map the winning Symbol (from the rule) back to the Player."""
        raise NotImplementedError("homework")

    def current_player(self) -> Player:
        raise NotImplementedError("homework")

    def render(self) -> str:
        raise NotImplementedError("homework")


# ============================================================================
# Acceptance test — your implementation must make this pass unchanged.
# ============================================================================
def demo() -> None:
    ajit = Player("Ajit", Symbol.X)
    vipul = Player("Vipul", Symbol.O)
    game = Game([ajit, vipul], Board(), KInARowRule())

    # X(0,0) O(0,1) X(1,1) O(0,2) X(2,2)  → X wins the main diagonal
    for r, c in [(0, 0), (0, 1), (1, 1), (0, 2), (2, 2)]:
        game.make_move(r, c)

    assert game.status() is GameStatus.WON, game.status()
    assert game.winner() == ajit, game.winner()
    print(game.render())
    print(f"winner: {game.winner().name} — all assertions passed ✔")

    # Edge: moving after game over must raise
    try:
        game.make_move(2, 0)
    except InvalidMoveError:
        print("post-game move correctly rejected ✔")
    else:
        raise AssertionError("expected InvalidMoveError after game over")


if __name__ == "__main__":
    demo()
