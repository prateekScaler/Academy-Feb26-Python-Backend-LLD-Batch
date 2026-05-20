"""
LSP vs ISP — same smell, two diagnostic angles.

The Penguin / Printer examples show how one symptom
(NotImplementedError in an override) is a violation of BOTH principles.
The fix has the same shape: split capabilities into small interfaces,
and let each class claim only what it actually delivers.
"""

from abc import ABC, abstractmethod


# ---------------------------------------------------------------
# Penguin example
# ---------------------------------------------------------------
class IFlyable(ABC):
    @abstractmethod
    def fly(self): ...


class ISwimmable(ABC):
    @abstractmethod
    def swim(self): ...


class IWalkable(ABC):
    @abstractmethod
    def walk(self): ...


class Sparrow(IFlyable, IWalkable):
    def fly(self):  return "flapping"
    def walk(self): return "hopping"


class Penguin(ISwimmable, IWalkable):
    # NOT IFlyable - no fly() at all
    def swim(self): return "swimming"
    def walk(self): return "waddling"


class Duck(IFlyable, ISwimmable, IWalkable):
    def fly(self):  return "flying"
    def swim(self): return "paddling"
    def walk(self): return "walking"


def takeoff(b: IFlyable):
    return b.fly()


# ---------------------------------------------------------------
# Multi-function printer example
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
    def print(self, doc): return f"printed {doc}"


class OfficeMFP(IPrinter, IScanner, IFax):
    def print(self, doc): return f"printed {doc}"
    def scan(self):       return "scanned"
    def fax(self, num):   return f"faxed to {num}"


def print_invoice(p: IPrinter, doc):
    return p.print(doc)


if __name__ == "__main__":
    # Penguin
    print("takeoff(Duck):", takeoff(Duck()))
    print("takeoff(Sparrow):", takeoff(Sparrow()))
    # takeoff(Penguin())   # static type check would reject

    # Printer
    print("inkjet:", print_invoice(BasicInkjet(), "doc.pdf"))
    print("mfp:", print_invoice(OfficeMFP(), "doc.pdf"))
