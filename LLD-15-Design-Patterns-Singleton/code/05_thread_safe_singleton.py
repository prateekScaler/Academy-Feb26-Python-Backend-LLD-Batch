"""
Thread-safe Singleton via double-checked locking
================================================
Naive lock = correct but slow (every call acquires the lock).
Double-checked locking = fast path is lock-free; only the FIRST creation
takes the lock.
"""

import threading
import time


# -----------------------------------------------------------------------
# DOUBLE-CHECKED LOCKING
# -----------------------------------------------------------------------
class Database:
    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        # 1st check (cheap, no lock) - fast path for all calls after creation
        if cls._instance is None:
            with cls._lock:
                # 2nd check (under lock) - another thread may have created it
                # while we were waiting on the lock
                if cls._instance is None:
                    print(f"[{threading.current_thread().name}] creating instance")
                    time.sleep(0.01)              # widen the race window
                    cls._instance = super().__new__(cls)
        return cls._instance


def stress_test():
    """Hammer Database() from many threads and confirm only ONE
    instance gets created."""
    print("\n--- Stress test: 20 threads racing on Database() ---")

    Database._instance = None    # reset for the demo
    instances = []

    def make():
        instances.append(Database())

    threads = [
        threading.Thread(target=make, name=f"T{i}") for i in range(20)
    ]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    unique = {id(x) for x in instances}
    print(f"\nCalls: {len(instances)}   Unique instances: {len(unique)}")
    assert len(unique) == 1, "Singleton invariant broken!"
    print("PASS - all 20 threads got the same instance.")


# -----------------------------------------------------------------------
# Same idea for the metaclass approach
# -----------------------------------------------------------------------
class SingletonMeta(type):
    _instances = {}
    _lock = threading.Lock()

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            with cls._lock:
                if cls not in cls._instances:
                    cls._instances[cls] = super().__call__(*args, **kwargs)
        return cls._instances[cls]


class Config(metaclass=SingletonMeta):
    def __init__(self):
        print(f"[{threading.current_thread().name}] Config initialized")
        self.value = 42


def stress_test_metaclass():
    print("\n--- Stress test: metaclass + double-checked locking ---")

    SingletonMeta._instances.clear()    # reset for the demo
    instances = []

    def make():
        instances.append(Config())

    threads = [
        threading.Thread(target=make, name=f"T{i}") for i in range(20)
    ]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    unique = {id(x) for x in instances}
    print(f"\nCalls: {len(instances)}   Unique instances: {len(unique)}")
    assert len(unique) == 1


if __name__ == "__main__":
    stress_test()
    stress_test_metaclass()
