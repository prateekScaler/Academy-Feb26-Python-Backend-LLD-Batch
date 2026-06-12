"""
console.py — the game-AGNOSTIC console toolkit. Master once, reuse everywhere.

One core loop (ask) + the four question shapes nearly every CLI round needs:
a bounded number, a non-empty string, a menu, a yes/no. Zero dependencies.
In a machine-coding interview: copy this file in, then write only the game.
"""

from __future__ import annotations

from enum import Enum
from typing import Callable, TypeVar

T = TypeVar("T")


def ask(prompt: str, parse: Callable[[str], T] = str,
        valid: Callable[[T], bool] = lambda v: True,
        error: str = "invalid input") -> T:
    """The validated-input loop: prompt -> parse -> validate -> retry.

    The ONLY input() loop in the whole project. Bad input is re-asked here,
    at the boundary — the engine never sees a raw string.
    """
    while True:
        raw = input(prompt).strip()
        try:
            value = parse(raw)
            if valid(value):
                return value
        except (ValueError, KeyError):
            pass
        print(f"  {error}")


def ask_nonempty(label: str) -> str:
    return ask(f"{label}: ", valid=lambda s: s != "", error="can't be empty")


def ask_int(label: str, lo: int, hi: int) -> int:
    return ask(f"{label} [{lo}-{hi}]: ", parse=int,
               valid=lambda v: lo <= v <= hi,
               error=f"please enter a number between {lo} and {hi}")


def ask_choice(label: str, options: dict[str, T]) -> T:
    """A menu. options maps UPPERCASE keys to values; typing is case-insensitive."""
    keys = "/".join(options)
    return ask(f"{label} [{keys}]: ",
               parse=lambda raw: options[raw.upper()],   # KeyError -> retry
               error=f"please type one of: {keys}")


def ask_enum(label: str, enum_cls: type[Enum]) -> Enum:
    """A menu built straight from an Enum — accepts member values."""
    return ask_choice(label, {m.value.upper(): m for m in enum_cls})


def ask_yes_no(label: str) -> bool:
    return ask_choice(label, {"Y": True, "N": False})
