"""Screen — an auditorium: a fixed grid of physical seats. `Cinema ◆ Screen ◆ Seat`
is a composition chain (a seat has no life outside its screen)."""

from .seat import Seat


class Screen:
    def __init__(self, screen_id: str, name: str, seats: list[Seat]):
        self.screen_id = screen_id
        self.name = name
        self.seats = seats
