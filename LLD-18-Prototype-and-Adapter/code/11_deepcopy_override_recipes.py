"""
LLD-18 · Prototype · Example 11 — Overriding __deepcopy__ : 4 real recipes.

Run:  python3 11_deepcopy_override_recipes.py

`copy.deepcopy(self)` is the default body of every `clone()` method. Most
of the time it's exactly right. But for four common shapes you'll want to
override __deepcopy__ to make clone() faster, safer, or correct:

    Recipe 1.  SHARE expensive read-only state across clones
                 (ML model, parser table, big pre-computed lookup).

    Recipe 2.  RESET per-instance runtime state on clone
                 (hp/target/history that belongs to the live instance,
                  not to the blueprint).

    Recipe 3.  REPLACE non-copyable members with fresh handles
                 (sockets, file handles, DB connections — deepcopy
                  raises TypeError on these, so YOU choose what to do).

    Recipe 4.  INVALIDATE caches on clone
                 (the clone needs to re-derive on first use, not inherit
                  the prototype's stale memoised value).
"""

from __future__ import annotations

import copy
import threading
from dataclasses import dataclass, field
from typing import Any


# =====================================================================
# Recipe 1 — SHARE expensive read-only state
# =====================================================================
class Recommender:
    """Embeddings are 800 MB and READ-ONLY. Per-clone history is mutable.

    Default deepcopy would duplicate 800 MB per clone — wasteful and slow.
    """

    def __init__(self) -> None:
        self.embeddings: dict[str, list[float]] = {f"u{i}": [0.0] * 768 for i in range(1000)}
        self.history: list[str] = []

    def __deepcopy__(self, memo: dict) -> "Recommender":
        new = Recommender.__new__(Recommender)
        new.embeddings = self.embeddings   # SHARE the giant dict
        new.history = []                   # fresh per clone
        return new


# =====================================================================
# Recipe 2 — RESET per-instance runtime state
# =====================================================================
@dataclass
class Enemy:
    name: str
    max_hp: int = 100
    hp: int = 100
    target: "Enemy | None" = None

    def __deepcopy__(self, memo: dict) -> "Enemy":
        # Skip carrying over per-battle state into the clone.
        return Enemy(name=self.name, max_hp=self.max_hp,
                     hp=self.max_hp,         # always full HP
                     target=None)            # never carry target


# =====================================================================
# Recipe 3 — REPLACE non-copyable members
# =====================================================================
class Worker:
    """Holds a Lock + a fake 'socket'. Sockets aren't deepcopy-able.

    Default deepcopy raises TypeError (in real code, on real sockets).
    Override to give each clone a fresh handle.
    """

    def __init__(self) -> None:
        self.name = "worker"
        self.task_log: list[str] = []
        self._lock = threading.Lock()       # cannot deepcopy locks
        self._socket = open(__file__, "r")  # cannot deepcopy file handles

    def __deepcopy__(self, memo: dict) -> "Worker":
        new = Worker.__new__(Worker)
        new.name = self.name
        new.task_log = list(self.task_log)   # independent list
        new._lock = threading.Lock()         # fresh handle
        new._socket = open(__file__, "r")    # fresh handle
        return new

    def close(self) -> None:
        self._socket.close()


# =====================================================================
# Recipe 4 — INVALIDATE caches on clone
# =====================================================================
class Report:
    """Holds rows + a memoised _summary_cache.

    On clone, the cache must be invalidated — the clone hasn't computed
    a summary yet, and inheriting the prototype's summary would be a lie.
    """

    def __init__(self, rows: list[dict]) -> None:
        self.rows = rows
        self._summary_cache: dict | None = None

    def summary(self) -> dict:
        if self._summary_cache is None:
            self._summary_cache = {"n": len(self.rows), "computed_for": id(self)}
        return self._summary_cache

    def __deepcopy__(self, memo: dict) -> "Report":
        new = Report.__new__(Report)
        new.rows = copy.deepcopy(self.rows, memo)
        new._summary_cache = None          # force the clone to recompute
        return new


# =====================================================================
# Demos
# =====================================================================
def demo_share() -> None:
    print("--- Recipe 1: SHARE expensive read-only state ---")
    a = Recommender()
    b = copy.deepcopy(a)
    print(f"  a.embeddings is b.embeddings → {a.embeddings is b.embeddings}  (shared, saves ~800 MB)")
    print(f"  a.history    is b.history    → {a.history is b.history}  (independent)")


def demo_reset() -> None:
    print("\n--- Recipe 2: RESET per-instance runtime state ---")
    orc_proto = Enemy(name="orc")
    orc_proto.hp = 35
    orc_proto.target = Enemy(name="player")
    spawn = copy.deepcopy(orc_proto)
    print(f"  prototype: hp={orc_proto.hp} target={orc_proto.target.name if orc_proto.target else None}")
    print(f"  spawn   : hp={spawn.hp} target={spawn.target}  (fresh on every clone)")


def demo_replace() -> None:
    print("\n--- Recipe 3: REPLACE non-copyable members ---")
    a = Worker()
    a.task_log.append("started")
    b = copy.deepcopy(a)
    print(f"  a._lock is b._lock    → {a._lock is b._lock}  (each clone has its own lock)")
    print(f"  a._socket is b._socket → {a._socket is b._socket}  (each clone has its own handle)")
    print(f"  a.task_log = {a.task_log} ; b.task_log = {b.task_log}  (independent)")
    a.close(); b.close()


def demo_invalidate() -> None:
    print("\n--- Recipe 4: INVALIDATE caches on clone ---")
    a = Report(rows=[{"x": 1}, {"x": 2}])
    _ = a.summary()
    print(f"  a._summary_cache (set) = {a._summary_cache}")
    b = copy.deepcopy(a)
    print(f"  b._summary_cache (after clone) = {b._summary_cache}  ← forced to None")
    print(f"  b.summary() = {b.summary()}  ← computed fresh, with b's own id")


if __name__ == "__main__":
    demo_share()
    demo_reset()
    demo_replace()
    demo_invalidate()
    print("\nFour patterns. One rule: __deepcopy__ is YOUR choice — Python defers to it.")
