"""
LLD-18 · Prototype · Example 1 — The minimal Prototype.

Run:  python3 01_basic_clone.py

A "prototype" is just an object that knows how to produce a copy of itself.
We expose one method: clone(). Internally it uses copy.deepcopy so every
clone is fully independent — mutations on one don't leak into the others.

Notice we *don't* need an ABC in Python — duck typing means anyone with
a .clone() method qualifies. The ABC is shown only for the people who
like the explicit contract.
"""

from __future__ import annotations

import copy
from abc import ABC, abstractmethod
from dataclasses import dataclass, field


# --- 1.  Formal Prototype interface (optional in Python) ---
class Prototype(ABC):
    @abstractmethod
    def clone(self) -> "Prototype": ...


# --- 2.  A concrete Prototype ---
@dataclass
class ReportTemplate(Prototype):
    title: str
    sections: list[str] = field(default_factory=list)
    style: dict[str, str] = field(default_factory=dict)

    def clone(self) -> "ReportTemplate":
        # deepcopy: every list/dict inside is independent in the clone
        return copy.deepcopy(self)


# --- 3.  Usage ---
if __name__ == "__main__":
    # Build the prototype once
    base = ReportTemplate(
        title="Weekly Sales Report",
        sections=["Summary", "Top Products", "Regional Breakdown"],
        style={"font": "Inter", "color": "#10b981"},
    )

    # Make many similar reports — each tweaks the clone, not the prototype
    q1 = base.clone()
    q1.title = "Q1 Sales Report"
    q1.sections.append("YoY Comparison")

    q2 = base.clone()
    q2.title = "Q2 Sales Report"
    q2.style["color"] = "#3b82f6"

    print("base    :", base)
    print("q1      :", q1)
    print("q2      :", q2)

    # Prove the clones are independent
    assert base.title == "Weekly Sales Report"          # unchanged
    assert "YoY Comparison" not in base.sections        # not leaked into base
    assert base.style["color"] == "#10b981"             # not leaked into base
    print("\nAll clones independent ✓")
