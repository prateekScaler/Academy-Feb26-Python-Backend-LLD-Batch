"""
Practical Singleton use cases
=============================
Three places where Singleton is genuinely the right call:

  1. Configuration manager
  2. Logger
  3. Connection pool

For each one we use the IMPLEMENTATION that fits best:
  - Config:     module-level (Pythonic, simplest)
  - Logger:     decorator (clean class, bolted-on)
  - Pool:       metaclass (could subclass for testing fakes)
"""

import threading


# ============================================================================
# 1) CONFIGURATION MANAGER - module-level
# ============================================================================
class _Config:
    """One place for app-wide settings."""

    def __init__(self):
        self.db_host = "localhost"
        self.db_port = 5432
        self.debug = True
        self.api_key = "secret-xyz"

    def __repr__(self):
        return f"Config(db={self.db_host}:{self.db_port}, debug={self.debug})"


config = _Config()    # the instance


# ============================================================================
# 2) LOGGER - decorator approach
# ============================================================================
def singleton(cls):
    instances = {}

    def get(*args, **kw):
        if cls not in instances:
            instances[cls] = cls(*args, **kw)
        return instances[cls]

    get.__wrapped__ = cls
    return get


@singleton
class Logger:
    def __init__(self):
        self.entries = []

    def info(self, msg):
        self.entries.append(f"[INFO]  {msg}")

    def error(self, msg):
        self.entries.append(f"[ERROR] {msg}")


# ============================================================================
# 3) CONNECTION POOL - metaclass approach (thread-safe)
# ============================================================================
class SingletonMeta(type):
    _instances = {}
    _lock = threading.Lock()

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            with cls._lock:
                if cls not in cls._instances:
                    cls._instances[cls] = super().__call__(*args, **kwargs)
        return cls._instances[cls]


class ConnectionPool(metaclass=SingletonMeta):
    def __init__(self, max_connections=5):
        self.max_connections = max_connections
        self.active = []
        self._cap_lock = threading.Lock()

    def acquire(self):
        with self._cap_lock:
            if len(self.active) >= self.max_connections:
                return None
            conn_id = f"conn-{len(self.active) + 1}"
            self.active.append(conn_id)
            return conn_id

    def release(self, conn_id):
        with self._cap_lock:
            if conn_id in self.active:
                self.active.remove(conn_id)


# ============================================================================
# Demo
# ============================================================================
def demo():
    print("--- Config ---")
    print(f"DB host (from anywhere): {config.db_host}")
    print(config)

    print("\n--- Logger ---")
    Logger().info("application started")
    Logger().info("user signed in")
    Logger().error("payment retry failed")
    print(f"Total entries (one Logger): {len(Logger().entries)}")

    print("\n--- Connection Pool ---")
    p1 = ConnectionPool(max_connections=3)
    p2 = ConnectionPool(max_connections=999)   # second arg IGNORED - same pool
    print(f"p1 is p2: {p1 is p2}")
    print(f"max_connections is still: {p1.max_connections}")

    c1 = p1.acquire()
    c2 = p1.acquire()
    c3 = p1.acquire()
    c4 = p1.acquire()   # None - pool exhausted
    print(f"acquired: {c1}, {c2}, {c3}; 4th attempt: {c4}")
    p1.release(c1)
    print(f"after release: active = {p1.active}")


if __name__ == "__main__":
    demo()
