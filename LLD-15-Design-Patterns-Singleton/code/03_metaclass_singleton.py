"""
Singleton via metaclass
=======================
A metaclass controls how classes themselves behave. Override its
__call__ to intercept ClassName() at the call site - BEFORE __new__
or __init__ run.

Pro: the class stays a real class. isinstance() works. Each subclass
gets its own singleton (cache is keyed on `cls`).

Con: the heaviest machinery; conflicts with ABCMeta unless combined.
"""

class SingletonMeta(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        # __call__ runs when someone writes ClassName(...)
        if cls not in cls._instances:
            cls._instances[cls] = super().__call__(*args, **kwargs)
        return cls._instances[cls]


class Database(metaclass=SingletonMeta):
    def __init__(self):
        print("[Database.__init__] running once")
        self.connection = "Connected"


def demo_happy_path():
    print("\n--- Happy path ---")
    a = Database()
    b = Database()
    print(f"a is b: {a is b}")                  # True
    print(f"isinstance(a, Database) = "
          f"{isinstance(a, Database)}")          # True (works! unlike decorator)


# -----------------------------------------------------------------------
# BREAK 1 - Metaclass conflict with ABCMeta
# -----------------------------------------------------------------------
def demo_break_abc_conflict():
    print("\n--- BREAK 1: metaclass conflict on multi-inheritance ---")
    from abc import ABC
    try:
        class WeirdDB(ABC, metaclass=SingletonMeta):
            pass
    except TypeError as e:
        print(f"TypeError: {e}")

    # Fix: combined metaclass
    from abc import ABCMeta

    class SingletonABCMeta(SingletonMeta, ABCMeta):
        pass

    class GoodDB(ABC, metaclass=SingletonABCMeta):
        pass

    print(f"Combined metaclass works: {GoodDB}")


# -----------------------------------------------------------------------
# BREAK 2 - Bypass via object.__new__
# -----------------------------------------------------------------------
def demo_break_object_new():
    print("\n--- BREAK 2: bypass via object.__new__ ---")
    a = Database()
    b = object.__new__(Database)   # bypasses metaclass!
    # b is not initialized - no .connection
    print(f"a is b: {a is b}")                          # False
    print(f"isinstance(b, Database) = "
          f"{isinstance(b, Database)}")                  # True (looks legit)
    print(f"b has connection? "
          f"{hasattr(b, 'connection')}")                 # False


# -----------------------------------------------------------------------
# BREAK 3 - deepcopy / pickle bypass __call__ too
# -----------------------------------------------------------------------
def demo_break_deepcopy():
    print("\n--- BREAK 3: deepcopy bypasses __call__ ---")
    import copy
    a = Database()
    b = copy.deepcopy(a)
    print(f"a is b: {a is b}")    # False - same vulnerability


# -----------------------------------------------------------------------
# Each subclass becomes its OWN singleton
# -----------------------------------------------------------------------
def demo_subclassing_behavior():
    print("\n--- Subclassing: each subclass is its own singleton ---")

    class Cache(metaclass=SingletonMeta):
        pass

    class RedisCache(Cache):
        pass

    class MemoryCache(Cache):
        pass

    r1, r2 = RedisCache(), RedisCache()
    m1, m2 = MemoryCache(), MemoryCache()

    print(f"r1 is r2: {r1 is r2}")          # True
    print(f"m1 is m2: {m1 is m2}")          # True
    print(f"r1 is m1: {r1 is m1}")          # False - different subclasses
    print(f"type(r1) = {type(r1).__name__}, "
          f"type(m1) = {type(m1).__name__}")


if __name__ == "__main__":
    demo_happy_path()
    demo_break_abc_conflict()
    demo_break_object_new()
    demo_break_deepcopy()
    demo_subclassing_behavior()
