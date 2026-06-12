"""
LLD-23 · Tic-Tac-Toe — the complete implementation we code live.

Run:  python3 01_tictactoe.py          # scripted demos (win, rejections, draw, bot, Gomoku)
      python3 01_tictactoe.py play     # interactive 2-player CLI game

Every line traces back to an LLD-22 decision:
  Cell (symbol; one fact today) <- FR-1 (tomorrow's facts land in the class)
  Player ABC + Human/Bot        <- FR-2 + FR-7 (Game can't tell them apart)
  turn = (i+1) % len(players)   <- FR-3
  InvalidMoveError, no turn flip<- FR-4
  WinRule Strategy              <- FR-5 (Gomoku = KInARowRule(5))
  GameStatus enum               <- FR-6 (the third state)
  render() outside make_move()  <- FR-8 + the CLI NFR
  moves: list[Move]             <- the game's memory: audit, replay, undo-when-asked
"""

from __future__ import annotations

import random
import sys
from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum

BOARD_SIZE = 3
WIN_LEN = 3


# === Enums & errors ==========================================================
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


class InvalidMoveError(Exception):
    """Occupied cell, out-of-bounds, or move after game over."""


# === Cell — FR-1: the smallest class in the build ============================
@dataclass
class Cell:
    """One fact today (symbol). Tomorrow's facts — blocked? bonus? trap? —
    land HERE, which is why the final design keeps it a class and not a
    bare Symbol|None value."""

    symbol: Symbol | None = None

    def is_empty(self) -> bool:
        return self.symbol is None


# === Board ===================================================================
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


# === WinRule — the FR-5 Strategy =============================================
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


# === The validated-input loop — ask until the answer is usable ==============
def ask(prompt: str, parse, valid, error: str):
    """Prompt -> parse -> validate -> retry. One tiny loop, reused for every
    question the CLI ever asks (row, col, symbol, difficulty, menu choice)."""
    while True:
        raw = input(prompt).strip()
        try:
            value = parse(raw)
            if valid(value):
                return value
        except (ValueError, KeyError):
            pass
        print(f"  {error}")


# === Player family — FR-2 + FR-7 =============================================
class Player(ABC):
    def __init__(self, name: str, symbol: Symbol):
        self.name = name
        self.symbol = symbol

    @abstractmethod
    def choose_move(self, board: Board) -> tuple[int, int]: ...


class HumanPlayer(Player):
    def choose_move(self, board: Board) -> tuple[int, int]:
        n = board.n
        print(f"{self.name} ({self.symbol.value}), your move.")
        row = ask(f"  row [0-{n - 1}]: ", int, lambda v: 0 <= v < n,
                  f"please enter a number between 0 and {n - 1}")
        col = ask(f"  col [0-{n - 1}]: ", int, lambda v: 0 <= v < n,
                  f"please enter a number between 0 and {n - 1}")
        return row, col


class MoveStrategy(ABC):
    @abstractmethod
    def choose(self, board: Board) -> tuple[int, int]: ...


class RandomMove(MoveStrategy):
    def choose(self, board: Board) -> tuple[int, int]:
        options = [(r, c) for r in range(board.n) for c in range(board.n)
                   if board.symbol_at(r, c) is None]
        return random.choice(options)


class BotPlayer(Player):
    STRATEGIES = {Difficulty.EASY: RandomMove}   # HARD -> MinimaxMove (stretch)

    def __init__(self, name: str, symbol: Symbol, difficulty: Difficulty = Difficulty.EASY):
        super().__init__(name, symbol)
        self.difficulty = difficulty
        self._strategy = self.STRATEGIES[difficulty]()

    def choose_move(self, board: Board) -> tuple[int, int]:
        return self._strategy.choose(board)


# === Game — the orchestrator =================================================
@dataclass(frozen=True)
class Move:
    player: Player
    row: int
    col: int


class Game:
    def __init__(self, players: list[Player], board: Board, rule: WinRule,
                 starting_index: int = 0):
        symbols = [p.symbol for p in players]
        if len(players) < 2 or len(set(symbols)) != len(symbols):
            raise ValueError("need >= 2 players with distinct symbols (FR-2)")
        self.players = players
        self.board = board
        self.rule = rule
        self._turn = starting_index
        self._status = GameStatus.IN_PROGRESS
        self._winner: Player | None = None
        self.moves: list[Move] = []   # the game's memory: audit, replay —
                                      # and the ten-line undo(), the day it's asked for

    # --- queries --------------------------------------------------------
    def status(self) -> GameStatus:
        return self._status

    def winner(self) -> Player | None:
        return self._winner

    def current_player(self) -> Player:
        return self.players[self._turn]

    def render(self) -> str:
        return self.board.render()

    # --- commands -------------------------------------------------------
    def make_move(self, row: int, col: int) -> None:
        if self._status is not GameStatus.IN_PROGRESS:
            raise InvalidMoveError("game already over")
        player = self.current_player()
        self.board.place(row, col, player.symbol)      # validates; raises on bad move
        self.moves.append(Move(player, row, col))
        winning_symbol = self.rule.winner(self.board)  # win BEFORE full
        if winning_symbol is not None:
            self._status = GameStatus.WON
            self._winner = next(p for p in self.players if p.symbol == winning_symbol)
        elif self.board.is_full():
            self._status = GameStatus.DRAW
        else:
            self._turn = (self._turn + 1) % len(self.players)

    def play_turn(self) -> Move:
        """Ask the current player (human OR bot — Game can't tell) and apply."""
        while True:
            row, col = self.current_player().choose_move(self.board)
            try:
                self.make_move(row, col)
                return self.moves[-1]
            except InvalidMoveError as e:
                print(f"  rejected: {e}")


