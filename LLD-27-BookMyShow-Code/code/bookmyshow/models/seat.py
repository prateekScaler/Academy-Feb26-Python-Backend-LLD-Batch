"""Seat — the *physical* seat. A value: its id and type never change. Whether it
is free is NOT here — that's per-show, so it lives on the ShowSeat."""

from dataclasses import dataclass

from ..enums import SeatType


@dataclass(frozen=True)
class Seat:
    seat_id: str           # "A1"
    seat_type: SeatType
