"""Optional and Union — handling 'might be None' and 'could be multiple types'."""


# --- The None problem ---
def find_user(user_id: int) -> dict | None:
    """Returns user dict or None if not found."""
    users = {1: {"name": "Alice", "age": 25}, 2: {"name": "Bob", "age": 30}}
    return users.get(user_id)


# Without types, you forget to handle None:
user = find_user(999)
# user["name"]  # TypeError: 'NoneType' object is not subscriptable
# With type hints, your IDE warns: "user might be None"
print(f"Found: {user['name']}")

if user is not None:
    print(f"Found: {user['name']}")
else:
    print("User not found — and we handled it!")


# --- Union: multiple possible types ---
def format_id(id_value: int | str) -> str:
    """Accept int or string ID, always return string."""
    if isinstance(id_value, int):
        return f"ID-{id_value:05d}"
    return f"ID-{id_value}"


print(f"\n  format_id(42) = '{format_id(42)}'")
print(f"  format_id('ABC') = '{format_id('ABC')}'")


# --- Optional is just Union[X, None] ---
# These are equivalent:
#   Optional[str]  ==  str | None  ==  Union[str, None]

from typing import Optional


def get_middle_name(full_name: str) -> Optional[str]:
    """Returns middle name or None."""
    parts = full_name.split()
    if len(parts) == 3:
        return parts[1]
    return None


print(f"\n  get_middle_name('John F Kennedy') = '{get_middle_name('John F Kennedy')}'")
print(f"  get_middle_name('Alice Bob') = {get_middle_name('Alice Bob')}")


# --- Python 3.10+ pipe syntax (preferred) ---
# Old: Union[int, str]  or  Optional[str]
# New: int | str         or  str | None
print("\n--- Syntax evolution ---")
print("  Python 3.9:  from typing import Optional, Union")
print("               def f(x: Optional[str]) -> Union[int, str]: ...")
print("  Python 3.10+: def f(x: str | None) -> int | str: ...")
print("  Prefer the | syntax — it's cleaner and built-in.")
