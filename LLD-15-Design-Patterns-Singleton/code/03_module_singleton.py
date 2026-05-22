"""
Singleton via module-level instance (the Pythonic way)
======================================================
Python imports each module at most once per interpreter and caches the
result in sys.modules. So any object you assign at module top level
is automatically a singleton across the entire process.

Use it like this:
    from database import database
    database.query("SELECT 1")

Every import gets the SAME object. No metaclass, no decorator, no __new__.
"""

class _Database:
    """Underscore prefix: 'don't instantiate me directly'."""

    def __init__(self):
        print("[_Database] initializing (only once per process)")
        self.connection = "postgresql://localhost:5432"

    def query(self, sql):
        return f"Executing: {sql}"


# THE singleton. Created at module load time.
database = _Database()


# -----------------------------------------------------------------------
# Demo - run this file to see the behavior
# -----------------------------------------------------------------------
def demo_happy_path():
    """The expected use - works perfectly."""
    print("\n--- Happy path ---")
    from importlib import import_module
    mod = import_module(__name__)   # re-imports cached module
    print(f"mod.database is database: {mod.database is database}")   # True
    print(database.query("SELECT 1"))


# -----------------------------------------------------------------------
# BREAK 1 - Someone instantiates _Database directly
# -----------------------------------------------------------------------
def demo_break_direct_instantiation():
    print("\n--- BREAK 1: someone instantiates _Database directly ---")
    rogue = _Database()
    print(f"database is rogue: {database is rogue}")   # False
    print("The underscore is convention, not enforcement.")


# -----------------------------------------------------------------------
# BREAK 2 - importlib.reload() creates a fresh instance
# -----------------------------------------------------------------------
def demo_break_reload():
    print("\n--- BREAK 2: importlib.reload() creates a fresh instance ---")
    import importlib
    import sys

    old_ref = database
    this_module = sys.modules[__name__]
    importlib.reload(this_module)
    new_ref = this_module.database

    print(f"old_ref is new_ref: {old_ref is new_ref}")    # False
    print("References taken before reload point at the OLD instance.")


# -----------------------------------------------------------------------
# BREAK 3 - Same file loaded under two module names
# -----------------------------------------------------------------------
def demo_break_two_paths():
    print("\n--- BREAK 3: two import paths -> two singletons ---")
    print("If 'myapp.database' and 'database' both resolve to this file,")
    print("sys.modules has two entries and database() runs twice.")
    print("Fix: use absolute imports consistently.")


if __name__ == "__main__":
    demo_happy_path()
    demo_break_direct_instantiation()
    demo_break_reload()
    demo_break_two_paths()
