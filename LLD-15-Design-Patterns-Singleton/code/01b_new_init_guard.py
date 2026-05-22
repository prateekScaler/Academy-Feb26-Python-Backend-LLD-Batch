"""
01b - The Basic Singleton + __init__ Guard
==========================================

Builds on 01a. Fixes the "__init__ runs every call" problem.

The trick:
  - When __new__ creates the instance for the first time, it also sets
    an `_initialized` flag on the new object to False.
  - __init__ checks that flag. If already initialized, it bails early.

Result: instance is shared AND __init__ only runs once.

This is the canonical "textbook" Singleton you'll see in interviews.
Remaining issues (covered in 01c and the thread-safety file):
  - threading race condition
  - copy.deepcopy bypasses __new__
  - pickle bypasses __new__
  - subclassing surprises
"""


class Database:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            print("[__new__] creating the one and only instance")
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False        # mark the new object
        return cls._instance

    def __init__(self):
        if self._initialized:                         # guard - bail early
            print("[__init__] skipped (already initialized)")
            return

        print("[__init__] running initialization")
        self.connection = "postgresql://localhost:5432"
        self._initialized = True


# ---------------------------------------------------------------------------
# Demo
# ---------------------------------------------------------------------------

def demo():
    print("--- Creating db1 ---")
    db1 = Database()

    print("\n--- Creating db2 ---")
    db2 = Database()

    print("\n--- Creating db3 ---")
    db3 = Database()

    print(f"\ndb1 is db2 is db3: {db1 is db2 is db3}")    # True
    print(f"db1.connection: {db1.connection}")

    # Look at the output: [__init__] running once, [__init__] skipped after.
    # State is preserved between calls.


if __name__ == "__main__":
    demo()
