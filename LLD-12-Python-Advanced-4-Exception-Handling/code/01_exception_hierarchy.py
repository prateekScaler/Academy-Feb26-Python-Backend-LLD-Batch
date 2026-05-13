"""Python's exception hierarchy — what inherits from what."""


# --- The hierarchy ---
# BaseException
# ├── SystemExit           (sys.exit())
# ├── KeyboardInterrupt    (Ctrl+C)
# ├── GeneratorExit
# └── Exception            ← your code catches THIS
#     ├── ValueError
#     ├── TypeError
#     ├── KeyError
#     ├── IndexError
#     ├── FileNotFoundError
#     ├── AttributeError
#     ├── RuntimeError
#     ├── StopIteration
#     ├── OSError
#     │   └── FileNotFoundError
#     │   └── PermissionError
#     │   └── ConnectionError
#     └── ... many more


# --- Why this matters ---
# NEVER catch BaseException — you'd swallow Ctrl+C and sys.exit()

# BAD:
# try:
#     something()
# except BaseException:    # Catches Ctrl+C! User can't stop program.
#     pass

# ALSO BAD:
# try:
#     something()
# except:                  # Bare except = catches BaseException!
#     pass

# GOOD:
# try:
#     something()
# except Exception:        # Catches all "normal" errors, not Ctrl+C
#     pass


# --- Multiple except blocks: order matters ---
try:
    d = {"a": 1}
    val = d["b"]          # KeyError
except KeyError:
    print("KeyError caught (specific)")
except Exception:
    print("Exception caught (general)")

# KeyError is caught first because it's more specific.
# If you swap the order, Exception catches everything and KeyError never runs.

print()

# --- Catching multiple exceptions in one block ---
try:
    result = int("hello")
except (ValueError, TypeError) as e:
    print(f"Caught: {type(e).__name__}: {e}")


# --- Getting exception info ---
try:
    x = 1 / 0
except ZeroDivisionError as e:
    print(f"\nException type: {type(e).__name__}")
    print(f"Message: {e}")
    print(f"Args: {e.args}")


# --- issubclass check ---
print(f"\nKeyError is subclass of Exception: {issubclass(KeyError, Exception)}")
print(f"KeyError is subclass of LookupError: {issubclass(KeyError, LookupError)}")
print(f"KeyboardInterrupt is subclass of Exception: {issubclass(KeyboardInterrupt, Exception)}")
