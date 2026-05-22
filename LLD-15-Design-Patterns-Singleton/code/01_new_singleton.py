"""
Singleton via __new__
=====================
Classic implementation. Override __new__ to intercept object creation
and return the same instance every call.

Run me to see the singleton in action AND four common ways it breaks.
"""

# -----------------------------------------------------------------------
# Working singleton (with __init__ guard)
# -----------------------------------------------------------------------
class Database:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            print("[__new__] creating the one and only instance")
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        # Guard - __init__ runs on every Database() call, but we
        # only want to set up state once.
        if self._initialized:
            return
        print("[__init__] running initialization")
        self.connection = "postgresql://localhost:5432"
        self._initialized = True


def demo_happy_path():
    print("\n--- Happy path ---")
    a = Database()
    b = Database()
    print(f"a is b: {a is b}")
    print(f"connection: {a.connection}")


# -----------------------------------------------------------------------
# BREAK 1 - Subclassing: a common naive mistake leaks instances
# -----------------------------------------------------------------------
def demo_break_subclassing():
    """A very common beginner mistake: hardcoding the base class name
    inside __new__. The first subclass to be instantiated "wins" - every
    subsequent call returns THAT instance, even from sibling subclasses."""
    print("\n--- BREAK 1: hardcoded parent ref leaks across subclasses ---")

    class BadBase:
        _instance = None

        def __new__(cls):
            # MISTAKE: hardcoded `BadBase` instead of `cls`
            if BadBase._instance is None:
                BadBase._instance = super().__new__(cls)
            return BadBase._instance

    class Postgres(BadBase):
        pass

    class MySQL(BadBase):
        pass

    a = Postgres()
    b = MySQL()
    print(f"type(a) = {type(a).__name__}")    # Postgres
    print(f"type(b) = {type(b).__name__}")    # Postgres  !!! should be MySQL
    print(f"a is b:  {a is b}")               # True - they share ONE instance
    print("MySQL() silently returned a Postgres. Type-confusion bomb planted.")

    print("\n  (Note: using `cls._instance` instead of `BadBase._instance`")
    print("   gives each subclass its OWN singleton - also surprising if")
    print("   you expected one shared instance for the whole family.)")


# -----------------------------------------------------------------------
# BREAK 2 - copy.deepcopy bypasses __new__
# -----------------------------------------------------------------------
def demo_break_deepcopy():
    print("\n--- BREAK 2: copy.deepcopy bypasses __new__ ---")
    import copy

    Database._instance = None
    Database._initialized = False

    a = Database()
    b = copy.deepcopy(a)
    print(f"a is b: {a is b}")               # False - two instances
    print(f"same class: {type(a) is type(b)}")  # True


# -----------------------------------------------------------------------
# BREAK 3 - pickle creates a new instance on load
# -----------------------------------------------------------------------
def demo_break_pickle():
    print("\n--- BREAK 3: pickle bypasses singleton on load ---")
    import pickle

    Database._instance = None
    Database._initialized = False

    a = Database()
    blob = pickle.dumps(a)

    # Simulate "fresh process" by resetting the class-level cache
    Database._instance = None

    b = pickle.loads(blob)
    print(f"a is b: {a is b}")  # False - pickle constructed a new one


# -----------------------------------------------------------------------
# BREAK 4 - Threading race condition (without lock)
# -----------------------------------------------------------------------
def demo_break_threading():
    print("\n--- BREAK 4: threading race (no lock) ---")
    import threading
    import time

    class RacyDB:
        _instance = None

        def __new__(cls):
            if cls._instance is None:
                # Force the race window to be wide by sleeping
                time.sleep(0.01)
                cls._instance = super().__new__(cls)
            return cls._instance

    instances = []

    def make():
        instances.append(RacyDB())

    threads = [threading.Thread(target=make) for _ in range(10)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    unique_ids = {id(x) for x in instances}
    print(f"created {len(instances)} 'singletons'")
    print(f"unique objects: {len(unique_ids)}")
    print("If unique > 1, the singleton invariant broke.")


if __name__ == "__main__":
    demo_happy_path()
    demo_break_subclassing()
    demo_break_deepcopy()
    demo_break_pickle()
    demo_break_threading()
