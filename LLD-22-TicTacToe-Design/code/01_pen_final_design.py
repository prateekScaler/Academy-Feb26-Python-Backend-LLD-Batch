"""
LLD-22 · Example 01 — The Pen design, resolved (E5 from LLD-21).

Run:  python3 01_pen_final_design.py

This is the design the six recap questions in LLD-22 walk you to:
  Q1  entities          -> Pen, Refill, Ink, Nib (nouns; no god class)
  Q2  write() placement -> abstract on Pen, overridden per pen
  Q3  the LSP trap      -> change_refill() must NOT live on Pen
  Q4  the fix           -> refilling is a CAPABILITY (Protocol)
  Q5  duplicate write() -> WritingStrategy injected into Pen
  Q6  final shape       -> flat hierarchy + Protocol + Strategy

Compare against the class diagram you submitted to the GitHub discussion.
"""

from __future__ import annotations
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Protocol, runtime_checkable


# === Supporting value types ==================================================
@dataclass(frozen=True)
class Ink:
    colour: str
    brand: str


@dataclass(frozen=True)
class Nib:
    radius: float


@dataclass
class Refill:
    nib: Nib
    ink: Ink


# === Writing behaviour as a Strategy (Q5) ====================================
class WritingStrategy(ABC):
    @abstractmethod
    def write(self) -> str: ...


class SmoothWriting(WritingStrategy):
    def write(self) -> str:
        return "writes smoothly"


class RoughWriting(WritingStrategy):
    def write(self) -> str:
        return "writes roughly"


class BoldWriting(WritingStrategy):
    def write(self) -> str:
        return "writes in bold strokes"


# === Pen base — flat hierarchy (Q2, Q6) ======================================
class Pen(ABC):
    def __init__(self, brand: str, name: str, strategy: WritingStrategy):
        self.brand = brand
        self.name = name
        self._strategy = strategy

    def write(self) -> str:
        return f"{self.brand} {self.name}: {self._strategy.write()}"


# === Refilling as a capability — Protocol (Q3, Q4) ===========================
@runtime_checkable
class RefillablePen(Protocol):
    def change_refill(self, refill: Refill) -> None: ...


# === Concrete pens ===========================================================
class GelPen(Pen):
    def __init__(self, brand: str, name: str, refill: Refill):
        super().__init__(brand, name, SmoothWriting())
        self._refill = refill

    def change_refill(self, refill: Refill) -> None:
        self._refill = refill


class BallPen(Pen):
    def __init__(self, brand: str, name: str, refill: Refill):
        super().__init__(brand, name, RoughWriting())
        self._refill = refill

    def change_refill(self, refill: Refill) -> None:
        self._refill = refill


class FountainPen(Pen):
    """No refill — holds ink + nib directly. Does NOT satisfy RefillablePen."""

    def __init__(self, brand: str, name: str, ink: Ink, nib: Nib):
        super().__init__(brand, name, BoldWriting())
        self._ink = ink
        self._nib = nib

    def change_ink(self, ink: Ink) -> None:
        self._ink = ink


class ThrowawayPen(Pen):
    """Has a refill inside, but it is sealed — also NOT RefillablePen."""

    def __init__(self, brand: str, name: str, refill: Refill):
        super().__init__(brand, name, RoughWriting())
        self._refill = refill


# === Callers ask for the CAPABILITY they need ================================
def restock_in_bulk(pens: list[RefillablePen], refill: Refill) -> None:
    """mypy rejects a FountainPen/ThrowawayPen in this list at the call site."""
    for p in pens:
        p.change_refill(refill)


def demo() -> None:
    blue = Ink("blue", "Camlin")
    fine = Nib(radius=0.4)
    refill = Refill(fine, blue)

    gel = GelPen("Pilot", "V5 Gel", refill)
    ball = BallPen("Reynolds", "045", refill)
    fountain = FountainPen("Lamy", "Safari", blue, Nib(radius=0.6))
    throwaway = ThrowawayPen("Cello", "Butterflow", refill)

    print("--- every pen writes (Q2: one contract) ---")
    for pen in (gel, ball, fountain, throwaway):
        print(" ", pen.write())

    print("\n--- bulk restock touches ONLY refillable pens (Q4) ---")
    refillable = [p for p in (gel, ball, fountain, throwaway) if isinstance(p, RefillablePen)]
    print("  refillable:", [p.name for p in refillable])
    restock_in_bulk(refillable, Refill(fine, Ink("black", "Camlin")))
    print("  restocked", len(refillable), "pens — FountainPen and ThrowawayPen untouched")

    print("\n--- swapping a writing style is data, not a subclass (Q5) ---")
    gel._strategy = BoldWriting()
    print(" ", gel.write())


if __name__ == "__main__":
    demo()
