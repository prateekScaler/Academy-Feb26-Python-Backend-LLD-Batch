"""UserDict, UserList, UserString — extend built-in types safely."""
from collections import UserDict, UserList, UserString


# --- Problem: subclassing dict directly is BROKEN ---
class BrokenUpperDict(dict):
    """Attempt: dict that uppercases all keys."""
    def __setitem__(self, key, value):
        super().__setitem__(key.upper(), value)

d = BrokenUpperDict()
d["hello"] = 1          # uses __setitem__ → "HELLO"
d.update({"world": 2})  # BYPASSES __setitem__! → "world" (lowercase!)
print(f"BrokenUpperDict: {d}")
print(f"  'hello' key? {'hello' in d}")   # False (it's HELLO)
print(f"  'world' key? {'world' in d}")   # True (update bypassed our code!)
print(f"  BUG: update() didn't uppercase the key!\n")


# --- Solution: UserDict wraps a dict, all methods go through __setitem__ ---
class UpperDict(UserDict):
    """Dict that uppercases all keys. Works correctly."""
    def __setitem__(self, key, value):
        super().__setitem__(key.upper(), value)

d2 = UpperDict()
d2["hello"] = 1
d2.update({"world": 2})  # now goes through __setitem__!
print(f"UpperDict (UserDict): {d2}")
print(f"  'HELLO' key? {'HELLO' in d2}")  # True
print(f"  'WORLD' key? {'WORLD' in d2}")  # True — fixed!


# --- UserList: validated list ---
class PositiveList(UserList):
    """List that only allows positive numbers."""
    def append(self, item):
        if item <= 0:
            raise ValueError(f"Only positive numbers! Got {item}")
        super().append(item)

    def __setitem__(self, index, item):
        if item <= 0:
            raise ValueError(f"Only positive numbers! Got {item}")
        super().__setitem__(index, item)

plist = PositiveList([1, 2, 3])
plist.append(4)
print(f"\nPositiveList: {plist}")

try:
    plist.append(-1)
except ValueError as e:
    print(f"  append(-1): {e}")

try:
    plist[0] = -5
except ValueError as e:
    print(f"  plist[0] = -5: {e}")


# --- UserString: custom string ---
class CaselessString(UserString):
    """String that compares case-insensitively."""
    def __eq__(self, other):
        if isinstance(other, (str, UserString)):
            return self.data.lower() == str(other).lower()
        return NotImplemented

    def __contains__(self, item):
        return item.lower() in self.data.lower()

s = CaselessString("Hello World")
print(f"\nCaselessString: '{s}'")
print(f"  == 'hello world'? {s == 'hello world'}")   # True
print(f"  == 'HELLO WORLD'? {s == 'HELLO WORLD'}")   # True
print(f"  'WORLD' in s? {'WORLD' in s}")              # True


# --- When to use User* classes ---
print("\n--- When to use User* ---")
print("  UserDict:   when you need to customize dict behavior (keys, values, access)")
print("  UserList:   when you need validation, logging, or custom list behavior")
print("  UserString: when you need case-insensitive or formatted strings")
print("  NEVER subclass dict/list/str directly — internal C methods bypass your overrides!")
