"""
The Hardened Singleton
======================
Combines every defense we've discussed:
  - Metaclass (per-class cache; isinstance() works; subclassing safe)
  - Double-checked locking (threading safe)
  - __copy__ / __deepcopy__ (copy module safe)
  - __reduce__ (pickle safe)

The only attacks it does NOT defend against:
  - object.__new__(Database)  - Python provides no way to block this
  - multiprocessing (a singleton is per-process by definition)
  - the same module imported under two paths
"""

import copy
import pickle
import threading


class SingletonMeta(type):
    """Custom metaclass: __call__ runs when someone writes ClassName(...).
    We cache instances per concrete class, with a lock for thread-safety."""

    _instances = {}
    _lock = threading.Lock()

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:                  # 1st check, no lock
            with cls._lock:
                if cls not in cls._instances:          # 2nd check, under lock
                    cls._instances[cls] = super().__call__(*args, **kwargs)
        return cls._instances[cls]


class Database(metaclass=SingletonMeta):
    def __init__(self):
        self.connection = "postgresql://localhost:5432"

    # Defeat copy / deepcopy
    def __copy__(self):
        return self

    def __deepcopy__(self, memo):
        return self

    # Defeat pickle: tell pickle "to recreate me, call Database()".
    # When pickle.loads runs, it calls Database() - our metaclass
    # returns the existing singleton.
    def __reduce__(self):
        return (Database, ())


# ---------------------------------------------------------------------------
# Verification
# ---------------------------------------------------------------------------

def verify_threading():
    print("--- Threading: 30 threads race to instantiate ---")
    # Reset for clean demo
    SingletonMeta._instances.clear()

    results = []

    def make():
        results.append(Database())

    threads = [threading.Thread(target=make) for _ in range(30)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    unique = {id(x) for x in results}
    print(f"calls: {len(results)}  unique instances: {len(unique)}")
    assert len(unique) == 1, "Singleton invariant broken under threads!"
    print("PASS")


def verify_deepcopy():
    print("\n--- deepcopy: should return the same instance ---")
    a = Database()
    b = copy.deepcopy(a)
    print(f"a is b: {a is b}")
    assert a is b, "deepcopy created a new instance!"
    print("PASS")


def verify_pickle():
    print("\n--- pickle round-trip: should return the same instance ---")
    a = Database()
    blob = pickle.dumps(a)
    b = pickle.loads(blob)
    print(f"a is b: {a is b}")
    assert a is b, "pickle.loads created a new instance!"
    print("PASS")


def verify_isinstance():
    print("\n--- isinstance() still works ---")
    a = Database()
    print(f"isinstance(a, Database) = {isinstance(a, Database)}")
    assert isinstance(a, Database)
    print("PASS")


def verify_subclassing_per_class():
    print("\n--- Subclassing: each subclass gets its OWN singleton ---")

    class Postgres(Database):
        pass

    class MySQL(Database):
        pass

    SingletonMeta._instances.clear()
    p1, p2 = Postgres(), Postgres()
    m1, m2 = MySQL(), MySQL()
    print(f"p1 is p2: {p1 is p2}  (Postgres singleton)")
    print(f"m1 is m2: {m1 is m2}  (MySQL singleton)")
    print(f"p1 is m1: {p1 is m1}  (different across subclasses)")
    assert p1 is p2 and m1 is m2 and p1 is not m1
    print("PASS")


def show_remaining_gap():
    print("\n--- Honest disclosure: what this still cannot stop ---")
    a = Database()
    rogue = object.__new__(Database)  # bypasses the metaclass entirely
    print(f"a is rogue: {a is rogue}  (False - Python lets you do this)")
    print("Defense: code review, not more machinery.")


if __name__ == "__main__":
    verify_threading()
    verify_deepcopy()
    verify_pickle()
    verify_isinstance()
    verify_subclassing_per_class()
    show_remaining_gap()
