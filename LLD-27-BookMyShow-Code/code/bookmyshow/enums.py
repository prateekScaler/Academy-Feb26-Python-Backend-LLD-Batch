"""Enums — the small named sets straight from the LLD-26 class diagram."""

from enum import Enum


class SeatType(Enum):
    GOLD = "gold"
    DIAMOND = "diamond"
    PLATINUM = "platinum"


class SeatStatus(Enum):
    AVAILABLE = "available"
    LOCKED = "locked"      # the third state a bool can't hold — held while paying
    BOOKED = "booked"


class PaymentMode(Enum):
    UPI = "upi"
    CREDIT_CARD = "credit_card"
    NETBANKING = "netbanking"


class TicketStatus(Enum):
    CONFIRMED = "confirmed"
    CANCELLED = "cancelled"
