"""exceptions.py — only for CONTRACT violations.

The flip that defines this problem: a full lot is NOT an exception (FR-4 returns
`None` — it's expected flow). These three are different — they mean the caller
broke a rule that must hold, so the engine refuses loudly instead of guessing.

In the layered build these map straight to HTTP status codes at the controller:
  InvalidTicketError -> 404 · AlreadyPaidError -> 409 · UnpaidExitError -> 402."""

from __future__ import annotations


class InvalidTicketError(Exception):
    """Unknown or already-used ticket — unlike a full lot, this IS exceptional."""


class AlreadyPaidError(Exception):
    """A ticket is paid exactly once (FR-9)."""


class UnpaidExitError(Exception):
    """The gate opens only for a paid ticket (FR-9)."""
