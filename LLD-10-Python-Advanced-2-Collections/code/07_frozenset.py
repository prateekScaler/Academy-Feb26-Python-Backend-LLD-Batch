"""frozenset — immutable set. Hashable, usable as dict key or set element."""


# --- Problem: sets can't be dict keys or set members ---
tags_a = {"python", "backend"}
tags_b = {"python", "ml"}

# Can't do this:
try:
    tag_groups = {tags_a: "team_a", tags_b: "team_b"}
except TypeError as e:
    print(f"set as dict key: {e}")

try:
    set_of_sets = {tags_a, tags_b}
except TypeError as e:
    print(f"set inside set:  {e}")


# --- Solution: frozenset ---
tags_a = frozenset({"python", "backend"})
tags_b = frozenset({"python", "ml"})

# Now it works!
tag_groups = {tags_a: "team_a", tags_b: "team_b"}
print(f"\nfrozenset as dict key: {tag_groups}")

set_of_sets = {tags_a, tags_b}
print(f"frozenset in set:     {set_of_sets}")


# --- All set operations work (return new frozensets) ---
print(f"\n  union:        {tags_a | tags_b}")
print(f"  intersection: {tags_a & tags_b}")
print(f"  difference:   {tags_a - tags_b}")


# --- Can't mutate ---
try:
    tags_a.add("django")  # type: ignore
except AttributeError as e:
    print(f"\n  Can't mutate: {e}")


# --- Real-world uses ---
print("\n--- Use cases ---")
print("  • Dict keys when key is a SET of items (feature combinations)")
print("  • Caching: frozenset of args as cache key")
print("  • Graph edges: frozenset({A, B}) = undirected edge")
print("  • Config: immutable set of permissions, roles, flags")
print("  • Set of sets: grouping unique combinations")
