"""
LLD-19 · Strategy · Example 11 — A tour of Strategy in the Python stdlib.

Run:  python3 11_stdlib_strategy_survey.py

Six stdlib functions that are textbook Strategy: each has a fixed
algorithm and one open parameter (a callable). Swapping the parameter
swaps the algorithm's "by what?" without rewriting the algorithm.

    1.  sorted(items, key=...)         — sort BY WHAT?
    2.  min / max(items, key=...)      — extremum BY WHAT?
    3.  filter(predicate, items)       — keep/drop RULE?
    4.  functools.reduce(op, items)    — combine HOW?
    5.  heapq.nlargest / nsmallest     — top-N BY WHAT?
    6.  sorted's underrated cousin:    — same idea, complex_key shape
        operator.itemgetter / attrgetter

Each section names which part is the fixed algorithm (the Context)
and which part is the swappable Strategy (the callable parameter).
"""

from __future__ import annotations
import operator
import heapq
from dataclasses import dataclass
from functools import reduce


# =====================================================================
# Sample data we'll re-use across the demos
# =====================================================================
@dataclass(frozen=True)
class Product:
    name: str
    price: float
    rating: float


PRODUCTS = [
    Product("MacBook Air",   1199.0, 4.7),
    Product("Dell XPS 13",    999.0, 4.5),
    Product("ThinkPad X1",   1699.0, 4.8),
    Product("Framework 13",  1299.0, 4.6),
]

WORDS = ["python", "go", "rust", "javascript", "c", "kotlin"]
NUMS  = [3, 7, 2, 8, 5, 1, 9, 4]


def banner(n: int, title: str) -> None:
    print(f"\n--- {n}. {title} ---")


# =====================================================================
# 1. sorted(key=...) — sort BY WHAT?
# =====================================================================
def demo_sorted() -> None:
    banner(1, "sorted(items, key=...)  —  algorithm: mergesort;  strategy: which field to compare by")

    by_price  = sorted(PRODUCTS, key=lambda p: p.price)
    by_rating = sorted(PRODUCTS, key=lambda p: -p.rating)   # negative → high-to-low
    by_name   = sorted(PRODUCTS, key=operator.attrgetter("name"))

    print(f"  cheapest first :  {[p.name for p in by_price]}")
    print(f"  best-rated     :  {[p.name for p in by_rating]}")
    print(f"  alpha by name  :  {[p.name for p in by_name]}")
    print("  (same mergesort runs every time — only the comparison key changes)")


# =====================================================================
# 2. min / max(key=...) — extremum BY WHAT?
# =====================================================================
def demo_min_max() -> None:
    banner(2, "max(items, key=...) / min(items, key=...)  —  algorithm: linear scan;  strategy: which metric")

    best_rating = max(PRODUCTS, key=lambda p: p.rating)
    cheapest    = min(PRODUCTS, key=lambda p: p.price)
    longest     = max(WORDS, key=len)
    shortest    = min(WORDS, key=len)

    print(f"  highest-rated   :  {best_rating.name}  ({best_rating.rating}★)")
    print(f"  cheapest        :  {cheapest.name}  (${cheapest.price})")
    print(f"  longest word    :  {longest!r}  ({len(longest)} chars)")
    print(f"  shortest word   :  {shortest!r}  ({len(shortest)} chars)")
    print("  (linear scan in each case — strategy answers 'extremum of what?')")


# =====================================================================
# 3. filter(predicate, items) — keep/drop RULE?
# =====================================================================
def demo_filter() -> None:
    banner(3, "filter(predicate, items)  —  algorithm: iterate-and-keep;  strategy: 'keep' predicate")

    cheap        = list(filter(lambda p: p.price < 1200, PRODUCTS))
    digit_only   = list(filter(str.isdigit, ["42", "hi", "7", "ok", "100"]))
    even_nums    = list(filter(lambda n: n % 2 == 0, NUMS))
    short_words  = list(filter(lambda w: len(w) <= 4, WORDS))

    print(f"  price < 1200    :  {[p.name for p in cheap]}")
    print(f"  digit strings   :  {digit_only}")
    print(f"  even numbers    :  {even_nums}")
    print(f"  short words     :  {short_words}")
    print("  (same loop walks every list — only the keep-predicate changes)")


