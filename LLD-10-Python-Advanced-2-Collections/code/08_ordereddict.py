"""OrderedDict — when insertion order matters for equality and operations."""
from collections import OrderedDict


# --- Since Python 3.7, regular dicts preserve insertion order ---
d1 = {"a": 1, "b": 2, "c": 3}
d2 = {"c": 3, "b": 2, "a": 1}

print(f"Regular dict: d1 == d2? {d1 == d2}")  # True! Order doesn't matter for ==


# --- OrderedDict: order IS part of equality ---
od1 = OrderedDict([("a", 1), ("b", 2), ("c", 3)])
od2 = OrderedDict([("c", 3), ("b", 2), ("a", 1)])

print(f"OrderedDict:  od1 == od2? {od1 == od2}")  # False! Order matters


# --- move_to_end ---
od = OrderedDict([("a", 1), ("b", 2), ("c", 3)])
print(f"\nOriginal: {od}")

od.move_to_end("a")              # move to end (right)
print(f"move_to_end('a'):       {od}")

od.move_to_end("c", last=False)  # move to beginning (left)
print(f"move_to_end('c', False): {od}")


# --- LRU Cache with OrderedDict ---
class LRUCache:
    """Least Recently Used Cache — O(1) get and put."""
    def __init__(self, capacity: int):
        self.cache: OrderedDict[str, str] = OrderedDict()
        self.capacity = capacity

    def get(self, key: str) -> str | None:
        if key in self.cache:
            self.cache.move_to_end(key)  # mark as recently used
            return self.cache[key]
        return None

    def put(self, key: str, value: str) -> None:
        if key in self.cache:
            self.cache.move_to_end(key)
        self.cache[key] = value
        if len(self.cache) > self.capacity:
            evicted = self.cache.popitem(last=False)  # remove oldest
            print(f"    evicted: {evicted}")


print("\nLRU Cache (capacity=3):")
cache = LRUCache(3)
for k, v in [("a", "1"), ("b", "2"), ("c", "3"), ("d", "4")]:
    cache.put(k, v)
    print(f"  put({k}): {list(cache.cache.keys())}")


# --- When to use OrderedDict vs dict ---
print("\n--- OrderedDict vs dict ---")
print("  dict (Python 3.7+): preserves order, but ignores it in ==")
print("  OrderedDict: order matters for ==, has move_to_end, popitem(last=)")
print("  Use OrderedDict for: LRU cache, order-sensitive equality, reordering")
print("  Use dict for: everything else (it's faster and lighter)")
