"""
01c - How the Classic Singleton Breaks
======================================

Same singleton as 01b. This file is about demonstrating the FOUR ways
a colleague (or a library, or a test runner) can accidentally break the
"one instance" invariant.

  Break 1: subclassing leaks instances (when parent ref is hardcoded)
  Break 2: object.__new__(cls) bypasses our __new__ entirely
  Break 3: pickle bypasses __new__ on load (cross-process scenario)
  Break 4: threading race - two threads both see _instance is None

Run me to see each one fail in front of you.

Interesting non-break: copy.deepcopy ACTUALLY survives this Singleton -
because deepcopy still routes through __new__, which returns the existing
instance. We demonstrate this at the end as a "counter-intuitive truth".
"""

import copy
import pickle
import threading
import time


class Database:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return
        self.connection = "postgresql://localhost:5432"
        self._initialized = True


# ---------------------------------------------------------------------------
# Break 1 - Subclassing leaks instances (common beginner mistake)
# ---------------------------------------------------------------------------

def demo_break_subclassing():
    """A naive Singleton hardcodes the parent class name. The first subclass
    to be instantiated wins, and every other subclass quietly returns a
    wrong-typed instance."""
    print("\n--- BREAK 1: hardcoded parent ref leaks across subclasses ---")

    class BadBase:
        _instance = None

        def __new__(cls):
            # MISTAKE: BadBase._instance instead of cls._instance
            if BadBase._instance is None:
                BadBase._instance = super().__new__(cls)
            return BadBase._instance

    class Postgres(BadBase): pass
    class MySQL(BadBase):    pass

    a = Postgres()
    b = MySQL()
    print(f"type(a) = {type(a).__name__}")        # Postgres
    print(f"type(b) = {type(b).__name__}")        # Postgres - !!! should be MySQL
    print(f"a is b:  {a is b}")                    # True
    print("MySQL() silently returned a Postgres. Type-confusion bomb.")


# ---------------------------------------------------------------------------
# Break 2 - object.__new__(cls) bypasses our __new__ entirely
# ---------------------------------------------------------------------------

def demo_break_object_new():
    """A determined caller can skip our __new__ by calling object's directly.
    Python provides no way to fully prevent this. It's the strongest
    reminder that Singleton is a discipline, not a security feature."""
    print("\n--- BREAK 2: object.__new__(cls) bypasses our __new__ ---")

    Database._instance = None

    a = Database()
    rogue = object.__new__(Database)            # bypasses our __new__ entirely

    print(f"a is rogue: {a is rogue}")           # False - rogue is brand new
    print(f"isinstance(rogue, Database): "
          f"{isinstance(rogue, Database)}")       # True - it LOOKS legit
    print(f"rogue has connection? "
          f"{hasattr(rogue, 'connection')}")      # False - not initialized
    print("rogue is a half-built Database with no init. Nasty.")


# ---------------------------------------------------------------------------
# Break 3 - pickle creates a new instance on load
# ---------------------------------------------------------------------------

def demo_break_pickle():
    print("\n--- BREAK 3: pickle bypasses singleton on load ---")

    Database._instance = None

    a = Database()
    blob = pickle.dumps(a)

    # Simulate a "fresh process" by clearing the class-level cache
    Database._instance = None

    b = pickle.loads(blob)
    print(f"a is b: {a is b}")                     # False - pickle made a new one


# ---------------------------------------------------------------------------
# Break 4 - Threading race (no lock)
# ---------------------------------------------------------------------------

def demo_break_threading():
    print("\n--- BREAK 4: threading race (no lock) ---")

    class RacyDB:
        _instance = None

        def __new__(cls):
            if cls._instance is None:
                # Widen the race window with a deliberate pause
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
    print("If unique > 1, the singleton invariant broke. "
          "(Fix: double-checked locking - see 02_thread_safe_singleton.py)")


# ---------------------------------------------------------------------------
# Counter-intuitive: copy.deepcopy actually SURVIVES this Singleton
# ---------------------------------------------------------------------------

def demo_deepcopy_survives():
    """A common belief: 'deepcopy breaks the Singleton.' For THIS
    implementation it doesn't - because deepcopy still routes the
    construction through cls.__new__(cls), and our __new__ returns
    the existing instance.

    Where deepcopy DOES break Singletons: when __reduce__ is customized
    or __slots__ is used in a way that bypasses __new__."""
    print("\n--- COUNTER-INTUITIVE: deepcopy survives this implementation ---")
    Database._instance = None

    a = Database()
    b = copy.deepcopy(a)

    print(f"a is b: {a is b}")     # True - because __new__ returned existing
    print("deepcopy went through our __new__ -> got back the existing instance.")
    print("Lesson: this Singleton happens to be deepcopy-safe.")


if __name__ == "__main__":
    demo_break_subclassing()
    demo_break_object_new()
    demo_break_pickle()
    demo_break_threading()
    demo_deepcopy_survives()
