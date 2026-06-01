"""
LLD-18 · Prototype · Example 10 — Two real-world Prototype pitfalls.

Run:  python3 10_proto_pitfalls_reset_and_singleton.py

Two patterns that come up in practice but rarely make it into textbooks:

  1.  Reset runtime state on clone.
      The prototype object accumulates state during use (mid-battle HP,
      open DB connections, training history). When you clone, that
      runtime state silently leaks into every new instance. Solution:
      a `clone_fresh()` that resets per-instance fields after copy.

  2.  Protect a Singleton from clone.
      copy.deepcopy bypasses __new__, so cloning a Singleton creates a
      second instance and silently breaks the "exactly one" guarantee.
      Plug __copy__ and __deepcopy__ to return self.
"""

import copy
from dataclasses import dataclass, field
from typing import Optional


# =====================================================================
# PITFALL 1 — Runtime state leaks via Prototype
# =====================================================================
@dataclass
class Orc:
    name: str
    max_hp: int = 100
    hp: int = 100                        # per-instance, mutates in battle
    target: Optional["Orc"] = None       # per-instance, mutates in battle
    inventory: list[str] = field(default_factory=list)

    def clone(self) -> "Orc":
        """Verbatim copy — including runtime battle state. DANGER."""
        return copy.deepcopy(self)

    def clone_fresh(self) -> "Orc":
        """Copy the blueprint, then reset the per-instance fields."""
        new = copy.deepcopy(self)
        new.hp = new.max_hp
        new.target = None
        new.inventory = []
        return new


def demo_reset_state() -> None:
    print("--- Pitfall 1: runtime state leaks via clone() ---")
    orc_proto = Orc(name="orc", inventory=["template-axe"])

    # Some bug or sloppy code uses the prototype as a live participant…
    orc_proto.hp = 35                    # took damage
    orc_proto.target = Orc(name="player")  # acquired a target
    orc_proto.inventory.append("looted-gold")

    leaky = orc_proto.clone()
    print(f"  leaky.hp={leaky.hp}  target={leaky.target.name if leaky.target else None}  "
          f"inventory={leaky.inventory}")
    print("  ↑ Born mid-battle, already aggro'd, holding looted gold. Bug.\n")

    fresh = orc_proto.clone_fresh()
    print(f"  fresh.hp={fresh.hp}  target={fresh.target}  inventory={fresh.inventory}")
    print("  ↑ Reset to a clean spawn — only the immutable blueprint copied.\n")


# =====================================================================
# PITFALL 2 — Singleton silently broken by copy.deepcopy
# =====================================================================
class UnsafeSingleton:
    """Singleton with no copy-protocol guard.

    For a no-state class, deepcopy happens to preserve identity through
    __new__ — but as soon as the singleton holds mutable state, deepcopy
    silently *overwrites* that state when the 'clone' lands on the same
    instance. That's the subtle breakage shown below.
    """
    _instance: Optional["UnsafeSingleton"] = None

    def __new__(cls) -> "UnsafeSingleton":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.feature_flags = {}     # mutable state
        return cls._instance


class SafeSingleton:
    """Singleton with __copy__ / __deepcopy__ guards. Stays single AND keeps state."""
    _instance: Optional["SafeSingleton"] = None

    def __new__(cls) -> "SafeSingleton":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.feature_flags = {}     # mutable state
        return cls._instance

    # Block the copy protocol — both flavours short-circuit to self.
    def __copy__(self) -> "SafeSingleton":
        return self

    def __deepcopy__(self, memo: dict) -> "SafeSingleton":
        return self


def demo_singleton_guard() -> None:
    print("--- Pitfall 2: Singleton + copy.deepcopy ---")

    # ---- Unsafe: deepcopy clobbers the singleton's live state ----
    a = UnsafeSingleton()
    a.feature_flags["dark_mode"] = True
    a.feature_flags["beta_search"] = True

    # Someone takes a "snapshot" of the singleton via deepcopy.
    # Default deepcopy returns the SAME instance (because __new__ is
    # called and returns _instance) — but in the process it replaces
    # a.feature_flags with a deepcopy of the original. Surprise: that
    # erases any concurrent writes that happened to the singleton.
    snapshot_flags = {"dark_mode": True}
    UnsafeSingleton._instance.feature_flags = snapshot_flags  # simulate snapshot
    b = copy.deepcopy(a)

    # Now some other code writes to "the singleton" thinking it's writing live state.
    b.feature_flags["new_homepage"] = True
    print(f"  UnsafeSingleton: a is b -> {a is b}")
    print(f"  a.feature_flags = {a.feature_flags}")
    print( "  ↑ a IS b (same object) AND deepcopy replaced its state mid-flight.")
    print( "    Concurrent writers see surprise wipes — the singleton is no longer trustworthy.\n")

    # ---- Safe: __deepcopy__ short-circuits, state is untouched ----
    x = SafeSingleton()
    x.feature_flags["dark_mode"] = True
    y = copy.deepcopy(x)
    y.feature_flags["beta_search"] = True
    print(f"  SafeSingleton:   x is y -> {x is y}")
    print(f"  x.feature_flags = {x.feature_flags}")
    print("  ↑ Both writes landed on the SAME instance, no surprise wipes.")
    print("    __copy__ / __deepcopy__ returned self instead of round-tripping the state.")


if __name__ == "__main__":
    demo_reset_state()
    demo_singleton_guard()
