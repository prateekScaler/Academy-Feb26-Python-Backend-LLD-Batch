"""
Singleton via decorator
=======================
Cleanest separation: the class stays a regular class, the decorator
handles caching.

Trade-off: after decoration, `Database` is no longer a class - it's
the cache function. Several real-world surprises follow.
"""

def singleton(cls):
    """Replace `cls` with a factory that caches the first instance."""
    instances = {}

    def get_instance(*args, **kwargs):
        if cls not in instances:
            instances[cls] = cls(*args, **kwargs)
        return instances[cls]

    # Expose original class for debugging / type-checking workarounds
    get_instance.__wrapped__ = cls
    return get_instance


@singleton
class Database:
    def __init__(self, host="localhost"):
        print(f"[Database.__init__] host={host}")
        self.host = host


def demo_happy_path():
    print("\n--- Happy path ---")
    a = Database()
    b = Database()
    print(f"a is b: {a is b}")  # True


# -----------------------------------------------------------------------
# BREAK 1 - isinstance fails: Database is a function now
# -----------------------------------------------------------------------
def demo_break_isinstance():
    print("\n--- BREAK 1: isinstance() raises TypeError ---")
    a = Database()
    try:
        # Database is a function, not a class
        print(isinstance(a, Database))
    except TypeError as e:
        print(f"TypeError: {e}")

    print(f"type(Database) = {type(Database).__name__}")  # function

    # Workaround using __wrapped__:
    print(f"isinstance(a, Database.__wrapped__) = "
          f"{isinstance(a, Database.__wrapped__)}")  # True


# -----------------------------------------------------------------------
# BREAK 2 - Can't subclass a function
# -----------------------------------------------------------------------
def demo_break_subclassing():
    print("\n--- BREAK 2: can't subclass a function ---")
    try:
        class ReadOnlyDatabase(Database):
            pass
    except TypeError as e:
        print(f"TypeError: {e}")


# -----------------------------------------------------------------------
# BREAK 3 - Constructor args silently dropped on subsequent calls
# -----------------------------------------------------------------------
def demo_break_silent_args():
    print("\n--- BREAK 3: args silently dropped on subsequent calls ---")

    # Reset the decorator cache for a clean demo
    Database.__wrapped__  # noqa  - ensure the closure exists

    @singleton
    class DB:
        def __init__(self, host):
            self.host = host

    prod = DB("prod.example.com")
    test = DB("localhost")   # <-- the second call is IGNORED

    print(f"prod.host = {prod.host}")
    print(f"test.host = {test.host}")   # also "prod.example.com" !!
    print(f"prod is test: {prod is test}")


# -----------------------------------------------------------------------
# BREAK 4 - deepcopy / pickle still bypass the decorator
# -----------------------------------------------------------------------
def demo_break_deepcopy():
    print("\n--- BREAK 4: deepcopy bypasses the decorator cache ---")
    import copy
    a = Database()
    b = copy.deepcopy(a)
    print(f"a is b: {a is b}")  # False


if __name__ == "__main__":
    demo_happy_path()
    demo_break_isinstance()
    demo_break_subclassing()
    demo_break_silent_args()
    demo_break_deepcopy()
