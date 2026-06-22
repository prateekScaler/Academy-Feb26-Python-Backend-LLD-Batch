"""Exceptions — one per contract violation, so the caller can branch on intent."""


class SeatUnavailableError(Exception):
    """One or more requested seats are already LOCKED or BOOKED (the lost race)."""


class HoldExpiredError(Exception):
    """Tried to confirm a hold whose seats had already freed themselves."""


class CutoffPassedError(Exception):
    """Tried to cancel within the no-cancel window before showtime."""
