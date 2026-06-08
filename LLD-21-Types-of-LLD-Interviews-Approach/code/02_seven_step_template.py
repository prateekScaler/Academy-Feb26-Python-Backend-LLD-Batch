"""
LLD-21 · Example 02 — The 7-step template, blank.

Copy this file at the start of any LLD interview. Fill in each section as
you go. The structure itself does half the heavy lifting: an interviewer
can see you're running the playbook just by glancing at your IDE.

Run:  python3 02_seven_step_template.py
(it will print TODOs for whatever you haven't filled in yet)
"""

from __future__ import annotations
from typing import Protocol


# ==============================================================================
# STEP 1 — CLARIFY  (0–5 min)
# ==============================================================================
#   Write the questions you asked + the answers you got.
#   3–5 questions: scope, scale, out-of-scope.
#
#   Q1: __________________________________________  A: ____________
#   Q2: __________________________________________  A: ____________
#   Q3: __________________________________________  A: ____________
#   Q4: __________________________________________  A: ____________
#   Q5: __________________________________________  A: ____________
# ==============================================================================


# ==============================================================================
# STEP 2 — REQUIREMENTS  (5–10 min)
# ==============================================================================
#   FUNCTIONAL (what it does):
#     - ____
#     - ____
#     - ____
#
#   NON-FUNCTIONAL (how):
#     - persistence:  ____
#     - concurrency:  ____
#     - scale:        ____
#     - out-of-scope: ____
# ==============================================================================


# ==============================================================================
# STEP 3 — ENTITIES & RELATIONSHIPS  (10–18 min)
# ==============================================================================
#   Nouns (classes):
#     - ____
#     - ____
#     - ____
#
#   Relationships (composition / aggregation / association / inheritance):
#     - ____  ◆  ____   (composition: dies together)
#     - ____  ◇  ____   (aggregation: outlives)
#     - ____  →  ____   (association: knows about)
# ==============================================================================


# ==============================================================================
# STEP 4 — APIs  (signatures only, 18–25 min)
# ==============================================================================

class MainEntity:
    def __init__(self) -> None: ...

    def primary_action(self, *args) -> None:
        """The thing the interviewer asked about. TODO."""
        raise NotImplementedError("STEP 5 — fill this in")

    def secondary_action(self, *args) -> None:
        """The next thing. TODO."""
        raise NotImplementedError("STEP 5 — fill this in")


class OpenVariableStrategy(Protocol):
    """The open variable that the interviewer hinted at being swappable."""

    def do(self, *args) -> None: ...


# ==============================================================================
# STEP 5 — CODE THE HAPPY PATH  (25–65 min)
# ==============================================================================
# Don't start with edge cases. Start with the single happiest, most
# specific input you can think of. Get it to print the right answer.
# Then add edges from your Step 1 list.


# ==============================================================================
# STEP 6 — DEMO  (65–80 min, in your main block)
# ==============================================================================

def demo_happy_path() -> None:
    print("--- Happy path ---")
    # entity = MainEntity()
    # entity.primary_action(...)
    print("TODO: fill in the happy path demo")


def demo_edge_cases() -> None:
    print("--- Edge cases ---")
    # for each edge case agreed in Step 1, write a 2-line scenario here
    print("TODO: fill in the edge case demos")


# ==============================================================================
# STEP 7 — TRADE-OFFS  (80–90 min)
# ==============================================================================

def step7_tradeoffs() -> None:
    print(
        """
--- Trade-offs (say these out loud, even if not asked) ---
  Persistence:  TODO  (where state lives, what survives a restart)
  Concurrency:  TODO  (what breaks under contention, what to lock)
  Extension:    TODO  (the next feature, and exactly where it slots in)
"""
    )


if __name__ == "__main__":
    print(
        "LLD-21 seven-step template — fill in each STEP block before the next.\n"
    )
    demo_happy_path()
    demo_edge_cases()
    step7_tradeoffs()
