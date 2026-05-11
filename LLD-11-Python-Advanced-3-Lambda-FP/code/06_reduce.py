"""reduce() — combine all elements into a single value.

map:    [a, b, c] → [f(a), f(b), f(c)]     (same count)
filter: [a, b, c] → [a, c]                  (fewer items)
reduce: [a, b, c] → single_value            (one result)
"""
from functools import reduce


# --- The idea: fold a list into one value ---
# reduce(func, [a, b, c, d])
#   Step 1: result = func(a, b)
#   Step 2: result = func(result, c)
#   Step 3: result = func(result, d)
#   → returns final result


# --- Example: sum all numbers ---
numbers = [1, 2, 3, 4, 5]

# Manual:
total = 0
for n in numbers:
    total = total + n
print(f"Manual sum: {total}")

# reduce:
total_reduce = reduce(lambda acc, x: acc + x, numbers)
print(f"reduce sum: {total_reduce}")

# What happened step by step:
# reduce(+, [1, 2, 3, 4, 5])
#   1 + 2 = 3
#   3 + 3 = 6
#   6 + 4 = 10
#   10 + 5 = 15


# --- Example: multiply all numbers ---
product = reduce(lambda acc, x: acc * x, numbers)
print(f"\nProduct: {product}")  # 1*2*3*4*5 = 120


# --- Example: find maximum ---
nums = [34, 12, 89, 3, 67, 45]
maximum = reduce(lambda acc, x: acc if acc > x else x, nums)
print(f"Max of {nums}: {maximum}")


# --- With initial value ---
# reduce(func, iterable, initial)
# Starts with initial instead of first element
total_with_start = reduce(lambda acc, x: acc + x, numbers, 100)
print(f"\nSum with initial 100: {total_with_start}")  # 100 + 1+2+3+4+5 = 115


# --- Real-world: flatten nested lists ---
nested = [[1, 2], [3, 4], [5, 6]]
flat = reduce(lambda acc, lst: acc + lst, nested)
print(f"\nFlatten {nested}: {flat}")  # [1, 2, 3, 4, 5, 6]


# --- Real-world: build a sentence ---
words = ["Python", "is", "awesome"]
sentence = reduce(lambda acc, word: f"{acc} {word}", words)
print(f"Sentence: '{sentence}'")


# --- When to use reduce ---
print("\n--- reduce guidelines ---")
print("  Use reduce for: combining all elements into one value")
print("  sum()    = reduce(+)     but sum() is built-in, use it")
print("  max()    = reduce(max)   but max() is built-in, use it")
print("  ''.join  = reduce(+str)  but join() is built-in, use it")
print()
print("  reduce is in functools (not built-in) because Python")
print("  prefers explicit loops or built-ins for most cases.")
print("  Use it when no built-in exists for your fold operation.")
