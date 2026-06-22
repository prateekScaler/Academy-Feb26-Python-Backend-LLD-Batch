"""SeatLocker — the concurrency approach, made pluggable (the LLD-26 promise).

LLD-26 listed several ways to enforce "one seat, one ticket". Here they are as a
strategy so the SAME race can run under each and you can watch what happens:

    PerShowLock  — our choice: one mutex per show. check-and-set is atomic.
    NaiveLocker  — no mutual exclusion; only to DEMONSTRATE the double-book bug.

How PerShowLock maps to a real, distributed system (named, not built here):
    one DB           -> SELECT ... FOR UPDATE on the show_seat row (pessimistic)
    optimistic       -> UPDATE ... WHERE status='AVAILABLE'; check rows-affected
    the hard floor   -> UNIQUE(show_id, seat_id) on confirmed bookings
    many services    -> a Redis lock with a TTL (the hold's TTL == the key's TTL)
"""

from abc import ABC, abstractmethod
from contextlib import nullcontext

from ..models import Show


class SeatLocker(ABC):
    @abstractmethod
    def guard(self, show: Show):
        """A context manager held around the check-and-set on this show."""


class PerShowLock(SeatLocker):
    """One mutex per show. Different shows never contend, so this scales fine and
    stays simple. The in-memory twin of `SELECT ... FOR UPDATE`."""

    def guard(self, show: Show):
        return show.lock


class NaiveLocker(SeatLocker):
    """No mutual exclusion — only here to DEMONSTRATE the race. check-then-act is
    two steps, so two threads both pass the check and both 'win'. Never ship this."""

    def guard(self, show: Show):
        return nullcontext()