# === Demos ===================================================================
def banner(t: str) -> None:
    print(f"\n--- {t} ---")


def demo_win() -> None:
    banner("happy path: X wins the diagonal")
    g = Game([_p("Ajit", "X"), _p("Vipul", "O")], Board(), KInARowRule())
    for r, c in [(0, 0), (0, 1), (1, 1), (0, 2), (2, 2)]:
        g.make_move(r, c)
    print(g.render())
    print(f"status={g.status().value}  winner={g.winner().name}")
    assert g.status() is GameStatus.WON and g.winner().name == "Ajit"


def demo_rejections() -> None:
    banner("FR-4: occupied / out-of-bounds / post-game")
    g = Game([_p("Ajit", "X"), _p("Vipul", "O")], Board(), KInARowRule())
    g.make_move(0, 0)
    for bad, why in [((0, 0), "occupied"), ((9, 9), "out of bounds")]:
        try:
            g.make_move(*bad)
        except InvalidMoveError as e:
            print(f"  rejected ({why}): {e}")
    assert g.current_player().name == "Vipul"   # rejections never flipped the turn
    print("  turn did not flip on any rejection ✔")
    for r, c in [(0, 1), (1, 1), (0, 2), (2, 2)]:   # X completes the diagonal
        g.make_move(r, c)
    try:
        g.make_move(2, 0)
    except InvalidMoveError as e:
        print(f"  rejected (game over): {e}")


def demo_draw() -> None:
    banner("FR-6: the third state")
    g = Game([_p("Ajit", "X"), _p("Vipul", "O")], Board(), KInARowRule())
    for r, c in [(0, 0), (0, 1), (0, 2), (1, 1), (1, 0), (2, 0), (1, 2), (2, 2), (2, 1)]:
        g.make_move(r, c)
    print(g.render())
    print(f"status={g.status().value}")
    assert g.status() is GameStatus.DRAW


def demo_bot() -> None:
    banner("FR-7: human-vs-bot — Game can't tell the difference")
    random.seed(7)
    g = Game([BotPlayer("EasyBot-1", Symbol.X), BotPlayer("EasyBot-2", Symbol.O)],
             Board(), KInARowRule())
    while g.status() is GameStatus.IN_PROGRESS:
        g.play_turn()
    print(g.render())
    print(f"status={g.status().value}" + (f"  winner={g.winner().name}" if g.winner() else ""))


def demo_gomoku() -> None:
    banner("Gomoku = two constructor arguments")
    g = Game([_p("Ajit", "X"), _p("Vipul", "O")], Board(n=5), KInARowRule(k=4))
    for c in range(4):
        g.make_move(0, c)          # X row 0
        if g.status() is GameStatus.IN_PROGRESS:
            g.make_move(1, c)      # O row 1
    print(g.render())
    print(f"5x5, k=4 → status={g.status().value}, winner={g.winner().name}")


def _p(name: str, sym: str) -> Player:
    """Scripted demos drive moves via make_move, so a minimal Player works."""
    class Scripted(Player):
        def choose_move(self, board: Board) -> tuple[int, int]:
            raise NotImplementedError
    return Scripted(name, Symbol(sym))


def _show(g: Game) -> None:
    """One board, lightly framed: a rule above, a breath below."""
    print("─" * (2 * g.board.n - 1))
    print(g.render())
    print()


def interactive() -> None:
    print("Tic-Tac-Toe — two players, 3x3, 0-indexed.")
    name1 = ask("Player 1 — name: ", str, lambda s: len(s) > 0, "name can't be empty")
    sym1 = ask(f"{name1} — symbol [X/O]: ", lambda raw: Symbol(raw.upper()),
               lambda v: True, "please type X or O")
    name2 = ask("Player 2 — name: ", str, lambda s: len(s) > 0, "name can't be empty")
    sym2 = Symbol.O if sym1 is Symbol.X else Symbol.X
    print(f"{name2} plays {sym2.value}.")
    g = Game([HumanPlayer(name1, sym1), HumanPlayer(name2, sym2)],
             Board(), KInARowRule())
    _show(g)
    while g.status() is GameStatus.IN_PROGRESS:
        g.play_turn()
        _show(g)
    print(f"{g.status().value.upper()}" + (f" — {g.winner().name} wins!" if g.winner() else ""))


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "play":
        interactive()
    else:
        demo_win()
        demo_rejections()
        demo_draw()
        demo_bot()
        demo_gomoku()
        print("\nall demos passed ✔")
