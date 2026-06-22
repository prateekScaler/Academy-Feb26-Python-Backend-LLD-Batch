"""Console — the game-agnostic input toolkit carried over from earlier classes.
It knows nothing about seats or bookings: it just turns messy stdin into clean,
validated values, and re-prompts on bad input. The CLI is the only caller."""

from __future__ import annotations

from typing import Callable, Sequence, TypeVar

T = TypeVar("T")


def ask(prompt: str) -> str:
    return input(prompt).strip()


def ask_nonempty(prompt: str) -> str:
    while True:
        value = ask(prompt)
        if value:
            return value
        print("  (please type something)")


def ask_choice(prompt: str, options: Sequence[str]) -> str:
    """Pick one of `options` (case-insensitive, prefix-friendly)."""
    lowered = [o.lower() for o in options]
    menu = " / ".join(options)
    while True:
        value = ask(f"{prompt} [{menu}]: ").lower()
        if value in lowered:
            return options[lowered.index(value)]
        matches = [o for o, lo in zip(options, lowered) if lo.startswith(value)]
        if value and len(matches) == 1:
            return matches[0]
        print(f"  (choose one of: {menu})")


def ask_seats(prompt: str) -> list[str]:
    """Comma/space separated seat ids -> a clean upper-cased list."""
    while True:
        raw = ask(prompt)
        seats = [s.upper() for s in raw.replace(",", " ").split()]
        if seats:
            return seats
        print("  (enter at least one seat, e.g. A1 A2)")


def ask_until(prompt: str, parse: Callable[[str], T]) -> T:
    """Apply `parse`; re-prompt on ValueError/KeyError with the message."""
    while True:
        raw = ask(prompt)
        try:
            return parse(raw)
        except (ValueError, KeyError) as exc:
            print(f"  ({exc})")
