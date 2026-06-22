"""Show — a movie on a screen at a time. It OWNS its ShowSeats (the per-show seat
state) and the lock that guards them — the per-show concurrency boundary.

The ShowSeats are built with prices already baked in; the service constructs them
(it knows the pricing strategy), so this model stays free of any strategy import."""

import threading

from .movie import Movie
from .screen import Screen
from .show_seat import ShowSeat


class Show:
    def __init__(self, show_id: str, movie: Movie, screen: Screen,
                 start_time: float, show_seats: dict[str, ShowSeat]):
        self.show_id = show_id
        self.movie = movie
        self.screen = screen
        self.start_time = start_time
        self.show_seats = show_seats
        self.lock = threading.Lock()    # guards the ShowSeats for THIS show

    def show_seat(self, seat_id: str) -> ShowSeat:
        return self.show_seats[seat_id]
