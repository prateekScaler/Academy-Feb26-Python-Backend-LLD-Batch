"""Money is integer **paise** everywhere — no float drift, and the penny problem
becomes a clean integer-remainder rule."""


def rupees(r: float) -> int:
    """₹ -> paise."""
    return int(round(r * 100))


def fmt(paise: int) -> str:
    """paise -> '₹x.xx'."""
    return f"₹{paise / 100:.2f}"
