"""models — the DOMAIN layer: pure objects, zero I/O, importable anywhere.

The re-exports below are the package's curated front door, so call sites read
`from models import Spot, Ticket` instead of the full module path. Delete a line
and only the short form breaks — the module itself stays reachable."""

from models.floor import Floor
from models.payment import Payment
from models.spot import Spot
from models.ticket import Ticket
from models.vehicle import Vehicle

__all__ = ["Floor", "Payment", "Spot", "Ticket", "Vehicle"]
