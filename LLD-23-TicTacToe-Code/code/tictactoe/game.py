"""Game — the orchestrator. Exactly the API the class derived: make_move /
status / winner / current_player / render.
No input(), no print() — the engine never learns it's a CLI."""

from __future__ import annotations

from dataclasses import dataclass

from enums import GameStatus
from exceptions import InvalidMoveError
from models.board import Board
from models.player import Player
from strategies.win_rule import WinRule


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
