"""Practice exercises — map, filter, reduce (isolated and combined).

Try each exercise yourself before looking at the solutions!
"""
from functools import reduce


# ============================================================
# DATA (used across exercises)
# ============================================================
students = [
    {"name": "Vipul", "psp": 85, "attendance": 92},
    {"name": "Kaarthik", "psp": 92, "attendance": 88},
    {"name": "Ajit", "psp": 78, "attendance": 95},
    {"name": "Gobi", "psp": 45, "attendance": 60},
    {"name": "Sneha", "psp": 91, "attendance": 85},
    {"name": "Priya", "psp": 55, "attendance": 70},
]

prices = [1200, 450, 3200, 890, 150, 2750, 600]


# ============================================================
# EXERCISE 1: map() — isolated
# Convert all prices to after-tax prices (18% GST)
# Expected: each price * 1.18
# ============================================================
print("=" * 50)
print("Exercise 1: Add 18% GST to all prices")
print("=" * 50)

# Your attempt:
# with_gst = ...

# Solution:
with_gst = list(map(lambda p: round(p * 1.18, 2), prices))
print(f"Original: {prices}")
print(f"With GST: {with_gst}")


# ============================================================
# EXERCISE 2: filter() — isolated
# Get students with attendance >= 85%
# ============================================================
print(f"\n{'=' * 50}")
print("Exercise 2: Students with attendance >= 85%")
print("=" * 50)

# Your attempt:
# regular = ...

# Solution:
regular = list(filter(lambda s: s["attendance"] >= 85, students))
print("Regular attendees:")
for s in regular:
    print(f"  {s['name']}: {s['attendance']}%")


# ============================================================
# EXERCISE 3: reduce() — isolated
# Find the total PSP across all students
# ============================================================
print(f"\n{'=' * 50}")
print("Exercise 3: Total PSP of all students")
print("=" * 50)

# Your attempt:
# total_psp = ...

# Solution:
total_psp = reduce(lambda acc, s: acc + s["psp"], students, 0)
print(f"Total PSP: {total_psp}")
print(f"Average PSP: {total_psp / len(students):.1f}")


# ============================================================
# EXERCISE 4: filter + map — combined
# Get NAMES of students with PSP >= 70 (strong performers)
# ============================================================
print(f"\n{'=' * 50}")
print("Exercise 4: Names of students with PSP >= 70")
print("=" * 50)

# FP way:
strong_names_fp = list(map(lambda s: s["name"], filter(lambda s: s["psp"] >= 70, students)))
print(f"FP way:            {strong_names_fp}")

# Comprehension way (more readable):
strong_names_comp = [s["name"] for s in students if s["psp"] >= 70]
print(f"Comprehension way: {strong_names_comp}")


# ============================================================
# EXERCISE 5: map + reduce — combined
# Calculate total revenue (all prices with GST)
# ============================================================
print(f"\n{'=' * 50}")
print("Exercise 5: Total revenue with 18% GST")
print("=" * 50)

# FP way:
total_revenue = reduce(lambda acc, p: acc + p, map(lambda p: p * 1.18, prices))
print(f"FP way:        ₹{total_revenue:,.2f}")

# Pythonic way:
total_pythonic = sum(p * 1.18 for p in prices)
print(f"Pythonic way:  ₹{total_pythonic:,.2f}")


# ============================================================
# EXERCISE 6: filter + map + reduce — all three combined
# Total PSP of students with attendance >= 80%
# ============================================================
print(f"\n{'=' * 50}")
print("Exercise 6: Total PSP of students with attendance >= 80%")
print("=" * 50)

# FP way (hard to read):
total_psp_regular = reduce(
    lambda acc, s: acc + s["psp"],
    filter(lambda s: s["attendance"] >= 80, students),
    0
)
print(f"FP way:        {total_psp_regular}")

# Pythonic way (much cleaner):
total_psp_pythonic = sum(s["psp"] for s in students if s["attendance"] >= 80)
print(f"Pythonic way:  {total_psp_pythonic}")


# ============================================================
# EXERCISE 7: Sorting with lambda
# Sort students by PSP descending, then by name alphabetically
# ============================================================
print(f"\n{'=' * 50}")
print("Exercise 7: Sort students by PSP (highest first)")
print("=" * 50)

by_psp = sorted(students, key=lambda s: s["psp"], reverse=True)
for rank, s in enumerate(by_psp, 1):
    print(f"  #{rank} {s['name']}: PSP={s['psp']}, Attendance={s['attendance']}%")


# ============================================================
# SUMMARY
# ============================================================
print(f"\n{'=' * 50}")
print("Key takeaways:")
print("=" * 50)
print("  map()    → transform every element (returns iterator)")
print("  filter() → keep elements that pass a test (returns iterator)")
print("  reduce() → combine all elements into one value")
print("  Comprehension usually beats map/filter for readability")
print("  Use FP functions when you already have a named function")
