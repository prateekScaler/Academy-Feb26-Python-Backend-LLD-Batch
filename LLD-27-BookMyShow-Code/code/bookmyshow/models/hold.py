"""Hold — a transient RECEIPT returned by `hold()`. NOT stored anywhere and NOT a
domain entity: the source of truth is each ShowSeat's status (== LOCKED). This
just carries enough for confirm() to find the locked seats again."""

from __future__ import annotations

from typing import TYPE_CHECKING, NamedTuple

if TYPE_CHECKING:                       # avoid an import cycle (Show is heavy)
    from .show import Show


class Hold(NamedTuple):
    show: "Show"
    seat_ids: tuple[str, ...]
    user_id: str
    expires_at: float
