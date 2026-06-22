"""Payment — one per ticket; money doesn't mutate, so it's frozen."""

from dataclasses import dataclass

from ..enums import PaymentMode


@dataclass(frozen=True)
class Payment:
    payment_id: str
    ticket_id: str
    amount: float
    mode: PaymentMode
    paid_at: float
