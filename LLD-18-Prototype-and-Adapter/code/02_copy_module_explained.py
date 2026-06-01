"""
LLD-18 · Prototype · Example 2 — The shallow-vs-deep trap.

Run:  python3 02_copy_module_explained.py

Single most common Prototype bug: using copy.copy() (shallow) when the
object holds mutable inner data. The clones look independent but secretly
share state through pointer equality.

This file demonstrates:
  1. The bug (shallow copy sharing inner list)
  2. The fix (deep copy)
  3. The performance lever (custom __deepcopy__ to share read-only state)
"""

import copy
from dataclasses import dataclass, field


# ====================================================================
# 1.  THE BUG — shallow copy shares mutable inner state
# ====================================================================
@dataclass
class CartShallow:
    items: list[str] = field(default_factory=list)

    def clone(self) -> "CartShallow":
        return copy.copy(self)        # shallow — DANGER


def demo_shallow_bug() -> None:
    print("--- Shallow copy bug ---")
    template = CartShallow()
    template.items.append("free-sample")

    c1 = template.clone()
    c1.items.append("book")           # only c1 should see this

    c2 = template.clone()
    print(f"  template.items = {template.items}")
    print(f"  c1.items       = {c1.items}")
    print(f"  c2.items       = {c2.items}")
    print(f"  id match?      template={id(template.items)}  c1={id(c1.items)}  c2={id(c2.items)}")
    print("  All three share THE SAME list — that's the bug.\n")


# ====================================================================
# 2.  THE FIX — deepcopy
# ====================================================================
@dataclass
class CartDeep:
    items: list[str] = field(default_factory=list)

    def clone(self) -> "CartDeep":
        return copy.deepcopy(self)    # deep — safe


def demo_deep_fix() -> None:
    print("--- Deep copy fix ---")
    template = CartDeep()
    template.items.append("free-sample")

    c1 = template.clone()
    c1.items.append("book")           # only c1 sees this

    c2 = template.clone()
    print(f"  template.items = {template.items}")
    print(f"  c1.items       = {c1.items}")
    print(f"  c2.items       = {c2.items}")
    print(f"  id match?      template={id(template.items)}  c1={id(c1.items)}  c2={id(c2.items)}")
    print("  Each cart has its OWN list — fixed.\n")


# ====================================================================
# 3.  THE PERFORMANCE LEVER — custom __deepcopy__
# ====================================================================
# Sometimes you DON'T want to deep-copy everything — e.g., a giant
# read-only model loaded into memory. Share it across clones; only copy
# the per-clone mutable state. Hook into Python's copy protocol:
class MLPredictor:
    def __init__(self) -> None:
        self.model = self._load_giant_model()        # 800 MB read-only
        self.history: list[str] = []                 # per-clone state

    @staticmethod
    def _load_giant_model() -> dict:
        # Pretend this is 800 MB of weights. We use a marker for the demo.
        return {"weights": "<800MB tensor>", "id": id(object())}

    def __deepcopy__(self, memo):
        new = MLPredictor.__new__(MLPredictor)   # skip __init__
        new.model = self.model                   # SHARE — don't copy 800 MB
        new.history = []                         # fresh per-clone state
        return new


def demo_custom_deepcopy() -> None:
    print("--- Custom __deepcopy__: share what's safe, copy what's mutable ---")
    p1 = MLPredictor()
    p2 = copy.deepcopy(p1)
    p3 = copy.deepcopy(p1)

    p1.history.append("p1: predicted X")
    p2.history.append("p2: predicted Y")

    print(f"  p1.history = {p1.history}")
    print(f"  p2.history = {p2.history}")
    print(f"  p3.history = {p3.history}")
    print(f"  model shared? {p1.model is p2.model is p3.model}")
    print("  Histories independent, model shared — cheap & correct.\n")


if __name__ == "__main__":
    demo_shallow_bug()
    demo_deep_fix()
    demo_custom_deepcopy()
