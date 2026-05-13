"""Exception handling best practices — the do's and don'ts."""


# --- DON'T 1: Bare except ---
# BAD:
# try:
#     do_something()
# except:                 # Catches EVERYTHING including Ctrl+C!
#     pass

# GOOD:
# try:
#     do_something()
# except Exception as e:  # Catches errors, not Ctrl+C
#     log(e)


# --- DON'T 2: Catch-all with pass ---
# BAD:
# try:
#     send_email(user)
# except Exception:
#     pass                # Silently swallows ALL errors. Debugging nightmare.

# GOOD:
# try:
#     send_email(user)
# except SMTPError as e:
#     logger.warning(f"Email failed: {e}")  # At least log it!
#     # Decide: retry? skip? re-raise?


# --- DON'T 3: Too broad except ---
# BAD:
# try:
#     user = get_user(id)
#     order = create_order(user, items)
#     send_confirmation(user, order)
# except Exception:
#     return "Something went wrong"  # WHERE did it go wrong??

# GOOD: catch specific, near the source
# user = get_user(id)           # let this crash if user not found
# try:
#     order = create_order(user, items)
# except InsufficientStockError as e:
#     return f"Out of stock: {e.item}"
# send_confirmation(user, order)


# --- DON'T 4: Using exceptions for flow control ---
# BAD:
def find_item_bad(items, target):
    try:
        return items.index(target)
    except ValueError:
        return -1

# OK for this case, but don't use exceptions for EXPECTED conditions.
# If 50% of calls will "fail", use an if-check instead.


# --- DO 1: Be specific ---
import json

data = '{"name": "Alice"}'
try:
    parsed = json.loads(data)
    name = parsed["name"]
except json.JSONDecodeError:
    print("Invalid JSON")
except KeyError:
    print("Missing 'name' field")


# --- DO 2: Use custom exceptions for business logic ---
class OrderError(Exception):
    pass

class OutOfStockError(OrderError):
    def __init__(self, item, available):
        self.item = item
        self.available = available
        super().__init__(f"{item}: only {available} left")


# --- DO 3: Always log exceptions ---
import logging
logger = logging.getLogger(__name__)

try:
    result = 1 / 0
except ZeroDivisionError:
    logger.exception("Division failed")  # logs full traceback
    # or: logger.error(f"Division failed", exc_info=True)


# --- Summary ---
print("\n" + "=" * 55)
print("Exception Best Practices:")
print("=" * 55)
print()
print("  DON'T:")
print("    ✗ Bare except (catches Ctrl+C)")
print("    ✗ except Exception: pass (swallows silently)")
print("    ✗ Too-broad try blocks (hard to debug)")
print("    ✗ Exceptions for expected flow control")
print()
print("  DO:")
print("    ✓ Catch specific exceptions (ValueError, KeyError)")
print("    ✓ Log exceptions (logger.exception())")
print("    ✓ Use custom exceptions for business logic")
print("    ✓ Keep try blocks small and focused")
print("    ✓ Use 'raise' to re-raise, 'raise X from Y' to chain")
print("    ✓ Use context managers ('with') for resource cleanup")
print("    ✓ Prefer EAFP over LBYL in Python")
