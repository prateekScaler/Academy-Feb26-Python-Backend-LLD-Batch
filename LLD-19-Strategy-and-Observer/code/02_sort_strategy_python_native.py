"""
LLD-19 · Strategy · Example 2 — Strategy in Pythonic form (callables).

Run:  python3 02_sort_strategy_python_native.py

In Python, a Strategy is usually a plain function, not a class — the
stdlib's `sorted(key=)` is the textbook example. This file shows the
same problem solved two ways and shows why the Pythonic form is
preferred when the algorithm has no state.
"""

from __future__ import annotations
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Callable


# ====================================================================
# The data
# ====================================================================
@dataclass(frozen=True)
class Product:
    name: str
    price: float
    rating: float
    released: str   # ISO date string


PRODUCTS = [
    Product("MacBook Air",   1199.0, 4.7, "2024-03-08"),
    Product("Dell XPS 13",    999.0, 4.5, "2023-11-14"),
    Product("ThinkPad X1",   1699.0, 4.8, "2024-01-22"),
    Product("Framework 13",  1299.0, 4.6, "2024-05-30"),
]


# ====================================================================
# Approach A — formal Strategy (overkill here, but instructive)
# ====================================================================
class SortStrategy(ABC):
    @abstractmethod
    def key(self, p: Product) -> object: ...


class SortByPrice(SortStrategy):
    def key(self, p: Product) -> object: return p.price


class SortByRating(SortStrategy):
    def key(self, p: Product) -> object: return -p.rating   # high-to-low


class SortByDate(SortStrategy):
    def key(self, p: Product) -> object: return p.released


def sort_with_strategy(items: list[Product], strategy: SortStrategy) -> list[Product]:
    return sorted(items, key=strategy.key)


# ====================================================================
# Approach B — Pythonic Strategy: just a callable
# ====================================================================
SortKey = Callable[[Product], object]

by_price   : SortKey = lambda p: p.price
by_rating  : SortKey = lambda p: -p.rating
by_date    : SortKey = lambda p: p.released

# Or as a one-liner via operator.attrgetter
import operator
by_name = operator.attrgetter("name")


# ====================================================================
# Demo
# ====================================================================
def main() -> None:
    print("--- Approach A (formal Strategy classes) ---")
    for strategy in [SortByPrice(), SortByRating(), SortByDate()]:
        top = sort_with_strategy(PRODUCTS, strategy)[0]
        print(f"  best by {strategy.__class__.__name__:>13}: {top.name}")

    print("\n--- Approach B (Pythonic — plain callables, just `sorted(key=)`) ---")
    for label, key in [
        ("price",  by_price),
        ("rating", by_rating),
        ("date",   by_date),
        ("name",   by_name),
    ]:
        top = sorted(PRODUCTS, key=key)[0]
        print(f"  best by {label:>6}: {top.name}")

    print("\nThe stdlib already IS the Strategy pattern — and the function form")
    print("is preferred when the algorithm has no state of its own.")


if __name__ == "__main__":
    main()
