"""Ticket — parking's `Move` record (FR-3). The event that outlives the stay:
billing reads it, audit reads it, a restart replays it. It stores the spot *id*,
not a live `Spot` ref — a ticket in a database long-outlives the in-memory object.

The lifecycle a ticket walks — ISSUED -> PAID -> EXITED — is the state machine the
three exceptions protect; `exit_time` stays None until the last transition."""

from __future__ import annotations

from dataclasses import dataclass

from models.vehicle import Vehicle


@dataclass
class Ticket:
    ticket_id: str
    vehicle: Vehicle
    floor_no: int
    spot_id: str
    entry_time: float
    exit_time: float | None = None
