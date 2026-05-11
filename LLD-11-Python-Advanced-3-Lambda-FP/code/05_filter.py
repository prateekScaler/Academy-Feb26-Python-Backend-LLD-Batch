"""filter() — keep only elements that pass a test.

map:    transform every element    → same count, different values
filter: keep/remove elements       → fewer elements, same values
"""


# --- The problem: keep only elements that match a condition ---
numbers = [1, -3, 5, -7, 10, -2, 8, 0, -4, 6]

# Approach 1: Manual loop
positives_loop = []
for n in numbers:
    if n > 0:
        positives_loop.append(n)
print(f"Loop:          {positives_loop}")

# Approach 2: List comprehension
positives_comp = [n for n in numbers if n > 0]
print(f"Comprehension: {positives_comp}")

# Approach 3: filter()
positives_filter = list(filter(lambda n: n > 0, numbers))
print(f"filter():      {positives_filter}")

# filter(function, iterable)
# The function returns True/False for each element.
# Only elements where function returns True are kept.


# --- filter with named functions ---
def is_even(n):
    return n % 2 == 0

evens = list(filter(is_even, range(1, 21)))
print(f"\nEven numbers 1-20: {evens}")


# --- filter with None = remove falsy values ---
messy = [0, 1, "", "hello", None, 42, False, "world", [], [1, 2]]

clean = list(filter(None, messy))
print(f"\nFilter None (remove falsy): {clean}")
# Keeps: 1, "hello", 42, "world", [1, 2]
# Removes: 0, "", None, False, []


# --- Real-world: filter students by PSP ---
students = [
    {"name": "Vipul", "psp": 85},
    {"name": "Gobi", "psp": 45},
    {"name": "Kaarthik", "psp": 92},
    {"name": "Ajit", "psp": 38},
    {"name": "Sneha", "psp": 75},
]

strong = list(filter(lambda s: s["psp"] >= 70, students))
print(f"\nStrong performers (PSP >= 70):")
for s in strong:
    print(f"  {s['name']}: {s['psp']}")


# --- Chaining map + filter ---
# Get names of strong performers (filter THEN map)
strong_names = list(map(lambda s: s["name"], filter(lambda s: s["psp"] >= 70, students)))
print(f"\nStrong performer names: {strong_names}")

# Same with comprehension (much more readable):
strong_names_v2 = [s["name"] for s in students if s["psp"] >= 70]
print(f"Comprehension:         {strong_names_v2}")


# --- filter vs comprehension ---
print("\n--- filter vs comprehension ---")
print("  filter():       filter(func, items)")
print("  comprehension:  [x for x in items if condition]")
print()
print("  Comprehension is usually more readable in Python.")
print("  filter() is useful when you already have a predicate function.")
