"""cli.py — Tic-Tac-Toe's edge. Everything that talks to a console lives in
console.py (generic) and here (game-specific). The engine never imports us.

Built entirely on the console.py toolkit — count the input() calls here: zero.
"""

from __future__ import annotations

from console import ask_choice, ask_enum, ask_int, ask_nonempty, ask_yes_no
from enums import GameStatus, Symbol
from exceptions import InvalidMoveError
from game import Game
from models.board import Board
from models.player import BotPlayer, Player
from strategies.win_rule import KInARowRule


class HumanPlayer(Player):
    """The input adapter — a Player whose 'brain' is the console."""

    def choose_move(self, board: Board) -> tuple[int, int]:
        n = board.n
        print(f"{self.name} ({self.symbol.value}), your move.")
        return ask_int("  row", 0, n - 1), ask_int("  col", 0, n - 1)


def _make_player(idx: int, taken: Symbol | None) -> Player:
    name = ask_nonempty(f"Player {idx} — name")
    if taken is None:
        symbol = ask_enum(f"{name} — symbol", Symbol)
    else:
        symbol = Symbol.O if taken is Symbol.X else Symbol.X
        print(f"{name} plays {symbol.value}.")
    kind = ask_choice(f"{name} — human or bot", {"H": "human", "B": "bot"})
    if kind == "human":
        return HumanPlayer(name, symbol)
    difficulty = ask_choice(f"{name} — difficulty",
                            {d.value.upper(): d for d in BotPlayer.STRATEGIES})
    return BotPlayer(name, symbol, difficulty)      # menu grows with the registry


def _show(game: Game) -> None:
    """One board, lightly framed: a rule above, a breath below."""
    print("─" * (2 * game.board.n - 1))
    print(game.render())
    print()


def run(game: Game) -> None:
    """render -> ask -> apply -> repeat. A rejection re-prompts the SAME player."""
    _show(game)
    while game.status() is GameStatus.IN_PROGRESS:
        player = game.current_player()
        row, col = player.choose_move(game.board)
        try:
            game.make_move(row, col)
        except InvalidMoveError as e:
            print(f"  rejected: {e}")
            continue
        if not isinstance(player, HumanPlayer):
            print(f"{player.name} ({player.symbol.value}) plays ({row}, {col})")
        _show(game)
    if game.winner() is not None:
        print(f"{game.winner().name} wins!")
    else:
        print("Draw.")


def play() -> None:
    print("Tic-Tac-Toe — 3x3, 0-indexed.")
    while True:
        p1 = _make_player(1, taken=None)
        p2 = _make_player(2, taken=p1.symbol)
        run(Game([p1, p2], Board(), KInARowRule()))
        if not ask_yes_no("Play again?"):
            break
        print()
