"""
01a - The Basic Singleton via __new__
=====================================

The smallest possible singleton:
  - A class variable `_instance` holds the one and only instance.
  - `__new__` checks for it. If absent, it creates one. Otherwise,
    it returns the existing one.

This file is intentionally minimal. There is a known issue here:
__init__ still runs on every Database() call. We fix that in 01b.
"""


class Database:
    _instance = None                        # class var - shared across all calls

    def __new__(cls):
        if cls._instance is None:
            print("[__new__] creating the one and only instance")
            cls._instance = super().__new__(cls)
        return cls._instance                # subsequent calls return SAME object

    def __init__(self):
        # PROBLEM: this runs every Database() call - even when __new__
        # returned the existing instance. Watch the output below.
        print("[__init__] running")
        self.connection = "postgresql://localhost:5432"


# ---------------------------------------------------------------------------
# Demo
# ---------------------------------------------------------------------------

def demo():
    print("--- Creating db1 ---")
    db1 = Database()

    print("\n--- Creating db2 ---")
    db2 = Database()

    print(f"\ndb1 is db2: {db1 is db2}")    # True - basic singleton works!
    print(f"db1.connection: {db1.connection}")

    # Look at the output above: [__init__] ran TWICE even though we only
    # have one instance. That overwrites state on every call. Bad.
    # Fix in 01b_new_init_guard.py.


if __name__ == "__main__":
    demo()
