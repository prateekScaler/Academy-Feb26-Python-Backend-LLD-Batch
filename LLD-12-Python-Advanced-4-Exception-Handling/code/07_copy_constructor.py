"""Copy constructor — shallow copy, deep copy, and the gotchas.

Python doesn't have a C++/Java-style copy constructor.
Instead, it uses copy.copy() and copy.deepcopy().
"""
import copy


# ===== PART 1: The Problem =====

print("=== Part 1: Assignment is NOT copying ===\n")

original = [1, 2, [3, 4]]
alias = original              # NOT a copy — same object!

alias.append(5)
print(f"  alias.append(5)")
print(f"  original: {original}")   # [1, 2, [3, 4], 5] — MODIFIED!
print(f"  alias:    {alias}")
print(f"  same object? {original is alias}")  # True!
print()


# ===== PART 2: Shallow Copy =====

print("=== Part 2: Shallow Copy ===\n")

original = [[1, 2], [3, 4], [5, 6]]

# Ways to shallow copy:
shallow1 = original.copy()          # list.copy()
shallow2 = list(original)           # list() constructor
shallow3 = original[:]              # slice
shallow4 = copy.copy(original)      # copy module

# Outer list is independent:
shallow1.append([7, 8])
print(f"  shallow1.append([7, 8])")
print(f"  original: {original}")     # NOT affected — outer list is independent
print(f"  shallow1: {shallow1}")
print()

# But inner lists are SHARED:
original = [[1, 2], [3, 4]]
shallow = original.copy()

shallow[0].append(99)
print(f"  shallow[0].append(99)")
print(f"  original: {original}")     # [[1, 2, 99], [3, 4]] — AFFECTED!
print(f"  shallow:  {shallow}")
print(f"  original[0] is shallow[0]: {original[0] is shallow[0]}")  # True!

#        original          shallow
#        ┌─────┐          ┌─────┐
#        │  ●──┼────┐ ┌───┼──●  │
#        │  ●──┼──┐ │ │ ┌─┼──●  │
#        └─────┘  │ │ │ │ └─────┘
#                 │ └─┼─┘
#                 │   │
#              [3, 4] [1, 2, 99]  ← shared!
print()


# ===== PART 3: Deep Copy =====

print("=== Part 3: Deep Copy ===\n")

original = [[1, 2], [3, 4]]
deep = copy.deepcopy(original)

deep[0].append(99)
print(f"  deep[0].append(99)")
print(f"  original: {original}")     # [[1, 2], [3, 4]] — NOT affected!
print(f"  deep:     {deep}")         # [[1, 2, 99], [3, 4]]
print(f"  original[0] is deep[0]: {original[0] is deep[0]}")  # False!
print()


# ===== PART 4: Copy with Classes =====

print("=== Part 4: Copy with objects ===\n")

class Student:
    def __init__(self, name, grades):
        self.name = name
        self.grades = grades   # mutable list!

    def __repr__(self):
        return f"Student({self.name}, {self.grades})"

alice = Student("Alice", [90, 85, 92])

# Shallow copy: grades list is shared
alice_shallow = copy.copy(alice)
alice_shallow.grades.append(100)
print(f"  Shallow copy:")
print(f"    alice:         {alice}")          # grades has 100 — SHARED!
print(f"    alice_shallow: {alice_shallow}")

# Deep copy: completely independent
alice = Student("Alice", [90, 85, 92])
alice_deep = copy.deepcopy(alice)
alice_deep.grades.append(100)
print(f"\n  Deep copy:")
print(f"    alice:      {alice}")             # grades unchanged
print(f"    alice_deep: {alice_deep}")


# ===== PART 5: Custom __copy__ and __deepcopy__ =====

print("\n=== Part 5: Custom copy behavior ===\n")

class Config:
    _instance_count = 0

    def __init__(self, settings):
        Config._instance_count += 1
        self.id = Config._instance_count
        self.settings = settings

    def __copy__(self):
        """Shallow copy: new Config with shared settings."""
        new = Config.__new__(Config)
        Config._instance_count += 1
        new.id = Config._instance_count
        new.settings = self.settings  # shared
        return new

    def __deepcopy__(self, memo):
        """Deep copy: new Config with independent settings."""
        new = Config.__new__(Config)
        Config._instance_count += 1
        new.id = Config._instance_count
        new.settings = copy.deepcopy(self.settings, memo)
        return new

    def __repr__(self):
        return f"Config(id={self.id}, settings={self.settings})"


cfg = Config({"debug": True, "db": {"host": "localhost"}})
cfg_shallow = copy.copy(cfg)
cfg_deep = copy.deepcopy(cfg)

print(f"  original: {cfg}")
print(f"  shallow:  {cfg_shallow}")
print(f"  deep:     {cfg_deep}")


# --- Summary ---
print("\n" + "=" * 55)
print("Copy cheatsheet:")
print("=" * 55)
print("  a = b            → alias (same object)")
print("  copy.copy(a)     → shallow (new outer, shared inner)")
print("  copy.deepcopy(a) → deep (completely independent)")
print()
print("  Shallow copy methods: .copy(), list(), [:], dict(), copy.copy()")
print("  Deep copy: only copy.deepcopy()")
print()
print("  Rule: if your object has nested mutables (list of lists,")
print("        object with list attributes), use deepcopy.")
print("        Otherwise, shallow copy is fine.")
