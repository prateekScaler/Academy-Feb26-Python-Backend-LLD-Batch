"""Policy as DATA, not code. Prices and windows live here — changing a tier or a
hold window is a one-line edit, no class touched (FR-5)."""

from .enums import SeatType

HOLD_TTL = 300.0        # seconds a LOCKED (unpaid) seat survives before it frees itself
CANCEL_CUTOFF = 3600.0  # FR-10: no cancel within 1 hour of show start

# A new tier is one entry, not a new class.
BASE_PRICE = {
    SeatType.GOLD: 150.0,
    SeatType.DIAMOND: 300.0,
    SeatType.PLATINUM: 450.0,
}
