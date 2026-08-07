"""Move — one recorded placement for undo/redo history."""

from __future__ import annotations

from models.player import Player


class Move:
    def __init__(self, player: Player, row: int, col: int):
        self.player = player
        self.row = row
        self.col = col
