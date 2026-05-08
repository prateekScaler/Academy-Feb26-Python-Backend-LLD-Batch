"""Counter — count things, find most common, do set math on counts."""
from collections import Counter


# --- Basic counting ---
words = "the cat sat on the mat the cat".split()
counts = Counter(words)
print(f"Counter: {counts}")
print(f"  counts['the'] = {counts['the']}")
print(f"  counts['dog'] = {counts['dog']}")  # 0 (not KeyError!)

# --- most_common(n) ---
print(f"\n  most_common(2): {counts.most_common(2)}")

# --- From any iterable ---
letter_counts = Counter("mississippi")
print(f"\nCounter('mississippi'): {letter_counts}")
print(f"  most_common(3): {letter_counts.most_common(3)}")

# --- Arithmetic on Counters ---
inventory_a = Counter(apples=3, bananas=2, oranges=5)
inventory_b = Counter(apples=1, bananas=4, grapes=2)

print(f"\nInventory A: {inventory_a}")
print(f"Inventory B: {inventory_b}")
print(f"  A + B (combine): {inventory_a + inventory_b}")
print(f"  A - B (subtract): {inventory_a - inventory_b}")  # drops ≤0
print(f"  A & B (minimum):  {inventory_a & inventory_b}")
print(f"  A | B (maximum):  {inventory_a | inventory_b}")

# --- Real-world: word frequency ---
text = "to be or not to be that is the question to be is to exist"
freq = Counter(text.split())
print(f"\nWord frequency:")
for word, count in freq.most_common(5):
    print(f"  '{word}': {count}")

# --- elements() — expand back ---
c = Counter(a=2, b=3)
print(f"\nCounter(a=2, b=3).elements(): {list(c.elements())}")

# --- total() (Python 3.10+) ---
print(f"Counter total: {c.total()}")
