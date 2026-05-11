"""Comprehensions vs map/filter — which to use when."""


students = [
    {"name": "Vipul", "psp": 85},
    {"name": "Kaarthik", "psp": 45},
    {"name": "Ajit", "psp": 92},
    {"name": "Gobi", "psp": 38},
]


# --- Transform (map equivalent) ---
# map + lambda
names_map = list(map(lambda s: s["name"].upper(), students))
# List comprehension
names_comp = [s["name"].upper() for s in students]

print(f"map+lambda: {names_map}")
print(f"comp:       {names_comp}")
print(f"  → Comprehension is more readable for simple transforms\n")


# --- Filter ---
# filter + lambda
honor_filter = list(filter(lambda s: s["psp"] >= 70, students))
# List comprehension
honor_comp = [s for s in students if s["psp"] >= 70]

print(f"filter:     {[s['name'] for s in honor_filter]}")
print(f"comp:       {[s['name'] for s in honor_comp]}")
print(f"  → Comprehension is more readable for simple filters\n")


# --- Filter + Transform (where FP gets ugly) ---
# map + filter + lambda (hard to read)
names_fp = list(map(lambda s: s["name"], filter(lambda s: s["psp"] >= 70, students)))
# List comprehension (reads like English)
names_lc = [s["name"] for s in students if s["psp"] >= 70]

print(f"FP chain:   {names_fp}")
print(f"comp:       {names_lc}")
print(f"  → Comprehension WINS when combining filter + transform\n")


# --- Dictionary comprehension ---
name_to_psp = {s["name"]: s["psp"] for s in students}
print(f"Dict comp: {name_to_psp}")

# --- Set comprehension ---
unique_psps = {s["psp"] for s in students}
print(f"Set comp:  {unique_psps}")

# --- Generator expression (lazy, saves memory) ---
total_psp = sum(s["psp"] for s in students)  # no [] = generator
print(f"\nTotal PSP (generator): {total_psp}")
avg_psp = total_psp / len(students)
print(f"Average PSP: {avg_psp:.2f}")


# --- Verdict ---
print("\n" + "=" * 55)
print("When to use what:")
print("=" * 55)
print("  List comprehension → transform and/or filter (90% of cases)")
print("  Dict comprehension → build dicts from iterables")
print("  Set comprehension  → unique values")
print("  Generator expr     → large data, one-pass (no memory overhead)")
print("  map()              → you already have a function (str.upper, int)")
print("  filter()           → you already have a predicate function")
print("  reduce()           → combine into single value (rare)")
