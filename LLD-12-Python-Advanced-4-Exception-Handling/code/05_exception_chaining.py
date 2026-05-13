"""Exception chaining — 'raise X from Y' preserves the original cause."""


# --- Problem: you catch one error, raise another. Original is lost. ---

class DatabaseError(Exception):
    pass

class UserNotFoundError(Exception):
    pass


# BAD: original error context is lost
def get_user_bad(user_id):
    try:
        # simulate DB error
        raise ConnectionError("Connection refused: port 5432")
    except ConnectionError:
        raise UserNotFoundError(f"Could not find user {user_id}")
        # The ConnectionError context is hidden!


# GOOD: chain exceptions with 'from'
def get_user_good(user_id):
    try:
        raise ConnectionError("Connection refused: port 5432")
    except ConnectionError as e:
        raise UserNotFoundError(f"Could not find user {user_id}") from e
        # Now the traceback shows BOTH: the original cause AND the new error


print("=== Without chaining ===")
try:
    get_user_bad(42)
except UserNotFoundError as e:
    print(f"  Error: {e}")
    print(f"  Cause: {e.__cause__}")  # None — lost!

print("\n=== With 'raise ... from ...' ===")
try:
    get_user_good(42)
except UserNotFoundError as e:
    print(f"  Error: {e}")
    print(f"  Cause: {e.__cause__}")  # ConnectionError preserved!
    print(f"  Cause message: {e.__cause__}")


# --- Suppress chaining: 'from None' ---
def parse_config(data):
    try:
        return int(data)
    except ValueError:
        raise TypeError("Config must be numeric") from None
        # 'from None' hides the original ValueError (intentional)

print("\n=== 'from None' — suppress chain ===")
try:
    parse_config("abc")
except TypeError as e:
    print(f"  Error: {e}")
    print(f"  Cause: {e.__cause__}")  # None — intentionally hidden


print("\n--- When to use ---")
print("  raise X from Y   → show both errors (most common)")
print("  raise X from None → hide original (when it's an implementation detail)")
print("  raise             → re-raise current exception (preserves traceback)")
