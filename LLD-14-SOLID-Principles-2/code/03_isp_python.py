"""
ISP in Python — three ways the principle shows up even though Python
has no `interface` keyword.

The point: ISP is about the *API surface* a client depends on. Whether
you express that surface as an ABC, a Protocol, or a duck-typed
contract, the rule is the same — clients should only see what they use.
"""

from abc import ABC, abstractmethod
from typing import Protocol


# ---------------------------------------------------------------
# Way 1: ABC (abstract base class)
# ---------------------------------------------------------------
class IPrinter(ABC):
    @abstractmethod
    def print(self, doc): ...


class IScanner(ABC):
    @abstractmethod
    def scan(self): ...


class IFax(ABC):
    @abstractmethod
    def fax(self, num): ...


class BasicInkjet(IPrinter):
    # Implements only what it can deliver.
    def print(self, doc):
        return f"printed {doc}"


class OfficeMFP(IPrinter, IScanner, IFax):
    def print(self, doc): return f"printed {doc}"
    def scan(self):       return "scanned"
    def fax(self, num):   return f"faxed to {num}"


def print_invoice(p: IPrinter, doc):
    # Client depends only on IPrinter - not scanning, not faxing.
    return p.print(doc)


# ---------------------------------------------------------------
# Way 2: Protocol (structural typing - no inheritance needed)
# ---------------------------------------------------------------
class SupportsClose(Protocol):
    def close(self) -> None: ...


def safely_close(thing: SupportsClose):
    """Works for ANY object with a .close() method - file, socket, DB."""
    thing.close()


# Notice: NeitherFile nor DBConnection inherits from SupportsClose.
# Protocols match by shape ("structural typing"), so ISP is honored
# without forcing a base class.
class File:
    def __init__(self, path): self.path = path
    def close(self):          print(f"closed {self.path}")


class DBConnection:
    def close(self):          print("db closed")


# ---------------------------------------------------------------
# Way 3: Duck typing (no ABC, no Protocol - just a documented contract)
# ---------------------------------------------------------------
class Cart:
    """Contract: anything passed as `discount` must have a .apply(total)."""

    def __init__(self, items, discount=None):
        self.items = items
        self.discount = discount

    def total(self):
        base = sum(i["price"] for i in self.items)
        if self.discount is None:
            return base
        return self.discount.apply(base)


class PercentOff:
    def __init__(self, percent): self.percent = percent
    def apply(self, total):      return total * (1 - self.percent)


class FlatOff:
    def __init__(self, amount): self.amount = amount
    def apply(self, total):     return total - self.amount


# The "interface" here is just .apply(total). Cart never demanded a
# fat object with .name(), .can_combine(), .audit_log() etc - the
# discount API is exactly as wide as Cart actually uses. That's ISP.


if __name__ == "__main__":
    # ABC
    print("ABC:", print_invoice(BasicInkjet(), "invoice-42"))
    print("ABC:", print_invoice(OfficeMFP(), "invoice-43"))

    # Protocol
    safely_close(File("/tmp/x"))
    safely_close(DBConnection())

    # Duck typing
    cart = Cart([{"price": 100}, {"price": 50}], discount=PercentOff(0.1))
    print("Cart total:", cart.total())   # 135.0
