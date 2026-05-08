"""defaultdict — never get a KeyError again."""
from collections import defaultdict


# --- Problem: grouping with plain dict ---
words = ["apple", "banana", "avocado", "blueberry", "cherry", "apricot"]

# Plain dict: must check if key exists every time
grouped = {}
for word in words:
    first_letter = word[0]
    if first_letter not in grouped:     # boilerplate!
        grouped[first_letter] = []
    grouped[first_letter].append(word)

print("Plain dict (verbose):")
for k, v in sorted(grouped.items()):
    print(f"  {k}: {v}")


# --- Solution: defaultdict ---
grouped2 = defaultdict(list)   # missing key → automatically creates empty list
for word in words:
    grouped2[word[0]].append(word)   # no if-check needed!

print("\ndefaultdict(list) (clean):")
for k, v in sorted(grouped2.items()):
    print(f"  {k}: {v}")


# --- More factories ---
# defaultdict(int) → missing key = 0 (great for counting)
counter = defaultdict(int)
for word in words:
    counter[word[0]] += 1   # no KeyError, starts at 0

print(f"\ndefaultdict(int) — counting:")
print(f"  {dict(counter)}")


# defaultdict(set) → missing key = empty set
tags = defaultdict(set)
tags["python"].add("backend")
tags["python"].add("scripting")
tags["java"].add("enterprise")
print(f"\ndefaultdict(set) — unique tags:")
print(f"  {dict(tags)}")


# --- Gotcha: accessing a key CREATES it ---
d = defaultdict(list)
print(f"\n'x' in d before access: {'x' in d}")
_ = d["x"]   # just accessing creates the key!
print(f"'x' in d after access:  {'x' in d}")
print("  Gotcha: reading d['x'] creates the key with default value!")