# =====================================================================
# 4. functools.reduce(op, items, initial) — combine HOW?
# =====================================================================
def demo_reduce() -> None:
    banner(4, "reduce(op, items, initial)  —  algorithm: left-fold;  strategy: 'combine' op")

    total   = reduce(operator.add, NUMS, 0)
    product = reduce(operator.mul, NUMS, 1)
    largest = reduce(lambda a, b: a if a > b else b, NUMS)
    concat  = reduce(lambda a, b: a + ", " + b, WORDS)

    print(f"  sum             :  {total}")
    print(f"  product         :  {product}")
    print(f"  max (via fold)  :  {largest}")
    print(f"  joined words    :  {concat!r}")
    print("  (reduce always threads an accumulator left-to-right — op decides what 'combine' means)")


# =====================================================================
# 5. heapq.nlargest / nsmallest — top-N BY WHAT?
# =====================================================================
def demo_heapq() -> None:
    banner(5, "heapq.nlargest / nsmallest(n, items, key=...)  —  algorithm: heap of size n;  strategy: rank by what")

    top3_expensive = heapq.nlargest(3, PRODUCTS, key=lambda p: p.price)
    top2_rated     = heapq.nlargest(2, PRODUCTS, key=lambda p: p.rating)
    cheap2         = heapq.nsmallest(2, PRODUCTS, key=lambda p: p.price)

    print(f"  top 3 by price   :  {[p.name for p in top3_expensive]}")
    print(f"  top 2 by rating  :  {[p.name for p in top2_rated]}")
    print(f"  cheapest 2       :  {[p.name for p in cheap2]}")
    print("  (heap mechanics are fixed — the key= strategy decides what 'largest' means)")


# =====================================================================
# 6. operator.itemgetter / attrgetter — the strategy ITSELF, named
# =====================================================================
def demo_operator_getters() -> None:
    banner(6, "operator.itemgetter / attrgetter  —  pre-built strategy objects you should know")

    rows = [
        {"name": "Ada",   "age": 27, "score": 91},
        {"name": "Grace", "age": 32, "score": 88},
        {"name": "Linus", "age": 41, "score": 95},
    ]

    # itemgetter — Strategy for dict/sequence access
    by_age   = sorted(rows, key=operator.itemgetter("age"))
    by_score = sorted(rows, key=operator.itemgetter("score"), reverse=True)
    print(f"  sorted by age    :  {[r['name'] for r in by_age]}")
    print(f"  sorted by score  :  {[r['name'] for r in by_score]}")

    # attrgetter — Strategy for attribute access
    expensive_first = sorted(PRODUCTS, key=operator.attrgetter("price"), reverse=True)
    print(f"  attrgetter sort  :  {[p.name for p in expensive_first]}")
    print("  (these are SAME LAMBDA as before — operator just gives them a faster, named form)")


# =====================================================================
# Closing summary
# =====================================================================
def summary() -> None:
    print("\n" + "=" * 64)
    print("  Six functions. One pattern.")
    print("=" * 64)
    print("""
  Each stdlib function above is a Context:
    - has a FIXED ALGORITHM  (sort / scan / iterate / fold / heap)
    - has ONE OPEN PARAMETER (the key= or predicate or op)

  The open parameter IS the Strategy. Swap the strategy → swap the
  question the algorithm answers. The algorithm doesn't change.

  This is why Python rarely needs the formal Strategy class hierarchy
  (Context + ABC + ConcreteStrategy) you'd see in Java. A function
  IS a strategy in Python.

  When asked in an interview: "give a Strategy pattern example you've
  used" — any of these six functions is a perfectly valid answer.
""")


if __name__ == "__main__":
    demo_sorted()
    demo_min_max()
    demo_filter()
    demo_reduce()
    demo_heapq()
    demo_operator_getters()
    summary()
