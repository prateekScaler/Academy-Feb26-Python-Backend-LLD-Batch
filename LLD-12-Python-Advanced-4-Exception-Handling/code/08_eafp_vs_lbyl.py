"""EAFP vs LBYL — two philosophies of error handling.

LBYL = Look Before You Leap  ("check first, then act")
EAFP = Easier to Ask Forgiveness than Permission  ("just do it, handle errors")

Python strongly favors EAFP.
"""


# --- Example 1: Dict access ---
d = {"name": "Alice", "age": 25}

# LBYL (Java/C style): check first
if "email" in d:
    email = d["email"]
else:
    email = "N/A"
print(f"LBYL: email = {email}")

# EAFP (Pythonic): just try it
try:
    email = d["email"]
except KeyError:
    email = "N/A"
print(f"EAFP: email = {email}")

# BEST: use .get() (Pythonic shortcut)
email = d.get("email", "N/A")
print(f"Best: email = {email}")


# --- Example 2: Type conversion ---
user_input = "hello"

# LBYL: check if it looks like a number
if user_input.isdigit():
    value = int(user_input)
else:
    value = 0
print(f"\nLBYL: value = {value}")
# BUG: isdigit() doesn't handle negative numbers or floats!

# EAFP: just try converting
try:
    value = int(user_input)
except ValueError:
    value = 0
print(f"EAFP: value = {value}")


# --- Example 3: File access ---
import os

# LBYL: check then open (race condition!)
filename = "/tmp/test_eafp.txt"
if os.path.exists(filename):
    # Another process could delete the file RIGHT HERE!
    f = open(filename)
    data = f.read()
    f.close()
else:
    data = ""

# EAFP: just open it
try:
    with open(filename) as f:
        data = f.read()
except FileNotFoundError:
    data = ""
print(f"\nEAFP file: read {len(data)} chars")


# --- Why Python prefers EAFP ---
print("\n--- Why EAFP? ---")
print("  1. No race conditions (LBYL check can become stale)")
print("  2. Fewer lines of code")
print("  3. Clearer intent ('try this, handle failure')")
print("  4. Duck typing works with EAFP ('just call .read()')")
print("  5. Exception handling is CHEAP in Python (optimized)")
print()
print("  LBYL makes sense when:")
print("    • The check is cheap and the operation is expensive")
print("    • You're in a tight loop (exceptions have slight overhead)")
print("    • The 'happy path' frequently fails (checking avoids exceptions)")
