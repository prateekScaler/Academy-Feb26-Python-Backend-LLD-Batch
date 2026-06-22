"""ShowSeat — THE entity of this problem (LLD-26's association class): the
(seat × show) pairing. The physical Seat is shared across shows; its *per-show*
state — status + price — lives here.

The transient "hold" is NOT a separate object: it is simply status == LOCKED
plus a `locked_until` stamp and the user holding it. State machine:

    AVAILABLE --hold()--> LOCKED --confirm()--> BOOKED
                            |
                            +--TTL lapses--> AVAILABLE (lazily, on next access)
"""

from dataclasses import dataclass

from ..enums import SeatStatus
from .seat import Seat


@dataclass
class ShowSeat:
    show_id: str
    seat: Seat
    price: float
    status: SeatStatus = SeatStatus.AVAILABLE
    locked_until: float = 0.0          # meaningful only while LOCKED
    held_by: str | None = None         # the user currently holding it
    ticket_id: str | None = None       # set once BOOKED

    @property
    def seat_id(self) -> str:
        return self.seat.seat_id

    def is_lock_expired(self, now: float) -> bool:
        return self.status is SeatStatus.LOCKED and now >= self.locked_until
