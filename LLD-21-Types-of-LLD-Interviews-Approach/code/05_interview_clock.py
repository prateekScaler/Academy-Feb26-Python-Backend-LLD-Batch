"""
LLD-21 · Example 05 — The interview clock.

A tiny CLI that walks you through a mock LLD interview on a 90-minute
clock. Prints what step you should be in, when to move on, and which
question to ask yourself in each phase.

Usage:
    python3 05_interview_clock.py           # 90-minute (real) clock
    python3 05_interview_clock.py 30        # 30-minute fast practice
    python3 05_interview_clock.py --silent  # no sleeping; print all steps now

The point is to practice STAYING ON THE CLOCK. Most candidates fail not
because they don't know what to do, but because they don't switch from
Step 4 to Step 5 when the budget runs out.
"""

from __future__ import annotations
import sys
import time


# Phases as a fraction of the total budget (sums to 1.0)
PHASES = [
    (
        "Step 1 — Clarify",
        0.055,  # ~5/90
        [
            "What's IN scope? (3 features max for an MVP)",
            "What's OUT of scope?",
            "Scale: in-memory? concurrent? approx N users?",
            "Persistence: stateless this round, or persist?",
            "Any specific format the interviewer wants?",
        ],
    ),
    (
        "Step 2 — Requirements",
        0.055,  # ~5/90
        [
            "List 3-5 functional requirements (verbs).",
            "List 3-4 non-functional requirements (scale, concurrency).",
            "Write them on the whiteboard / IDE comment header.",
        ],
    ),
    (
        "Step 3 — Entities & relationships",
        0.088,  # ~8/90
        [
            "Circle nouns in your requirements — those are classes.",
            "Underline verbs — those are methods.",
            "Draw composition (◆) vs aggregation (◇) carefully.",
            "Name the OPEN VARIABLE (the thing likely to change). That's your Strategy.",
        ],
    ),
    (
        "Step 4 — APIs",
        0.077,  # ~7/90
        [
            "For each class, write 2–5 method signatures.",
            "Types in/out. No bodies yet.",
            "Read the signatures aloud. Do they sound right?",
        ],
    ),
    (
        "Step 5 — Code the happy path, then edges",
        0.44,   # ~40/90 — the meat
        [
            "Build the SINGLE simplest happy path end-to-end first.",
            "Print as you go. Make it runnable.",
            "Then add the edges you agreed in Step 1, ONE AT A TIME.",
            "Narrate every pattern you use: 'Strategy here because…'",
        ],
    ),
    (
        "Step 6 — Demo & verify",
        0.166,  # ~15/90
        [
            "Run the code on screen.",
            "Walk one happy path execution.",
            "Walk one edge case execution.",
            "If it crashes — narrate the fix, stay calm.",
        ],
    ),
    (
        "Step 7 — Trade-offs & extensions",
        0.111,  # ~10/90
        [
            "Persistence: where does state live? What survives a crash?",
            "Concurrency: where do you lock? Why per-X and not per-Y?",
            "Extension: name the next feature and the EXACT class it'd live in.",
            "'If I had 10 more minutes I'd…' — always end with this.",
        ],
    ),
]


def banner(text: str, width: int = 72) -> None:
    bar = "=" * width
    print(f"\n{bar}\n  {text}\n{bar}")


def run_phase(name: str, prompts: list[str], minutes: float, silent: bool) -> None:
    banner(f"{name}   ({minutes:.1f} min)")
    print("Self-prompts for this phase:")
    for i, p in enumerate(prompts, 1):
        print(f"  {i}. {p}")
    if silent:
        return
    print(f"\nGo. You have {minutes:.1f} minutes. Next phase starts then.")
    time.sleep(minutes * 60)


def parse_args() -> tuple[float, bool]:
    """Returns (total_minutes, silent)."""
    silent = "--silent" in sys.argv
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    total = float(args[0]) if args else 90.0
    return total, silent


def main() -> None:
    total, silent = parse_args()
    banner(f"LLD Interview Clock — {total:.0f} minute round" + ("  (silent mode)" if silent else ""))
    if not silent:
        print("Tip: keep your code editor open in another window.")
        print("Each phase ends when you hear silence and the next banner prints.\n")
    for name, frac, prompts in PHASES:
        run_phase(name, prompts, minutes=total * frac, silent=silent)
    banner("Done. Stop coding. Talk through trade-offs if not already.")
    print(
        "If you ran out of time on Step 5: next time, "
        "shave Step 1+2 by 1 minute each and start coding 2 minutes earlier."
    )


if __name__ == "__main__":
    main()
